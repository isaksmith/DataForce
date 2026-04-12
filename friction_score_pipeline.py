"""
Build a session-level banking friction score using rule-based components.

Logic summary:
1. Load and defensively clean messy CSVs (trim/case normalize, safe timestamp parsing).
2. Canonicalize feature/channel/outcome values and standardize IDs/codes.
3. Engineer retry/experience signals (24h prior attempts/failures, prior session count, failure streak).
4. Join feature cost and customer risk context.
5. Compute editable score components, clamp to 0-100, and bucket into friction bands.
6. Validate utility with support follow-up rates in 24h and 72h windows.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable, Optional, Tuple

import numpy as np
import pandas as pd


CANONICAL_FEATURES = {
    "login",
    "balance_check",
    "transfer",
    "bill_pay",
    "mobile_deposit",
    "card_controls",
    "statement_download",
    "new_account",
    "loan_payment",
    "p2p_payment",
}

SCORE_WEIGHTS: Dict[str, float] = {
    "outcome_abandon": 20.0,
    "outcome_failure": 35.0,
    "has_error_code": 10.0,
    "severe_error_code": 10.0,
    "repeat_attempt_24h": 15.0,
    "prior_failed_attempt_24h": 15.0,
    "multi_fail_streak": 10.0,
    "feature_risk_max": 15.0,
    "customer_new_or_low_experience": 10.0,
}

RISK_CONFIG = {
    "repeat_window_hours": 24,
    "new_enrollment_days": 90,
    "low_experience_prior_sessions_threshold": 3,
}


def normalize_text(value: object) -> str:
    """Normalize free-text by lowercasing and collapsing whitespace."""
    if pd.isna(value):
        return ""
    value = str(value).strip().lower()
    value = re.sub(r"[\t\r\n]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value


def normalize_customer_id(value: object) -> str:
    """Normalize customer IDs to uppercase alphanumeric."""
    text = normalize_text(value).upper()
    return re.sub(r"[^A-Z0-9]", "", text)


def normalize_branch_code(value: object) -> str:
    """Normalize branch code style (e.g., br21 -> BR021)."""
    text = normalize_text(value).upper()
    text = re.sub(r"[^A-Z0-9]", "", text)
    match = re.fullmatch(r"([A-Z]+)(\d+)", text)
    if not match:
        return text
    prefix, digits = match.groups()
    return f"{prefix}{digits.zfill(3)}"


def normalize_channel(value: object) -> str:
    """Map channel variants to canonical values."""
    text = normalize_text(value)
    if any(token in text for token in ("mobile", "app", "ios", "android")):
        return "mobile"
    if any(token in text for token in ("web", "online", "browser", "desktop")):
        return "web"
    return "unknown"


def normalize_outcome(value: object) -> str:
    """Map outcome variants to success/failure/abandon."""
    text = normalize_text(value)
    if any(token in text for token in ("abandon", "aborted", "drop", "quit", "timeout")):
        return "abandon"
    if any(token in text for token in ("fail", "error", "denied", "reject", "unsuccess")):
        return "failure"
    if any(token in text for token in ("success", "complete", "resolved", "ok")):
        return "success"
    return "unknown"


def normalize_feature(value: object) -> str:
    """Map feature variants to canonical feature names."""
    text = normalize_text(value)
    text = text.replace("-", " ").replace("_", " ").replace("/", " ")
    text = re.sub(r"\s+", " ", text).strip()

    exact_map = {
        "signin": "login",
        "sign in": "login",
        "log in": "login",
        "login": "login",
        "check balance": "balance_check",
        "balance check": "balance_check",
        "billpay": "bill_pay",
        "bill pay": "bill_pay",
        "mobile deposit": "mobile_deposit",
        "card controls": "card_controls",
        "statement download": "statement_download",
        "new account": "new_account",
        "loan payment": "loan_payment",
        "p2p payment": "p2p_payment",
    }
    if text in exact_map:
        return exact_map[text]
    if text.replace(" ", "_") in CANONICAL_FEATURES:
        return text.replace(" ", "_")

    keyword_rules: Tuple[Tuple[Iterable[str], str], ...] = (
        (("sign", "login", "authenticate"), "login"),
        (("balance",), "balance_check"),
        (("transfer", "wire", "ach"), "transfer"),
        (("bill", "pay bill"), "bill_pay"),
        (("deposit", "check capture"), "mobile_deposit"),
        (("card", "lock", "unlock"), "card_controls"),
        (("statement", "download"), "statement_download"),
        (("new account", "account opening", "open account"), "new_account"),
        (("loan", "mortgage"), "loan_payment"),
        (("p2p", "person to person", "zelle"), "p2p_payment"),
    )
    for keywords, canonical in keyword_rules:
        if any(word in text for word in keywords):
            return canonical
    return "unknown"


def safe_to_datetime(series: pd.Series) -> pd.Series:
    """Safely parse datetimes from mixed formats."""
    return pd.to_datetime(series, errors="coerce")


def load_csv(path: Path) -> pd.DataFrame:
    """Load CSV in string mode for robust messy-data handling."""
    return pd.read_csv(path, dtype=str, keep_default_na=True)


def compute_prior_failure_streak(is_failure_like: pd.Series) -> pd.Series:
    """
    Compute prior consecutive failure count before each row in sorted session order.
    Example: [F,F,S,F] -> prior streak [0,1,2,0]
    """
    result = np.zeros(len(is_failure_like), dtype=int)
    streak = 0
    for i, failed in enumerate(is_failure_like.fillna(False).astype(bool).tolist()):
        result[i] = streak
        streak = streak + 1 if failed else 0
    return pd.Series(result, index=is_failure_like.index)


def clean_customers(customers: pd.DataFrame) -> pd.DataFrame:
    """Clean customers dataset and derive customer risk helpers."""
    df = customers.copy()
    df.columns = [c.strip() for c in df.columns]

    for col in ("customer_id", "home_branch", "segment", "products_held", "digital_enroll_date", "churn_flag", "tenure_months"):
        if col not in df.columns:
            df[col] = np.nan

    df["customer_id_norm"] = df["customer_id"].map(normalize_customer_id)
    df["home_branch_norm"] = df["home_branch"].map(normalize_branch_code)
    df["segment_norm"] = df["segment"].map(normalize_text)
    df["digital_enroll_ts"] = safe_to_datetime(df["digital_enroll_date"])
    df["tenure_months"] = pd.to_numeric(df["tenure_months"], errors="coerce")
    df["churn_flag"] = pd.to_numeric(df["churn_flag"], errors="coerce").fillna(0).astype(int)

    products = df["products_held"].fillna("").astype(str)
    split_counts = products.str.count(r"[;,|]") + products.str.contains(r"\s&\s| and ", case=False, regex=True).astype(int)
    df["product_count_derived"] = np.where(products.str.strip().eq(""), 0, split_counts + 1)

    keep_cols = [
        "customer_id_norm",
        "tenure_months",
        "segment_norm",
        "digital_enroll_ts",
        "churn_flag",
        "product_count_derived",
        "home_branch_norm",
    ]
    return df[keep_cols].drop_duplicates(subset=["customer_id_norm"])


def clean_error_codes(error_codes: pd.DataFrame) -> pd.DataFrame:
    """Clean error code table and infer severity signals."""
    df = error_codes.copy()
    df.columns = [c.strip() for c in df.columns]
    if "error_code" not in df.columns:
        df["error_code"] = np.nan
    if "description" not in df.columns:
        df["description"] = np.nan

    severe_keywords = ("critical", "fraud", "security", "outage", "system", "timeout", "lockout", "severe")

    df["error_code_norm"] = df["error_code"].fillna("").astype(str).str.strip().str.upper()
    df["error_description_norm"] = df["description"].map(normalize_text)
    df["is_severe_error"] = df["error_description_norm"].apply(
        lambda x: int(any(keyword in x for keyword in severe_keywords))
    )

    return df[["error_code_norm", "error_description_norm", "is_severe_error"]].drop_duplicates("error_code_norm")


def clean_feature_costs(feature_costs: pd.DataFrame) -> pd.DataFrame:
    """Clean feature costs and compute failure cost premium."""
    df = feature_costs.copy()
    df.columns = [c.strip() for c in df.columns]
    for col in ("feature_canonical", "avg_cost_per_success_usd", "avg_cost_per_failure_usd"):
        if col not in df.columns:
            df[col] = np.nan

    df["feature_canonical"] = df["feature_canonical"].map(normalize_feature)
    df["avg_cost_per_success_usd"] = pd.to_numeric(df["avg_cost_per_success_usd"], errors="coerce")
    df["avg_cost_per_failure_usd"] = pd.to_numeric(df["avg_cost_per_failure_usd"], errors="coerce")
    df["failure_cost_premium"] = df["avg_cost_per_failure_usd"] - df["avg_cost_per_success_usd"]
    return df[["feature_canonical", "avg_cost_per_success_usd", "avg_cost_per_failure_usd", "failure_cost_premium"]]


def clean_sessions(digital_sessions: pd.DataFrame) -> pd.DataFrame:
    """Clean digital sessions and standardize core analysis fields."""
    df = digital_sessions.copy()
    df.columns = [c.strip() for c in df.columns]
    for col in (
        "session_id",
        "customer_id",
        "channel",
        "feature_used",
        "session_start",
        "session_end",
        "session_outcome",
        "error_code",
    ):
        if col not in df.columns:
            df[col] = np.nan

    df["session_id_norm"] = df["session_id"].fillna("").astype(str).str.strip()
    df["customer_id_norm"] = df["customer_id"].map(normalize_customer_id)
    df["channel_norm"] = df["channel"].map(normalize_channel)
    df["feature_canonical"] = df["feature_used"].map(normalize_feature)
    df["session_outcome_norm"] = df["session_outcome"].map(normalize_outcome)
    df["session_start_ts"] = safe_to_datetime(df["session_start"])
    df["session_end_ts"] = safe_to_datetime(df["session_end"])
    df["session_ts"] = df["session_end_ts"].fillna(df["session_start_ts"])
    df["error_code_norm"] = df["error_code"].fillna("").astype(str).str.strip().str.upper()
    df["has_error_code"] = (df["error_code_norm"] != "").astype(int)
    df["is_failure_like"] = df["session_outcome_norm"].isin(["failure", "abandon"]).astype(int)
    return df


def engineer_retry_features(sessions: pd.DataFrame, repeat_window_hours: int) -> pd.DataFrame:
    """Compute customer/session history features used in scoring."""
    df = sessions.copy()
    df = df.sort_values(["customer_id_norm", "session_ts", "session_id_norm"], na_position="last").reset_index(drop=True)
    df["prior_session_count"] = df.groupby("customer_id_norm").cumcount()
    df["prior_same_feature_attempts_24h"] = 0.0
    df["prior_same_feature_failures_24h"] = 0.0
    df["prior_failed_streak_same_feature"] = 0

    window_ns = int(pd.Timedelta(hours=repeat_window_hours).value)
    group_cols = ["customer_id_norm", "feature_canonical"]
    for _, grp in df.groupby(group_cols, dropna=False, sort=False):
        grp_sorted = grp.sort_values(["session_ts", "session_id_norm"], na_position="last")
        idx = grp_sorted.index

        streak = compute_prior_failure_streak(grp_sorted["is_failure_like"])
        df.loc[idx, "prior_failed_streak_same_feature"] = streak.values

        valid = grp_sorted.dropna(subset=["session_ts"])
        if valid.empty:
            continue

        ts = valid["session_ts"].astype("int64").to_numpy()
        failures = valid["is_failure_like"].astype(int).to_numpy()
        n = len(valid)

        left_bounds = np.searchsorted(ts, ts - window_ns, side="left")
        positions = np.arange(n)
        prior_attempts = positions - left_bounds

        failure_cumsum = np.cumsum(failures)
        failure_before = np.where(positions > 0, failure_cumsum[positions - 1], 0)
        failure_left = np.where(left_bounds > 0, failure_cumsum[left_bounds - 1], 0)
        prior_failures = failure_before - failure_left

        df.loc[valid.index, "prior_same_feature_attempts_24h"] = prior_attempts
        df.loc[valid.index, "prior_same_feature_failures_24h"] = prior_failures

    df["is_repeat_retry_pattern"] = (
        (df["prior_same_feature_attempts_24h"] > 0)
        & ((df["prior_same_feature_failures_24h"] > 0) | (df["prior_failed_streak_same_feature"] >= 1))
    ).astype(int)
    return df


def build_friction_score(
    sessions: pd.DataFrame,
    customers: pd.DataFrame,
    error_codes: pd.DataFrame,
    feature_costs: pd.DataFrame,
    score_weights: Dict[str, float],
    risk_config: Dict[str, float],
) -> pd.DataFrame:
    """Build score components and final friction_score per session."""
    df = engineer_retry_features(sessions, repeat_window_hours=int(risk_config["repeat_window_hours"]))

    df = df.merge(error_codes, how="left", on="error_code_norm")
    df["is_severe_error"] = df["is_severe_error"].fillna(0).astype(int)

    df = df.merge(feature_costs, how="left", on="feature_canonical")
    df["failure_cost_premium"] = df["failure_cost_premium"].fillna(0.0)

    # Scale feature risk from cost premium to [0, feature_risk_max]
    min_premium = df["failure_cost_premium"].min()
    max_premium = df["failure_cost_premium"].max()
    denom = max(max_premium - min_premium, 1e-9)
    premium_scaled = ((df["failure_cost_premium"] - min_premium) / denom).clip(0, 1)
    df["score_feature_risk"] = premium_scaled * float(score_weights["feature_risk_max"])

    df = df.merge(customers, how="left", on="customer_id_norm")

    # Customer risk: newly enrolled or low digital experience.
    new_days = int(risk_config["new_enrollment_days"])
    low_exp_threshold = int(risk_config["low_experience_prior_sessions_threshold"])
    days_since_enroll = (df["session_ts"] - df["digital_enroll_ts"]).dt.total_seconds() / 86400.0
    is_newly_enrolled = days_since_enroll.between(0, new_days, inclusive="both").fillna(False)
    is_low_experience = df["prior_session_count"].fillna(0) < low_exp_threshold
    df["is_new_or_low_experience"] = (is_newly_enrolled | is_low_experience).astype(int)

    # Score components
    df["score_outcome"] = np.select(
        [
            df["session_outcome_norm"].eq("failure"),
            df["session_outcome_norm"].eq("abandon"),
        ],
        [
            score_weights["outcome_failure"],
            score_weights["outcome_abandon"],
        ],
        default=0.0,
    )

    df["score_error"] = (
        df["has_error_code"] * score_weights["has_error_code"]
        + df["is_severe_error"] * score_weights["severe_error_code"]
    )

    df["score_repeat_attempt"] = (
        (df["prior_same_feature_attempts_24h"] > 0).astype(int) * score_weights["repeat_attempt_24h"]
        + (df["prior_same_feature_failures_24h"] > 0).astype(int) * score_weights["prior_failed_attempt_24h"]
        + (df["prior_failed_streak_same_feature"] >= 2).astype(int) * score_weights["multi_fail_streak"]
    )

    df["score_customer_risk"] = df["is_new_or_low_experience"] * score_weights["customer_new_or_low_experience"]

    df["friction_score_raw"] = (
        df["score_outcome"]
        + df["score_error"]
        + df["score_repeat_attempt"]
        + df["score_feature_risk"]
        + df["score_customer_risk"]
    )
    df["friction_score"] = df["friction_score_raw"].clip(0, 100)

    df["friction_band"] = pd.cut(
        df["friction_score"],
        bins=[-0.001, 33.3333, 66.6667, 100.0],
        labels=["low", "medium", "high"],
        include_lowest=True,
    )
    return df


def clean_support_interactions(support: pd.DataFrame) -> pd.DataFrame:
    """Clean support interactions for follow-up linkage analysis."""
    df = support.copy()
    df.columns = [c.strip() for c in df.columns]
    if "customer_id" not in df.columns:
        df["customer_id"] = np.nan
    if "interaction_ts" not in df.columns:
        df["interaction_ts"] = np.nan

    df["customer_id_norm"] = df["customer_id"].map(normalize_customer_id)
    df["interaction_ts"] = safe_to_datetime(df["interaction_ts"])
    return df[["customer_id_norm", "interaction_ts"]].dropna(subset=["customer_id_norm", "interaction_ts"])


def compute_support_followup_flags(
    sessions: pd.DataFrame, support: pd.DataFrame, hours: int
) -> pd.Series:
    """Flag sessions followed by a support interaction within N hours."""
    if support.empty:
        return pd.Series(False, index=sessions.index)

    tolerance_ns = int(pd.Timedelta(hours=hours).value)
    flags = pd.Series(False, index=sessions.index)

    support_clean = support.dropna(subset=["interaction_ts"]).copy()
    if support_clean.empty:
        return flags

    support_clean["ts_ns"] = support_clean["interaction_ts"].astype("int64")
    support_map = {
        cust: grp["ts_ns"].sort_values().to_numpy()
        for cust, grp in support_clean.groupby("customer_id_norm", sort=False)
    }

    left = sessions[["customer_id_norm", "session_ts"]].copy()
    left = left.dropna(subset=["session_ts"])
    if left.empty:
        return flags
    left["ts_ns"] = left["session_ts"].astype("int64")

    for cust, grp in left.groupby("customer_id_norm", sort=False):
        support_ts = support_map.get(cust)
        if support_ts is None or len(support_ts) == 0:
            continue
        session_ts = grp["ts_ns"].to_numpy()
        right_idx = np.searchsorted(support_ts, session_ts, side="left")

        valid_pos = right_idx < len(support_ts)
        if not np.any(valid_pos):
            continue

        candidate_ts = np.full(len(grp), np.iinfo(np.int64).max, dtype=np.int64)
        candidate_ts[valid_pos] = support_ts[right_idx[valid_pos]]
        matched = (candidate_ts - session_ts) <= tolerance_ns
        flags.loc[grp.index] = matched

    return flags


def print_diagnostics(scored_sessions: pd.DataFrame) -> None:
    """Print summary statistics and analysis outputs."""
    print("\n=== Friction score summary ===")
    print(scored_sessions["friction_score"].describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).to_string())

    print("\n=== Top features by average friction score ===")
    top_features = (
        scored_sessions.groupby("feature_canonical", dropna=False)["friction_score"]
        .agg(["mean", "count"])
        .sort_values("mean", ascending=False)
        .head(15)
    )
    print(top_features.to_string(float_format=lambda v: f"{v:,.2f}"))

    print("\n=== Top error codes by average friction score ===")
    with_error = scored_sessions[scored_sessions["error_code_norm"].ne("")]
    if with_error.empty:
        print("No sessions with error code found.")
    else:
        top_errors = (
            with_error.groupby("error_code_norm")["friction_score"]
            .agg(["mean", "count"])
            .sort_values("mean", ascending=False)
            .head(15)
        )
        print(top_errors.to_string(float_format=lambda v: f"{v:,.2f}"))

    print("\n=== Score component means ===")
    components = [
        "score_outcome",
        "score_error",
        "score_repeat_attempt",
        "score_feature_risk",
        "score_customer_risk",
        "friction_score",
    ]
    print(scored_sessions[components].mean().to_string(float_format=lambda v: f"{v:,.2f}"))


def print_support_validation(scored_sessions: pd.DataFrame) -> None:
    """Print support follow-up rates by friction band for 24h and 72h."""
    for horizon in (24, 72):
        col = f"support_followup_{horizon}h"
        if col not in scored_sessions.columns:
            continue
        summary = (
            scored_sessions.groupby("friction_band", observed=True)[col]
            .agg(session_count="size", followup_rate="mean")
            .reset_index()
        )
        summary["followup_rate"] = summary["followup_rate"].fillna(0) * 100
        print(f"\n=== Support follow-up within {horizon}h by friction band ===")
        print(summary.to_string(index=False, float_format=lambda v: f"{v:,.2f}"))


def run_pipeline(
    data_dir: Path,
    output_path: Optional[Path] = None,
    score_weights: Optional[Dict[str, float]] = None,
) -> pd.DataFrame:
    """Run full friction-score pipeline and return one row per session."""
    score_weights = score_weights or SCORE_WEIGHTS

    print(f"[friction_pipeline] loading customers from {data_dir / 'customers.csv'}", flush=True)
    customers = clean_customers(load_csv(data_dir / "customers.csv"))
    print(f"[friction_pipeline] loading sessions from {data_dir / 'digital_sessions.csv'}", flush=True)
    sessions = clean_sessions(load_csv(data_dir / "digital_sessions.csv"))
    print(f"[friction_pipeline] loading support interactions from {data_dir / 'support_interactions.csv'}", flush=True)
    support = clean_support_interactions(load_csv(data_dir / "support_interactions.csv"))
    print(f"[friction_pipeline] loading error codes from {data_dir / 'error_codes.csv'}", flush=True)
    error_codes = clean_error_codes(load_csv(data_dir / "error_codes.csv"))
    print(f"[friction_pipeline] loading feature costs from {data_dir / 'feature_costs.csv'}", flush=True)
    feature_costs = clean_feature_costs(load_csv(data_dir / "feature_costs.csv"))

    print("[friction_pipeline] building friction scores", flush=True)
    scored = build_friction_score(
        sessions=sessions,
        customers=customers,
        error_codes=error_codes,
        feature_costs=feature_costs,
        score_weights=score_weights,
        risk_config=RISK_CONFIG,
    )

    print("[friction_pipeline] computing support follow-up flags", flush=True)
    scored["support_followup_24h"] = compute_support_followup_flags(scored, support, hours=24)
    scored["support_followup_72h"] = compute_support_followup_flags(scored, support, hours=72)

    print_diagnostics(scored)
    print_support_validation(scored)

    selected_cols = [
        "session_id_norm",
        "customer_id_norm",
        "session_ts",
        "channel_norm",
        "feature_canonical",
        "session_outcome_norm",
        "error_code_norm",
        "prior_session_count",
        "prior_same_feature_attempts_24h",
        "prior_same_feature_failures_24h",
        "prior_failed_streak_same_feature",
        "is_repeat_retry_pattern",
        "failure_cost_premium",
        "tenure_months",
        "segment_norm",
        "digital_enroll_ts",
        "churn_flag",
        "product_count_derived",
        "score_outcome",
        "score_error",
        "score_repeat_attempt",
        "score_feature_risk",
        "score_customer_risk",
        "friction_score",
        "friction_band",
        "support_followup_24h",
        "support_followup_72h",
    ]
    final_df = scored[selected_cols].copy()
    final_df = final_df.rename(columns={"session_id_norm": "session_id", "customer_id_norm": "customer_id"})

    if output_path is None:
        output_path = data_dir / "session_friction_scores.csv"
    final_df.to_csv(output_path, index=False)
    print(f"\nSaved session-level friction scores to: {output_path}")

    return final_df


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Build session-level friction score for banking digital sessions.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("Hack The Plains 2026 Datasets"),
        help="Directory containing input CSV files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional output CSV path for scored sessions.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(data_dir=args.data_dir, output_path=args.output)

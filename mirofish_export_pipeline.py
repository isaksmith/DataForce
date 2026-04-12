"""Export MiroFish-ready simulation artifacts from DataForce banking datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd

from friction_score_pipeline import (
    RISK_CONFIG,
    clean_customers,
    clean_error_codes,
    clean_feature_costs,
    clean_support_interactions,
    load_csv,
    normalize_text,
    run_pipeline,
)


def ensure_artifacts_dir(path: Path) -> Path:
    """Create artifacts directory if needed and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def json_default(value: Any) -> Any:
    """Serialize pandas and datetime-like values safely for JSON output."""
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    return value


def digital_experience_level(prior_sessions: float, enroll_ts: pd.Timestamp | None, reference_ts: pd.Timestamp) -> str:
    """Bucket customer digital experience using enrollment recency and prior sessions."""
    if pd.notna(enroll_ts):
        days_since_enroll = (reference_ts - enroll_ts).days
        if days_since_enroll <= int(RISK_CONFIG["new_enrollment_days"]):
            return "new"
    if pd.isna(prior_sessions):
        return "unknown"
    if prior_sessions <= int(RISK_CONFIG["low_experience_prior_sessions_threshold"]):
        return "low"
    if prior_sessions <= 12:
        return "moderate"
    return "high"


def patience_band(avg_friction_score: float) -> str:
    """Convert mean friction into a rough patience tolerance band."""
    if pd.isna(avg_friction_score):
        return "unknown"
    if avg_friction_score >= 65:
        return "low"
    if avg_friction_score >= 35:
        return "medium"
    return "high"


def build_customer_personas(scored_sessions: pd.DataFrame, customers: pd.DataFrame) -> list[dict[str, Any]]:
    """Create customer persona records for simulation seeding."""
    reference_ts = scored_sessions["session_ts"].max()
    if pd.isna(reference_ts):
        reference_ts = pd.Timestamp.today().normalize()

    customer_rollup = (
        scored_sessions.groupby("customer_id", dropna=False)
        .agg(
            total_sessions=("session_id", "count"),
            avg_friction_score=("friction_score", "mean"),
            high_friction_rate=("friction_band", lambda s: float((s == "high").mean())),
            retry_rate=("is_repeat_retry_pattern", "mean"),
            support_followup_24h_rate=("support_followup_24h", "mean"),
            support_followup_72h_rate=("support_followup_72h", "mean"),
            top_feature=("feature_canonical", lambda s: s.mode().iloc[0] if not s.mode().empty else "unknown"),
            preferred_channel=("channel_norm", lambda s: s.mode().iloc[0] if not s.mode().empty else "unknown"),
            latest_session_ts=("session_ts", "max"),
            prior_session_count_max=("prior_session_count", "max"),
        )
        .reset_index()
    )

    merged = customers.merge(customer_rollup, how="left", left_on="customer_id_norm", right_on="customer_id")
    personas: list[dict[str, Any]] = []
    for row in merged.to_dict(orient="records"):
        prior_sessions = row.get("prior_session_count_max")
        avg_friction = row.get("avg_friction_score")
        segment = row.get("segment_norm") or "unknown"
        support_24h = row.get("support_followup_24h_rate")
        support_72h = row.get("support_followup_72h_rate")

        persona = {
            "customer_id": row.get("customer_id_norm"),
            "segment": segment,
            "tenure_months": row.get("tenure_months"),
            "product_count_derived": row.get("product_count_derived"),
            "home_branch": row.get("home_branch_norm"),
            "churn_flag": row.get("churn_flag"),
            "digital_enroll_ts": row.get("digital_enroll_ts"),
            "digital_experience_level": digital_experience_level(prior_sessions, row.get("digital_enroll_ts"), reference_ts),
            "patience_tolerance": patience_band(avg_friction),
            "support_seeking_tendency": "high" if pd.notna(support_24h) and support_24h >= 0.35 else "medium" if pd.notna(support_24h) and support_24h >= 0.15 else "low",
            "trust_in_digital_banking": "low" if pd.notna(avg_friction) and avg_friction >= 60 else "medium" if pd.notna(avg_friction) and avg_friction >= 35 else "high",
            "preferred_channel": row.get("preferred_channel") or "unknown",
            "likely_feature_mix": row.get("top_feature") or "unknown",
            "total_sessions": row.get("total_sessions"),
            "avg_friction_score": avg_friction,
            "high_friction_rate": row.get("high_friction_rate"),
            "retry_rate": row.get("retry_rate"),
            "support_followup_24h_rate": support_24h,
            "support_followup_72h_rate": support_72h,
            "recent_activity_ts": row.get("latest_session_ts"),
        }

        if segment == "student":
            persona["persona_notes"] = "Mobile-first customer likely to prefer self-service and fast recovery flows."
        elif segment == "wealth":
            persona["persona_notes"] = "High-service-expectation customer with lower tolerance for unresolved friction."
        elif segment == "smb":
            persona["persona_notes"] = "Business-oriented customer likely sensitive to transfer and operational disruptions."
        else:
            persona["persona_notes"] = "General retail-style banking customer persona derived from observed session behavior."

        personas.append(persona)

    return personas


def build_customer_personas_from_customers_only(customers: pd.DataFrame) -> list[dict[str, Any]]:
    """Create baseline personas using only the customers dataset."""
    reference_ts = pd.Timestamp.today().normalize()
    personas: list[dict[str, Any]] = []

    for row in customers.to_dict(orient="records"):
        enroll_ts = row.get("digital_enroll_ts")
        segment = row.get("segment_norm") or "unknown"
        product_count = row.get("product_count_derived")
        tenure_months = row.get("tenure_months")
        churn_flag = row.get("churn_flag")

        experience = digital_experience_level(0, enroll_ts, reference_ts)
        if experience == "unknown" and pd.notna(tenure_months):
            experience = "moderate" if tenure_months >= 24 else "low"

        trust = "low" if churn_flag == 1 else "medium" if experience in {"new", "low"} else "high"
        patience = "low" if churn_flag == 1 else "medium" if experience in {"new", "low"} else "high"

        if segment == "student":
            preferred_channel = "mobile"
            support_tendency = "low"
            notes = "Student persona likely to prefer mobile-first self-service banking."
        elif segment == "wealth":
            preferred_channel = "hybrid"
            support_tendency = "high"
            notes = "Wealth persona likely expects low-friction, high-touch support experiences."
        elif segment == "smb":
            preferred_channel = "web"
            support_tendency = "medium"
            notes = "SMB persona likely values reliability for operational and transfer-heavy tasks."
        else:
            preferred_channel = "mobile" if experience in {"new", "low"} else "web"
            support_tendency = "medium" if churn_flag == 1 else "low"
            notes = "Retail-style persona inferred only from profile attributes without session history."

        if pd.notna(product_count) and product_count >= 4:
            likely_feature_mix = "multi_product_servicing"
        elif pd.notna(product_count) and product_count >= 2:
            likely_feature_mix = "everyday_banking"
        else:
            likely_feature_mix = "single_product_focus"

        personas.append({
            "customer_id": row.get("customer_id_norm"),
            "segment": segment,
            "tenure_months": tenure_months,
            "product_count_derived": product_count,
            "home_branch": row.get("home_branch_norm"),
            "churn_flag": churn_flag,
            "digital_enroll_ts": enroll_ts,
            "digital_experience_level": experience,
            "patience_tolerance": patience,
            "support_seeking_tendency": support_tendency,
            "trust_in_digital_banking": trust,
            "preferred_channel": preferred_channel,
            "likely_feature_mix": likely_feature_mix,
            "persona_notes": notes,
        })

    return personas


def build_session_journeys(scored_sessions: pd.DataFrame) -> list[dict[str, Any]]:
    """Create compact journey summaries by customer and feature."""
    journey_rollup = (
        scored_sessions.sort_values(["customer_id", "session_ts", "session_id"], na_position="last")
        .groupby(["customer_id", "feature_canonical"], dropna=False)
        .agg(
            sessions=("session_id", "count"),
            avg_friction_score=("friction_score", "mean"),
            retry_rate=("is_repeat_retry_pattern", "mean"),
            support_followup_24h_rate=("support_followup_24h", "mean"),
            support_followup_72h_rate=("support_followup_72h", "mean"),
            last_outcome=("session_outcome_norm", "last"),
            common_error=("error_code_norm", lambda s: s.mode().iloc[0] if not s.mode().empty else ""),
            common_channel=("channel_norm", lambda s: s.mode().iloc[0] if not s.mode().empty else "unknown"),
        )
        .reset_index()
    )

    journey_rollup["journey_archetype"] = journey_rollup.apply(classify_journey_archetype, axis=1)
    return journey_rollup.to_dict(orient="records")


def classify_journey_archetype(row: pd.Series) -> str:
    """Assign a journey archetype using aggregate session behavior."""
    if row["support_followup_24h_rate"] >= 0.5:
        return "fail_then_support_escalation"
    if row["retry_rate"] >= 0.5 and row["last_outcome"] == "success":
        return "fail_then_retry_success"
    if row["avg_friction_score"] >= 65:
        return "repeated_failure_or_abandonment"
    if row["avg_friction_score"] < 25 and row["last_outcome"] == "success":
        return "smooth_success_journey"
    return "mixed_friction_journey"


def build_support_patterns(support: pd.DataFrame) -> list[dict[str, Any]]:
    """Aggregate support behavior into simulation-friendly summaries."""
    patterns = (
        support.groupby(["interaction_type_norm", "reason_code_norm"], dropna=False)
        .agg(
            interaction_count=("interaction_id_norm", "count"),
            unresolved_rate=("is_unresolved", "mean"),
        )
        .reset_index()
        .sort_values("interaction_count", ascending=False)
    )
    return patterns.to_dict(orient="records")


def build_feature_risk_lookup(feature_costs: pd.DataFrame) -> list[dict[str, Any]]:
    """Export feature costs as risk lookup records."""
    return feature_costs.sort_values("failure_cost_premium", ascending=False).to_dict(orient="records")


def build_error_taxonomy(error_codes: pd.DataFrame) -> list[dict[str, Any]]:
    """Export error metadata for scenario design."""
    return error_codes.sort_values(["is_severe_error", "error_code_norm"], ascending=[False, True]).to_dict(orient="records")


def build_seed_report(
    personas: list[dict[str, Any]],
    journeys: list[dict[str, Any]],
    support_patterns: list[dict[str, Any]],
    feature_risks: list[dict[str, Any]],
) -> str:
    """Create a concise Markdown summary for MiroFish upload."""
    top_persona_segments = pd.Series([item.get("segment", "unknown") for item in personas]).value_counts().head(5)
    top_journeys = pd.Series([item.get("journey_archetype", "unknown") for item in journeys]).value_counts().head(5)
    top_support_reasons = pd.Series([item.get("reason_code_norm", "unknown") for item in support_patterns]).value_counts().head(5)
    highest_risk_features = pd.DataFrame(feature_risks).head(5)

    lines = [
        "# DataForce Simulation Seed Report",
        "",
        "## Purpose",
        "This report summarizes the DataForce banking data transformed into MiroFish-ready simulation artifacts.",
        "",
        "## Persona segment mix",
    ]
    lines.extend(f"- `{segment}`: {count}" for segment, count in top_persona_segments.items())

    lines.extend([
        "",
        "## Journey archetypes",
    ])
    lines.extend(f"- `{archetype}`: {count}" for archetype, count in top_journeys.items())

    lines.extend([
        "",
        "## Dominant support reasons",
    ])
    lines.extend(f"- `{reason}`" for reason in top_support_reasons.index)

    lines.extend([
        "",
        "## Highest-risk features by failure cost premium",
    ])
    if not highest_risk_features.empty:
        for _, row in highest_risk_features.iterrows():
            lines.append(
                f"- `{row['feature_canonical']}`: premium=${row['failure_cost_premium']:.3f} "
                f"(success=${row['avg_cost_per_success_usd']:.3f}, failure=${row['avg_cost_per_failure_usd']:.3f})"
            )

    lines.extend([
        "",
        "## Recommended initial scenarios",
        "- High-friction login recovery for low-experience customers",
        "- SMB transfer failure with rapid support escalation",
        "- Mobile deposit guidance for image-quality errors",
        "- Wealth segment frustration after unresolved support",
    ])
    return "\n".join(lines) + "\n"


def write_json(path: Path, payload: list[dict[str, Any]]) -> None:
    """Write JSON payload with stable formatting."""
    path.write_text(json.dumps(payload, indent=2, default=json_default), encoding="utf-8")


def export_artifacts(data_dir: Path, artifacts_dir: Path) -> dict[str, Path]:
    """Run DataForce scoring pipeline and export MiroFish seed artifacts."""
    print(f"[mirofish_export] starting export with data_dir={data_dir} artifacts_dir={artifacts_dir}", flush=True)
    artifacts_dir = ensure_artifacts_dir(artifacts_dir)
    scored_output = artifacts_dir / "session_friction_scores.csv"
    print("[mirofish_export] running friction score pipeline", flush=True)
    scored_sessions = run_pipeline(data_dir=data_dir, output_path=scored_output)

    print("[mirofish_export] loading cleaned reference tables", flush=True)
    customers = clean_customers(load_csv(data_dir / "customers.csv"))
    support = clean_support_interactions(load_csv(data_dir / "support_interactions.csv"))
    error_codes = clean_error_codes(load_csv(data_dir / "error_codes.csv"))
    feature_costs = clean_feature_costs(load_csv(data_dir / "feature_costs.csv"))

    print("[mirofish_export] building personas and journey artifacts", flush=True)
    personas = build_customer_personas(scored_sessions, customers)
    journeys = build_session_journeys(scored_sessions)
    support_patterns = build_support_patterns(support)
    feature_risks = build_feature_risk_lookup(feature_costs)
    error_taxonomy = build_error_taxonomy(error_codes)
    seed_report = build_seed_report(personas, journeys, support_patterns, feature_risks)

    output_paths = {
        "scored_sessions": scored_output,
        "customer_personas": artifacts_dir / "customer_personas.json",
        "session_journeys": artifacts_dir / "session_journeys.json",
        "support_patterns": artifacts_dir / "support_patterns.json",
        "feature_risk_lookup": artifacts_dir / "feature_risk_lookup.json",
        "error_taxonomy": artifacts_dir / "error_taxonomy.json",
        "simulation_seed_report": artifacts_dir / "simulation_seed_report.md",
    }

    write_json(output_paths["customer_personas"], personas)
    write_json(output_paths["session_journeys"], journeys)
    write_json(output_paths["support_patterns"], support_patterns)
    write_json(output_paths["feature_risk_lookup"], feature_risks)
    write_json(output_paths["error_taxonomy"], error_taxonomy)
    output_paths["simulation_seed_report"].write_text(seed_report, encoding="utf-8")

    print("[mirofish_export] export completed", flush=True)

    return output_paths


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Export MiroFish-ready banking simulation artifacts.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("Hack The Plains 2026 Datasets"),
        help="Directory containing source CSV files.",
    )
    parser.add_argument(
        "--artifacts-dir",
        type=Path,
        default=Path("artifacts"),
        help="Directory where exported artifacts will be written.",
    )
    parser.add_argument(
        "--customers-only",
        action="store_true",
        help="Export only baseline customer personas from customers.csv.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    if args.customers_only:
        artifacts_dir = ensure_artifacts_dir(args.artifacts_dir)
        print(f"[mirofish_export] exporting customers-only personas from {args.data_dir / 'customers.csv'}", flush=True)
        customers = clean_customers(load_csv(args.data_dir / "customers.csv"))
        personas = build_customer_personas_from_customers_only(customers)
        output_paths = {
            "customer_personas": artifacts_dir / "customer_personas.json",
        }
        write_json(output_paths["customer_personas"], personas)
        print("[mirofish_export] customers-only export completed", flush=True)
    else:
        output_paths = export_artifacts(data_dir=args.data_dir, artifacts_dir=args.artifacts_dir)
    print("Exported MiroFish artifacts:")
    for key, value in output_paths.items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    main()

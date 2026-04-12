from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from dataforce_utils import add_download, apply_global_font

apply_global_font()
REPO_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_DIR / "Hack The Plains 2026 Datasets"

st.markdown(
    """
    <style>
    .friction-card {
        background: rgba(17, 24, 39, 0.72);
        border: 1px solid rgba(148, 163, 184, 0.26);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 14px;
        box-shadow: 0 10px 24px rgba(2, 6, 23, 0.24);
        backdrop-filter: blur(2px);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1.1;
    }
    .kpi-label {
        font-size: 0.92rem;
        color: #cbd5e1;
        margin-top: 4px;
    }
    .top-priority-item {
        border: 1px solid rgba(148, 163, 184, 0.25);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 12px;
        background: rgba(15, 23, 42, 0.6);
    }
    .priority-title {
        font-weight: 700;
        color: #f8fafc;
    }
    .priority-meta {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin-top: 2px;
    }
    .priority-rank {
        display: inline-block;
        min-width: 24px;
        height: 24px;
        line-height: 24px;
        border-radius: 999px;
        text-align: center;
        background: #5d5fef;
        color: white;
        font-weight: 700;
        margin-right: 8px;
        font-size: 0.84rem;
    }
    .tag {
        display: inline-block;
        border-radius: 999px;
        padding: 2px 8px;
        font-size: 0.72rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .tag-blue { background: rgba(59,130,246,0.18); color: #bfdbfe; }
    .tag-pink { background: rgba(236,72,153,0.2); color: #fbcfe8; }
    .tag-orange { background: rgba(245,158,11,0.2); color: #fde68a; }
    .tag-green { background: rgba(16,185,129,0.2); color: #bbf7d0; }
    .insight-bar {
        border: 1px solid rgba(99, 102, 241, 0.35);
        background: rgba(49, 46, 129, 0.36);
        border-radius: 12px;
        padding: 18px 22px;
        margin-top: 14px;
        color: #e2e8f0;
        font-weight: 500;
        text-align: center;
    }
    .insight-title {
        font-size: 1.55rem;
        font-weight: 700;
        margin-bottom: 6px;
        line-height: 1.2;
        color: #f8fafc;
    }
    .insight-text {
        font-size: 1.1rem;
        line-height: 1.5;
    }
    .funnel-wrap {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin-top: 12px;
        margin-bottom: 10px;
    }
    .funnel-box {
        border-radius: 10px;
        color: #ffffff;
        padding: 12px 12px;
        text-align: center;
        font-weight: 700;
    }
    .funnel-sub {
        font-size: 0.78rem;
        font-weight: 500;
        opacity: 0.95;
    }
    .side-panel {
        background: rgba(15, 23, 42, 0.52);
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 14px;
    }
    .section-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #e5e7eb;
        margin-bottom: 10px;
    }
    .section-gap-sm {
        height: 10px;
    }
    .section-gap-md {
        height: 18px;
    }
    .section-gap-lg {
        height: 26px;
    }
    .zoom-icon {
        color: #cbd5e1;
        font-size: 1.1rem;
        line-height: 1.6;
        text-align: right;
        padding-top: 2px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_precomputed_scores() -> pd.DataFrame:
    candidate_paths = [
        DATA_DIR / "session_friction_scores.csv",
        REPO_DIR / "session_friction_scores.csv",
        Path.cwd() / "Hack The Plains 2026 Datasets" / "session_friction_scores.csv",
        Path.cwd() / "session_friction_scores.csv",
    ]
    path = next((p for p in candidate_paths if p.exists()), None)
    if path is None:
        raise FileNotFoundError("session_friction_scores.csv not found in known locations")
    df = pd.read_csv(path, low_memory=False)
    if "session_ts" in df.columns:
        df["session_ts"] = pd.to_datetime(df["session_ts"], errors="coerce")
    return df


def build_feature_view(df: pd.DataFrame) -> pd.DataFrame:
    feature = (
        df.groupby("feature_canonical", dropna=False)
        .agg(
            sessions=("feature_canonical", "size"),
            failure_rate=("session_outcome_norm", lambda s: (s == "failure").mean()),
            abandon_rate=("session_outcome_norm", lambda s: (s == "abandon").mean()),
            friction_mean=("friction_score", "mean"),
            premium_mean=("failure_cost_premium", "mean"),
            support_24h=("support_followup_24h", "mean"),
            support_72h=("support_followup_72h", "mean"),
        )
        .reset_index()
    )
    feature["failure_like_rate"] = feature["failure_rate"] + feature["abandon_rate"]
    feature["avoidable_failure_cost"] = feature["sessions"] * feature["failure_like_rate"] * feature["premium_mean"].clip(lower=0)
    return feature.sort_values("avoidable_failure_cost", ascending=False)


def fmt_money(val: float) -> str:
    if pd.isna(val):
        return "$0"
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val/1_000:.1f}K"
    return f"${val:,.0f}"


def fmt_count(val: int) -> str:
    if val >= 1_000_000:
        return f"{val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"{val/1_000:.0f}K"
    return f"{val:,}"


def feature_label(name: str) -> str:
    return str(name).replace("_", " ").title()


def priority_tags(row: pd.Series) -> str:
    tags = []
    if row["sessions"] >= row["sessions_p75"]:
        tags.append("<span class='tag tag-blue'>High volume</span>")
    if row["premium_mean"] >= row["premium_p75"]:
        tags.append("<span class='tag tag-pink'>High cost</span>")
    if row["failure_like_rate"] >= row["failure_p75"]:
        tags.append("<span class='tag tag-orange'>High friction</span>")
    if row["support_24h"] >= row["support_p75"]:
        tags.append("<span class='tag tag-green'>Support-heavy</span>")
    return "".join(tags[:2])


with st.sidebar:
    st.header("View controls")
    lookback = st.selectbox("Date window", ["Last 30 days", "Last 90 days", "All data"], index=0)

    st.markdown("### Filters")
    channel_filter = st.multiselect("Channel", ["mobile", "web", "unknown"])

try:
    scored_df = load_precomputed_scores()
except FileNotFoundError:
    st.error(
        "Precomputed scores not found. Generate it with:\n\n"
        "`./.venv/bin/python friction_score_pipeline.py --output 'Hack The Plains 2026 Datasets/session_friction_scores.csv'`"
    )
    st.stop()

scored_df = scored_df.dropna(subset=["session_ts"]).copy()
if lookback != "All data" and not scored_df.empty:
    max_ts = scored_df["session_ts"].max()
    days = 30 if lookback == "Last 30 days" else 90
    scored_df = scored_df[scored_df["session_ts"] >= max_ts - pd.Timedelta(days=days)]

if channel_filter:
    scored_df = scored_df[scored_df["channel_norm"].isin(channel_filter)]

feature_df = build_feature_view(scored_df)
if feature_df.empty:
    st.warning("No data available for current filters.")
    st.stop()

total_sessions = int(len(scored_df))
failed_sessions = int(scored_df["session_outcome_norm"].isin(["failure", "abandon"]).sum())
support_24h = int(scored_df["support_followup_24h"].sum())
support_72h = int(scored_df["support_followup_72h"].sum())
unresolved_proxy = max(int(support_72h * 0.21), 0)

avoidable_cost = float(feature_df["avoidable_failure_cost"].sum())
overall_failure_rate = float(failed_sessions / max(total_sessions, 1))
fail_to_support = float(support_24h / max(failed_sessions, 1))

st.markdown("## Digital Friction")
st.markdown("<div class='section-gap-sm'></div>", unsafe_allow_html=True)
st.markdown(
    "<style>h1,h2,h3,[data-testid='stCaptionContainer']{color:#e5e7eb !important;}</style>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4, gap="large")
k1.markdown(
    f"<div class='friction-card'><div class='kpi-value'>{fmt_money(avoidable_cost)}</div><div class='kpi-label'>Est. avoidable failure cost</div></div>",
    unsafe_allow_html=True,
)
k2.markdown(
    f"<div class='friction-card'><div class='kpi-value'>{overall_failure_rate*100:.1f}%</div><div class='kpi-label'>Overall failure rate</div></div>",
    unsafe_allow_html=True,
)
k3.markdown(
    f"<div class='friction-card'><div class='kpi-value'>{fmt_count(total_sessions)}</div><div class='kpi-label'>Sessions analyzed</div></div>",
    unsafe_allow_html=True,
)
k4.markdown(
    f"<div class='friction-card'><div class='kpi-value'>{fail_to_support*100:.0f}%</div><div class='kpi-label'>Failures → support (24h)</div></div>",
    unsafe_allow_html=True,
)

st.markdown("<div class='section-gap-sm'></div>", unsafe_allow_html=True)
main_col, side_col = st.columns([2.6, 1.1], gap="large")
with main_col:
    c_a, c_b = st.columns(2, gap="large")
    show_labels = c_a.checkbox("Show point labels", value=False)
    show_legend = c_b.checkbox("Show legend", value=False)
    zoom_in = float(st.session_state.get("friction_zoom", 1.25))

    plot_df = feature_df.copy()
    fx_q = feature_df["failure_like_rate"].quantile(0.65)
    premium_q = feature_df["premium_mean"].quantile(0.65)
    plot_df["priority_zone"] = (plot_df["failure_like_rate"] >= fx_q) & (plot_df["premium_mean"] >= premium_q)
    x_vals = (plot_df["failure_like_rate"] * 100).clip(lower=0)
    y_vals = plot_df["premium_mean"].clip(lower=0)
    x_low = float(x_vals.quantile(0.02))
    x_high = float(x_vals.quantile(0.98))
    y_low = float(y_vals.quantile(0.02))
    y_high = float(y_vals.quantile(0.98))

    x_pad = max((x_high - x_low) * 0.15, 0.8)
    y_pad = max((y_high - y_low) * 0.15, 0.25)
    x_base_min = max(0.0, x_low - x_pad)
    x_base_max = max(x_base_min + 1.2, x_high + x_pad)
    y_base_min = max(0.0, y_low - y_pad)
    y_base_max = max(y_base_min + 0.5, y_high + y_pad)

    x_center = (x_base_min + x_base_max) / 2
    y_center = (y_base_min + y_base_max) / 2
    x_half = max((x_base_max - x_base_min) / (2 * zoom_in), 0.6)
    y_half = max((y_base_max - y_base_min) / (2 * zoom_in), 0.25)

    x_min = max(0.0, x_center - x_half)
    x_max = x_center + x_half
    y_min = max(0.0, y_center - y_half)
    y_max = y_center + y_half

    fig = px.scatter(
        plot_df,
        x=plot_df["failure_like_rate"] * 100,
        y="premium_mean",
        size="sessions",
        size_max=64,
        color="feature_canonical",
        hover_data={
            "sessions": True,
            "failure_like_rate": ":.2%",
            "premium_mean": ":.2f",
            "avoidable_failure_cost": ":,.0f",
        },
        labels={"x": "Failure Rate (%)", "premium_mean": "Failure Cost Premium ($)"},
        title="Feature Failure Risk vs Failure Cost Premium",
    )
    fig.update_traces(opacity=0.86, marker=dict(line=dict(width=1, color="white"), sizemin=10))
    fig.update_layout(
        xaxis_range=[x_min, x_max],
        yaxis_range=[y_min, y_max],
        plot_bgcolor="rgba(15,23,42,0.42)",
        paper_bgcolor="rgba(15,23,42,0.2)",
        font=dict(color="#cbd5e1"),
        margin=dict(l=20, r=20, t=45, b=20),
        height=560,
        showlegend=show_legend,
        xaxis=dict(gridcolor="rgba(148,163,184,0.20)", zerolinecolor="rgba(148,163,184,0.18)"),
        yaxis=dict(gridcolor="rgba(148,163,184,0.20)", zerolinecolor="rgba(148,163,184,0.18)"),
        legend_title_text="Feature",
    )
    fig.add_shape(
        type="rect",
        x0=fx_q * 100,
        y0=premium_q,
        x1=x_max,
        y1=y_max,
        line=dict(color="#6b70f7", width=2, dash="dot"),
        fillcolor="rgba(107,112,247,0.07)",
    )
    fig.add_annotation(
        x=(fx_q * 100 + x_max) / 2,
        y=y_max,
        text="<b>Priority Zone</b><br><span style='font-size:11px'>High impact → Fix now</span>",
        showarrow=False,
        yshift=16,
        align="left",
        bgcolor="rgba(15,23,42,0.82)",
        bordercolor="rgba(148,163,184,0.45)",
        borderwidth=1,
    )
    if show_labels:
        for row in plot_df.head(6).itertuples():
            fig.add_annotation(
                x=row.failure_like_rate * 100,
                y=row.premium_mean,
                text=feature_label(row.feature_canonical).lower().replace(" ", "_"),
                showarrow=False,
                yshift=18,
                font=dict(size=11, color="#e2e8f0"),
                bgcolor="rgba(15,23,42,0.82)",
                bordercolor="rgba(148,163,184,0.45)",
                borderwidth=1,
            )
    st.plotly_chart(fig, use_container_width=True)
    caption_col, zoom_col = st.columns([3.6, 1.1], gap="small")
    caption_col.caption("Bubble size = session volume · Top-right = fix first")
    with zoom_col:
        icon_col, slider_col = st.columns([0.25, 1.0], gap="small")
        icon_col.markdown("<div class='zoom-icon'>🔍</div>", unsafe_allow_html=True)
        slider_col.slider(
            "Zoom",
            min_value=1.0,
            max_value=1.6,
            value=zoom_in,
            step=0.05,
            key="friction_zoom",
            label_visibility="collapsed",
        )

with side_col:
    st.markdown("<div class='section-title'>Top Priorities</div>", unsafe_allow_html=True)
    top_priorities = feature_df.head(4).copy()
    top_priorities["sessions_p75"] = feature_df["sessions"].quantile(0.75)
    top_priorities["premium_p75"] = feature_df["premium_mean"].quantile(0.75)
    top_priorities["failure_p75"] = feature_df["failure_like_rate"].quantile(0.75)
    top_priorities["support_p75"] = feature_df["support_24h"].quantile(0.75)
    for i, row in enumerate(top_priorities.itertuples(), start=1):
        row_s = pd.Series(row._asdict())
        tags_html = priority_tags(row_s)
        st.markdown(
            (
                "<div class='top-priority-item'>"
                f"<div><span class='priority-rank'>{i}</span><span class='priority-title'>{feature_label(row.feature_canonical)}</span></div>"
                f"<div class='priority-meta'>{fmt_count(int(row.sessions))} sessions · {row.failure_like_rate*100:.0f}% fail · ${row.premium_mean:.2f} premium</div>"
                f"<div style='margin-top:6px'>{tags_html}</div>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )
    st.markdown("<div class='section-title'>Friction Funnel (All Features)</div>", unsafe_allow_html=True)
    st.markdown(
        (
            "<div class='funnel-wrap'>"
            f"<div class='funnel-box' style='background:#5d5fef'>{fmt_count(total_sessions)}<div class='funnel-sub'>Sessions</div></div>"
            f"<div class='funnel-box' style='background:#ec4899'>{fmt_count(failed_sessions)}<div class='funnel-sub'>Failed ({overall_failure_rate*100:.1f}%)</div></div>"
            f"<div class='funnel-box' style='background:#f59e0b'>{fmt_count(support_24h)}<div class='funnel-sub'>Support ({fail_to_support*100:.0f}%)</div></div>"
            f"<div class='funnel-box' style='background:#10b981'>{fmt_count(unresolved_proxy)}<div class='funnel-sub'>Unresolved (proxy)</div></div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )

top4 = feature_df.head(4)
priority_share = top4["avoidable_failure_cost"].sum() / max(avoidable_cost, 1e-9)
st.markdown("<div class='section-gap-md'></div>", unsafe_allow_html=True)
st.markdown(
    (
        "<div class='insight-bar'>"
        "<div class='insight-title'>Insight</div>"
        "<div class='insight-text'>"
        f"{len(top4)} features in the priority zone drive <strong>{priority_share*100:.0f}%</strong> "
        f"of avoidable failure cost. Addressing them could reduce support exposure by approximately "
        f"<strong>{fmt_money(top4['avoidable_failure_cost'].sum())}</strong>."
        "</div>"
        "</div>"
    ),
    unsafe_allow_html=True,
)
st.markdown("<div class='section-gap-lg'></div>", unsafe_allow_html=True)

with st.expander("Scored session output", expanded=False):
    st.caption("Use this table for QA/export while keeping the dashboard view clean.")
    preferred_cols = [
        ("session_id", ["session_id_norm", "session_id"]),
        ("customer_id", ["customer_id_norm", "customer_id"]),
        ("session_ts", ["session_ts"]),
        ("channel_norm", ["channel_norm"]),
        ("feature_canonical", ["feature_canonical"]),
        ("session_outcome_norm", ["session_outcome_norm"]),
        ("error_code_norm", ["error_code_norm"]),
        ("friction_score", ["friction_score"]),
        ("friction_band", ["friction_band"]),
        ("support_followup_24h", ["support_followup_24h"]),
        ("support_followup_72h", ["support_followup_72h"]),
    ]
    selected_cols = []
    rename_map = {}
    for canonical_name, candidates in preferred_cols:
        source_col = next((col for col in candidates if col in scored_df.columns), None)
        if source_col is not None:
            selected_cols.append(source_col)
            rename_map[source_col] = canonical_name
    out_df = scored_df[selected_cols].rename(columns=rename_map)
    add_download(out_df, "session_friction_scores_filtered.csv")
    st.dataframe(out_df.head(400), use_container_width=True)

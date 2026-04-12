from pathlib import Path
import json
import subprocess

import streamlit as st

try:
    import pandas as pd
    import plotly.express as px
    from streamlit_agraph import Config as AGraphConfig, Edge, Node, agraph
    from dataforce_utils import apply_global_font, load_simulation_frames, run_mesa_simulation_from_sample
    _DEPS_OK = True
except Exception as _import_err:
    _DEPS_OK = False
    _import_err_msg = str(_import_err)

if not _DEPS_OK:
    st.title("Customer Simulations - In Progress")
    st.warning(
        "This page is unavailable in the current environment because one or more "
        f"dependencies could not be loaded: `{_import_err_msg}`"
    )
    st.stop()

apply_global_font()
REPO_DIR = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_DIR / "artifacts"
# Prefer full file; fall back to committed sample for cloud deployments
_FULL_PATH = ARTIFACTS_DIR / "customer_personas.json"
_SAMPLE_PATH = ARTIFACTS_DIR / "customer_personas_sample.json"
PERSONA_PATH = _FULL_PATH if _FULL_PATH.exists() else _SAMPLE_PATH

st.title("Customer Simulations - In Progress")

st.markdown(
    """
    <style>
    .sim-card {
        background: rgba(15, 23, 42, 0.68);
        border: 1px solid rgba(148, 163, 184, 0.24);
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 14px;
    }
    .sim-label {
        font-size: 0.84rem;
        color: #cbd5e1;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .sim-value {
        font-size: 1.95rem;
        font-weight: 700;
        color: #f8fafc;
        margin-top: 4px;
    }
    .sim-note {
        color: #cbd5e1;
        font-size: 0.92rem;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_personas() -> pd.DataFrame:
    if not PERSONA_PATH.exists():
        raise FileNotFoundError(PERSONA_PATH)
    with PERSONA_PATH.open("r", encoding="utf-8") as f:
        payload = json.load(f)
    return pd.DataFrame(payload)


def regenerate_personas() -> tuple[bool, str]:
    """Regenerate customer personas from customers.csv."""
    result = subprocess.run(
        ["python3", "-u", str(REPO_DIR / "mirofish_export_pipeline.py"), "--customers-only"],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
    )
    output = (result.stdout or "") + ("\n" + result.stderr if result.stderr else "")
    return result.returncode == 0, output.strip()


def persona_file_status() -> dict:
    """Return simple metadata about the persona artifact."""
    if not PERSONA_PATH.exists():
        return {"exists": False, "modified": None, "size_kb": None}
    stat = PERSONA_PATH.stat()
    return {
        "exists": True,
        "modified": pd.Timestamp(stat.st_mtime, unit="s").strftime("%Y-%m-%d %H:%M:%S"),
        "size_kb": round(stat.st_size / 1024, 1),
    }


def format_graph_label(value: str) -> str:
    """Convert snake_case graph labels into readable title text."""
    return str(value).replace("_", " ").strip().title()


@st.cache_data(show_spinner=False)
def build_persona_graph(personas_df: pd.DataFrame) -> tuple[list[dict], list[tuple[str, str, str]]]:
    segment_counts = personas_df["segment"].fillna("unknown").astype(str).value_counts().to_dict()
    experience_counts = personas_df["digital_experience_level"].fillna("unknown").astype(str).value_counts().to_dict()
    channel_counts = personas_df["preferred_channel"].fillna("unknown").astype(str).value_counts().to_dict()
    support_counts = personas_df["support_seeking_tendency"].fillna("unknown").astype(str).value_counts().to_dict()
    trust_counts = personas_df["trust_in_digital_banking"].fillna("unknown").astype(str).value_counts().to_dict()

    nodes = [
        {"id": "persona_artifact", "label": "customer_personas.json", "group": "dataset", "details": f"Generated persona seed artifact with {len(personas_df):,} customer personas."},
        {"id": "customer_persona", "label": "Customer Persona", "group": "entity", "details": "Generated customer-agent seed used for simulation and scenario design."},
        {"id": "segment", "label": format_graph_label("segment"), "group": "attribute", "details": "Customer segment classification."},
        {"id": "digital_experience_level", "label": format_graph_label("digital_experience_level"), "group": "attribute", "details": "Inferred experience bucket from enrollment and activity context."},
        {"id": "preferred_channel", "label": format_graph_label("preferred_channel"), "group": "attribute", "details": "Likely preferred digital channel."},
        {"id": "support_seeking_tendency", "label": format_graph_label("support_seeking_tendency"), "group": "attribute", "details": "Likelihood of seeking support after friction."},
        {"id": "trust_in_digital_banking", "label": format_graph_label("trust_in_digital_banking"), "group": "attribute", "details": "Derived trust level in digital banking."},
    ]

    links = [
        ("persona_artifact", "customer_persona", "contains"),
        ("customer_persona", "segment", "classified by"),
        ("customer_persona", "digital_experience_level", "has"),
        ("customer_persona", "preferred_channel", "prefers"),
        ("customer_persona", "support_seeking_tendency", "expresses"),
        ("customer_persona", "trust_in_digital_banking", "retains"),
    ]

    for prefix, counts, group in [
        ("segment", segment_counts, "segment_value"),
        ("experience", experience_counts, "experience_value"),
        ("channel", channel_counts, "channel_value"),
        ("support", support_counts, "support_value"),
        ("trust", trust_counts, "trust_value"),
    ]:
        parent = {
            "segment": "segment",
            "experience": "digital_experience_level",
            "channel": "preferred_channel",
            "support": "support_seeking_tendency",
            "trust": "trust_in_digital_banking",
        }[prefix]
        for value, count in sorted(counts.items()):
            node_id = f"{prefix}::{value}"
            nodes.append({
                "id": node_id,
                "label": format_graph_label(value),
                "group": group,
                "details": f"{count:,} personas with value '{value}'.",
            })
            links.append((parent, node_id, "maps to"))

    return nodes, links


def render_persona_graph(personas_df: pd.DataFrame) -> None:
    nodes, links = build_persona_graph(personas_df)
    color_map = {
        "dataset": "#2563eb",
        "entity": "#7c3aed",
        "attribute": "#0f766e",
        "segment_value": "#f59e0b",
        "experience_value": "#6366f1",
        "channel_value": "#ec4899",
        "support_value": "#ef4444",
        "trust_value": "#14b8a6",
    }

    graph_nodes = []
    for node in nodes:
        if node["group"] in {"dataset", "entity"}:
            size = 36
        elif node["group"] == "attribute":
            size = 28
        else:
            size = 22

        graph_nodes.append(
            Node(
                id=node["id"],
                label=node["label"],
                title=node["details"],
                size=size,
                color=color_map.get(node["group"], "#334155"),
                shape="dot",
                font={"color": "#ffffff", "strokeWidth": 6, "strokeColor": "#000000", "size": 14},
            )
        )

    graph_edges = [
        Edge(source=source, target=target, label=label, color="#94a3b8")
        for source, target, label in links
    ]

    config = AGraphConfig(
        width="100%",
        height=760,
        directed=True,
        physics=True,
        hierarchical=False,
        nodeHighlightBehavior=True,
        highlightColor="#dbeafe",
        collapsible=False,
        staticGraph=False,
        staticGraphWithDragAndDrop=False,
        link={'labelProperty': 'label', 'renderLabel': True},
        nodeSpacing=220,
        levelSeparation=220,
        springLength=260,
        springConstant=0.02,
        damping=0.35,
    )

    agraph(nodes=graph_nodes, edges=graph_edges, config=config)

    with st.expander("Persona relationship notes"):
        for source, target, label in links:
            st.markdown(f"- `{source}` **{label}** `{target}`")


frames = load_simulation_frames()
customers = frames["customers"].copy()
costs = frames["costs"].copy()

try:
    personas = load_personas()
except FileNotFoundError:
    st.error(
        "No persona artifact found. Expected `artifacts/customer_personas.json` or "
        "`artifacts/customer_personas_sample.json`. Generate one with: "
        "`python3 -u mirofish_export_pipeline.py --customers-only`."
    )
    st.stop()

if PERSONA_PATH == _SAMPLE_PATH:
    st.info(
        "Running on a representative **5,000-persona sample** (stratified by segment). "
        "For the full dataset, generate `artifacts/customer_personas.json` locally.",
        icon="ℹ️",
    )

segment_options = sorted(personas["segment"].dropna().astype(str).unique().tolist())
feature_options = sorted(costs["feature_canonical"].dropna().astype(str).str.replace("_", " ").str.title().unique().tolist())
channel_options = ["Mobile", "Web"]
error_options = ["NA", "AUTH_FAIL", "TIMEOUT", "E010", "E020", "E050", "E099"]
intervention_options = ["None", "Tooltip", "Guided Help", "Chatbot Intercept", "Agent Escalation"]

st.markdown("### Simulation controls")

status = persona_file_status()
artifact_col, action_col = st.columns([1.6, 1.0])
with artifact_col:
    st.markdown("#### Persona artifact")
    if status["exists"]:
        st.success(f"Loaded artifact • {status['size_kb']} KB")
        st.caption(f"Updated: {status['modified']}")
    else:
        st.error("Persona artifact missing")
with action_col:
    st.markdown("#### Refresh personas")
    if st.button("Regenerate personas", use_container_width=True):
        with st.spinner("Rebuilding `customer_personas.json`..."):
            ok, output = regenerate_personas()
        if ok:
            load_personas.clear()
            st.success("Personas regenerated successfully.")
            st.code(output or "Completed.")
            st.rerun()
        else:
            st.error("Persona regeneration failed.")
            st.code(output or "No output returned.")

control_cols = st.columns(3)
with control_cols[0]:
    selected_segment = st.selectbox("Persona segment", ["All segments"] + segment_options)
    feature = st.selectbox("Feature", feature_options, index=feature_options.index("Transfer") if "Transfer" in feature_options else 0)
with control_cols[1]:
    channel = st.selectbox("Channel", channel_options, index=0)
    error_code = st.selectbox("Error code", error_options, index=0)
with control_cols[2]:
    intervention = st.selectbox("Intervention", intervention_options, index=2)
    num_agents = st.slider("Simulated customers", min_value=25, max_value=500, value=150, step=25)

if selected_segment != "All segments":
    segment_personas = personas[personas["segment"].astype(str) == selected_segment].copy()
else:
    segment_personas = personas.copy()

if segment_personas.empty:
    st.warning("No personas match the selected segment.")
    st.stop()

st.markdown("### Persona Knowledge Graph")
render_persona_graph(segment_personas)

st.markdown("### Persona mix")
col1, col2 = st.columns(2)
with col1:
    segment_chart = px.histogram(
        segment_personas,
        x="digital_experience_level",
        color="segment",
        barmode="group",
        title="Digital experience distribution",
    )
    st.plotly_chart(segment_chart, use_container_width=True)
with col2:
    support_chart = px.histogram(
        segment_personas,
        x="support_seeking_tendency",
        color="trust_in_digital_banking",
        barmode="group",
        title="Support tendency vs. trust",
    )
    st.plotly_chart(support_chart, use_container_width=True)

run_sim = st.button("Run simulation", type="primary", use_container_width=True)

if run_sim:
    population = customers.copy()
    if selected_segment != "All segments":
        population = population[population["segment"].astype(str).str.lower() == selected_segment.lower()]

    if population.empty:
        st.error("No matching customer rows found in `customers.csv` for this segment.")
        st.stop()

    results = run_mesa_simulation_from_sample(
        num_agents=num_agents,
        customers=population,
        feature=feature,
        channel=channel,
        error_code=error_code,
        intervention=intervention,
        costs=costs,
    )

    if results.empty:
        st.warning("Simulation returned no results.")
        st.stop()

    outcome_summary = results.groupby("Outcome", dropna=False).agg(
        customers=("Outcome", "size"),
        avg_friction=("FrictionScore", "mean"),
        avg_cost=("EstimatedCost", "mean"),
    ).reset_index()

    k1, k2, k3 = st.columns(3)
    k1.metric("Avg friction score", f"{results['FrictionScore'].mean():.1f}")
    k2.metric("Avg escalation probability", f"{results['EscalationProbability'].mean() * 100:.1f}%")
    k3.metric("Avg estimated cost", f"${results['EstimatedCost'].mean():.2f}")

    outcome_fig = px.bar(
        outcome_summary,
        x="Outcome",
        y="customers",
        color="Outcome",
        title="Simulated outcome distribution",
        text="customers",
    )
    st.plotly_chart(outcome_fig, use_container_width=True)

    friction_fig = px.box(
        results,
        x="segment",
        y="FrictionScore",
        color="Outcome",
        title="Friction score spread by sampled segment",
    )
    st.plotly_chart(friction_fig, use_container_width=True)

    cost_fig = px.histogram(
        results,
        x="EstimatedCost",
        color="Outcome",
        nbins=25,
        title="Estimated support cost distribution",
    )
    st.plotly_chart(cost_fig, use_container_width=True)

    st.markdown("### Sample persona records")
    st.dataframe(
        segment_personas[[
            "customer_id",
            "segment",
            "digital_experience_level",
            "preferred_channel",
            "support_seeking_tendency",
            "trust_in_digital_banking",
            "persona_notes",
        ]].head(50),
        use_container_width=True,
    )

    st.markdown("### Simulation output sample")
    st.dataframe(results.head(100), use_container_width=True)

    persona_download = segment_personas.to_csv(index=False).encode("utf-8")
    result_download = results.to_csv(index=False).encode("utf-8")
    d1, d2 = st.columns(2)
    with d1:
        st.download_button(
            "Download filtered personas",
            data=persona_download,
            file_name="filtered_customer_personas.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with d2:
        st.download_button(
            "Download simulation results",
            data=result_download,
            file_name="customer_simulation_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    dominant_outcome = outcome_summary.sort_values("customers", ascending=False).iloc[0]["Outcome"]
    explanation = (
        f"For the selected {feature.lower()} scenario on {channel.lower()}, the '{intervention}' intervention produced "
        f"'{dominant_outcome}' most often across {num_agents} simulated customers. "
        f"This run uses persona-derived channel preference, support tendency, and trust signals from `customers.csv`."
    )
    st.markdown("### Scenario summary")
    st.info(explanation)
else:
    pass

st.markdown("### How this page maps to MiroFish")
st.markdown(
    """
- Uses `artifacts/customer_personas.json` as the first customer-agent seed.
- Uses `customers.csv` to sample a simulation population.
- Uses `feature_costs.csv` to approximate failure and support cost.
- Provides a hackathon-friendly preview before wiring full MiroFish backend execution.
"""
)
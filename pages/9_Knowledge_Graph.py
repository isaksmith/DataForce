import streamlit as st

try:
    from streamlit_agraph import Config as AGraphConfig, Edge, Node, agraph
    _AGRAPH_OK = True
    _AGRAPH_ERR = ""
except Exception as _err:
    _AGRAPH_OK = False
    _AGRAPH_ERR = str(_err)

from dataforce_utils import apply_global_font

apply_global_font()
st.title("Knowledge Graph")
st.caption("Explore a separate relationship graph for each dataset to understand its keys, dependencies, and downstream links.")

if not _AGRAPH_OK:
    st.warning(
        "Interactive graph rendering is unavailable in this deployment environment "
        f"because `streamlit_agraph` could not be loaded: `{_AGRAPH_ERR}`"
    )


def format_graph_label(value: str) -> str:
    """Convert snake_case graph labels into readable title text."""
    return str(value).replace("_", " ").strip().title()


def render_interactive_graph(graph: dict) -> None:
    if not _AGRAPH_OK:
        return

    color_map = {
        "dataset": "#2563eb",
        "field": "#059669",
        "key": "#111827",
        "related": "#d97706",
    }

    graph_nodes = []
    for node in graph["nodes"]:
        size = 36 if node["group"] == "dataset" else 28 if node["group"] == "key" else 24
        graph_nodes.append(
            Node(
                id=node["id"],
                label=format_graph_label(node["label"]),
                title=node["details"],
                size=size,
                color=color_map.get(node["group"], "#334155"),
                shape="dot",
                font={"color": "#ffffff", "strokeWidth": 6, "strokeColor": "#000000", "size": 14},
            )
        )

    graph_edges = [
        Edge(source=source, target=target, label=label, color="#94a3b8")
        for source, target, label in graph["links"]
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
        springLength=240,
        springConstant=0.02,
        damping=0.35,
    )

    agraph(nodes=graph_nodes, edges=graph_edges, config=config)


graphs = {
    "customers.csv": {
        "nodes": [
            {"id": "customers", "label": "customers.csv", "group": "dataset", "details": "Customer master profile table"},
            {"id": "customer_id", "label": "customer_id", "group": "key", "details": "Primary key"},
            {"id": "segment", "label": "segment", "group": "field", "details": "Customer segment"},
            {"id": "tenure_months", "label": "tenure_months", "group": "field", "details": "Customer tenure"},
            {"id": "home_branch", "label": "home_branch", "group": "field", "details": "Branch reference"},
            {"id": "branches", "label": "branches.csv", "group": "related", "details": "Resolved branch location data"},
            {"id": "digital_sessions", "label": "digital_sessions.csv", "group": "related", "details": "Behavior linked by customer_id"},
            {"id": "support_interactions", "label": "support_interactions.csv", "group": "related", "details": "Support linked by customer_id"},
        ],
        "links": [
            ("customers", "customer_id", "contains"),
            ("customers", "segment", "describes"),
            ("customers", "tenure_months", "measures"),
            ("customers", "home_branch", "contains"),
            ("home_branch", "branches", "maps to"),
            ("customer_id", "digital_sessions", "joins to"),
            ("customer_id", "support_interactions", "joins to"),
        ],
    },
    "digital_sessions.csv": {
        "nodes": [
            {"id": "digital_sessions", "label": "digital_sessions.csv", "group": "dataset", "details": "Digital behavior and failure event stream"},
            {"id": "customer_id", "label": "customer_id", "group": "key", "details": "Links back to customer profile"},
            {"id": "feature_used", "label": "feature_used", "group": "field", "details": "Feature or journey step used"},
            {"id": "session_outcome", "label": "session_outcome", "group": "field", "details": "Success, error, abandon"},
            {"id": "error_code", "label": "error_code", "group": "field", "details": "Session-level error output"},
            {"id": "error_codes", "label": "error_codes.csv", "group": "related", "details": "Error descriptions"},
            {"id": "feature_costs", "label": "feature_costs.csv", "group": "related", "details": "Cost weighting by feature"},
            {"id": "support_interactions", "label": "support_interactions.csv", "group": "related", "details": "Potential downstream escalation"},
        ],
        "links": [
            ("digital_sessions", "customer_id", "contains"),
            ("digital_sessions", "feature_used", "tracks"),
            ("digital_sessions", "session_outcome", "tracks"),
            ("digital_sessions", "error_code", "contains"),
            ("error_code", "error_codes", "defines"),
            ("feature_used", "feature_costs", "maps to"),
            ("digital_sessions", "support_interactions", "may escalate to"),
        ],
    },
    "support_interactions.csv": {
        "nodes": [
            {"id": "support_interactions", "label": "support_interactions.csv", "group": "dataset", "details": "Support demand and resolution events"},
            {"id": "customer_id", "label": "customer_id", "group": "key", "details": "Links back to customer profile"},
            {"id": "interaction_type", "label": "interaction_type", "group": "field", "details": "Call, chat, branch, email"},
            {"id": "reason_code", "label": "reason_code", "group": "field", "details": "Support reason taxonomy"},
            {"id": "resolution_status", "label": "resolution_status", "group": "field", "details": "Outcome of support case"},
            {"id": "customers", "label": "customers.csv", "group": "related", "details": "Customer context by customer_id"},
            {"id": "digital_sessions", "label": "digital_sessions.csv", "group": "related", "details": "Likely pre-support digital friction"},
        ],
        "links": [
            ("support_interactions", "customer_id", "contains"),
            ("support_interactions", "interaction_type", "categorizes"),
            ("support_interactions", "reason_code", "categorizes"),
            ("support_interactions", "resolution_status", "captures"),
            ("customer_id", "customers", "joins to"),
            ("support_interactions", "digital_sessions", "may follow"),
        ],
    },
    "error_codes.csv": {
        "nodes": [
            {"id": "error_codes", "label": "error_codes.csv", "group": "dataset", "details": "Error code lookup table"},
            {"id": "error_code", "label": "error_code", "group": "key", "details": "Shared error identifier"},
            {"id": "description", "label": "description", "group": "field", "details": "Human-readable error meaning"},
            {"id": "digital_sessions", "label": "digital_sessions.csv", "group": "related", "details": "Error events in sessions"},
            {"id": "support_interactions", "label": "support_interactions.csv", "group": "related", "details": "Support reasons that may align to errors"},
        ],
        "links": [
            ("error_codes", "error_code", "contains"),
            ("error_codes", "description", "defines"),
            ("error_code", "digital_sessions", "joins to"),
            ("error_codes", "support_interactions", "informs"),
        ],
    },
    "feature_costs.csv": {
        "nodes": [
            {"id": "feature_costs", "label": "feature_costs.csv", "group": "dataset", "details": "Cost model by feature"},
            {"id": "feature_canonical", "label": "feature_canonical", "group": "key", "details": "Canonical feature name"},
            {"id": "success_cost", "label": "avg_cost_per_success_usd", "group": "field", "details": "Average success cost"},
            {"id": "failure_cost", "label": "avg_cost_per_failure_usd", "group": "field", "details": "Average failure cost"},
            {"id": "digital_sessions", "label": "digital_sessions.csv", "group": "related", "details": "Feature activity normalized into canonical names"},
            {"id": "support_interactions", "label": "support_interactions.csv", "group": "related", "details": "Supports deflection / ROI story"},
        ],
        "links": [
            ("feature_costs", "feature_canonical", "contains"),
            ("feature_costs", "success_cost", "measures"),
            ("feature_costs", "failure_cost", "measures"),
            ("feature_canonical", "digital_sessions", "maps from"),
            ("feature_costs", "support_interactions", "supports analysis"),
        ],
    },
    "branches.csv": {
        "nodes": [
            {"id": "branches", "label": "branches.csv", "group": "dataset", "details": "Branch location table"},
            {"id": "branch_code", "label": "branch_code", "group": "key", "details": "Branch identifier"},
            {"id": "branch_city", "label": "branch_city", "group": "field", "details": "Branch city"},
            {"id": "branch_state", "label": "branch_state", "group": "field", "details": "Branch state"},
            {"id": "customers", "label": "customers.csv", "group": "related", "details": "Customer home branch reference"},
        ],
        "links": [
            ("branches", "branch_code", "contains"),
            ("branches", "branch_city", "describes"),
            ("branches", "branch_state", "describes"),
            ("branch_code", "customers", "resolves for"),
        ],
    },
}

selected = st.selectbox("Dataset graph", list(graphs.keys()))
graph = graphs[selected]

if _AGRAPH_OK:
    render_interactive_graph(graph)
else:
    st.info("Showing relationship notes only.")

st.markdown("### Relationship notes")
for source, target, label in graph["links"]:
    st.markdown(f"- `{source}` **{label}** `{target}`")

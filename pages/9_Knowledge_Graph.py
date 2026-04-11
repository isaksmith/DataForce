import math

import plotly.graph_objects as go
import streamlit as st

from dataforce_utils import apply_global_font

apply_global_font()
st.title("Knowledge Graph")
st.caption("Explore a separate relationship graph for each dataset to understand its keys, dependencies, and downstream links.")

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

color_map = {
    "dataset": "#2563eb",
    "field": "#059669",
    "key": "#111827",
    "related": "#d97706",
}

nodes = graph["nodes"]
links = graph["links"]
radius = 1.0
angles = [2 * math.pi * i / len(nodes) for i in range(len(nodes))]
positions = {
    node["id"]: (radius * math.cos(angle), radius * math.sin(angle))
    for node, angle in zip(nodes, angles)
}

edge_x = []
edge_y = []
for source, target, _label in links:
    x0, y0 = positions[source]
    x1, y1 = positions[target]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    line=dict(width=1.8, color="#94a3b8"),
    hoverinfo="none",
    mode="lines",
)

node_x, node_y, node_text, node_hover, node_color, node_size = [], [], [], [], [], []
for node in nodes:
    x, y = positions[node["id"]]
    node_x.append(x)
    node_y.append(y)
    node_text.append(node["label"])
    node_hover.append(f"<b>{node['label']}</b><br>{node['details']}")
    node_color.append(color_map.get(node["group"], "#334155"))
    node_size.append(34 if node["group"] == "key" else 50)

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode="markers+text",
    text=node_text,
    textposition="middle center",
    hovertext=node_hover,
    hoverinfo="text",
    marker=dict(size=node_size, color=node_color, line=dict(width=2, color="#ffffff")),
    textfont=dict(color="#ffffff", size=11),
)

annotations = []
for source, target, label in links:
    x0, y0 = positions[source]
    x1, y1 = positions[target]
    annotations.append(
        dict(
            x=(x0 + x1) / 2,
            y=(y0 + y1) / 2,
            text=label,
            showarrow=False,
            font=dict(size=10, color="#475569"),
            bgcolor="rgba(255,255,255,0.75)",
        )
    )

fig = go.Figure(data=[edge_trace, node_trace])
fig.update_layout(
    showlegend=False,
    hovermode="closest",
    margin=dict(b=20, l=20, r=20, t=20),
    annotations=annotations,
    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    height=760,
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### Relationship notes")
for source, target, label in links:
    st.markdown(f"- `{source}` **{label}** `{target}`")

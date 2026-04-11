import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dataforce_utils import add_download, load_csv, plot_value_counts, render_overview, render_preview, render_r_blurb

st.title("Digital Sessions")
df = load_csv("digital_sessions.csv")

channel_filter = st.multiselect("Channel", sorted(df["channel"].dropna().astype(str).unique()))
outcome_filter = st.multiselect("Session outcome", sorted(df["session_outcome"].dropna().astype(str).unique()))
feature_filter = st.multiselect("Feature used", sorted(df["feature_used"].dropna().astype(str).unique())[:50])

filtered = df.copy()
if channel_filter:
    filtered = filtered[filtered["channel"].astype(str).isin(channel_filter)]
if outcome_filter:
    filtered = filtered[filtered["session_outcome"].astype(str).isin(outcome_filter)]
if feature_filter:
    filtered = filtered[filtered["feature_used"].astype(str).isin(feature_filter)]

render_overview(filtered)
add_download(filtered, "digital_sessions_filtered.csv")
render_preview(filtered)

st.subheader("Visualizations")
st.plotly_chart(plot_value_counts(filtered["session_outcome"], "Session outcomes"), use_container_width=True)
st.plotly_chart(plot_value_counts(filtered["feature_used"], "Top features used", horizontal=True), use_container_width=True)
st.plotly_chart(plot_value_counts(filtered["channel"], "Sessions by channel"), use_container_width=True)

st.subheader("Session flow Sankey")
sankey_source = filtered.copy()
sankey_source["channel"] = sankey_source["channel"].fillna("Unknown").astype(str)
sankey_source["feature_used"] = sankey_source["feature_used"].fillna("Unknown").astype(str)
sankey_source["session_outcome"] = sankey_source["session_outcome"].fillna("Unknown").astype(str)

top_features_for_sankey = sankey_source["feature_used"].value_counts().head(8).index.tolist()
sankey_source["feature_group"] = sankey_source["feature_used"].where(
    sankey_source["feature_used"].isin(top_features_for_sankey), "Other features"
)

channel_to_feature = (
    sankey_source.groupby(["channel", "feature_group"], dropna=False)
    .size()
    .reset_index(name="value")
)
feature_to_outcome = (
    sankey_source.groupby(["feature_group", "session_outcome"], dropna=False)
    .size()
    .reset_index(name="value")
)

left_nodes = [f"Channel: {name}" for name in channel_to_feature["channel"].unique()]
middle_nodes = [f"Feature: {name}" for name in channel_to_feature["feature_group"].unique()]
right_nodes = [f"Outcome: {name}" for name in feature_to_outcome["session_outcome"].unique()]
nodes = left_nodes + middle_nodes + right_nodes
node_index = {label: idx for idx, label in enumerate(nodes)}

sources = [node_index[f"Channel: {row.channel}"] for row in channel_to_feature.itertuples()]
targets = [node_index[f"Feature: {row.feature_group}"] for row in channel_to_feature.itertuples()]
values = [row.value for row in channel_to_feature.itertuples()]

sources += [node_index[f"Feature: {row.feature_group}"] for row in feature_to_outcome.itertuples()]
targets += [node_index[f"Outcome: {row.session_outcome}"] for row in feature_to_outcome.itertuples()]
values += [row.value for row in feature_to_outcome.itertuples()]

sankey_fig = go.Figure(
    data=[
        go.Sankey(
            node=dict(label=nodes, pad=18, thickness=18),
            link=dict(source=sources, target=targets, value=values),
        )
    ]
)
sankey_fig.update_layout(
    title_text="Flow from channel to feature to session outcome",
    font_size=12,
    height=780,
    margin=dict(l=20, r=20, t=60, b=20),
)
st.plotly_chart(sankey_fig, use_container_width=True, height=780)

if "error_code" in filtered.columns:
    top_errors = filtered["error_code"].fillna("Unknown").astype(str).value_counts().head(15).reset_index()
    top_errors.columns = ["error_code", "count"]
    fig = px.bar(top_errors, x="count", y="error_code", orientation="h", title="Top error codes")
    st.plotly_chart(fig, use_container_width=True)

render_r_blurb("Digital Sessions", "digital_sessions.csv")

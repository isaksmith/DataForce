import plotly.express as px
import streamlit as st

from dataforce_utils import add_download, load_csv, plot_value_counts, render_overview, render_preview, render_r_blurb

st.title("Support Interactions")
df = load_csv("support_interactions.csv")

interaction_filter = st.multiselect("Interaction type", sorted(df["interaction_type"].dropna().astype(str).unique()))
resolution_filter = st.multiselect("Resolution status", sorted(df["resolution_status"].dropna().astype(str).unique()))

filtered = df.copy()
if interaction_filter:
    filtered = filtered[filtered["interaction_type"].astype(str).isin(interaction_filter)]
if resolution_filter:
    filtered = filtered[filtered["resolution_status"].astype(str).isin(resolution_filter)]

render_overview(filtered)
add_download(filtered, "support_interactions_filtered.csv")
render_preview(filtered)

st.subheader("Visualizations")
st.plotly_chart(plot_value_counts(filtered["interaction_type"], "Interactions by type"), use_container_width=True)
st.plotly_chart(plot_value_counts(filtered["reason_code"], "Top support reasons", horizontal=True), use_container_width=True)
resolution_counts = filtered["resolution_status"].fillna("Unknown").astype(str).value_counts().reset_index()
resolution_counts.columns = ["resolution_status", "count"]
fig = px.pie(resolution_counts, names="resolution_status", values="count", title="Resolution mix")
st.plotly_chart(fig, use_container_width=True)

render_r_blurb("Support Interactions", "support_interactions.csv")

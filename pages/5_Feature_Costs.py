import plotly.express as px
import streamlit as st

from dataforce_utils import apply_global_font, add_download, load_csv, render_overview, render_preview, render_r_blurb

apply_global_font()

st.title("Feature Costs")
df = load_csv("feature_costs.csv")

feature_filter = st.multiselect("Feature", sorted(df["feature_canonical"].dropna().astype(str).unique()))
filtered = df.copy()
if feature_filter:
    filtered = filtered[filtered["feature_canonical"].astype(str).isin(feature_filter)]

render_overview(filtered)
add_download(filtered, "feature_costs_filtered.csv")
render_preview(filtered)

st.subheader("Visualizations")
tidy = filtered.melt(id_vars="feature_canonical", var_name="cost_type", value_name="usd_cost")
fig = px.bar(tidy, x="feature_canonical", y="usd_cost", color="cost_type", barmode="group", title="Success vs failure cost")
st.plotly_chart(fig, use_container_width=True)

render_r_blurb("Feature Costs", "feature_costs.csv")

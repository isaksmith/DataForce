import streamlit as st

from dataforce_utils import add_download, load_csv, plot_value_counts, render_overview, render_preview, render_r_blurb

st.title("Branches")
df = load_csv("branches.csv")

state_filter = st.multiselect("State", sorted(df["branch_state"].dropna().unique()))
city_filter = st.multiselect("City", sorted(df["branch_city"].dropna().unique()))

filtered = df.copy()
if state_filter:
    filtered = filtered[filtered["branch_state"].isin(state_filter)]
if city_filter:
    filtered = filtered[filtered["branch_city"].isin(city_filter)]

render_overview(filtered)
add_download(filtered, "branches_filtered.csv")
render_preview(filtered)

st.subheader("Visualizations")
st.plotly_chart(plot_value_counts(filtered["branch_state"], "Branches by state"), use_container_width=True)
st.plotly_chart(plot_value_counts(filtered["branch_city"], "Top branch cities", horizontal=True), use_container_width=True)

render_r_blurb("Branches", "branches.csv")

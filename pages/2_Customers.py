import pandas as pd
import plotly.express as px
import streamlit as st

from dataforce_utils import add_download, load_csv, plot_value_counts, render_overview, render_preview, render_r_blurb

st.title("Customers")
df = load_csv("customers.csv")

tenure = pd.to_numeric(df.get("tenure_months"), errors="coerce")
segment_filter = st.multiselect("Segment", sorted(df["segment"].dropna().astype(str).unique()))
churn_filter = st.multiselect("Churn flag", sorted(df["churn_flag"].dropna().astype(str).unique()))

filtered = df.copy()
if segment_filter:
    filtered = filtered[filtered["segment"].astype(str).isin(segment_filter)]
if churn_filter:
    filtered = filtered[filtered["churn_flag"].astype(str).isin(churn_filter)]

render_overview(filtered)
add_download(filtered, "customers_filtered.csv")
render_preview(filtered)

st.subheader("Visualizations")
st.plotly_chart(plot_value_counts(filtered["segment"], "Customers by segment"), use_container_width=True)
if "tenure_months" in filtered.columns:
    tenure_filtered = pd.to_numeric(filtered["tenure_months"], errors="coerce").dropna()
    fig = px.histogram(tenure_filtered, nbins=40, title="Tenure distribution")
    st.plotly_chart(fig, use_container_width=True)
st.plotly_chart(plot_value_counts(filtered["home_branch"], "Top home branches", horizontal=True), use_container_width=True)

render_r_blurb("Customers", "customers.csv")

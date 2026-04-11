import plotly.express as px
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
if "error_code" in filtered.columns:
    top_errors = filtered["error_code"].fillna("Unknown").astype(str).value_counts().head(15).reset_index()
    top_errors.columns = ["error_code", "count"]
    fig = px.bar(top_errors, x="count", y="error_code", orientation="h", title="Top error codes")
    st.plotly_chart(fig, use_container_width=True)

render_r_blurb("Digital Sessions", "digital_sessions.csv")

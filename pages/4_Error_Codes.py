import pandas as pd
import plotly.express as px
import streamlit as st

from dataforce_utils import apply_global_font, add_download, load_csv, render_overview, render_preview, render_r_blurb

apply_global_font()

st.title("Error Codes")
df = load_csv("error_codes.csv")
sessions = load_csv("digital_sessions.csv")

search = st.text_input("Search description or code")
filtered = df.copy()
if search:
    mask = filtered.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False))
    filtered = filtered[mask.any(axis=1)]

session_errors = sessions.copy()
session_errors["error_code"] = session_errors["error_code"].fillna("No Error").astype(str)
session_errors["feature_used"] = session_errors["feature_used"].fillna("Unknown").astype(str)

usage = (
    session_errors.groupby("error_code", dropna=False)
    .size()
    .reset_index(name="session_count")
)

top_feature = (
    session_errors.groupby(["error_code", "feature_used"], dropna=False)
    .size()
    .reset_index(name="feature_count")
    .sort_values(["error_code", "feature_count"], ascending=[True, False])
    .drop_duplicates("error_code")
    .rename(columns={"feature_used": "top_feature"})[["error_code", "top_feature", "feature_count"]]
)

filtered = (
    filtered.merge(usage, on="error_code", how="left")
    .merge(top_feature, on="error_code", how="left")
)
filtered["session_count"] = filtered["session_count"].fillna(0).astype(int)
filtered["top_feature"] = filtered["top_feature"].fillna("No linked sessions")
filtered["feature_count"] = filtered["feature_count"].fillna(0).astype(int)

render_overview(filtered)
add_download(filtered, "error_codes_filtered.csv")

st.subheader("Error impact summary")
summary = filtered[["error_code", "description", "session_count", "top_feature"]].sort_values(
    "session_count", ascending=False
)
st.dataframe(summary, use_container_width=True)

st.subheader("Visualizations")
top_errors = summary.head(10).copy()
fig = px.scatter(
    top_errors,
    x="session_count",
    y="error_code",
    size="session_count",
    color="top_feature",
    hover_data=["description"],
    title="Error code impact by session volume",
)
fig.update_traces(marker=dict(sizemode="area", sizeref=max(top_errors["session_count"].max() / 60, 1)))
fig.update_layout(yaxis={"categoryorder": "total ascending"}, xaxis_title="Linked sessions", yaxis_title="Error code")
st.plotly_chart(fig, use_container_width=True)

feature_breakdown = (
    session_errors.groupby(["feature_used", "error_code"], dropna=False)
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
    .head(20)
)
feature_breakdown["error_code"] = feature_breakdown["error_code"].replace("NA", "No Error")
fig2 = px.treemap(
    feature_breakdown,
    path=["feature_used", "error_code"],
    values="count",
    title="Which features are driving specific error codes",
)
st.plotly_chart(fig2, use_container_width=True)

st.subheader("Detailed reference")
render_preview(filtered)

render_r_blurb("Error Codes", "error_codes.csv")

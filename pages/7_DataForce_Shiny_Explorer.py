import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dataforce_utils import apply_global_font, DATASETS, load_csv

apply_global_font()

st.title("DataForce Shiny Explorer")
st.caption("A cloned explorer page modeled directly after the Shiny app: dataset selector, optional filter, summary stats, primary chart, and table preview.")

selected = st.selectbox("Dataset", list(DATASETS.keys()))
df = load_csv(DATASETS[selected])

filter_col = st.selectbox("Optional filter column", ["None"] + list(df.columns))
filtered = df.copy()
if filter_col != "None":
    options = sorted(filtered[filter_col].dropna().astype(str).unique().tolist())[:100]
    chosen = st.multiselect("Filter values", options)
    if chosen:
        filtered = filtered[filtered[filter_col].astype(str).isin(chosen)]

c1, c2, c3 = st.columns(3)
c1.metric("Rows", f"{len(filtered):,}")
c2.metric("Columns", f"{filtered.shape[1]:,}")
c3.metric("Missing values", f"{int(filtered.isna().sum().sum()):,}")

label = selected
fig = None

if label == "Branches":
    plot_df = filtered.groupby("branch_state", dropna=False).size().reset_index(name="count")
    plot_df["branch_state"] = plot_df["branch_state"].fillna("Unknown")
    fig = px.bar(plot_df, x="branch_state", y="count", color="branch_state", title="Branches by state")
elif label == "Customers":
    plot_df = filtered.groupby("segment", dropna=False).size().reset_index(name="count")
    plot_df["segment"] = plot_df["segment"].fillna("Unknown")
    fig = px.bar(plot_df, x="count", y="segment", color="segment", orientation="h", title="Customers by segment")
elif label == "Digital Sessions":
    plot_df = filtered.groupby("session_outcome", dropna=False).size().reset_index(name="count")
    plot_df["session_outcome"] = plot_df["session_outcome"].fillna("Unknown")
    fig = px.bar(plot_df, x="session_outcome", y="count", color="session_outcome", title="Session outcomes")
elif label == "Error Codes":
    sessions_df = load_csv("digital_sessions.csv").copy()
    sessions_df["error_code"] = sessions_df["error_code"].fillna("NA").astype(str)
    sessions_df["feature_used"] = sessions_df["feature_used"].fillna("Unknown").astype(str)
    error_summary = (
        sessions_df.groupby(["error_code", "feature_used"], dropna=False)
        .size()
        .reset_index(name="feature_count")
        .sort_values(["error_code", "feature_count"], ascending=[True, False])
        .drop_duplicates("error_code")
        .rename(columns={"feature_used": "top_feature"})
        .merge(sessions_df.groupby("error_code", dropna=False).size().reset_index(name="session_count"), on="error_code")
        .merge(filtered, on="error_code", how="inner")
        .sort_values("session_count", ascending=False)
        .head(10)
    )
    fig = px.scatter(
        error_summary,
        x="session_count",
        y="error_code",
        size="session_count",
        color="top_feature",
        hover_data=["description"],
        title="Error code impact",
    )
elif label == "Feature Costs":
    tidy = filtered.melt(id_vars="feature_canonical", var_name="cost_type", value_name="usd_cost")
    fig = px.bar(tidy, x="feature_canonical", y="usd_cost", color="cost_type", barmode="group", title="Feature cost comparison")
else:
    plot_df = filtered.groupby("interaction_type", dropna=False).size().reset_index(name="count")
    plot_df["interaction_type"] = plot_df["interaction_type"].fillna("Unknown")
    fig = px.bar(plot_df, x="interaction_type", y="count", color="interaction_type", title="Support interactions by type")

st.plotly_chart(fig, use_container_width=True)
st.dataframe(filtered.head(500), use_container_width=True)

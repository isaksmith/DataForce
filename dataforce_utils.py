from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "Hack The Plains 2026 Datasets"
DATASETS = {
    "Branches": "branches.csv",
    "Customers": "customers.csv",
    "Digital Sessions": "digital_sessions.csv",
    "Error Codes": "error_codes.csv",
    "Feature Costs": "feature_costs.csv",
    "Support Interactions": "support_interactions.csv",
}

R_PAGE_TEXT = {
    "Branches": "Use ggplot2 to chart branch counts by state and city. A Shiny page can pair a DT table with branch distribution charts.",
    "Customers": "Use dplyr and ggplot2 to summarize tenure, segment, churn, and branch relationships with interactive filters.",
    "Digital Sessions": "Use dplyr, lubridate, DT, and plotly to profile feature usage, channel behavior, failures, and errors over time.",
    "Error Codes": "Use a searchable Shiny reference page and join sessions to show which error codes drive friction most often.",
    "Feature Costs": "Use ggplot2 or plotly to compare success and failure costs by feature and rank the most expensive failure paths.",
    "Support Interactions": "Use dplyr and ggplot2 to analyze interaction type, support reason, and resolution patterns with filters by channel and status.",
}


@st.cache_data(show_spinner=False)
def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def render_overview(df: pd.DataFrame) -> None:
    c1, c2, c3 = st.columns(3)
    c1.metric("Rows", f"{len(df):,}")
    c2.metric("Columns", f"{df.shape[1]:,}")
    c3.metric("Missing values", f"{int(df.isna().sum().sum()):,}")


def render_preview(df: pd.DataFrame) -> None:
    st.subheader("Data preview")
    st.dataframe(df.head(200), use_container_width=True)


def add_download(df: pd.DataFrame, file_name: str) -> None:
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download current data view", data=csv_bytes, file_name=file_name, mime="text/csv")


def render_r_blurb(page_name: str, dataset_file: str) -> None:
    st.subheader("R / Shiny blueprint")
    st.info(R_PAGE_TEXT[page_name])
    st.code(
        f"""library(shiny)\nlibrary(readr)\nlibrary(dplyr)\nlibrary(ggplot2)\nlibrary(DT)\n\ndf <- read_csv(\"Hack The Plains 2026 Datasets/{dataset_file}\", show_col_types = FALSE)\n\nui <- fluidPage(\n  titlePanel(\"{page_name}\"),\n  sidebarLayout(\n    sidebarPanel(\n      helpText(\"Add dataset-specific filters here\")\n    ),\n    mainPanel(\n      plotOutput(\"plot\"),\n      DTOutput(\"table\")\n    )\n  )\n)\n\nserver <- function(input, output, session) {{\n  output$plot <- renderPlot({{\n    print(head(df))\n  }})\n  output$table <- renderDT(datatable(df))\n}}\n\nshinyApp(ui, server)\n""",
        language="r",
    )


def plot_value_counts(series: pd.Series, title: str, top_n: int = 15, horizontal: bool = False):
    counts = series.fillna("Unknown").astype(str).value_counts().head(top_n).reset_index()
    counts.columns = [series.name or "value", "count"]
    if horizontal:
        return px.bar(counts, x="count", y=counts.columns[0], orientation="h", title=title)
    return px.bar(counts, x=counts.columns[0], y="count", color=counts.columns[0], title=title)

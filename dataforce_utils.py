from pathlib import Path

import mesa
import pandas as pd
import plotly.express as px
import streamlit as st


def apply_global_font() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], [data-testid="stAppViewContainer"],
        [data-testid="stSidebar"], [data-testid="stMarkdownContainer"],
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"],
        button, input, textarea, select {
            font-family: 'IBM Plex Sans', sans-serif !important;
        }

        [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            top: 50%;
            left: 50%;
            width: 42px;
            height: 42px;
            margin-left: -21px;
            margin-top: -21px;
            border: 4px solid rgba(37, 99, 235, 0.16);
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: dataforce-spin 0.9s linear infinite;
            z-index: 999998;
            opacity: 0;
            pointer-events: none;
        }

        [data-testid="stAppViewContainer"]:has(div[data-testid="stStatusWidget"])::after {
            opacity: 1;
        }

        @keyframes dataforce-spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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


def canonicalize_channel(value: str) -> str:
    raw = str(value).strip().lower()
    if raw in {"web", "www", "browser"}:
        return "Web"
    if raw in {"mobile", "moble", "phone", "app"}:
        return "Mobile"
    if raw in {"unknown", "nan", "none", ""}:
        return "Unknown"
    return raw.title()


def canonicalize_feature(value: str) -> str:
    raw = str(value).strip().lower()
    normalized = raw.replace("-", "_").replace("/", "_").replace(" ", "_")
    mapping = {
        "login": "Login",
        "signin": "Login",
        "sign_in": "Login",
        "billpay": "Bill Pay",
        "bill_pay": "Bill Pay",
        "balancecheck": "Balance Check",
        "balance_check": "Balance Check",
        "bal_chk": "Balance Check",
        "transfer": "Transfer",
        "funds_transfer": "Transfer",
        "xfer": "Transfer",
        "mobile_deposit": "Mobile Deposit",
        "mdeposit": "Mobile Deposit",
        "mobiledeposit": "Mobile Deposit",
        "statement_download": "Statement Download",
        "stmt_dl": "Statement Download",
        "statement": "Statement Download",
        "open_acct": "New Account",
        "new_account": "New Account",
    }
    if normalized in mapping:
        return mapping[normalized]
    if normalized in {"unknown", "nan", "none", ""}:
        return "Unknown"
    return raw.title()


@st.cache_data(show_spinner=False)
def load_simulation_frames() -> dict:
    customers = load_csv("customers.csv").copy()
    sessions = load_csv("digital_sessions.csv").copy()
    support = load_csv("support_interactions.csv").copy()
    errors = load_csv("error_codes.csv").copy()
    costs = load_csv("feature_costs.csv").copy()

    sessions["channel_canonical"] = sessions["channel"].fillna("Unknown").map(canonicalize_channel)
    sessions["feature_used_canonical"] = sessions["feature_used"].fillna("Unknown").map(canonicalize_feature)
    sessions["session_outcome"] = sessions["session_outcome"].fillna("Unknown").astype(str)
    sessions["error_code"] = sessions["error_code"].fillna("NA").astype(str)

    customers["tenure_months"] = pd.to_numeric(customers["tenure_months"], errors="coerce")
    customers["churn_flag"] = pd.to_numeric(customers["churn_flag"], errors="coerce").fillna(0).astype(int)
    customers["digital_enroll_date"] = pd.to_datetime(customers["digital_enroll_date"], errors="coerce")
    customers["digital_tenure_days"] = (pd.Timestamp("today").normalize() - customers["digital_enroll_date"]).dt.days
    customers["digital_tenure_days"] = customers["digital_tenure_days"].fillna(0).clip(lower=0)

    support["interaction_type"] = support["interaction_type"].fillna("unknown").astype(str).str.lower()
    support["reason_code"] = support["reason_code"].fillna("OTHER").astype(str)
    support["resolution_status"] = support["resolution_status"].fillna("unknown").astype(str).str.lower()

    return {
        "customers": customers,
        "sessions": sessions,
        "support": support,
        "errors": errors,
        "costs": costs,
    }


def simulate_customer_journey(segment: str, digital_tenure_days: int, feature: str, channel: str, error_code: str, churn_flag: int, intervention: str) -> dict:
    friction_score = 20
    if error_code not in {"NA", "Unknown", ""}:
        friction_score += 30
    if digital_tenure_days < 90:
        friction_score += 15
    if churn_flag:
        friction_score += 15
    if channel == "Mobile":
        friction_score += 5
    if feature in {"Transfer", "Mobile Deposit", "New Account", "Login"}:
        friction_score += 10

    intervention_lift = {
        "None": 0,
        "Tooltip": 8,
        "Guided Help": 15,
        "Chatbot Intercept": 12,
        "Agent Escalation": -10,
    }.get(intervention, 0)

    adjusted_score = max(0, min(100, friction_score - intervention_lift))

    if intervention == "Agent Escalation":
        outcome = "Escalated to Support"
        escalation_probability = 0.95
    elif adjusted_score >= 65:
        outcome = "Escalated to Support"
        escalation_probability = 0.75
    elif adjusted_score >= 40:
        outcome = "Resolved with Assistance"
        escalation_probability = 0.35
    else:
        outcome = "Resolved Digitally"
        escalation_probability = 0.1

    explanation = (
        f"Segment {segment} using {channel} for {feature} produced a friction score of {adjusted_score}. "
        f"The selected intervention '{intervention}' led to the simulated outcome '{outcome}'."
    )

    return {
        "friction_score": adjusted_score,
        "outcome": outcome,
        "escalation_probability": escalation_probability,
        "explanation": explanation,
    }


def estimate_feature_cost(feature: str, costs: pd.DataFrame) -> tuple[float, float]:
    canonical = feature.lower().replace(" ", "_")
    row = costs[costs["feature_canonical"].astype(str).str.lower() == canonical]
    if row.empty:
        return 0.01, 12.0
    return float(row["avg_cost_per_success_usd"].iloc[0]), float(row["avg_cost_per_failure_usd"].iloc[0])


class CustomerAgent(mesa.Agent):
    def __init__(self, model, segment: str, digital_tenure_days: int, feature: str, channel: str, error_code: str, churn_flag: int):
        super().__init__(unique_id=f"agent-{id(self)}", model=model)
        self.segment = segment
        self.digital_tenure_days = digital_tenure_days
        self.feature = feature
        self.channel = channel
        self.error_code = error_code
        self.churn_flag = churn_flag
        self.outcome = "Pending"
        self.friction_score = 0
        self.escalation_probability = 0.0
        self.estimated_cost = 0.0

    def step(self):
        result = simulate_customer_journey(
            segment=self.segment,
            digital_tenure_days=self.digital_tenure_days,
            feature=self.feature,
            channel=self.channel,
            error_code=self.error_code,
            churn_flag=self.churn_flag,
            intervention=self.model.intervention,
        )
        self.friction_score = result["friction_score"]
        self.outcome = result["outcome"]
        self.escalation_probability = result["escalation_probability"]
        success_cost, failure_cost = estimate_feature_cost(self.feature, self.model.costs)
        self.estimated_cost = {
            "Escalated to Support": failure_cost,
            "Resolved with Assistance": (failure_cost + success_cost) / 2,
            "Resolved Digitally": success_cost,
        }.get(self.outcome, failure_cost)


class SupportSimulationModel(mesa.Model):
    def __init__(self, num_agents: int, segment: str, digital_tenure_days: int, feature: str, channel: str, error_code: str, churn_flag: int, intervention: str, costs: pd.DataFrame):
        super().__init__()
        self.intervention = intervention
        self.costs = costs
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "Outcome": "outcome",
                "FrictionScore": "friction_score",
                "EscalationProbability": "escalation_probability",
                "EstimatedCost": "estimated_cost",
            }
        )
        for _ in range(num_agents):
            CustomerAgent(self, segment, digital_tenure_days, feature, channel, error_code, churn_flag)

    def step(self):
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)


def run_mesa_simulation(num_agents: int, segment: str, digital_tenure_days: int, feature: str, channel: str, error_code: str, churn_flag: int, intervention: str, costs: pd.DataFrame) -> pd.DataFrame:
    model = SupportSimulationModel(
        num_agents=num_agents,
        segment=segment,
        digital_tenure_days=digital_tenure_days,
        feature=feature,
        channel=channel,
        error_code=error_code,
        churn_flag=churn_flag,
        intervention=intervention,
        costs=costs,
    )
    model.step()
    agent_df = model.datacollector.get_agent_vars_dataframe().reset_index(drop=True)
    return agent_df


def run_mesa_simulation_from_sample(num_agents: int, customers: pd.DataFrame, feature: str, channel: str, error_code: str, intervention: str, costs: pd.DataFrame) -> pd.DataFrame:
    if customers.empty:
        return pd.DataFrame(columns=["Outcome", "FrictionScore", "EscalationProbability", "EstimatedCost"])

    sampled = customers.sample(n=num_agents, replace=True).reset_index(drop=True)
    results = []
    for row in sampled.itertuples():
        result = run_mesa_simulation(
            num_agents=1,
            segment=str(getattr(row, "segment", "Retail")),
            digital_tenure_days=int(getattr(row, "digital_tenure_days", 0)),
            feature=feature,
            channel=channel,
            error_code=error_code,
            churn_flag=int(getattr(row, "churn_flag", 0)),
            intervention=intervention,
            costs=costs,
        )
        result["segment"] = str(getattr(row, "segment", "Retail"))
        result["tenure_months"] = getattr(row, "tenure_months", None)
        results.append(result)
    return pd.concat(results, ignore_index=True)

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

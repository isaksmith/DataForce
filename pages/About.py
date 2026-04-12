import streamlit as st
from dataforce_utils import apply_global_font

apply_global_font()

st.markdown(
    """
    <style>
    .about-hero {
        background: linear-gradient(135deg, rgba(37,99,235,0.12) 0%, rgba(99,102,241,0.10) 100%);
        border: 1px solid rgba(99,102,241,0.3);
        border-radius: 16px;
        padding: 2.2rem 2.4rem 1.8rem;
        margin-bottom: 1.8rem;
    }
    .about-hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: #f8fafc;
        margin-bottom: 0.4rem;
        letter-spacing: -0.01em;
    }
    .about-hero .tagline {
        font-size: 1.15rem;
        color: #94a3b8;
        margin-top: 0;
    }
    .about-section {
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        padding: 1.5rem 1.8rem;
        margin-bottom: 1.2rem;
    }
    .about-section h3 {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 0.6rem;
        margin-top: 0;
    }
    .about-section p, .about-section li {
        color: #94a3b8;
        font-size: 0.97rem;
        line-height: 1.65;
    }
    .about-section ul {
        padding-left: 1.2rem;
        margin: 0.4rem 0 0;
    }
    .component-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(99,102,241,0.25);
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        height: 100%;
    }
    .component-card .icon {
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
    }
    .component-card h4 {
        font-size: 1rem;
        font-weight: 700;
        color: #e2e8f0;
        margin: 0 0 0.4rem;
    }
    .component-card p {
        color: #94a3b8;
        font-size: 0.9rem;
        line-height: 1.55;
        margin: 0;
    }
    .stack-pill {
        display: inline-block;
        background: rgba(37,99,235,0.15);
        border: 1px solid rgba(37,99,235,0.3);
        color: #93c5fd;
        border-radius: 999px;
        padding: 3px 12px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 3px 4px 3px 0;
    }
    .dataset-row {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        padding: 0.45rem 0;
        border-bottom: 1px solid rgba(148,163,184,0.1);
    }
    .dataset-row:last-child { border-bottom: none; }
    .dataset-name {
        font-weight: 600;
        color: #c7d2fe;
        font-size: 0.92rem;
        min-width: 200px;
    }
    .dataset-desc {
        color: #94a3b8;
        font-size: 0.88rem;
    }
    .team-note {
        text-align: center;
        color: #64748b;
        font-size: 0.88rem;
        margin-top: 2rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(148,163,184,0.12);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="about-hero">
      <h1>DataForce</h1>
      <p class="tagline">
        A unified digital friction intelligence platform — built for Hack The Plains 2026.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Vision ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="about-section">
      <h3>The Vision</h3>
      <p>
        Every time a banking customer hits a failed transaction, an unclear error, or an
        abandoned session, the bank pays — in support costs, in churn risk, and in eroded
        trust. DataForce turns that passive error log into an active intervention system.
      </p>
      <p style="margin-top:0.6rem;">
        The goal: sit between the customer and the expensive $12.00 support call, and either
        fix the issue automatically or drastically reduce the time a human agent spends on it.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Core Components ───────────────────────────────────────────────────────────
st.markdown("### Core components")
c1, c2 = st.columns(2, gap="medium")

with c1:
    st.markdown(
        """
        <div class="component-card">
          <h4>Friction Engine</h4>
          <p>
            The analytical backbone of DataForce. Every digital session is scored using a
            composite of error codes, session outcomes, feature failure cost premiums, retry
            patterns, and 24/72-hour support follow-up signals. The resulting friction score
            drives the Feature Friction Matrix — a prioritization view that ranks which banking
            features to fix first based on both failure rate and financial cost. Built in Python
            using Pandas, with precomputed scores loaded via <code>friction_score_pipeline.py</code>.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        """
        <div class="component-card">
          <h4>Proactive Intervention Layer</h4>
          <p>
            When the Friction Engine detects a score spike, it triggers a targeted intervention
            before the customer navigates to "Contact Us." Contextual tooltips surface the exact
            reason for an error (e.g., "Image too blurry" instead of "Error 505"). Dynamic
            micro-tutorials guide low-experience or newly enrolled customers through the failing
            feature. A chatbot intercept offers instant resolution — turning a $12.00 support
            call into a $0.01 digital fix. Intervention type and outcome are modeled directly
            in the Customer Simulations page using Mesa agent-based simulation.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

# ── Pages ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="about-section">
      <h3>What's in this app</h3>
      <ul>
        <li>
          <strong>Home</strong> — National command-center view of the branch network on an
          interactive choropleth map, with a scrolling telemetry ticker and headline metrics:
          total sessions, failed transactions, top error codes, support ticket volume, and
          total friction cost.
        </li>
        <li>
          <strong>Explorer</strong> — General-purpose dataset browser. Select any of the six
          source datasets, optionally filter by column value, and get a row/column summary,
          a dataset-specific chart, and a scrollable data preview — mirroring the companion
          R Shiny workflow.
        </li>
        <li>
          <strong>Branches</strong> — Explores the bank's physical branch network. Filter by
          state and city, view branch counts per state and city in bar charts, and download
          filtered data.
        </li>
        <li>
          <strong>Customers</strong> — Explores the customer base by segment and churn status.
          Surfaces a segment breakdown, tenure distribution histogram, and top home branches.
        </li>
        <li>
          <strong>Digital Sessions</strong> — Analyzes session behavior across channels and
          features. Includes outcome, feature, and channel distributions plus a three-stage
          Sankey diagram (Channel → Feature → Outcome) and a top error codes chart.
        </li>
        <li>
          <strong>Error Codes</strong> — Cross-references the error code reference table with
          session data to show which errors are most impactful, which features drive them, and
          provides a searchable impact summary and treemap.
        </li>
        <li>
          <strong>Feature Costs</strong> — Displays the financial cost model per banking feature:
          average cost of a successful session vs. a failed one, and the failure cost premium
          that drives friction score risk weighting.
        </li>
        <li>
          <strong>Support Interactions</strong> — Analyzes support contact behavior: interaction
          volume by type, top reason codes, and resolution mix. Support data feeds the friction
          score pipeline's 24h and 72h follow-up flags.
        </li>
        <li>
          <strong>Friction Score</strong> — The analytical core. Visualizes precomputed session
          friction scores to identify which features cause the most customer pain and financial
          cost. Features a KPI bar, Feature Friction Matrix scatter plot, ranked priority list,
          and full feature breakdown table.
        </li>
        <li>
          <strong>Knowledge Graph</strong> — Interactive force-directed graph showing how the
          six datasets relate to each other: primary keys, foreign key links, field descriptions,
          and downstream dependencies.
        </li>
        <li>
          <strong>Customer Simulations</strong> — Agent-based simulation of customer behavior
          during friction events. Configure feature, channel, error code, and intervention type,
          then view outcome distributions, friction score spreads, and estimated support costs
          across a sampled customer population. Customer personas are generated by
          <a href="https://github.com/isaksmith/MiroFish" target="_blank" style="color:#93c5fd;">MiroFish</a>,
          an open-source social simulation framework, which transforms raw customer profiles
          into structured persona seeds — encoding segment, digital experience level, preferred
          channel, support-seeking tendency, and trust in digital banking — that drive each
          agent's behavior in the simulation.
        </li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Datasets ──────────────────────────────────────────────────────────────────
st.markdown("### Datasets")
st.markdown(
    """
    <div class="about-section">
      <div class="dataset-row"><span class="dataset-name">branches.csv</span><span class="dataset-desc">Branch locations by state and city across KS, OK, NE, and MO</span></div>
      <div class="dataset-row"><span class="dataset-name">customers.csv</span><span class="dataset-desc">349,655 customer profiles with segment, tenure, churn flag, and enrollment date</span></div>
      <div class="dataset-row"><span class="dataset-name">digital_sessions.csv</span><span class="dataset-desc">Session logs with channel, feature used, outcome, error code, and prior session count</span></div>
      <div class="dataset-row"><span class="dataset-name">error_codes.csv</span><span class="dataset-desc">Error code reference table with descriptions</span></div>
      <div class="dataset-row"><span class="dataset-name">feature_costs.csv</span><span class="dataset-desc">Average cost per success and failure for each banking feature</span></div>
      <div class="dataset-row"><span class="dataset-name">support_interactions.csv</span><span class="dataset-desc">Support contact records with interaction type, reason code, and resolution status</span></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Tech Stack ────────────────────────────────────────────────────────────────
st.markdown("### Tech stack")
st.markdown(
    """
    <div class="about-section">
      <span class="stack-pill">Python 3.9</span>
      <span class="stack-pill">Streamlit 1.50</span>
      <span class="stack-pill">Pandas 2.2</span>
      <span class="stack-pill">Plotly 5.24</span>
      <span class="stack-pill">Folium 0.18</span>
      <span class="stack-pill">streamlit-folium</span>
      <span class="stack-pill">streamlit-agraph</span>
      <span class="stack-pill">Mesa 2.4</span>
      <span class="stack-pill">PyArrow 16.1</span>
      <span class="stack-pill">Requests</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='team-note'>Built for Hack The Plains 2026 · DataForce</div>",
    unsafe_allow_html=True,
)

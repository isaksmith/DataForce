# Customer Simulations — pages/Customer_Simulations.py

## Overview

The **Customer Simulations** page runs agent-based simulations of customer behavior during digital banking friction events. It uses generated customer personas as agent seeds and a Mesa-based simulation engine to model how different customer types respond to errors and interventions.

## What it shows

### Persona artifact status
Displays the current state of `artifacts/customer_personas.json` — file size, last modified timestamp, and a button to regenerate it on demand by running `mirofish_export_pipeline.py --customers-only`.

### Simulation controls

| Control | Description |
|---|---|
| **Persona segment** | Filter simulated population to a specific segment (retail, student, wealth, smb) or all |
| **Feature** | Banking feature being simulated (e.g., Transfer, Login, Deposit) |
| **Channel** | Access channel: Mobile or Web |
| **Error code** | Error encountered during the session (NA, AUTH_FAIL, TIMEOUT, E010, E020, E050, E099) |
| **Intervention** | Support intervention applied: None, Tooltip, Guided Help, Chatbot Intercept, Agent Escalation |
| **Simulated customers** | Number of agents to simulate (25–500, step 25) |

### Persona Knowledge Graph
An interactive `streamlit-agraph` graph showing the structure of the loaded persona artifact — how personas are classified by segment, digital experience level, preferred channel, support seeking tendency, and trust level, with value-level breakdown nodes.

### Persona mix charts
- **Digital experience distribution** — histogram by experience level, colored by segment
- **Support tendency vs. trust** — histogram of support seeking tendency, colored by trust level

### Simulation results (after clicking "Run simulation")

| Output | Description |
|---|---|
| **KPI metrics** | Avg friction score, avg escalation probability, avg estimated cost |
| **Outcome distribution** | Bar chart of simulated outcome counts (success, failure, escalation, etc.) |
| **Friction score spread** | Box plot of friction scores by segment and outcome |
| **Estimated cost distribution** | Histogram of support cost per customer by outcome |
| **Sample persona records** | Table of up to 50 persona records for the selected segment |
| **Simulation output sample** | First 100 rows of raw simulation results |
| **Downloads** | Export filtered personas and simulation results as CSV |

## Data sources

| Source | Description |
|---|---|
| `artifacts/customer_personas.json` | Generated persona seeds (run `mirofish_export_pipeline.py --customers-only` to create) |
| `Hack The Plains 2026 Datasets/customers.csv` | Raw customer data used to sample simulation population |
| `Hack The Plains 2026 Datasets/feature_costs.csv` | Cost model used to estimate financial impact per simulated session |

## Generating personas

If `artifacts/customer_personas.json` is missing, the page will show an error. Generate it with:

```bash
python3 -u mirofish_export_pipeline.py --customers-only
```

Or click the **Regenerate personas** button on the page itself.

## Simulation engine

The simulation uses `run_mesa_simulation_from_sample` from `dataforce_utils`, which implements a Mesa agent-based model. Each agent is initialized from a sampled customer row and persona attributes, then steps through a friction event with the configured feature, channel, error, and intervention. Outputs include friction score, escalation probability, and estimated cost per agent.

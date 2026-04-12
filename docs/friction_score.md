# Friction Score — pages/9_Friction_Score.py

## Overview

The **Friction Score** page is the analytical core of DataForce. It visualizes precomputed session friction scores to identify which banking features are causing the most customer pain and financial cost, and surfaces the highest-priority intervention targets.

## What it shows

### KPI bar (top)

| Metric | Description |
|---|---|
| **Est. avoidable failure cost** | Total estimated cost of failures that could be prevented, summed across all features |
| **Overall failure rate** | Percentage of sessions ending in failure or abandonment |
| **Sessions analyzed** | Total sessions in the current filter window |
| **Failures → support (24h)** | Percentage of failed sessions that led to a support contact within 24 hours |

### Main scatter plot — Feature Friction Matrix

A bubble scatter chart with:
- **X-axis:** Failure + abandon rate (%) per feature
- **Y-axis:** Failure cost premium (USD) per feature
- **Bubble size:** Avoidable failure cost
- **Color:** Priority zone (high friction + high cost = flagged)
- **Labels:** Optional feature name labels
- Zoom control via sidebar slider

### Side panel

- **Top priority features** — ranked list of features in the priority zone, each showing rank badge, feature name, session count, failure rate, avg friction score, and tags (High volume, High cost, High friction, Support-heavy)
- **Insight bar** — auto-generated summary of the single highest-priority feature

### Bottom section

- **Feature breakdown table** — sortable table with all features: sessions, failure rate, abandon rate, friction mean, cost premium, support follow-up rates, avoidable cost
- **Download** — export the feature breakdown as CSV

## Data sources

Reads precomputed scores from one of these paths (in order):
1. `Hack The Plains 2026 Datasets/session_friction_scores.csv`
2. `session_friction_scores.csv` (repo root)
3. `Hack The Plains 2026 Datasets/session_friction_scores.csv` (cwd-relative)
4. `session_friction_scores.csv` (cwd)

> To generate scores: `python friction_score_pipeline.py --output 'Hack The Plains 2026 Datasets/session_friction_scores.csv'`

## Key derived columns used

| Column | Description |
|---|---|
| `friction_score` | Composite score (0–100) for each session |
| `session_outcome_norm` | Normalized outcome: success / failure / abandon |
| `feature_canonical` | Canonical feature name |
| `failure_cost_premium` | Cost difference between failure and success for this feature |
| `support_followup_24h` | 1 if customer contacted support within 24h of session |
| `support_followup_72h` | 1 if customer contacted support within 72h of session |
| `channel_norm` | Normalized channel name |

## Sidebar controls

- **Date window** — Last 30 days / Last 90 days / All data (relative to max session timestamp)
- **Channel** — multiselect filter for mobile, web, unknown

## Priority zone logic

A feature is flagged as a **priority zone** target if both:
- Its failure + abandon rate ≥ 65th percentile across all features
- Its failure cost premium ≥ 65th percentile across all features

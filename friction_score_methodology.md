# Friction Score Methodology

This document explains how the `friction_score` is calculated, what data each part references, and which values are derived/proxy values.

## Purpose

`friction_score` is a session-level score (0-100) estimating how much friction a customer experienced during a digital banking session.

## Data sources used

| File | How it is used |
| --- | --- |
| `digital_sessions.csv` | Core session events, outcome, channel, feature used, timestamps, error code presence |
| `customers.csv` | Customer context: tenure, segment, digital enrollment timing, churn flag, product count (derived) |
| `error_codes.csv` | Error metadata and inferred severe error signal |
| `feature_costs.csv` | Cost per success/failure by feature, used for feature risk premium |
| `support_interactions.csv` | Validation signal: whether support contact follows session within 24h/72h |

## Field normalization and cleaning

The pipeline standardizes messy source values:

1. Canonical feature names (`login`, `balance_check`, `transfer`, etc.).
2. Canonical channels (`mobile`, `web`, `unknown`).
3. Canonical outcomes (`success`, `failure`, `abandon`, `unknown`).
4. Safe datetime parsing (`errors="coerce"`).
5. Normalized IDs and branch formats.

If a value cannot be mapped reliably, it is set to `unknown`.

## Engineered session signals

Sessions are sorted by customer and timestamp. For each session, the pipeline computes:

- `prior_session_count`
- `prior_same_feature_attempts_24h`
- `prior_same_feature_failures_24h`
- `prior_failed_streak_same_feature`
- `is_repeat_retry_pattern`
- `failure_cost_premium = avg_cost_per_failure_usd - avg_cost_per_success_usd`

## Scoring components and formula

The score is additive and then clamped to `[0, 100]`.

### Component columns

- `score_outcome`
- `score_error`
- `score_repeat_attempt`
- `score_feature_risk`
- `score_customer_risk`
- `friction_score`

### Default weights

| Signal | Default weight |
| --- | ---: |
| Outcome = abandon | +20 |
| Outcome = failure | +35 |
| Has error code | +10 |
| Severe error code | +10 |
| Prior same-feature attempt within 24h | +15 |
| Prior same-feature failure within 24h | +15 |
| Multi-fail streak (>=2) | +10 |
| Feature risk premium (scaled) | +0 to +15 |
| New/low-experience customer | +10 |

### Score expression

`friction_score_raw = score_outcome + score_error + score_repeat_attempt + score_feature_risk + score_customer_risk`

`friction_score = clip(friction_score_raw, 0, 100)`

Bands:
- `low`: 0-33.33
- `medium`: 33.33-66.67
- `high`: 66.67-100

## Validation output

The pipeline flags whether each session is followed by support contact within:

- `support_followup_24h`
- `support_followup_72h`

These are computed by matching on customer and checking timestamp windows (not explicit session-to-ticket IDs).

## “Imaginary data” / synthetic values

No synthetic rows are generated in the scoring pipeline. All scored sessions come from `digital_sessions.csv`.

However, some fields are **derived or proxy** values (not raw source columns):

1. `product_count_derived` (estimated from `products_held` text delimiters).
2. `is_severe_error` (inferred from keyword rules in error description).
3. `score_feature_risk` (scaled transform of cost premium).
4. `is_new_or_low_experience` (rule using enrollment recency and prior sessions).
5. `support_followup_24h/72h` (time-window linkage, inferred relationship).
6. Dashboard-only `Unresolved (proxy)` count is a visual proxy (`~21%` of 72h follow-ups), not a source-system field.

So: the model uses real session data, but includes engineered features and one dashboard proxy metric for storytelling.

## Known interpretation notes

- `Unknown` feature/channel/outcome appears when source values are missing/unmappable.
- Weights are rule-based and editable in `friction_score_pipeline.py` (`SCORE_WEIGHTS`, `RISK_CONFIG`).
- This is a first-pass interpretable scoring framework, not a trained predictive model.

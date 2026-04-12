# DataForce Dataset Explorer

This repository includes:
- a multi-page Python app built with Streamlit
- a starter R app built with Shiny

## Python app (Streamlit)

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run DataForce.py
```

If `streamlit` is not on PATH, use:

```bash
./.venv/bin/python -m streamlit run DataForce.py
```

The Python app includes:
- entry page: `DataForce.py`
- dataset pages: `pages/`
- shared helpers: `dataforce_utils.py`

## Friction Score page requirements

The `Digital Friction` page (`pages/9_Friction_Score.py`) reads a precomputed file:

- `session_friction_scores.csv`

The app looks for it in:

1. `Hack The Plains 2026 Datasets/session_friction_scores.csv` (repo default)
2. repo root
3. current working directory equivalents

If the file is missing, generate it once with:

```bash
./.venv/bin/python friction_score_pipeline.py --output "Hack The Plains 2026 Datasets/session_friction_scores.csv"
```

### Notes

- The precomputed CSV is large and tracked with **Git LFS** in this repo.
- If you clone this repo fresh, run `git lfs pull` to fetch the full CSV file.
- Scoring logic and assumptions are documented in `friction_score_methodology.md`.

## What the site includes

Each dataset gets its own page with:
- summary metrics
- interactive filters
- data preview table
- download button for the filtered view
- multiple Python visualizations
- a matching R/Shiny blueprint and starter snippet

Datasets covered:
- `branches.csv`
- `customers.csv`
- `digital_sessions.csv`
- `error_codes.csv`
- `feature_costs.csv`
- `support_interactions.csv`

## R app

A starter Shiny app is available in `shiny_app/app.R`.

To run it in an R environment:

```r
setwd("shiny_app")
shiny::runApp()
```

Required R packages:
- `shiny`
- `readr`
- `dplyr`
- `ggplot2`
- `DT`
- `plotly`
- `tidyr`

## Environment note

`Rscript` was not available in the current workspace environment, so the Shiny app was scaffolded but not executed here.

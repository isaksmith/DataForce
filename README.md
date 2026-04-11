# DataForce Dataset Explorer

This repo now includes two starter experiences for exploring each hackathon dataset:
- a multi-page Python app built with `Streamlit`
- a starter R app built with `Shiny`

## Python app

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the site:

```bash
streamlit run app.py
```

The Python app includes:
- a landing page in `app.py`
- dataset-specific pages in `pages/`
- shared helpers in `dataforce_utils.py`

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

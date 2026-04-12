# Home — DataForce.py

## Overview

The **Home** page is the landing screen of the DataForce application. It presents a national-level command-center view of the bank's branch network and key operational metrics using a terminal-inspired aesthetic.

## What it shows

| Section | Description |
|---|---|
| **Ticker bar** | Scrolling live-telemetry feed with headline stats (total sessions, failed transactions, error counts, support tickets) |
| **Interactive map** | Folium choropleth map of the US showing branch density by state, with circle markers for each city showing branch count on hover/click |
| **Left panel** | Live telemetry (sessions, failed transactions), error tracking (ERR_AUTH, ERR_TIMEOUT, ERR_DEPOSIT), and cost-per-feature summary |
| **Center panel** | The map, plus a summary grid (demographics, session logs, support alerts) and a total friction cost alert block |
| **Right panel** | Customer demographics, support saturation (live tickets, agent load), and average friction score |

## Data sources

- `Hack The Plains 2026 Datasets/branches.csv` — used to compute branch counts per state and city for the map

## Key metrics displayed

- **Total sessions:** 2,000,000
- **Failed transactions:** 4.8%
- **ERR_AUTH:** 15K · **ERR_TIMEOUT:** 8K · **ERR_DEPOSIT:** 5K
- **Active profiles:** 355,000
- **Live support tickets:** 65,000
- **Total friction cost:** $12,450.00
- **Avg friction score:** 22.55

> Note: Most headline figures on this page are static display values used for the hackathon demo presentation. Dynamic data comes from `branches.csv` for the map only.

## Navigation

This is the root entry point (`DataForce.py`). All other pages are accessible from the sidebar.

# UK Retail Sales Analytics (2023-2025)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![pandas](https://img.shields.io/badge/pandas-2.x-150458?logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![SQLite](https://img.shields.io/badge/SQL-SQLite-07405E?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![matplotlib](https://img.shields.io/badge/matplotlib-charts-11557C)](https://matplotlib.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An end-to-end analytics project on three years of UK e-commerce/retail orders - SQL for aggregation, pandas for cleaning and exploration, matplotlib for the static charts, and a hand-rolled SVG dashboard for the live view. Built as a portfolio piece for BI/data analyst roles.

**[Live interactive dashboard](https://claude.ai/code/artifact/88582870-21c9-4bde-af98-92acd9b011fc)** - revenue, category, regional, and promo breakdowns, with hover tooltips and a data table under every chart.

![Monthly revenue by year](images/01_yoy_revenue_trend.png)

## Key findings

**Revenue grew ~31% from 2023 to 2025**, with November-December consistently the strongest months every year - seasonal staffing and inventory planning should anchor to that shape, not the annual average.

**Electronics drives 43% of revenue but only a 17.3% margin and a 10% return rate** - the highest of any category. Beauty & Personal Care is the mirror image: 6% of revenue at a 47% margin. A modest category-mix shift would move profit more than a volume push would.

**Promo weeks (Black Friday, Boxing Day, Summer Sale) run at ~2.2x an ordinary day's revenue, for about 5 points of margin** - a defensible trade at these numbers, and one worth watching if promo frequency increases.

**London + South East are 40% of revenue** - the obvious first market for regional expansion or localized marketing spend, with North West a clear third.

**Average order value is flat (~GBP 70) across Consumer, SME, and Corporate segments** - the segments differ in order frequency, not basket size, which points retention efforts at frequency rather than upsell.

## Visuals

![Revenue by category](images/02_category_revenue.png)
![Revenue by UK region](images/03_regional_revenue.png)
![Promo campaign impact](images/05_promo_impact.png)
![Return rate by category](images/06_return_rate.png)

## Project structure

```
data/uk_retail_orders_2023_2025.csv - raw export (deliberately has a few dupes/nulls/casing issues)
data/uk_retail_orders_clean.csv - curated output of the cleaning pipeline
data/retail.db - SQLite db the sql folder queries run against
data/query_results/ - each sql query's output, saved as CSV
sql/ - the SQL analysis layer, 8 queries plus schema
scripts/generate_dataset.py - synthesizes the raw dataset (seasonality, promo calendar, messiness)
scripts/clean_data.py - raw to curated, with printed rationale for every fix
scripts/build_sqlite_db.py - curated CSV to SQLite, runs the sql folder queries
scripts/make_visuals.py - curated CSV to images folder PNGs (shared style module)
scripts/build_notebook.py - assembles notebooks/uk_retail_analysis.ipynb
notebooks/uk_retail_analysis.ipynb - full narrative: load, inspect, clean, EDA, findings
dashboard/index.html - the live dashboard (self-contained HTML/CSS/JS)
dashboard/data.json - aggregates the dashboard reads
images/ - exported chart PNGs, used in this README and the notebook
```

## Tech stack & approach

| Layer | Tool | What it's doing |
|---|---|---|
| Data | pandas / NumPy | Synthesizing a realistic dataset, then a documented raw to curated cleaning pipeline |
| Analysis | SQLite + SQL | 8 queries covering trend, category, region, segment, promo, returns, and channel |
| Static visuals | matplotlib | A shared style module (palette, spacing, label rules) so every chart reads as one system |
| Live dashboard | HTML / CSS / vanilla JS + inline SVG | KPI tiles, 7 interactive charts with hover tooltips, light/dark theme, per-chart data tables |
| Notebook | Jupyter (nbformat) | The full analysis narrative, pre-executed so it renders on GitHub with no setup |

## Reproduce it locally

```bash
git clone https://github.com/deshikniron99/uk-retail-sales-analytics.git
cd uk-retail-sales-analytics
pip install pandas numpy matplotlib

python scripts/generate_dataset.py
python scripts/clean_data.py
python scripts/build_sqlite_db.py
python scripts/make_visuals.py
```

Then open notebooks/uk_retail_analysis.ipynb for the full walkthrough, or dashboard/index.html directly in a browser for the live view.

## A note on the data

The dataset is **synthetically generated** (see scripts/generate_dataset.py) rather than scraped or licensed - it's built with realistic seasonality, year-over-year growth, a promo calendar, and deliberate messiness (duplicate rows, inconsistent region casing, missing values) specifically so the cleaning and analysis steps have real problems to solve. All figures in this README follow from that data, not from any real retailer.

Built by [Deshik Soyam](https://github.com/deshikniron99) - MSc Management with Data Analytics, BPP University.

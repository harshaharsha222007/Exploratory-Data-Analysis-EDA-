# Exploratory Data Analysis (EDA)

Exploratory Data Analysis (EDA) project to analyze datasets, identify patterns, trends, distributions, and outliers using statistical analysis and data visualization.

## Overview
This project loads an Excel dataset, validates data quality, profiles numeric columns, examines distributions and outliers, compares product performance, analyzes time-based trends, and visualizes relationships between key variables.

## Project structure

- `eda_analysis.py` — main analysis script
- `eda_output/` — generated charts and CSV exports
- `requirements.txt` — Python dependencies

## Requirements

```bash
pip install -r requirements.txt
```

## Run

1. Place your Excel file (for example, `dataset.xlsx`) in the project folder.
2. Update the column names in `eda_analysis.py` if your dataset differs.
3. Run:

```bash
python eda_analysis.py
```

## Output
The script saves summary charts and CSVs into `./eda_output/`.

## Typical outputs
- `descriptive_stats.csv`
- `outliers.csv`
- `product_performance.csv`
- `yearly_trend.csv`
- `correlation.csv`
- `distributions.png`
- `outliers_boxplot.png`
- `product_performance.png`
- `yearly_trend.png`
- `monthly_trend.png`
- `correlation_heatmap.png`
- `scatter_relationships.png`
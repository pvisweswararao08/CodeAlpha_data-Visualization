# Task 2 — Finance Exploratory Data Analysis (EDA)

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-purple?style=flat-square)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualisation-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> **Complete Exploratory Data Analysis on synthetic stock market data — 12 charts, 4 statistical tests, and a 39-second live animated dashboard.**

---

## Overview

A full EDA pipeline on **3 years of synthetic stock market data** (2022–2024) covering 12 stocks across 6 sectors. Includes statistical hypothesis testing, anomaly detection, feature engineering, and a live animated GIF dashboard.

---

## Dataset

Generated synthetically by `finance_eda.py` and saved as `eda_output/finance_dataset.csv`.

| Property | Value |
|---|---|
| Stocks | 12 (AAPL, MSFT, GOOGL, AMZN, TSLA, JPM, BAC, GS, JNJ, PFE, XOM, CVX) |
| Sectors | Technology · Consumer · Automotive · Finance · Healthcare · Energy |
| Date Range | Jan 2022 – Dec 2024 (business days only) |
| Rows | 9,384 |
| Columns | Date, Ticker, Open, High, Low, Close, Volume, PE_Ratio, Beta, Dividend_Yield, Market_Cap, Sector |

---

## EDA Steps

1. **Meaningful Questions** — 8 analytical questions defined before analysis
2. **Data Structure** — shape, dtypes, missing values, duplicates
3. **Feature Engineering** — daily returns, MA20, MA50, RSI, Z-score, Bollinger Bands
4. **Visualisations** — 12 charts (dark theme)
5. **Hypothesis Testing** — Shapiro-Wilk, T-Test, ANOVA, Kolmogorov-Smirnov
6. **Data Quality** — issues identified with recommendations

---

## 12 Charts Generated

| Chart | Description |
|---|---|
| `fig1_price_history.png` | Stock price history + MA20 & MA50 overlays |
| `fig2_missing_values.png` | Missing value heatmap |
| `fig3_return_distributions.png` | Daily return histograms with normal fit |
| `fig4_correlation_heatmap.png` | Cross-stock correlation matrix |
| `fig5_risk_return.png` | Risk–return scatter by sector |
| `fig6_sector_performance.png` | Cumulative sector returns (3-year) |
| `fig7_volume_analysis.png` | Trading volume by stock & day of week |
| `fig8_anomaly_detection.png` | Z-score anomaly detection (73 flagged) |
| `fig9_pe_beta_boxplot.png` | PE Ratio & Beta distributions by sector |
| `fig10_day_of_week.png` | Day-of-week return effect |
| `fig11_rolling_volatility.png` | 20-day rolling volatility |
| `fig12_summary_dashboard.png` | Full EDA summary dashboard |

---

## Hypothesis Testing Results

| Test | Question | Result | Conclusion |
|---|---|---|---|
| **Shapiro-Wilk** | Are returns normally distributed? | p ≈ 0.000 | ❌ All stocks FAIL — fat tails |
| **T-Test** | Is mean return significantly ≠ 0? | p > 0.05 | ❌ No significant mean return |
| **ANOVA** | Do sectors have different returns? | F=0.44, p=0.82 | ❌ No significant difference |
| **KS-Test** | Are PE Ratios normal? | p = 0.97 | ✅ PE Ratios ARE normal |

---

## Key Findings

- 📉 **Non-Normal Returns** — All 12 stocks fail normality test (fat tails = real-world finance behaviour)
- 🎯 **Efficient Market** — No stock has statistically significant mean return (random walk)
- 🔴 **73 Anomalies** — Z-score spikes flagged, mostly during the 2022 market crash
- 🏦 **Sector Clustering** — JPM, BAC, GS move together; Healthcare provides diversification
- ⚡ **TSLA Most Volatile** — Highest rolling volatility but also highest average daily return
- 📅 **No Day-of-Week Effect** — ANOVA confirms no significant Mon–Fri return difference

---

## Live Animation

The script `finance_eda_video.py` generates a **39-second animated GIF** dashboard:
- 391 frames at 10 FPS
- 6 live panels: price lines, sector lines, volume bars, return histogram, cumulative returns, live stats

```bash
python -X utf8 finance_eda_video.py
# Output: eda_output/finance_eda_live.gif
```

> **Note:** The GIF (~38 MB) is excluded from this repo due to GitHub file size limits. Generate it locally.

---

## How to Run

### 1. Install Dependencies
```bash
pip install pandas numpy matplotlib seaborn scipy
```

### 2. Run EDA
```bash
python -X utf8 finance_eda.py
```
Charts saved to `eda_output/`

### 3. Generate Live Animation (optional)
```bash
python -X utf8 finance_eda_video.py
```

---

## Project Structure

```
task2_eda/
├── finance_eda.py          ← Full EDA pipeline
├── finance_eda_video.py    ← Live animated dashboard
├── index.html              ← Web dashboard
├── README.md
├── requirements.txt
├── .gitignore
└── eda_output/
    ├── finance_dataset.csv
    ├── fig1_price_history.png
    ├── fig2_missing_values.png
    ├── ...
    └── fig12_summary_dashboard.png
```

---

## Technologies

- **Python 3.8+** — tested on Python 3.14
- **Pandas** — data loading, cleaning, feature engineering
- **NumPy** — numerical computation
- **Matplotlib** — dark-themed visualisations + animation
- **Seaborn** — heatmaps and styled plots
- **SciPy** — Shapiro-Wilk, T-Test, ANOVA, KS-Test

---

## License

MIT License — free to use and modify.

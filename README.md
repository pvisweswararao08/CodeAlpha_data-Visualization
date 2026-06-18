# 📊 CodeAlpha — Data Science Project

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-purple?style=flat-square)
![NumPy](https://img.shields.io/badge/NumPy-ML%20from%20Scratch-orange?style=flat-square)
![Matplotlib](https://img.shields.io/badge/Matplotlib-Visualisation-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

> A complete data science pipeline — **Exploratory Data Analysis** + **Machine Learning** on synthetic stock market data covering 12 stocks across 6 sectors (2022–2024).

---

## 📁 Project Structure

```
CodeAlpha_data-Visualization/
│
├── task2_eda/                        ← Task 2: Exploratory Data Analysis
│   ├── finance_eda.py                   Full EDA pipeline (12 charts + 4 tests)
│   ├── finance_eda_video.py             Live animated GIF dashboard (39s)
│   ├── index.html                       Web dashboard
│   ├── requirements.txt
│   └── eda_output/
│       ├── finance_dataset.csv          Synthetic dataset (9,384 rows)
│       ├── fig1_price_history.png
│       ├── fig2_missing_values.png
│       ├── fig3_return_distributions.png
│       ├── fig4_correlation_heatmap.png
│       ├── fig5_risk_return.png
│       ├── fig6_sector_performance.png
│       ├── fig7_volume_analysis.png
│       ├── fig8_anomaly_detection.png
│       ├── fig9_pe_beta_boxplot.png
│       ├── fig10_day_of_week.png
│       ├── fig11_rolling_volatility.png
│       └── fig12_summary_dashboard.png
│
└── task3_ml/                         ← Task 3: Machine Learning Prediction
    ├── task3_ml_prediction.py           Pure NumPy ML pipeline (no sklearn)
    ├── index.html                       Web dashboard
    ├── requirements.txt
    └── ml_output/
        ├── model_results.csv            All metrics (RMSE, MAE, R², Dir. Acc.)
        ├── fig1_actual_vs_predicted.png
        ├── fig2_price_predictions.png
        ├── fig3_model_comparison.png
        ├── fig4_feature_importance.png
        ├── fig5_directional_accuracy.png
        ├── fig6_r2_heatmap.png
        └── fig7_ml_dashboard.png
```

---

## 📌 Task 2 — Exploratory Data Analysis

### Dataset
| Property | Value |
|---|---|
| Stocks | 12 (AAPL, MSFT, GOOGL, AMZN, TSLA, JPM, BAC, GS, JNJ, PFE, XOM, CVX) |
| Sectors | Technology · Consumer · Automotive · Finance · Healthcare · Energy |
| Date Range | Jan 2022 – Dec 2024 |
| Rows | **9,384** |

### Key Findings
- 📉 All 12 stocks fail normality test — fat tails (leptokurtic distribution)
- 🎯 No stock has statistically significant mean return — consistent with efficient market hypothesis
- 🔴 **73 price anomalies** detected via Z-score (|Z| > 3) — mostly during 2022 crash
- 🏦 Finance stocks (JPM, BAC, GS) are highly correlated — Healthcare provides diversification
- ⚡ TSLA is most volatile — Healthcare most stable
- 📅 No day-of-week effect (ANOVA p = 0.82)

### Hypothesis Testing
| Test | Result |
|---|---|
| Shapiro-Wilk (normality) | ❌ All stocks fail — fat tails |
| T-Test (mean ≠ 0) | ❌ No significant mean return |
| ANOVA (sector returns) | ❌ No significant sector difference |
| KS-Test (PE normality) | ✅ PE Ratios are normally distributed |

### Run Task 2
```bash
pip install pandas numpy matplotlib seaborn scipy
python -X utf8 task2_eda/finance_eda.py
```

---

## 🤖 Task 3 — Machine Learning Stock Prediction

> All models built **from scratch in pure NumPy** — no scikit-learn!

### Models
| Model | Method | Best RMSE Stock |
|---|---|---|
| Linear Regression | OLS Normal Equation | JNJ (0.01283) |
| Ridge Regression | L2-Regularised OLS | JNJ (0.01274) ✅ |
| Neural Network (MLP) | Adam + ReLU + Xavier | JNJ (0.08675) |

### Neural Network Architecture
```
Input(17) → Dense(64, ReLU) → Dense(1, Linear)
Optimiser: Adam | lr=5e-4 | Epochs=150 | Batch=64
```

### Results Summary
| Metric | Value |
|---|---|
| Avg Ridge RMSE | ~0.026 |
| Avg NN Directional Acc. | ~46.6% |
| Best Directional Acc. | PFE — 56.1% |
| Features Engineered | 17 |
| Train / Test Split | 80% / 20% |

### Run Task 3
```bash
pip install pandas numpy matplotlib seaborn
python -X utf8 task3_ml/task3_ml_prediction.py
```

---

## 🚀 Technologies

| Tool | Purpose |
|---|---|
| Python 3.8+ | Core language (tested on 3.14) |
| Pandas | Data loading & feature engineering |
| NumPy | ML models from scratch |
| Matplotlib | Dark-themed charts & animation |
| Seaborn | Heatmaps & styled plots |
| SciPy | Hypothesis testing |

---

## 📄 License

MIT License — free to use and modify.

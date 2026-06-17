# Finance EDA & ML Project

A full data science project covering **Exploratory Data Analysis (EDA)** and **Machine Learning** on a synthetic stock market dataset.

---

## Project Structure

```
finance-project/
├── index.html                        ← Web dashboard (host on EdgeOne)
├── README.md
├── .gitignore
├── task2_eda/
│   ├── finance_eda.py                ← Full EDA pipeline
│   ├── finance_eda_video.py          ← Live animated GIF
│   └── eda_output/
│       ├── finance_dataset.csv
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
│       ├── fig12_summary_dashboard.png
│       └── finance_eda_live.gif
└── task3_ml/
    ├── task3_ml_prediction.py        ← ML pipeline (pure NumPy)
    └── ml_output/
        ├── model_results.csv
        ├── fig1_actual_vs_predicted.png
        ├── fig2_price_predictions.png
        ├── fig3_model_comparison.png
        ├── fig4_feature_importance.png
        ├── fig5_directional_accuracy.png
        ├── fig6_r2_heatmap.png
        └── fig7_ml_dashboard.png
```

---

## Task 2 — Exploratory Data Analysis (EDA)

### Dataset
- **12 stocks**: AAPL, MSFT, GOOGL, AMZN, TSLA, JPM, BAC, GS, JNJ, PFE, XOM, CVX
- **6 sectors**: Technology, Consumer, Automotive, Finance, Healthcare, Energy
- **Date range**: Jan 2022 – Dec 2024 (business days)
- **9,384 rows × 12 columns** (OHLCV + PE, Beta, Dividend Yield, Market Cap)

### Steps Performed
1. Meaningful questions formulated before analysis
2. Data structure explored (dtypes, shape, missing values, duplicates)
3. Feature engineering (daily returns, moving averages, RSI, volatility, Z-score)
4. 12 visualisation charts generated
5. Hypothesis testing: Shapiro-Wilk, T-Test, ANOVA, Kolmogorov-Smirnov
6. Data quality issues identified with recommendations

### Key Findings
- All 12 stocks fail normality test (fat tails — real-world financial behaviour)
- No stock has a statistically significant mean return (efficient market)
- 73 price anomalies detected via Z-score (|Z| > 3)
- TSLA most volatile; Healthcare (JNJ, PFE) most defensive

### Requirements
```bash
pip install pandas numpy matplotlib seaborn scipy
python -X utf8 task2_eda/finance_eda.py
```

---

## Task 3 — Machine Learning: Stock Price Prediction

### Models (Pure NumPy — no sklearn required)
| Model | Description |
|---|---|
| **Linear Regression** | OLS via normal equation |
| **Ridge Regression** | L2-regularised linear model |
| **Neural Network (MLP)** | 2-layer feedforward NN with Adam optimiser |

### Features Engineered
- Lag returns (1, 2, 3, 5, 10 days)
- Moving average ratios (MA5, MA10, MA20, MA50)
- Bollinger Band position
- RSI (14-day)
- MACD & MACD histogram
- Volume ratio
- Rolling volatility
- Day of week, Month

### Evaluation Metrics
- RMSE, MAE, R²
- Directional Accuracy (can model predict up/down movement?)

### Requirements
```bash
pip install pandas numpy matplotlib seaborn
python -X utf8 task3_ml/task3_ml_prediction.py
```

---

## Web Dashboard
Open `index.html` in any browser or host on **Tencent EdgeOne** for a live public URL.

---

## Technologies Used
- **Python 3.x** — pandas, numpy, matplotlib, seaborn, scipy
- **Machine Learning** — implemented from scratch with NumPy (no sklearn)
- **Visualisation** — matplotlib dark theme, 19 charts total
- **Animation** — matplotlib FuncAnimation → GIF (261 frames)
- **Hosting** — Tencent EdgeOne (static site) + GitHub

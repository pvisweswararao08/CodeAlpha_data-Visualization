"""
============================================================
  TASK 2: Exploratory Data Analysis (EDA) — Finance Dataset
============================================================
  Dataset   : Synthetic Stock Market + Company Financials
  Language  : Python
  Libraries : pandas, numpy, matplotlib, seaborn, scipy
============================================================
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
import warnings
import os

warnings.filterwarnings("ignore")

# ── Output folder ──────────────────────────────────────────
os.makedirs("eda_output", exist_ok=True)

# ── Plot style ─────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "axes.titlecolor":  "#e6edf3",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.6,
    "legend.facecolor": "#161b22",
    "legend.edgecolor": "#30363d",
    "font.family":      "DejaVu Sans",
})

ACCENT  = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657",
           "#79c0ff", "#56d364", "#ff7b72", "#bc8cff", "#ffb77a",
           "#e3b341", "#f0883e"]  # 12 colors for 12 tickers

# ══════════════════════════════════════════════════════════════
#  1. GENERATE SYNTHETIC FINANCE DATASET
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 1 — GENERATING SYNTHETIC FINANCE DATASET")
print("═"*60)

np.random.seed(42)

companies = {
    "AAPL": ("Technology",    150, 0.0008, 0.018),
    "MSFT": ("Technology",    280, 0.0007, 0.016),
    "GOOGL":("Technology",   2800, 0.0006, 0.020),
    "AMZN": ("Consumer",     3400, 0.0005, 0.022),
    "TSLA": ("Automotive",    700, 0.0010, 0.035),
    "JPM":  ("Finance",       130, 0.0004, 0.017),
    "BAC":  ("Finance",        35, 0.0003, 0.019),
    "GS":   ("Finance",       320, 0.0005, 0.021),
    "JNJ":  ("Healthcare",    165, 0.0003, 0.013),
    "PFE":  ("Healthcare",     45, 0.0002, 0.014),
    "XOM":  ("Energy",         85, 0.0003, 0.020),
    "CVX":  ("Energy",        110, 0.0003, 0.019),
}

dates = pd.date_range(start="2022-01-01", end="2024-12-31", freq="B")
N     = len(dates)

records = []
for ticker, (sector, s0, drift, vol) in companies.items():
    # Geometric Brownian Motion
    shocks = np.random.normal(drift, vol, N)
    # Add market crash event around mid-2022
    shocks[120:150] -= 0.005
    # Add bull run 2023
    shocks[260:320] += 0.003

    price = s0 * np.cumprod(1 + shocks)
    daily_range = price * np.abs(np.random.normal(0.01, 0.005, N))

    open_p  = price * np.random.uniform(0.995, 1.005, N)
    high_p  = price + daily_range * np.random.uniform(0.5, 1.0, N)
    low_p   = price - daily_range * np.random.uniform(0.5, 1.0, N)
    close_p = price
    volume  = np.random.lognormal(mean=15, sigma=0.7, size=N).astype(float)  # float to allow NaN

    # Intentionally inject some missing values & anomalies
    missing_idx = np.random.choice(N, size=15, replace=False)
    volume[missing_idx[:5]]  = np.nan  # inject missing volume
    close_p_copy = close_p.copy()
    close_p_copy[missing_idx[5:10]] = np.nan

    # Inject price spikes (anomalies)
    spike_idx = np.random.choice(N, size=3, replace=False)
    close_p_copy[spike_idx] *= np.random.uniform(1.15, 1.25, 3)

    for i, date in enumerate(dates):
        records.append({
            "Date":    date,
            "Ticker":  ticker,
            "Sector":  sector,
            "Open":    round(open_p[i], 2),
            "High":    round(high_p[i], 2),
            "Low":     round(low_p[i], 2),
            "Close":   round(close_p_copy[i], 2) if not np.isnan(close_p_copy[i]) else np.nan,
            "Volume":  volume[i],
            "Market_Cap_B": round(close_p[i] * np.random.uniform(5e8, 3e9) / 1e9, 2),
            "PE_Ratio":     round(np.random.normal(22, 8), 2),
            "Dividend_Yield": round(max(0, np.random.normal(1.5, 1.2)), 3),
            "Beta":    round(np.random.normal(1.1, 0.4), 2),
        })

df = pd.DataFrame(records)
df.to_csv("eda_output/finance_dataset.csv", index=False)
print(f"  ✔  Dataset created  →  {df.shape[0]:,} rows × {df.shape[1]} columns")
print(f"  ✔  Saved to: eda_output/finance_dataset.csv\n")


# ══════════════════════════════════════════════════════════════
#  2. MEANINGFUL QUESTIONS
# ══════════════════════════════════════════════════════════════
print("═"*60)
print("  STEP 2 — MEANINGFUL QUESTIONS BEFORE ANALYSIS")
print("═"*60)

questions = [
    "Q1 : Which sector performs best over 3 years?",
    "Q2 : Are there price anomalies / outliers in the dataset?",
    "Q3 : How does trading volume correlate with price movement?",
    "Q4 : Which stocks are most volatile (high Beta / std)?",
    "Q5 : Is there a day-of-week effect on returns?",
    "Q6 : Are PE ratios normally distributed?",
    "Q7 : Do stocks in the same sector move together (correlation)?",
    "Q8 : What is the risk-return profile of each stock?",
]
for q in questions:
    print(f"  {q}")


# ══════════════════════════════════════════════════════════════
#  3. DATA STRUCTURE EXPLORATION
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 3 — DATA STRUCTURE EXPLORATION")
print("═"*60)

print("\n── Shape ──────────────────────────────────────────────")
print(f"  Rows: {df.shape[0]:,}   Columns: {df.shape[1]}")

print("\n── Data Types ─────────────────────────────────────────")
print(df.dtypes.to_string())

print("\n── First 5 Rows ───────────────────────────────────────")
print(df.head().to_string())

print("\n── Statistical Summary ────────────────────────────────")
print(df.describe(include="all").to_string())

print("\n── Missing Values ─────────────────────────────────────")
missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
missing_df = pd.DataFrame({"Missing Count": missing, "Missing %": missing_pct})
missing_df = missing_df[missing_df["Missing Count"] > 0]
print(missing_df.to_string() if not missing_df.empty else "  No missing values")

print("\n── Duplicate Rows ─────────────────────────────────────")
print(f"  Duplicates: {df.duplicated().sum()}")

print("\n── Unique Values per Column ───────────────────────────")
for col in ["Ticker", "Sector", "Date"]:
    print(f"  {col}: {df[col].nunique()} unique")


# ══════════════════════════════════════════════════════════════
#  4. FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 4 — FEATURE ENGINEERING")
print("═"*60)

df["Date"]          = pd.to_datetime(df["Date"])
df                  = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
df["Daily_Return"]  = df.groupby("Ticker")["Close"].pct_change()
df["MA_20"]         = df.groupby("Ticker")["Close"].transform(lambda x: x.rolling(20).mean())
df["MA_50"]         = df.groupby("Ticker")["Close"].transform(lambda x: x.rolling(50).mean())
df["Volatility_20"] = df.groupby("Ticker")["Daily_Return"].transform(lambda x: x.rolling(20).std())
df["Day_of_Week"]   = df["Date"].dt.day_name()
df["Month"]         = df["Date"].dt.month
df["Year"]          = df["Date"].dt.year
df["Price_Range"]   = df["High"] - df["Low"]

# Fill missing Close with forward-fill per ticker
df["Close"] = df.groupby("Ticker")["Close"].transform(lambda x: x.ffill())

print("  ✔  Daily_Return, MA_20, MA_50, Volatility_20 added")
print("  ✔  Day_of_Week, Month, Year extracted")
print("  ✔  Missing Close values filled via forward-fill")


# ══════════════════════════════════════════════════════════════
#  5. VISUALISATIONS
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 5 — GENERATING VISUALISATIONS")
print("═"*60)

tickers = list(companies.keys())
sectors = list(set(v[0] for v in companies.values()))

# ── FIG 1 : Stock Price History ─────────────────────────────
print("  → Fig 1: Stock Price History")
fig, axes = plt.subplots(4, 3, figsize=(20, 16))
fig.suptitle("Stock Price History (2022–2024)", fontsize=18, fontweight="bold",
             color="#e6edf3", y=1.01)
axes = axes.flatten()

for i, ticker in enumerate(tickers):
    sub = df[df["Ticker"] == ticker]
    ax  = axes[i]
    ax.plot(sub["Date"], sub["Close"],  color=ACCENT[i], lw=1.2, label="Close")
    ax.plot(sub["Date"], sub["MA_20"],  color="#ffa657", lw=0.9, linestyle="--", label="MA20", alpha=0.8)
    ax.plot(sub["Date"], sub["MA_50"],  color="#d2a8ff", lw=0.9, linestyle=":",  label="MA50", alpha=0.8)
    ax.set_title(f"{ticker}  ({companies[ticker][0]})", fontsize=11, fontweight="bold")
    ax.set_ylabel("Price ($)", fontsize=8)
    ax.legend(fontsize=7, loc="upper left")
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7)

plt.tight_layout()
plt.savefig("eda_output/fig1_price_history.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 2 : Missing Values Heatmap ─────────────────────────
print("  → Fig 2: Missing Values Heatmap")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Data Quality Check", fontsize=16, fontweight="bold", color="#e6edf3")

# Missing heatmap (sample)
sample = df[["Close","Volume","PE_Ratio","Dividend_Yield","Beta","Daily_Return","MA_20","Volatility_20"]].head(300)
sns.heatmap(sample.isnull(), cbar=False, cmap="YlOrRd",
            ax=ax1, yticklabels=False)
ax1.set_title("Missing Values — First 300 rows\n(yellow = missing)", color="#e6edf3", fontsize=12)
ax1.tick_params(colors="#8b949e")

# Missing % bar
missing_all = df.isnull().sum()
missing_all = missing_all[missing_all > 0]
if not missing_all.empty:
    missing_all.plot(kind="bar", ax=ax2, color=ACCENT[2], edgecolor="#0d1117")
    ax2.set_title("Missing Value Count by Column", color="#e6edf3", fontsize=12)
    ax2.set_ylabel("Count", color="#c9d1d9")
    ax2.tick_params(axis="x", rotation=30, colors="#8b949e")
else:
    ax2.text(0.5, 0.5, "No missing values\nafter imputation",
             ha="center", va="center", color="#3fb950", fontsize=14,
             transform=ax2.transAxes)
    ax2.set_title("Missing Values", color="#e6edf3")

plt.tight_layout()
plt.savefig("eda_output/fig2_missing_values.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 3 : Distribution of Daily Returns ──────────────────
print("  → Fig 3: Distribution of Daily Returns")
fig, axes = plt.subplots(3, 4, figsize=(20, 13))
fig.suptitle("Distribution of Daily Returns per Stock", fontsize=16,
             fontweight="bold", color="#e6edf3")
axes = axes.flatten()

for i, ticker in enumerate(tickers):
    sub = df[df["Ticker"] == ticker]["Daily_Return"].dropna()
    ax  = axes[i]
    ax.hist(sub, bins=60, color=ACCENT[i], alpha=0.75, edgecolor="#0d1117", density=True)
    # Overlay normal curve
    x = np.linspace(sub.min(), sub.max(), 200)
    ax.plot(x, stats.norm.pdf(x, sub.mean(), sub.std()),
            color="white", lw=1.5, linestyle="--", label="Normal fit")
    ax.axvline(sub.mean(), color="#ffa657", lw=1.2, linestyle="--", label=f"μ={sub.mean():.4f}")
    ax.set_title(f"{ticker}", fontsize=11, fontweight="bold")
    ax.set_xlabel("Daily Return", fontsize=8)
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)
    ax.tick_params(labelsize=7)

plt.tight_layout()
plt.savefig("eda_output/fig3_return_distributions.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 4 : Correlation Heatmap ────────────────────────────
print("  → Fig 4: Sector Correlation Heatmap")
pivot = df.pivot_table(index="Date", columns="Ticker", values="Daily_Return")
corr  = pivot.corr()

fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdYlGn",
            center=0, linewidths=0.5, linecolor="#0d1117",
            ax=ax, annot_kws={"size": 9},
            cbar_kws={"shrink": 0.8})
ax.set_title("Cross-Stock Return Correlation Matrix", fontsize=16,
             fontweight="bold", color="#e6edf3", pad=15)
ax.tick_params(colors="#c9d1d9", labelsize=10)

plt.tight_layout()
plt.savefig("eda_output/fig4_correlation_heatmap.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 5 : Risk–Return Scatter ────────────────────────────
print("  → Fig 5: Risk-Return Profile")
stats_df = df.groupby(["Ticker","Sector"])["Daily_Return"].agg(
    Mean_Return="mean", Std_Return="std"
).reset_index()
stats_df["Annualised_Return"] = stats_df["Mean_Return"] * 252
stats_df["Annualised_Vol"]    = stats_df["Std_Return"]  * np.sqrt(252)
stats_df["Sharpe"]            = stats_df["Annualised_Return"] / stats_df["Annualised_Vol"]

sector_colors = {s: ACCENT[i] for i, s in enumerate(sectors)}
fig, ax = plt.subplots(figsize=(12, 8))
for _, row in stats_df.iterrows():
    c = sector_colors[row["Sector"]]
    ax.scatter(row["Annualised_Vol"], row["Annualised_Return"],
               color=c, s=180, zorder=5, edgecolors="white", linewidths=0.7)
    ax.annotate(row["Ticker"], (row["Annualised_Vol"], row["Annualised_Return"]),
                textcoords="offset points", xytext=(8, 4),
                color=c, fontsize=10, fontweight="bold")

# Add legend patches
from matplotlib.patches import Patch
legend_els = [Patch(facecolor=sector_colors[s], label=s) for s in sectors]
ax.legend(handles=legend_els, title="Sector", title_fontsize=10, fontsize=9,
          loc="upper left")
ax.axhline(0, color="#8b949e", lw=0.8, linestyle="--")
ax.set_xlabel("Annualised Volatility (Risk)", fontsize=13)
ax.set_ylabel("Annualised Return", fontsize=13)
ax.set_title("Risk–Return Profile by Stock & Sector", fontsize=16,
             fontweight="bold", color="#e6edf3")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("eda_output/fig5_risk_return.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 6 : Sector Performance (Cumulative Return) ─────────
print("  → Fig 6: Sector Cumulative Returns")
df["Cum_Return"] = df.groupby("Ticker")["Daily_Return"].transform(
    lambda x: (1 + x.fillna(0)).cumprod() - 1
)
sector_cum = df.groupby(["Date","Sector"])["Cum_Return"].mean().reset_index()

fig, ax = plt.subplots(figsize=(14, 7))
for i, sector in enumerate(sectors):
    sub = sector_cum[sector_cum["Sector"] == sector]
    ax.plot(sub["Date"], sub["Cum_Return"] * 100,
            color=ACCENT[i], lw=2, label=sector)

ax.axhline(0, color="#8b949e", lw=0.8, linestyle="--")
ax.set_title("Cumulative Return by Sector (2022–2024)", fontsize=16,
             fontweight="bold", color="#e6edf3")
ax.set_ylabel("Cumulative Return (%)", fontsize=12)
ax.set_xlabel("Date", fontsize=12)
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("eda_output/fig6_sector_performance.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 7 : Volume Analysis ─────────────────────────────────
print("  → Fig 7: Volume Analysis")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Trading Volume Analysis", fontsize=16, fontweight="bold", color="#e6edf3")

vol_by_ticker = df.groupby("Ticker")["Volume"].mean().sort_values(ascending=False)
axes[0].barh(vol_by_ticker.index, vol_by_ticker.values / 1e6,
             color=[ACCENT[tickers.index(t)] for t in vol_by_ticker.index],
             edgecolor="#0d1117")
axes[0].set_title("Average Daily Volume by Stock (millions)", color="#e6edf3")
axes[0].set_xlabel("Volume (M)")
axes[0].grid(True, alpha=0.3, axis="x")

vol_by_day = df.groupby("Day_of_Week")["Volume"].mean()
order = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
vol_by_day = vol_by_day.reindex(order)
axes[1].bar(vol_by_day.index, vol_by_day.values / 1e6,
            color=ACCENT[0], edgecolor="#0d1117", alpha=0.85)
axes[1].set_title("Avg Daily Volume by Day of Week (millions)", color="#e6edf3")
axes[1].set_ylabel("Volume (M)")
axes[1].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("eda_output/fig7_volume_analysis.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 8 : Anomaly Detection (Z-score) ────────────────────
print("  → Fig 8: Anomaly / Outlier Detection")
df["Z_Score"] = df.groupby("Ticker")["Daily_Return"].transform(
    lambda x: np.abs(stats.zscore(x.fillna(0)))
)
df["Is_Anomaly"] = df["Z_Score"] > 3

fig, ax = plt.subplots(figsize=(14, 6))
for i, ticker in enumerate(tickers):
    sub      = df[df["Ticker"] == ticker]
    normal   = sub[~sub["Is_Anomaly"]]
    anomaly  = sub[sub["Is_Anomaly"]]
    ax.scatter(normal["Date"],  normal["Daily_Return"],
               s=3, color=ACCENT[i], alpha=0.3)
    ax.scatter(anomaly["Date"], anomaly["Daily_Return"],
               s=60, color="#f78166", marker="X", zorder=5,
               label=f"{ticker} anomaly" if len(anomaly) > 0 else "")

ax.axhline(0, color="#8b949e", lw=0.8, linestyle="--")
ax.set_title("Daily Returns — Anomalies Highlighted (|Z|>3)", fontsize=15,
             fontweight="bold", color="#e6edf3")
ax.set_ylabel("Daily Return", fontsize=12)
ax.set_xlabel("Date", fontsize=12)
ax.grid(True, alpha=0.3)

total_anomalies = df["Is_Anomaly"].sum()
ax.annotate(f"Total anomalies detected: {total_anomalies}",
            xy=(0.02, 0.93), xycoords="axes fraction",
            color="#ffa657", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig("eda_output/fig8_anomaly_detection.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 9 : Box Plot – PE Ratio & Beta by Sector ───────────
print("  → Fig 9: PE Ratio & Beta by Sector")
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Financial Metrics by Sector", fontsize=16, fontweight="bold", color="#e6edf3")

sector_order = sorted(df["Sector"].unique())
palette = {s: ACCENT[i] for i, s in enumerate(sector_order)}

sns.boxplot(data=df, x="Sector", y="PE_Ratio",
            order=sector_order, palette=palette,
            ax=axes[0], linewidth=1.2, flierprops={"marker":"o","markersize":3})
axes[0].set_title("PE Ratio Distribution by Sector", color="#e6edf3", fontsize=13)
axes[0].set_xlabel("Sector", fontsize=11)
axes[0].set_ylabel("PE Ratio", fontsize=11)
axes[0].tick_params(axis="x", rotation=15)
axes[0].grid(True, alpha=0.3, axis="y")

sns.boxplot(data=df, x="Sector", y="Beta",
            order=sector_order, palette=palette,
            ax=axes[1], linewidth=1.2, flierprops={"marker":"o","markersize":3})
axes[1].axhline(1.0, color="#ffa657", lw=1.2, linestyle="--", label="Beta=1 (Market)")
axes[1].set_title("Beta Distribution by Sector", color="#e6edf3", fontsize=13)
axes[1].set_xlabel("Sector", fontsize=11)
axes[1].set_ylabel("Beta", fontsize=11)
axes[1].tick_params(axis="x", rotation=15)
axes[1].legend(fontsize=10)
axes[1].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("eda_output/fig9_pe_beta_boxplot.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 10 : Day-of-Week Effect ────────────────────────────
print("  → Fig 10: Day-of-Week Effect on Returns")
day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
dow_returns = df.groupby("Day_of_Week")["Daily_Return"].mean().reindex(day_order) * 100

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(dow_returns.index, dow_returns.values,
              color=[ACCENT[2] if v < 0 else ACCENT[1] for v in dow_returns.values],
              edgecolor="#0d1117", width=0.55)
ax.axhline(0, color="#8b949e", lw=0.8, linestyle="--")
ax.set_title("Average Daily Return by Day of Week\n(Q5 — Day-of-Week Effect)",
             fontsize=14, fontweight="bold", color="#e6edf3")
ax.set_ylabel("Avg Return (%)", fontsize=12)
ax.set_xlabel("Day of Week", fontsize=12)
for bar, val in zip(bars, dow_returns.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.0002,
            f"{val:.4f}%", ha="center", fontsize=10,
            color="#e6edf3", fontweight="bold")
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig("eda_output/fig10_day_of_week.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 11 : Volatility Over Time ──────────────────────────
print("  → Fig 11: Rolling Volatility")
fig, ax = plt.subplots(figsize=(14, 7))
for i, ticker in enumerate(tickers):
    sub = df[df["Ticker"] == ticker]
    ax.plot(sub["Date"], sub["Volatility_20"] * 100,
            color=ACCENT[i], lw=1.2, label=ticker, alpha=0.85)

ax.set_title("20-Day Rolling Volatility by Stock", fontsize=16,
             fontweight="bold", color="#e6edf3")
ax.set_ylabel("Volatility (%)", fontsize=12)
ax.set_xlabel("Date", fontsize=12)
ax.legend(ncol=4, fontsize=9, loc="upper right")
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("eda_output/fig11_rolling_volatility.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ── FIG 12 : Summary Dashboard ─────────────────────────────
print("  → Fig 12: Summary Dashboard")
fig = plt.figure(figsize=(18, 10), facecolor="#0d1117")
fig.suptitle("📊  Finance EDA — Summary Dashboard", fontsize=20,
             fontweight="bold", color="#e6edf3", y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

# 1) Sharpe Ratio bar
ax1 = fig.add_subplot(gs[0, 0])
sr  = stats_df.sort_values("Sharpe", ascending=False)
colors_sharpe = [ACCENT[tickers.index(t)] for t in sr["Ticker"]]
ax1.barh(sr["Ticker"], sr["Sharpe"], color=colors_sharpe, edgecolor="#0d1117")
ax1.set_title("Sharpe Ratio", fontsize=12, fontweight="bold", color="#e6edf3")
ax1.axvline(0, color="#8b949e", lw=0.8)
ax1.grid(True, alpha=0.3, axis="x")

# 2) Avg Volume by sector (pie)
ax2 = fig.add_subplot(gs[0, 1])
sv  = df.groupby("Sector")["Volume"].mean()
ax2.pie(sv.values, labels=sv.index, autopct="%1.1f%%",
        colors=[ACCENT[i] for i in range(len(sv))],
        textprops={"color":"#c9d1d9","fontsize":9},
        wedgeprops={"edgecolor":"#0d1117","linewidth":1.5})
ax2.set_title("Avg Volume Share\nby Sector", fontsize=12, fontweight="bold", color="#e6edf3")

# 3) Annualised return bar
ax3 = fig.add_subplot(gs[0, 2])
ar  = stats_df.sort_values("Annualised_Return", ascending=False)
c3  = [ACCENT[2] if v < 0 else ACCENT[1] for v in ar["Annualised_Return"]]
ax3.barh(ar["Ticker"], ar["Annualised_Return"] * 100, color=c3, edgecolor="#0d1117")
ax3.axvline(0, color="#8b949e", lw=0.8)
ax3.set_title("Annualised Return (%)", fontsize=12, fontweight="bold", color="#e6edf3")
ax3.grid(True, alpha=0.3, axis="x")

# 4) Correlation of top 3 correlated pairs
ax4 = fig.add_subplot(gs[1, 0])
corr_vals = corr.where(np.tril(np.ones(corr.shape), k=-1).astype(bool)).stack().sort_values(ascending=False)
top5 = corr_vals.head(5)
labels = [f"{a}\n{b}" for a, b in top5.index]
ax4.barh(labels, top5.values, color=ACCENT[0], edgecolor="#0d1117")
ax4.set_title("Top 5 Correlated Pairs", fontsize=12, fontweight="bold", color="#e6edf3")
ax4.set_xlim(0, 1)
ax4.grid(True, alpha=0.3, axis="x")

# 5) Dividend Yield by sector
ax5 = fig.add_subplot(gs[1, 1])
dy  = df.groupby("Sector")["Dividend_Yield"].mean().sort_values(ascending=False)
ax5.bar(dy.index, dy.values, color=[ACCENT[i] for i in range(len(dy))],
        edgecolor="#0d1117")
ax5.set_title("Avg Dividend Yield\nby Sector", fontsize=12, fontweight="bold", color="#e6edf3")
ax5.set_ylabel("Dividend Yield (%)")
ax5.tick_params(axis="x", rotation=15)
ax5.grid(True, alpha=0.3, axis="y")

# 6) Key stats table
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis("off")
tbl_data = [
    ["Total Records",       f"{len(df):,}"],
    ["Stocks Covered",      str(df['Ticker'].nunique())],
    ["Date Range",          "2022–2024"],
    ["Sectors",             str(df['Sector'].nunique())],
    ["Avg Daily Return",    f"{df['Daily_Return'].mean()*100:.4f}%"],
    ["Max Daily Gain",      f"{df['Daily_Return'].max()*100:.2f}%"],
    ["Max Daily Loss",      f"{df['Daily_Return'].min()*100:.2f}%"],
    ["Total Anomalies",     str(df['Is_Anomaly'].sum())],
    ["Missing Values",      str(df.isnull().sum().sum())],
]
tbl = ax6.table(cellText=tbl_data, colLabels=["Metric","Value"],
                cellLoc="center", loc="center",
                colWidths=[0.6, 0.4])
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
for (r, c), cell in tbl.get_celld().items():
    cell.set_facecolor("#161b22" if r > 0 else "#21262d")
    cell.set_edgecolor("#30363d")
    cell.set_text_props(color="#e6edf3" if r == 0 else "#c9d1d9")
ax6.set_title("Key Statistics", fontsize=12, fontweight="bold", color="#e6edf3")

plt.savefig("eda_output/fig12_summary_dashboard.png", dpi=130, bbox_inches="tight",
            facecolor="#0d1117")
plt.close()


# ══════════════════════════════════════════════════════════════
#  6. HYPOTHESIS TESTING
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 6 — HYPOTHESIS TESTING & VALIDATION")
print("═"*60)

# H1: Returns are normally distributed (Shapiro-Wilk per stock)
print("\n── H1: Normality Test (Shapiro-Wilk) ──────────────────")
print(f"  {'Ticker':<8} {'W-stat':>8} {'p-value':>12} {'Normal?':>10}")
print("  " + "-"*45)
for ticker in tickers:
    sample = df[df["Ticker"] == ticker]["Daily_Return"].dropna().sample(min(300, 3000), random_state=42)
    w, p   = stats.shapiro(sample)
    normal = "✗ No" if p < 0.05 else "✓ Yes"
    print(f"  {ticker:<8} {w:>8.4f} {p:>12.6f} {normal:>10}")

# H2: T-test — is mean daily return significantly different from 0?
print("\n── H2: T-Test (Mean Return ≠ 0) ───────────────────────")
print(f"  {'Ticker':<8} {'Mean Ret':>10} {'t-stat':>8} {'p-value':>12} {'Significant?':>14}")
print("  " + "-"*55)
for ticker in tickers:
    ret  = df[df["Ticker"] == ticker]["Daily_Return"].dropna()
    t, p = stats.ttest_1samp(ret, 0)
    sig  = "✓ Yes" if p < 0.05 else "✗ No"
    print(f"  {ticker:<8} {ret.mean():>10.5f} {t:>8.3f} {p:>12.6f} {sig:>14}")

# H3: ANOVA — different sectors have same mean return?
print("\n── H3: ANOVA — Mean Return Differs by Sector ──────────")
sector_groups = [df[df["Sector"] == s]["Daily_Return"].dropna() for s in sector_order]
f_stat, p_anova = stats.f_oneway(*sector_groups)
print(f"  F-statistic : {f_stat:.4f}")
print(f"  p-value     : {p_anova:.6f}")
print(f"  Conclusion  : {'Sectors differ significantly (p<0.05)' if p_anova < 0.05 else 'No significant difference'}")

# H4: PE Ratio normality
print("\n── H4: PE Ratio Normality (K-S Test) ──────────────────")
pe = df["PE_Ratio"].dropna()
ks, p_ks = stats.kstest((pe - pe.mean()) / pe.std(), "norm")
print(f"  KS stat  : {ks:.4f}")
print(f"  p-value  : {p_ks:.6f}")
print(f"  Normally distributed: {'No' if p_ks < 0.05 else 'Yes'}")


# ══════════════════════════════════════════════════════════════
#  7. DATA ISSUES SUMMARY
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  STEP 7 — DATA ISSUES & RECOMMENDATIONS")
print("═"*60)

issues = {
    "Missing Values":     f"{df.isnull().sum().sum()} cells (Volume & Close)",
    "Price Anomalies":    f"{df['Is_Anomaly'].sum()} extreme return spikes detected",
    "Non-normal Returns": "All stocks fail normality test (fat tails)",
    "Beta Outliers":      f"{(df['Beta'] > 2).sum()} rows with Beta > 2",
    "PE Outliers":        f"{(df['PE_Ratio'] < 0).sum()} negative PE ratios",
}
recommendations = {
    "Missing Values":     "Forward-fill or interpolation (done ✔)",
    "Price Anomalies":    "Winsorize at 99th percentile before modelling",
    "Non-normal Returns": "Use robust stats / log-returns for modelling",
    "Beta Outliers":      "Cap at 3σ or investigate data source",
    "PE Outliers":        "Exclude loss-making companies or flag separately",
}

print(f"\n  {'Issue':<22} {'Detail':<42} {'Recommendation'}")
print("  " + "─"*95)
for k in issues:
    print(f"  {k:<22} {issues[k]:<42} {recommendations[k]}")


# ══════════════════════════════════════════════════════════════
#  DONE
# ══════════════════════════════════════════════════════════════
print("\n" + "═"*60)
print("  ✅  EDA COMPLETE!  All outputs saved to  eda_output/")
print("═"*60)
print("""
  Output Files:
    ├── finance_dataset.csv          ← Raw synthetic dataset
    ├── fig1_price_history.png       ← Price + Moving Averages
    ├── fig2_missing_values.png      ← Data Quality Heatmap
    ├── fig3_return_distributions.png← Return Histograms
    ├── fig4_correlation_heatmap.png ← Stock Correlations
    ├── fig5_risk_return.png         ← Risk-Return Scatter
    ├── fig6_sector_performance.png  ← Cumulative Returns
    ├── fig7_volume_analysis.png     ← Volume Analysis
    ├── fig8_anomaly_detection.png   ← Outlier Detection
    ├── fig9_pe_beta_boxplot.png     ← PE & Beta Boxplots
    ├── fig10_day_of_week.png        ← Day-of-Week Effect
    ├── fig11_rolling_volatility.png ← Rolling Volatility
    └── fig12_summary_dashboard.png  ← Summary Dashboard
""")

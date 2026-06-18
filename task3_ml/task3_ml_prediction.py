"""
============================================================
  TASK 3: Machine Learning — Stock Price Prediction
  Pure NumPy/Pandas — no sklearn required
  Models : Linear Regression, Ridge, Neural Network (MLP)
  Output : ml_output/ charts + results CSV
============================================================
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings, os
warnings.filterwarnings("ignore")

os.makedirs("ml_output", exist_ok=True)

# ── Style ──────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0d1117", "axes.facecolor": "#161b22",
    "axes.edgecolor": "#30363d",   "axes.labelcolor": "#c9d1d9",
    "axes.titlecolor": "#e6edf3",  "xtick.color": "#8b949e",
    "ytick.color": "#8b949e",      "text.color": "#c9d1d9",
    "grid.color": "#21262d",       "grid.linestyle": "--",
    "grid.alpha": 0.6,             "legend.facecolor": "#161b22",
    "legend.edgecolor": "#30363d", "font.family": "DejaVu Sans",
})
ACCENT = ["#58a6ff","#3fb950","#f78166","#d2a8ff","#ffa657",
          "#79c0ff","#56d364","#ff7b72","#bc8cff","#ffb77a",
          "#e3b341","#f0883e"]
BG = "#0d1117"

print("=" * 60)
print("  TASK 3 - ML STOCK PRICE PREDICTION (Pure NumPy)")
print("=" * 60)

# ══════════════════════════════════════════════════════════
#  HELPER: Pure-NumPy ML Models
# ══════════════════════════════════════════════════════════

class StandardScaler:
    def fit_transform(self, X):
        self.mean_ = X.mean(axis=0)
        self.std_  = X.std(axis=0) + 1e-8
        return (X - self.mean_) / self.std_
    def transform(self, X):
        return (X - self.mean_) / self.std_

class LinearRegression:
    """OLS via normal equation with optional ridge penalty."""
    def __init__(self, alpha=0.0):
        self.alpha = alpha
    def fit(self, X, y):
        Xb = np.c_[np.ones(len(X)), X]
        I  = np.eye(Xb.shape[1]); I[0,0] = 0
        self.coef_ = np.linalg.lstsq(Xb.T @ Xb + self.alpha * I,
                                      Xb.T @ y, rcond=None)[0]
    def predict(self, X):
        Xb = np.c_[np.ones(len(X)), X]
        return Xb @ self.coef_
    @property
    def feature_importances_(self):
        return np.abs(self.coef_[1:]) / (np.abs(self.coef_[1:]).sum() + 1e-9)

class MLP:
    """2-layer neural network with Adam optimiser."""
    def __init__(self, hidden=64, lr=1e-3, epochs=200, batch=64, random_state=42):
        self.hidden = hidden; self.lr = lr
        self.epochs = epochs; self.batch = batch
        np.random.seed(random_state)

    def _relu(self, z):      return np.maximum(0, z)
    def _relu_grad(self, z): return (z > 0).astype(float)

    def fit(self, X, y):
        n, d = X.shape
        h    = self.hidden
        # Xavier init
        self.W1 = np.random.randn(d, h) * np.sqrt(2/d)
        self.b1 = np.zeros(h)
        self.W2 = np.random.randn(h, 1) * np.sqrt(2/h)
        self.b2 = np.zeros(1)
        # Adam state
        m = {k: np.zeros_like(v) for k,v in
             [("W1",self.W1),("b1",self.b1),("W2",self.W2),("b2",self.b2)]}
        v = {k: np.zeros_like(v) for k,v in
             [("W1",self.W1),("b1",self.b1),("W2",self.W2),("b2",self.b2)]}
        t = 0; b1a=0.9; b2a=0.999; eps=1e-8

        y = y.reshape(-1, 1)
        for _ in range(self.epochs):
            idx = np.random.permutation(n)
            for start in range(0, n, self.batch):
                t += 1
                bi = idx[start:start+self.batch]
                Xb, yb = X[bi], y[bi]
                # Forward
                Z1 = Xb @ self.W1 + self.b1
                A1 = self._relu(Z1)
                Z2 = A1 @ self.W2 + self.b2
                loss = Z2 - yb
                # Backward
                dZ2 = loss / len(bi)
                dW2 = A1.T @ dZ2
                db2 = dZ2.sum(axis=0)
                dA1 = dZ2 @ self.W2.T
                dZ1 = dA1 * self._relu_grad(Z1)
                dW1 = Xb.T @ dZ1
                db1 = dZ1.sum(axis=0)
                # Adam update
                for name, param, grad in [
                    ("W1",self.W1,dW1),("b1",self.b1,db1),
                    ("W2",self.W2,dW2),("b2",self.b2,db2)]:
                    m[name] = b1a*m[name] + (1-b1a)*grad
                    v[name] = b2a*v[name] + (1-b2a)*grad**2
                    mh = m[name]/(1-b1a**t)
                    vh = v[name]/(1-b2a**t)
                    param -= self.lr * mh / (np.sqrt(vh)+eps)

    def predict(self, X):
        A1 = self._relu(X @ self.W1 + self.b1)
        return (A1 @ self.W2 + self.b2).flatten()

    @property
    def feature_importances_(self):
        imp = np.abs(self.W1).mean(axis=1)
        return imp / (imp.sum() + 1e-9)

def rmse(y, yhat):  return float(np.sqrt(np.mean((y - yhat)**2)))
def mae(y, yhat):   return float(np.mean(np.abs(y - yhat)))
def r2(y, yhat):    return float(1 - np.sum((y-yhat)**2) / (np.sum((y-y.mean())**2)+1e-9))
def dir_acc(y, yh): return float(np.mean(np.sign(y) == np.sign(yh)) * 100)

# ══════════════════════════════════════════════════════════
#  1. LOAD DATA
# ══════════════════════════════════════════════════════════
print("\n[1] Loading dataset...")
df = pd.read_csv("../task2_eda/eda_output/finance_dataset.csv", parse_dates=["Date"])
df = df.sort_values(["Ticker","Date"]).reset_index(drop=True)
df["Close"] = df.groupby("Ticker")["Close"].transform(lambda x: x.ffill())
print(f"    Rows: {len(df):,}  |  Tickers: {df['Ticker'].nunique()}")

tickers = ["AAPL","MSFT","GOOGL","AMZN","TSLA","JPM","BAC","GS","JNJ","PFE","XOM","CVX"]

# ══════════════════════════════════════════════════════════
#  2. FEATURE ENGINEERING
# ══════════════════════════════════════════════════════════
print("\n[2] Engineering features...")

def make_features(sub):
    sub = sub.copy().sort_values("Date").reset_index(drop=True)
    c = sub["Close"]
    for lag in [1,2,3,5,10]:
        sub[f"Ret_lag{lag}"] = c.pct_change(lag)
    for w in [5,10,20,50]:
        sub[f"MA{w}_ratio"] = c / (c.rolling(w).mean() + 1e-9)
    # Bollinger
    mid = c.rolling(20).mean(); std = c.rolling(20).std()
    sub["BB_pos"] = (c - (mid - 2*std)) / (4*std + 1e-9)
    # RSI
    d = c.diff()
    sub["RSI"] = 100 - 100/(1+(d.clip(lower=0).rolling(14).mean()
                               /(-d.clip(upper=0).rolling(14).mean()+1e-9)))
    # MACD
    sub["MACD"]      = c.ewm(span=12).mean() - c.ewm(span=26).mean()
    sub["MACD_hist"] = sub["MACD"] - sub["MACD"].ewm(span=9).mean()
    # Volume
    if "Volume" in sub.columns:
        sub["Vol_ratio"] = sub["Volume"] / (sub["Volume"].rolling(10).mean() + 1e-9)
    else:
        sub["Vol_ratio"] = 1.0
    sub["Volatility"]  = sub["Ret_lag1"].rolling(20).std()
    sub["Day_of_week"] = pd.to_datetime(sub["Date"]).dt.dayofweek
    sub["Month"]       = pd.to_datetime(sub["Date"]).dt.month
    sub["Target_Ret"]  = c.pct_change().shift(-1)
    sub["Target_Price"]= c.shift(-1)
    return sub

all_data = [make_features(df[df["Ticker"]==t].copy()) for t in tickers]
df_feat  = pd.concat(all_data, ignore_index=True)

FEATURE_COLS = [
    "Ret_lag1","Ret_lag2","Ret_lag3","Ret_lag5","Ret_lag10",
    "MA5_ratio","MA10_ratio","MA20_ratio","MA50_ratio",
    "BB_pos","RSI","MACD","MACD_hist","Vol_ratio",
    "Volatility","Day_of_week","Month"
]
print(f"    Features: {len(FEATURE_COLS)}  |  Dataset shape: {df_feat.shape}")

# ══════════════════════════════════════════════════════════
#  3. TRAIN & EVALUATE
# ══════════════════════════════════════════════════════════
print("\n[3] Training models...")
print(f"    {'Ticker':<8} {'LR_RMSE':>9} {'Ridge_RMSE':>11} "
      f"{'MLP_RMSE':>10} {'MLP_DA':>8}")
print("    " + "-"*52)

results, all_preds = [], {}

models_def = {
    "Linear Regression": LinearRegression(alpha=0.0),
    "Ridge Regression":  LinearRegression(alpha=1.0),
    "Neural Network":    MLP(hidden=64, lr=5e-4, epochs=150, batch=64),
}

for ticker in tickers:
    sub = df_feat[df_feat["Ticker"]==ticker].copy()
    sub = sub.dropna(subset=FEATURE_COLS+["Target_Ret","Target_Price"])
    sub = sub.sort_values("Date").reset_index(drop=True)

    split    = int(len(sub) * 0.8)
    train    = sub.iloc[:split]
    test     = sub.iloc[split:]

    scaler   = StandardScaler()
    Xtr      = scaler.fit_transform(train[FEATURE_COLS].values.astype(float))
    Xte      = scaler.transform(test[FEATURE_COLS].values.astype(float))
    ytr      = train["Target_Ret"].values.astype(float)
    yte      = test["Target_Ret"].values.astype(float)

    pdata    = {"Date": test["Date"].values,
                "Actual_Close": test["Target_Price"].values,
                "Actual_Return": yte}

    last_price = float(train["Close"].iloc[-1])
    rmse_vals  = {}

    for name, model in models_def.items():
        model.fit(Xtr, ytr)
        pred = model.predict(Xte)
        pdata[f"{name}_pred"] = pred
        pdata[f"{name}_price"] = last_price * np.cumprod(1 + pred)
        pdata[f"{name}_fi"]    = model.feature_importances_

        results.append({"Ticker": ticker, "Model": name,
                        "RMSE": rmse(yte, pred),  "MAE": mae(yte, pred),
                        "R2":   r2(yte, pred),    "Dir_Acc": dir_acc(yte, pred)})
        rmse_vals[name] = rmse(yte, pred)

    all_preds[ticker] = pdata
    nn_da = dir_acc(yte, pdata["Neural Network_pred"])
    print(f"    {ticker:<8} {rmse_vals['Linear Regression']:>9.5f} "
          f"{rmse_vals['Ridge Regression']:>11.5f} "
          f"{rmse_vals['Neural Network']:>10.5f} {nn_da:>7.1f}%")

results_df = pd.DataFrame(results)
results_df.to_csv("ml_output/model_results.csv", index=False)

# ══════════════════════════════════════════════════════════
#  4. VISUALISATIONS
# ══════════════════════════════════════════════════════════
print("\n[4] Generating charts...")

# ── Fig 1: Actual vs Predicted Returns (Neural Network) ───
print("    -> Fig 1: Actual vs Predicted Returns")
fig, axes = plt.subplots(4, 3, figsize=(20,16))
fig.suptitle("Task 3 — Neural Network: Actual vs Predicted Returns",
             fontsize=17, fontweight="bold", color="#e6edf3", y=1.01)
axes = axes.flatten()
for i, t in enumerate(tickers):
    ax    = axes[i]
    pd_   = all_preds[t]
    dates = pd.to_datetime(pd_["Date"])
    ax.plot(dates, pd_["Actual_Return"]*100,       color="#8b949e", lw=0.8, alpha=0.7, label="Actual")
    ax.plot(dates, pd_["Neural Network_pred"]*100, color=ACCENT[i], lw=1.3, alpha=0.9, label="NN Pred")
    ax.axhline(0, color="#30363d", lw=0.8)
    ax.set_title(t, fontsize=11, fontweight="bold")
    ax.set_ylabel("Return (%)", fontsize=8)
    ax.legend(fontsize=7); ax.tick_params(labelsize=7); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("ml_output/fig1_actual_vs_predicted.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ── Fig 2: Predicted Price Path ────────────────────────────
print("    -> Fig 2: Predicted Price Path")
fig, axes = plt.subplots(4, 3, figsize=(20,16))
fig.suptitle("Task 3 — Predicted vs Actual Price (Test Set)",
             fontsize=17, fontweight="bold", color="#e6edf3", y=1.01)
axes = axes.flatten()
for i, t in enumerate(tickers):
    ax    = axes[i]
    pd_   = all_preds[t]
    dates = pd.to_datetime(pd_["Date"])
    ax.plot(dates, pd_["Actual_Close"],              color="white",   lw=1.5, label="Actual")
    ax.plot(dates, pd_["Linear Regression_price"],   color="#ffa657", lw=1.0, linestyle="--", label="LR",    alpha=0.8)
    ax.plot(dates, pd_["Ridge Regression_price"],    color="#d2a8ff", lw=1.0, linestyle=":",  label="Ridge", alpha=0.8)
    ax.plot(dates, pd_["Neural Network_price"],      color=ACCENT[i], lw=1.3, label="NN",    alpha=0.9)
    ax.set_title(t, fontsize=11, fontweight="bold")
    ax.set_ylabel("Price ($)", fontsize=8)
    ax.legend(fontsize=7); ax.tick_params(labelsize=7); ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("ml_output/fig2_price_predictions.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ── Fig 3: Model Comparison ────────────────────────────────
print("    -> Fig 3: Model Comparison")
fig, axes = plt.subplots(1, 3, figsize=(18,7))
fig.suptitle("Task 3 — Model Performance Comparison",
             fontsize=16, fontweight="bold", color="#e6edf3")
metrics_info = [("RMSE","RMSE (lower=better)","#f78166"),
                ("MAE", "MAE  (lower=better)","#ffa657"),
                ("Dir_Acc","Directional Accuracy % (higher=better)","#3fb950")]
for j,(metric,title,color) in enumerate(metrics_info):
    ax    = axes[j]
    pivot = results_df.groupby("Model")[metric].mean()
    bars  = ax.bar(pivot.index, pivot.values, color=color, edgecolor=BG, alpha=0.85)
    ax.set_title(title, fontsize=12, fontweight="bold", color="#e6edf3")
    ax.tick_params(axis="x", rotation=15, labelsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    for bar, val in zip(bars, pivot.values):
        label = f"{val:.1f}%" if metric=="Dir_Acc" else f"{val:.5f}"
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()*1.01,
                label, ha="center", fontsize=9, color="#e6edf3", fontweight="bold")
plt.tight_layout()
plt.savefig("ml_output/fig3_model_comparison.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ── Fig 4: Feature Importance ─────────────────────────────
print("    -> Fig 4: Feature Importance")
nn_fis = [all_preds[t]["Neural Network_fi"] for t in tickers]
avg_fi = np.mean(nn_fis, axis=0)
fi_df  = pd.DataFrame({"Feature": FEATURE_COLS, "Importance": avg_fi})
fi_df  = fi_df.sort_values("Importance")
fig, ax = plt.subplots(figsize=(12,9))
ax.barh(fi_df["Feature"], fi_df["Importance"],
        color=ACCENT[0], edgecolor=BG, alpha=0.85)
ax.set_title("Neural Network — Average Feature Importance\n(input weight magnitude across all 12 stocks)",
             fontsize=14, fontweight="bold", color="#e6edf3")
ax.set_xlabel("Importance Score", fontsize=11)
ax.grid(True, alpha=0.3, axis="x")
plt.tight_layout()
plt.savefig("ml_output/fig4_feature_importance.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ── Fig 5: Directional Accuracy ────────────────────────────
print("    -> Fig 5: Directional Accuracy per Stock")
model_names = ["Linear Regression","Ridge Regression","Neural Network"]
da_pivot    = results_df.pivot(index="Ticker", columns="Model", values="Dir_Acc")
x = np.arange(len(tickers)); w = 0.25
fig, ax = plt.subplots(figsize=(14,7))
for j,(m,c) in enumerate(zip(model_names,[ACCENT[2],ACCENT[4],ACCENT[0]])):
    ax.bar(x + j*w, da_pivot[m], w, label=m, color=c, edgecolor=BG, alpha=0.85)
ax.axhline(50, color="#8b949e", lw=1.2, linestyle="--", label="Random (50%)")
ax.set_xticks(x + w); ax.set_xticklabels(tickers, fontsize=10)
ax.set_ylabel("Directional Accuracy (%)", fontsize=12)
ax.set_title("Directional Accuracy per Stock & Model\n(can model predict up/down correctly?)",
             fontsize=14, fontweight="bold", color="#e6edf3")
ax.legend(fontsize=10); ax.set_ylim(0,100); ax.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig("ml_output/fig5_directional_accuracy.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ── Fig 6: R2 Heatmap ─────────────────────────────────────
print("    -> Fig 6: R2 Heatmap")
r2_pivot = results_df.pivot(index="Ticker", columns="Model", values="R2")
fig, ax  = plt.subplots(figsize=(11,9))
sns.heatmap(r2_pivot, annot=True, fmt=".3f", cmap="RdYlGn",
            center=0, linewidths=0.5, linecolor=BG, ax=ax,
            annot_kws={"size":10}, cbar_kws={"shrink":0.8})
ax.set_title("R2 Score by Stock & Model\n(higher = better fit)",
             fontsize=14, fontweight="bold", color="#e6edf3", pad=15)
ax.tick_params(colors="#c9d1d9", labelsize=10)
plt.tight_layout()
plt.savefig("ml_output/fig6_r2_heatmap.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ── Fig 7: ML Summary Dashboard ───────────────────────────
print("    -> Fig 7: ML Summary Dashboard")
fig = plt.figure(figsize=(18,10), facecolor=BG)
fig.suptitle("Task 3 - ML Prediction Summary Dashboard",
             fontsize=20, fontweight="bold", color="#e6edf3", y=0.98)
gs = gridspec.GridSpec(2,3, figure=fig, hspace=0.45, wspace=0.35,
                       left=0.06, right=0.97, top=0.88, bottom=0.07)

# Best model pie
ax1 = fig.add_subplot(gs[0,0])
best_model   = results_df.loc[results_df.groupby("Ticker")["RMSE"].idxmin()]
model_counts = best_model["Model"].value_counts()
ax1.pie(model_counts.values, labels=model_counts.index, autopct="%1.0f%%",
        colors=[ACCENT[0],ACCENT[1],ACCENT[2]][:len(model_counts)],
        textprops={"color":"#c9d1d9","fontsize":9},
        wedgeprops={"edgecolor":BG,"linewidth":1.5})
ax1.set_title("Best Model\n(lowest RMSE per stock)", fontsize=11,
              fontweight="bold", color="#e6edf3")

# RMSE per ticker (NN)
ax2 = fig.add_subplot(gs[0,1])
nn_rmse = results_df[results_df["Model"]=="Neural Network"].set_index("Ticker")["RMSE"]
ax2.bar(nn_rmse.index, nn_rmse.values,
        color=[ACCENT[i] for i in range(len(tickers))], edgecolor=BG)
ax2.set_title("Neural Network RMSE\nper Stock (test set)", fontsize=11,
              fontweight="bold", color="#e6edf3")
ax2.set_ylabel("RMSE", fontsize=9)
ax2.tick_params(axis="x", rotation=45, labelsize=8)
ax2.grid(True, alpha=0.3, axis="y")

# Avg Directional Accuracy
ax3 = fig.add_subplot(gs[0,2])
da_avg = results_df.groupby("Model")["Dir_Acc"].mean()
bars   = ax3.bar(da_avg.index, da_avg.values,
                 color=[ACCENT[2],ACCENT[4],ACCENT[0]], edgecolor=BG, alpha=0.85)
ax3.axhline(50, color="#8b949e", lw=1.2, linestyle="--")
ax3.set_title("Avg Directional Accuracy\nby Model", fontsize=11,
              fontweight="bold", color="#e6edf3")
ax3.set_ylim(0,100); ax3.tick_params(axis="x", rotation=15, labelsize=9)
ax3.grid(True, alpha=0.3, axis="y")
for bar, val in zip(bars, da_avg.values):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
             f"{val:.1f}%", ha="center", fontsize=9, color="#e6edf3")

# Feature importance top 8
ax4 = fig.add_subplot(gs[1,0:2])
fi_top = fi_df.tail(8)
ax4.barh(fi_top["Feature"], fi_top["Importance"],
         color=ACCENT[0], edgecolor=BG, alpha=0.85)
ax4.set_title("Top 8 Features (Neural Network)", fontsize=11,
              fontweight="bold", color="#e6edf3")
ax4.grid(True, alpha=0.3, axis="x")

# Stats table
ax5 = fig.add_subplot(gs[1,2])
ax5.axis("off")
nn_res  = results_df[results_df["Model"]=="Neural Network"]
best_da = nn_res.loc[nn_res["Dir_Acc"].idxmax()]
tbl_data= [
    ["Models Trained",   "3 (LR, Ridge, NN)"],
    ["Stocks Covered",   "12"],
    ["Training Split",   "80% / 20%"],
    ["Features Used",    str(len(FEATURE_COLS))],
    ["Best DA Stock",    f"{best_da['Ticker']} ({best_da['Dir_Acc']:.1f}%)"],
    ["Avg NN RMSE",      f"{nn_res['RMSE'].mean():.5f}"],
    ["Avg NN R2",        f"{nn_res['R2'].mean():.4f}"],
    ["Avg Dir. Acc.",    f"{nn_res['Dir_Acc'].mean():.1f}%"],
]
tbl = ax5.table(cellText=tbl_data, colLabels=["Metric","Value"],
                cellLoc="center", loc="center", colWidths=[0.6,0.4])
tbl.auto_set_font_size(False); tbl.set_fontsize(9)
for (r,c), cell in tbl.get_celld().items():
    cell.set_facecolor("#161b22" if r>0 else "#21262d")
    cell.set_edgecolor("#30363d")
    cell.set_text_props(color="#e6edf3" if r==0 else "#c9d1d9")
ax5.set_title("Key ML Statistics", fontsize=11, fontweight="bold", color="#e6edf3")

plt.savefig("ml_output/fig7_ml_dashboard.png", dpi=130,
            bbox_inches="tight", facecolor=BG)
plt.close()

# ══════════════════════════════════════════════════════════
#  DONE
# ══════════════════════════════════════════════════════════
nn_res = results_df[results_df["Model"]=="Neural Network"]
print("\n" + "=" * 60)
print("  TASK 3 COMPLETE!")
print("=" * 60)
print(f"""
  Models    : Linear Regression, Ridge Regression, Neural Network
  Stocks    : {len(tickers)}
  Features  : {len(FEATURE_COLS)}
  Avg NN R2 : {nn_res['R2'].mean():.4f}
  Avg Dir.  : {nn_res['Dir_Acc'].mean():.1f}%

  Saved to ml_output/:
    model_results.csv
    fig1_actual_vs_predicted.png
    fig2_price_predictions.png
    fig3_model_comparison.png
    fig4_feature_importance.png
    fig5_directional_accuracy.png
    fig6_r2_heatmap.png
    fig7_ml_dashboard.png
""")

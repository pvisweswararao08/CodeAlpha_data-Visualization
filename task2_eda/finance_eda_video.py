"""
============================================================
  FINANCE EDA — LIVE ANIMATED VIDEO DASHBOARD
  Saves as: eda_output/finance_eda_live.mp4 (or .gif)
============================================================
"""
import sys
sys.stdout.reconfigure(encoding="utf-8")

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter
from matplotlib.lines import Line2D
import warnings
warnings.filterwarnings("ignore")

# ── Config ─────────────────────────────────────────────────
STEP        = 2       # days to advance per frame (smaller = more frames = slower)
FPS         = 10      # lower fps = slower playback
OUTPUT_MP4  = "eda_output/finance_eda_live.mp4"
OUTPUT_GIF  = "eda_output/finance_eda_live.gif"

ACCENT = [
    "#58a6ff","#3fb950","#f78166","#d2a8ff","#ffa657",
    "#79c0ff","#56d364","#ff7b72","#bc8cff","#ffb77a",
    "#e3b341","#f0883e"
]
BG      = "#0d1117"
PANEL   = "#161b22"
BORDER  = "#30363d"
TEXT1   = "#e6edf3"
TEXT2   = "#8b949e"

# ── Load & Prepare Data ────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv("eda_output/finance_dataset.csv", parse_dates=["Date"])
df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)
df["Close"] = df.groupby("Ticker")["Close"].transform(lambda x: x.ffill())
df["Daily_Return"] = df.groupby("Ticker")["Close"].pct_change()

tickers = ["AAPL","MSFT","GOOGL","AMZN","TSLA","JPM","BAC","GS","JNJ","PFE","XOM","CVX"]
sectors = {"AAPL":"Tech","MSFT":"Tech","GOOGL":"Tech","AMZN":"Consumer",
           "TSLA":"Auto","JPM":"Finance","BAC":"Finance","GS":"Finance",
           "JNJ":"Health","PFE":"Health","XOM":"Energy","CVX":"Energy"}
sector_list = ["Tech","Consumer","Auto","Finance","Health","Energy"]
sector_colors = {s: ACCENT[i] for i, s in enumerate(sector_list)}
ticker_color  = {t: ACCENT[i] for i, t in enumerate(tickers)}

# Normalised close (base=100) per ticker
dates_all = sorted(df["Date"].unique())
pivot_close = df.pivot_table(index="Date", columns="Ticker", values="Close").ffill()
pivot_norm  = pivot_close.div(pivot_close.iloc[0]) * 100   # index to 100

# Sector average normalised price
for sec in sector_list:
    cols = [t for t in tickers if sectors[t] == sec]
    pivot_norm[f"__{sec}"] = pivot_norm[cols].mean(axis=1)

# Rolling 20-day volume per ticker
pivot_vol = df.pivot_table(index="Date", columns="Ticker", values="Volume").ffill()
pivot_vol_roll = pivot_vol.rolling(20).mean()

# Cumulative return
pivot_ret  = df.pivot_table(index="Date", columns="Ticker", values="Daily_Return").fillna(0)
pivot_cumret = (1 + pivot_ret).cumprod() - 1   # fraction

frames_dates = dates_all[::STEP]
N_FRAMES     = len(frames_dates)

print(f"  Tickers: {len(tickers)}  |  Trading days: {len(dates_all)}  |  Frames: {N_FRAMES}")
print(f"  Approx duration: {N_FRAMES/FPS:.1f}s @ {FPS}fps\n")

# ── Figure Layout ──────────────────────────────────────────
fig = plt.figure(figsize=(20, 11.25), facecolor=BG)   # 16:9 aspect
fig.patch.set_facecolor(BG)

gs = gridspec.GridSpec(
    3, 3,
    figure=fig,
    hspace=0.45, wspace=0.35,
    left=0.05, right=0.97,
    top=0.88,  bottom=0.07,
)

ax_main  = fig.add_subplot(gs[0:2, 0:2])   # big: stock prices
ax_sector= fig.add_subplot(gs[0,   2])     # sector perf
ax_vol   = fig.add_subplot(gs[1,   2])     # volume bars
ax_ret   = fig.add_subplot(gs[2,   0])     # daily return dist
ax_heat  = fig.add_subplot(gs[2,   1])     # top/bottom performers
ax_stats = fig.add_subplot(gs[2,   2])     # live stats

for ax in [ax_main, ax_sector, ax_vol, ax_ret, ax_heat, ax_stats]:
    ax.set_facecolor(PANEL)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.tick_params(colors=TEXT2, labelsize=8)
    ax.xaxis.label.set_color(TEXT2)
    ax.yaxis.label.set_color(TEXT2)
    ax.title.set_color(TEXT1)
    ax.grid(color="#21262d", linestyle="--", alpha=0.5)

# ── Title ──────────────────────────────────────────────────
title_text = fig.text(
    0.5, 0.955,
    "📈  Finance EDA — Live Market Dashboard  (2022–2024)",
    ha="center", va="center",
    fontsize=18, fontweight="bold", color=TEXT1,
    fontfamily="DejaVu Sans"
)
date_text = fig.text(
    0.5, 0.925,
    "", ha="center", va="center",
    fontsize=13, color="#ffa657", fontweight="bold"
)

# ── Pre-create line objects for main chart ─────────────────
main_lines = {}
for t in tickers:
    ln, = ax_main.plot([], [], color=ticker_color[t], lw=1.4,
                       label=t, alpha=0.9)
    main_lines[t] = ln

ax_main.set_title("Stock Price Index (Base = 100)", fontsize=12, fontweight="bold", pad=6)
ax_main.set_ylabel("Normalised Price", fontsize=9)
ax_main.legend(ncol=6, fontsize=7.5, loc="upper left",
               facecolor=PANEL, edgecolor=BORDER,
               labelcolor=TEXT1)
ax_main.set_xlim(dates_all[0], dates_all[-1])
ax_main.set_ylim(40, 350)

# ── Sector lines ───────────────────────────────────────────
sector_lines = {}
for sec in sector_list:
    ln, = ax_sector.plot([], [], color=sector_colors[sec], lw=2, label=sec)
    sector_lines[sec] = ln

ax_sector.set_title("Sector Performance", fontsize=11, fontweight="bold", pad=6)
ax_sector.set_ylabel("Index", fontsize=9)
ax_sector.legend(fontsize=7, loc="upper left", facecolor=PANEL,
                 edgecolor=BORDER, labelcolor=TEXT1)
ax_sector.set_xlim(dates_all[0], dates_all[-1])
ax_sector.set_ylim(40, 300)

# ── Volume bars (updated each frame) ──────────────────────
ax_vol.set_title("20-Day Avg Volume by Stock", fontsize=11, fontweight="bold", pad=6)
ax_vol.set_xlabel("")
vol_bars = ax_vol.bar(tickers, [0]*len(tickers),
                      color=[ticker_color[t] for t in tickers],
                      edgecolor=BG, width=0.6)
ax_vol.tick_params(axis="x", rotation=45, labelsize=7)
ax_vol.set_ylim(0, 12e6)
ax_vol.yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f"{x/1e6:.0f}M")
)

# ── Return distribution (histogram updated) ────────────────
ax_ret.set_title("Market Daily Return Dist.", fontsize=11, fontweight="bold", pad=6)
ax_ret.set_xlabel("Return", fontsize=8)
ax_ret.set_ylabel("Count", fontsize=8)
ax_ret.set_xlim(-0.12, 0.12)

# ── Top/Bottom performers bar ──────────────────────────────
ax_heat.set_title("Cumulative Return (%)", fontsize=11, fontweight="bold", pad=6)
ax_heat.set_xlim(-1, 1)
heat_bars = ax_heat.barh(tickers, [0]*len(tickers),
                          color=[ticker_color[t] for t in tickers],
                          edgecolor=BG, height=0.6)
ax_heat.axvline(0, color=TEXT2, lw=0.8)
ax_heat.tick_params(axis="y", labelsize=8)
ax_heat.set_xlabel("Cum. Return", fontsize=8)

# ── Stats panel ────────────────────────────────────────────
ax_stats.axis("off")
ax_stats.set_title("Live Statistics", fontsize=11, fontweight="bold", pad=6)
stats_text = ax_stats.text(
    0.05, 0.95, "",
    transform=ax_stats.transAxes,
    va="top", ha="left",
    fontsize=9, color=TEXT1,
    fontfamily="monospace",
    linespacing=1.8,
)

# ── Animation init ─────────────────────────────────────────
def init():
    for ln in main_lines.values():
        ln.set_data([], [])
    for ln in sector_lines.values():
        ln.set_data([], [])
    return list(main_lines.values()) + list(sector_lines.values())

# ── Animation update ───────────────────────────────────────
def update(frame_idx):
    cur_date  = frames_dates[frame_idx]
    cur_dates = [d for d in dates_all if d <= cur_date]

    # ── Main price lines ───────────────────────────────────
    norm_slice = pivot_norm.loc[pivot_norm.index <= cur_date]
    for t in tickers:
        vals = norm_slice[t].values
        main_lines[t].set_data(norm_slice.index, vals)

    # ── Sector lines ───────────────────────────────────────
    for sec in sector_list:
        vals = norm_slice[f"__{sec}"].values
        sector_lines[sec].set_data(norm_slice.index, vals)

    # ── Volume bars ────────────────────────────────────────
    vol_slice = pivot_vol_roll.loc[pivot_vol_roll.index <= cur_date]
    if len(vol_slice) > 0:
        row = vol_slice.iloc[-1]
        for bar, t in zip(vol_bars, tickers):
            val = row.get(t, 0)
            h   = 0 if (val is None or np.isnan(val)) else float(val)
            bar.set_height(max(h, 0))

    # ── Return distribution ────────────────────────────────
    ax_ret.cla()
    ax_ret.set_facecolor(PANEL)
    ax_ret.set_title("Market Daily Return Dist.", fontsize=11,
                     fontweight="bold", pad=6, color=TEXT1)
    ax_ret.set_xlabel("Return", fontsize=8, color=TEXT2)
    ax_ret.set_ylabel("Count", fontsize=8, color=TEXT2)
    ax_ret.grid(color="#21262d", linestyle="--", alpha=0.5)
    ax_ret.tick_params(colors=TEXT2, labelsize=8)
    for spine in ax_ret.spines.values():
        spine.set_edgecolor(BORDER)

    ret_slice = pivot_ret.loc[pivot_ret.index <= cur_date]
    all_rets  = ret_slice.values.flatten()
    all_rets  = all_rets[~np.isnan(all_rets)]
    all_rets  = all_rets[np.abs(all_rets) < 0.15]
    if len(all_rets) > 10:
        ax_ret.hist(all_rets, bins=60, color="#58a6ff", alpha=0.8,
                    edgecolor=BG, density=False)
        mu = all_rets.mean()
        ax_ret.axvline(mu, color="#ffa657", lw=1.5, label=f"mu={mu:.4f}")
        ax_ret.axvline(0, color=TEXT2, lw=0.8, linestyle="--")
        ax_ret.legend(fontsize=8, facecolor=PANEL,
                      edgecolor=BORDER, labelcolor=TEXT1)

    # ── Cumulative return bars ─────────────────────────────
    cumret_slice = pivot_cumret.loc[pivot_cumret.index <= cur_date]
    if len(cumret_slice) > 0:
        cum_row = cumret_slice.iloc[-1]
        vals    = [float(cum_row.get(t, 0)) for t in tickers]
        max_abs = max(max(abs(v) for v in vals), 0.01)
        ax_heat.set_xlim(-max_abs * 1.2, max_abs * 1.2)
        for bar, val in zip(heat_bars, vals):
            bar.set_width(val)
            bar.set_x(min(val, 0))
            bar.set_color("#3fb950" if val >= 0 else "#f78166")

        best_t  = cum_row.idxmax()
        worst_t = cum_row.idxmin()
        best_v  = cum_row.max()  * 100
        worst_v = cum_row.min()  * 100
        mkt_ret = cum_row.mean() * 100
        days_in = len(cur_dates)

        ret_slice2   = pivot_ret.loc[pivot_ret.index <= cur_date]
        last_ret_val = float(ret_slice2.iloc[-1].mean()) * 100 if len(ret_slice2) > 0 else 0.0

        stats_str = (
            f"  Date   : {cur_date.strftime('%d %b %Y')}\n"
            f"  Day    : {days_in} / {len(dates_all)}\n"
            f"  Prog.  : {days_in/len(dates_all)*100:.1f}%\n"
            f"\n"
            f"  Best   : {best_t}  {best_v:+.1f}%\n"
            f"  Worst  : {worst_t}  {worst_v:+.1f}%\n"
            f"\n"
            f"  Mkt Ret: {mkt_ret:+.1f}%\n"
            f"  Day Ret: {last_ret_val:+.3f}%\n"
            f"\n"
            f"  Stocks : {len(tickers)}\n"
            f"  Sectors: 6\n"
        )
        stats_text.set_text(stats_str)

    # update date label
    date_text.set_text(f"  {cur_date.strftime('%B %d, %Y')}")

    pct = int(frame_idx / N_FRAMES * 100)
    if frame_idx % 20 == 0:
        print(f"  Rendering... {pct}%  [{frame_idx}/{N_FRAMES} frames]",
              end="\r")

    return (list(main_lines.values()) +
            list(sector_lines.values()) +
            list(vol_bars) +
            list(heat_bars) +
            [stats_text, date_text])

# ── Render ─────────────────────────────────────────────────
print("Building animation...")
anim = FuncAnimation(
    fig,
    update,
    frames=N_FRAMES,
    init_func=init,
    interval=1000 / FPS,
    blit=False,
)

# Try MP4 first, fall back to GIF
saved = False
try:
    writer = FFMpegWriter(fps=FPS, bitrate=4000,
                          metadata={"title": "Finance EDA Live"})
    print(f"\nSaving MP4 → {OUTPUT_MP4}")
    anim.save(OUTPUT_MP4, writer=writer, dpi=100)
    print(f"\n✅  MP4 saved:  {OUTPUT_MP4}")
    saved = True
except Exception as e:
    print(f"\n⚠️  MP4 failed ({e}), trying GIF...")

if not saved:
    writer = PillowWriter(fps=FPS)
    print(f"Saving GIF → {OUTPUT_GIF}")
    anim.save(OUTPUT_GIF, writer=writer, dpi=80)
    print(f"\n✅  GIF saved:  {OUTPUT_GIF}")

plt.close()
print("\nDone! Open the file to watch the live EDA video.")

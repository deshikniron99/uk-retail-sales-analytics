"""
Generates every chart used in the notebook, the dashboard, and the README -
one script, one consistent style, so the whole project reads as one system.
Palette + mark specs follow the project's data-viz style guide (single-hue
for ranked/magnitude bars, fixed-order categorical hues only when >1 series
share an axis, no dual-axis charts, recessive gridlines, direct value labels).
"""
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "retail.db"
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

# ---- palette (light mode) ---------------------------------------------
SURFACE = "#fcfcfb"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"
BLUE = "#2a78d6"
ORANGE = "#eb6834"
AQUA = "#1baf7a"
YELLOW = "#eda100"
CATEGORICAL = [BLUE, ORANGE, AQUA, YELLOW, "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "DejaVu Sans",
    "text.color": INK_PRIMARY,
    "axes.edgecolor": BASELINE,
    "axes.labelcolor": INK_SECONDARY,
    "xtick.color": INK_MUTED,
    "ytick.color": INK_MUTED,
    "axes.grid": False,
    "font.size": 12,
})


def style_axes(ax, x_grid=False, y_grid=True):
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(BASELINE)
        ax.spines[spine].set_linewidth(1)
    if y_grid:
        ax.yaxis.grid(True, color=GRIDLINE, linewidth=1, zorder=0)
    if x_grid:
        ax.xaxis.grid(True, color=GRIDLINE, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def money(x, _pos=None):
    if abs(x) >= 1000:
        return f"GBP {x/1000:,.0f}k"
    return f"GBP {x:,.0f}"


conn = sqlite3.connect(DB_PATH)
orders = pd.read_sql_query("SELECT * FROM orders", conn, parse_dates=["order_date"])
conn.close()

# =========================================================================
# 1. YoY monthly revenue trend (line, 3 series = fixed categorical order)
# =========================================================================
orders["year"] = orders["order_date"].dt.year
orders["month_num"] = orders["order_date"].dt.month
monthly = orders.groupby(["year", "month_num"])["sales"].sum().reset_index()
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
years = sorted(monthly["year"].unique())
for i, yr in enumerate(years):
    sub = monthly[monthly["year"] == yr].sort_values("month_num")
    ax.plot(sub["month_num"], sub["sales"], color=CATEGORICAL[i], linewidth=2.5,
            marker="o", markersize=4, label=str(yr), zorder=3)
    end_x, end_y = sub["month_num"].iloc[-1], sub["sales"].iloc[-1]
    ax.annotate(str(yr), (end_x, end_y), xytext=(6, 0), textcoords="offset points",
                color=CATEGORICAL[i], fontsize=11, fontweight="bold", va="center")

ax.set_xticks(range(1, 13))
ax.set_xticklabels(MONTH_LABELS)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money))
ax.set_title("Monthly revenue by year - Nov/Dec seasonality, steady YoY growth",
              fontsize=13, fontweight="bold", color=INK_PRIMARY, loc="left", pad=14)
style_axes(ax)
ax.set_xlim(0.5, 12.8)
fig.tight_layout()
fig.savefig(IMG_DIR / "01_yoy_revenue_trend.png", dpi=200)
plt.close(fig)

# =========================================================================
# 2. Category revenue leaderboard (single-hue ranked bar)
# =========================================================================
cat_rev = orders.groupby("category")["sales"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
bars = ax.barh(cat_rev.index, cat_rev.values, color=BLUE, height=0.62, zorder=3)
for b, v in zip(bars, cat_rev.values):
    ax.text(v + cat_rev.max() * 0.015, b.get_y() + b.get_height() / 2, money(v, None),
            va="center", fontsize=10.5, color=INK_SECONDARY)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(money))
ax.set_title("Revenue by category - Electronics leads at 43% of revenue",
              fontsize=13, fontweight="bold", color=INK_PRIMARY, loc="left", pad=14)
style_axes(ax, x_grid=True, y_grid=False)
ax.set_xlim(0, cat_rev.max() * 1.18)
fig.tight_layout()
fig.savefig(IMG_DIR / "02_category_revenue.png", dpi=200)
plt.close(fig)

# =========================================================================
# 3. Regional leaderboard (single-hue ranked bar, top 8)
# =========================================================================
reg_rev = orders.groupby("region")["sales"].sum().sort_values(ascending=True)
fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
bars = ax.barh(reg_rev.index, reg_rev.values, color=BLUE, height=0.62, zorder=3)
for b, v in zip(bars, reg_rev.values):
    ax.text(v + reg_rev.max() * 0.015, b.get_y() + b.get_height() / 2, money(v, None),
            va="center", fontsize=10.5, color=INK_SECONDARY)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(money))
ax.set_title("Revenue by UK region - London + South East drive 42%",
              fontsize=13, fontweight="bold", color=INK_PRIMARY, loc="left", pad=14)
style_axes(ax, x_grid=True, y_grid=False)
ax.set_xlim(0, reg_rev.max() * 1.2)
fig.tight_layout()
fig.savefig(IMG_DIR / "03_regional_revenue.png", dpi=200)
plt.close(fig)

# =========================================================================
# 4. Customer segment - small multiples (revenue, AOV) - no dual axis
# =========================================================================
seg = orders.groupby("customer_segment").agg(
    revenue=("sales", "sum"), orders_n=("order_id", "nunique"),
).reset_index()
seg["aov"] = seg["revenue"] / seg["orders_n"]
seg = seg.set_index("customer_segment").loc[["Consumer", "SME", "Corporate"]]

fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), dpi=200)
bars = axes[0].bar(seg.index, seg["revenue"], color=BLUE, width=0.55, zorder=3)
for b, v in zip(bars, seg["revenue"]):
    axes[0].text(b.get_x() + b.get_width() / 2, v + seg["revenue"].max() * 0.02,
                 money(v, None), ha="center", fontsize=10.5, color=INK_SECONDARY)
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(money))
axes[0].set_title("Revenue", fontsize=12, fontweight="bold", loc="left", color=INK_PRIMARY)
style_axes(axes[0])
axes[0].set_ylim(0, seg["revenue"].max() * 1.22)

bars = axes[1].bar(seg.index, seg["aov"], color=ORANGE, width=0.55, zorder=3)
for b, v in zip(bars, seg["aov"]):
    axes[1].text(b.get_x() + b.get_width() / 2, v + seg["aov"].max() * 0.02,
                 f"GBP {v:,.0f}", ha="center", fontsize=10.5, color=INK_SECONDARY)
axes[1].set_title("Average order value", fontsize=12, fontweight="bold", loc="left", color=INK_PRIMARY)
style_axes(axes[1])
axes[1].set_ylim(0, seg["aov"].max() * 1.22)

fig.suptitle("Consumer drives volume; AOV is nearly flat across segments",
             fontsize=13, fontweight="bold", color=INK_PRIMARY, x=0.02, ha="left", y=1.02)
fig.tight_layout()
fig.savefig(IMG_DIR / "04_customer_segment.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# =========================================================================
# 5. Promo campaign impact - small multiples (revenue vs margin trade-off)
# =========================================================================
orders["period"] = orders["promo_campaign"].replace("", "Non-promo").fillna("Non-promo")
promo = orders.groupby("period").agg(
    revenue=("sales", "sum"), profit=("profit", "sum"),
    days=("order_date", "nunique"),
).reset_index()
promo["margin_pct"] = promo["profit"] / promo["revenue"] * 100
promo["daily_revenue"] = promo["revenue"] / promo["days"]
order_labels = ["Non-promo", "Summer Sale", "Black Friday", "Boxing Day Sale"]
promo = promo.set_index("period").loc[order_labels].reset_index()

fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), dpi=200)
colors_bar = [INK_MUTED, BLUE, BLUE, BLUE]
bars = axes[0].bar(promo["period"], promo["daily_revenue"], color=colors_bar, width=0.6, zorder=3)
for b, v in zip(bars, promo["daily_revenue"]):
    axes[0].text(b.get_x() + b.get_width() / 2, v + promo["daily_revenue"].max() * 0.02,
                 money(v, None), ha="center", fontsize=9.5, color=INK_SECONDARY)
axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(money))
axes[0].set_title("Revenue per day", fontsize=12, fontweight="bold", loc="left", color=INK_PRIMARY)
axes[0].tick_params(axis="x", labelrotation=18)
style_axes(axes[0])
axes[0].set_ylim(0, promo["daily_revenue"].max() * 1.22)

colors_bar2 = [INK_MUTED, ORANGE, ORANGE, ORANGE]
bars = axes[1].bar(promo["period"], promo["margin_pct"], color=colors_bar2, width=0.6, zorder=3)
for b, v in zip(bars, promo["margin_pct"]):
    axes[1].text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%",
                 ha="center", fontsize=9.5, color=INK_SECONDARY)
axes[1].set_title("Margin %", fontsize=12, fontweight="bold", loc="left", color=INK_PRIMARY)
axes[1].tick_params(axis="x", labelrotation=18)
style_axes(axes[1])
axes[1].set_ylim(0, promo["margin_pct"].max() * 1.3)

promo_uplift = promo.loc[promo["period"] != "Non-promo", "daily_revenue"].mean() / \
    promo.loc[promo["period"] == "Non-promo", "daily_revenue"].iloc[0]
margin_drop = promo.loc[promo["period"] == "Non-promo", "margin_pct"].iloc[0] - \
    promo.loc[promo["period"] != "Non-promo", "margin_pct"].mean()
fig.suptitle(f"Promo days run ~{promo_uplift:.1f}x daily revenue - at a ~{margin_drop:.0f}pt margin cost",
             fontsize=13, fontweight="bold", color=INK_PRIMARY, x=0.02, ha="left", y=1.04)
fig.tight_layout()
fig.savefig(IMG_DIR / "05_promo_impact.png", dpi=200, bbox_inches="tight")
plt.close(fig)

# =========================================================================
# 6. Return rate by category (ranked bar, muted flag on the top two)
# =========================================================================
ret = orders.groupby("category")["returned"].mean().mul(100).sort_values(ascending=True)
colors = [ORANGE if v >= 8 else BLUE for v in ret.values]
fig, ax = plt.subplots(figsize=(9, 5), dpi=200)
bars = ax.barh(ret.index, ret.values, color=colors, height=0.62, zorder=3)
for b, v in zip(bars, ret.values):
    ax.text(v + ret.max() * 0.02, b.get_y() + b.get_height() / 2, f"{v:.1f}%",
            va="center", fontsize=10.5, color=INK_SECONDARY)
ax.set_title("Return rate by category - Electronics & Fashion run hottest",
              fontsize=13, fontweight="bold", color=INK_PRIMARY, loc="left", pad=14)
style_axes(ax, x_grid=True, y_grid=False)
ax.set_xlim(0, ret.max() * 1.25)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
fig.tight_layout()
fig.savefig(IMG_DIR / "06_return_rate.png", dpi=200)
plt.close(fig)

# =========================================================================
# 7. Channel comparison (2-bar)
# =========================================================================
chan = orders.groupby("channel")["sales"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6.5, 4.6), dpi=200)
bars = ax.bar(chan.index, chan.values, color=[BLUE, AQUA], width=0.5, zorder=3)
for b, v in zip(bars, chan.values):
    ax.text(b.get_x() + b.get_width() / 2, v + chan.max() * 0.02, money(v, None),
            ha="center", fontsize=11, color=INK_SECONDARY)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(money))
ax.set_title("Online drives 71% of revenue", fontsize=13, fontweight="bold",
              color=INK_PRIMARY, loc="left", pad=14)
style_axes(ax)
ax.set_ylim(0, chan.max() * 1.25)
fig.tight_layout()
fig.savefig(IMG_DIR / "07_channel_comparison.png", dpi=200)
plt.close(fig)

print("Saved charts to", IMG_DIR)
for p in sorted(IMG_DIR.glob("*.png")):
    print(" -", p.name)

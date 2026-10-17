"""Stage 4: make portfolio-quality charts and save them in outputs/figures/.

Chart design rules used here (so you can explain them):
  * One question per chart, and the title says what is plotted (not what it "proves").
  * One color for one measure (blue = churn). Gray = everyone else / context.
  * Bars start at zero, so bar lengths are honest.
  * A dashed line shows the overall churn rate, so every group is compared to a baseline.
  * Every group's customer count is shown, so small groups are not mistaken for big ones.

Run it from the project folder:   python scripts/04_make_charts.py
"""

import matplotlib

matplotlib.use("Agg")  # draw to files only; no pop-up windows needed

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Patch

from config import FIGURES_DIR, SMALL_GROUP, churn_rate_table, load_clean

FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Colors. A small fixed set, used for the same job every time.
# ---------------------------------------------------------------------------
SURFACE = "#fcfcfb"   # chart background
INK = "#0b0b0b"       # titles
INK_2 = "#52514e"     # subtitles, value labels
MUTED = "#898781"     # axis text, footnotes, "stayed" context color
GRID = "#e1e0d9"      # gridlines
AXIS = "#c3c2b7"      # baseline
BLUE = "#2a78d6"      # churn (the thing we study)
SEQUENTIAL_BLUE = LinearSegmentedColormap.from_list(
    "seq_blue", ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
)
SOURCE_NOTE = (
    "Source: IBM Telco Customer Churn sample dataset (fictional company). "
    "Shows association, not cause."
)

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE,
    "font.family": "sans-serif",
    "text.color": INK_2,
    "axes.labelcolor": MUTED,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "axes.edgecolor": AXIS,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.grid": False,
})

df = load_clean()
overall_rate = df["churn_flag"].mean() * 100


def add_titles(fig, title: str, subtitle: str) -> None:
    """Left-aligned title, subtitle and source footnote."""
    fig.text(0.02, 0.955, title, fontsize=15, fontweight="bold", color=INK, va="top")
    fig.text(0.02, 0.895, subtitle, fontsize=10.5, color=INK_2, va="top")
    fig.text(0.02, 0.012, SOURCE_NOTE, fontsize=8, color=MUTED, va="bottom")


def percent_axis(value, _position) -> str:
    return f"{value:.0f}%"


def churn_bar_chart(column, title, filename, order=None, horizontal=False):
    """Bar chart of churn rate for each group in `column`."""
    table = churn_rate_table(df, column)
    if order is not None:
        table = table.set_index(column).loc[order].reset_index()
    elif not hasattr(df[column].dtype, "categories"):
        # Unordered text groups: sort from highest to lowest churn rate.
        table = table.sort_values("churn_rate_pct", ascending=False)
    table[column] = table[column].astype(str)

    labels = [
        f"{name}\n{n:,} customers" if not horizontal else f"{name}  ({n:,})"
        for name, n in zip(table[column], table["customers"])
    ]
    rates = table["churn_rate_pct"].tolist()
    top = max(max(rates), overall_rate) * 1.22

    if horizontal:
        fig, ax = plt.subplots(figsize=(8.5, 1.4 + 0.7 * len(table)))
        positions = list(range(len(table)))[::-1]
        ax.barh(positions, rates, height=0.5, color=BLUE)
        ax.set_yticks(positions, labels, fontsize=10)
        ax.set_xlim(0, top)
        ax.xaxis.set_major_formatter(FuncFormatter(percent_axis))
        ax.xaxis.grid(True, color=GRID, linewidth=1)
        ax.set_axisbelow(True)
        for pos, rate in zip(positions, rates):
            # Put the value INSIDE long bars (white text) so the dashed line never
            # strikes through it; short bars get the value just outside the tip.
            if rate > top * 0.15:
                ax.text(rate - top * 0.012, pos, f"{rate:.1f}%", va="center", ha="right",
                        fontsize=10.5, color="white", fontweight="bold")
            else:
                ax.text(rate + top * 0.012, pos, f"{rate:.1f}%", va="center",
                        fontsize=10.5, color=INK_2, fontweight="bold")
        # zorder < bars: the line shows in the gaps but never cuts through a bar's label
        ax.axvline(overall_rate, color=INK_2, linestyle="--", linewidth=1.2, zorder=0.8)
        ax.text(overall_rate - top * 0.012, len(table) - 0.45,
                f"All customers: {overall_rate:.1f}%", fontsize=9, color=INK_2,
                ha="right", va="bottom")
        ax.tick_params(axis="y", length=0)
        top_margin = 0.80
    else:
        fig, ax = plt.subplots(figsize=(8.5, 5.4))
        positions = list(range(len(table)))
        ax.bar(positions, rates, width=0.45, color=BLUE)
        ax.set_xticks(positions, labels, fontsize=10)
        ax.set_ylim(0, top)
        ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
        ax.yaxis.grid(True, color=GRID, linewidth=1)
        ax.set_axisbelow(True)
        for pos, rate in zip(positions, rates):
            ax.text(pos, rate + top * 0.015, f"{rate:.1f}%", ha="center",
                    fontsize=11, color=INK_2, fontweight="bold")
        ax.axhline(overall_rate, color=INK_2, linestyle="--", linewidth=1.2)
        ax.text(len(table) - 0.55, overall_rate + top * 0.015,
                f"All customers: {overall_rate:.1f}%", fontsize=9, color=INK_2,
                ha="right", va="bottom")
        ax.tick_params(axis="x", length=0)
        top_margin = 0.84

    small = table[table["customers"] < SMALL_GROUP]
    note = ""
    if len(small) > 0:
        note = f"  Groups under {SMALL_GROUP} customers should be read with caution."
    add_titles(
        fig, title,
        "Share of customers who churned. Dashed line = churn rate for all customers." + note,
    )
    fig.tight_layout(rect=[0.01, 0.045, 0.99, top_margin])
    fig.savefig(FIGURES_DIR / filename, dpi=200)
    plt.close(fig)
    print(f"saved {filename}")


# ---------------------------------------------------------------------------
# Charts 1-6: churn rate for one characteristic at a time
# ---------------------------------------------------------------------------
churn_bar_chart(
    "Contract", "Churn rate by contract type", "fig01_churn_by_contract.png",
    order=["Month-to-month", "One year", "Two year"],
)
churn_bar_chart(
    "tenure_group", "Churn rate by customer tenure", "fig02_churn_by_tenure_group.png",
)
churn_bar_chart(
    "charge_band", "Churn rate by monthly charges", "fig03_churn_by_charge_band.png",
)
churn_bar_chart(
    "InternetService", "Churn rate by internet service type",
    "fig04_churn_by_internet_service.png",
)
churn_bar_chart(
    "PaymentMethod", "Churn rate by payment method",
    "fig05_churn_by_payment_method.png", horizontal=True,
)
churn_bar_chart(
    "TechSupport", "Churn rate by tech support", "fig06_churn_by_tech_support.png",
)

# ---------------------------------------------------------------------------
# Chart 7: how do tenure and monthly charges look for churned vs stayed customers?
# Two panels side by side (small multiples) sharing one legend.
# Each group is scaled to 100% so a smaller group (churned) can be compared fairly.
# ---------------------------------------------------------------------------
plot_df = df.copy()
plot_df["Outcome"] = plot_df["Churn"].map({"Yes": "Churned", "No": "Stayed"})
colors = {"Stayed": MUTED, "Churned": BLUE}

fig, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
for ax, column, label in zip(
    axes, ["tenure", "MonthlyCharges"], ["Tenure (months)", "Monthly charges ($)"]
):
    sns.histplot(
        data=plot_df, x=column, hue="Outcome", hue_order=["Stayed", "Churned"],
        palette=colors, stat="percent", common_norm=False, bins=24,
        element="step", alpha=0.35, linewidth=2, legend=False, ax=ax,
    )
    ax.set_xlabel(label, fontsize=10)
    ax.set_ylabel("% of customers in group" if column == "tenure" else "")
    ax.yaxis.set_major_formatter(FuncFormatter(percent_axis))
    ax.yaxis.grid(True, color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0)

handles = [Patch(facecolor=colors[k], alpha=0.6, label=k) for k in ["Stayed", "Churned"]]
fig.legend(handles=handles, loc="upper right", bbox_to_anchor=(0.98, 0.95),
           frameon=False, ncol=2, fontsize=10)
add_titles(
    fig, "Tenure and monthly charges: customers who stayed vs churned",
    "Each color is scaled to 100% of its own group, so the two shapes can be compared directly.",
)
fig.tight_layout(rect=[0.01, 0.045, 0.99, 0.84])
fig.savefig(FIGURES_DIR / "fig07_tenure_and_charges_distributions.png", dpi=200)
plt.close(fig)
print("saved fig07_tenure_and_charges_distributions.png")

# ---------------------------------------------------------------------------
# Chart 8: heatmap - contract type AND tenure together.
# Why: contract and tenure overlap. This shows whether a pattern holds inside
# each tenure group or could be tenure in disguise.
# ---------------------------------------------------------------------------
rates = df.pivot_table(index="Contract", columns="tenure_group",
                       values="churn_flag", aggfunc="mean", observed=True).mul(100)
counts = df.pivot_table(index="Contract", columns="tenure_group",
                        values="churn_flag", aggfunc="count", observed=True)
rates = rates.loc[["Month-to-month", "One year", "Two year"]]
counts = counts.loc[["Month-to-month", "One year", "Two year"]]

annotations = rates.copy().astype(object)
for r in rates.index:
    for c in rates.columns:
        n = counts.loc[r, c]
        if n != n or n == 0:        # n != n is True only for NaN: no customers here
            annotations.loc[r, c] = ""
        else:
            star = "*" if n < SMALL_GROUP else ""
            annotations.loc[r, c] = f"{rates.loc[r, c]:.1f}%{star}\n{int(n):,} customers"

fig, ax = plt.subplots(figsize=(9.5, 5))
sns.heatmap(
    rates, annot=annotations.values, fmt="", cmap=SEQUENTIAL_BLUE, vmin=0,
    linewidths=3, linecolor=SURFACE, cbar_kws={"label": "Churn rate (%)", "shrink": 0.8},
    annot_kws={"fontsize": 10}, ax=ax,
)
# Text color: white on dark cells, near-black on light cells, so it is always readable.
# seaborn skips empty (NaN) cells, so we pair texts only with cells that have data.
filled_cells = [value for row in rates.values for value in row if value == value]
for text, value in zip(ax.texts, filled_cells):
    text.set_color("white" if value >= 40 else INK)
ax.set_xlabel("Tenure group", fontsize=10)
ax.set_ylabel("")
ax.tick_params(axis="both", length=0, labelsize=10)
plt.setp(ax.get_yticklabels(), rotation=0)
add_titles(
    fig, "Churn rate by contract type and tenure group",
    f"Darker = higher churn rate. * = fewer than {SMALL_GROUP} customers in that cell.",
)
fig.tight_layout(rect=[0.01, 0.045, 0.99, 0.84])
fig.savefig(FIGURES_DIR / "fig08_churn_contract_by_tenure_heatmap.png", dpi=200)
plt.close(fig)
print("saved fig08_churn_contract_by_tenure_heatmap.png")

print("\nDone. Charts saved in outputs/figures/.")

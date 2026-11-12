"""Charts step: turn the SQL answers into PNG charts for the README."""

from pathlib import Path

import matplotlib.pyplot as plt

from query import run_query

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHART_DIR = PROJECT_ROOT / "charts"

# --- Colours (a colour-blind-safe pair) and chart styling --------------------
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GREY = "#b9b8b1"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BACKGROUND = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": BACKGROUND,
    "axes.facecolor": BACKGROUND,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "axes.axisbelow": True,
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "font.size": 11,
})

# State codes (FIPS) -> names, so charts show names instead of numbers
STATE_NAMES = {
    1: "Alabama", 2: "Alaska", 4: "Arizona", 5: "Arkansas", 6: "California",
    8: "Colorado", 9: "Connecticut", 10: "Delaware", 11: "Washington DC",
    12: "Florida", 13: "Georgia", 15: "Hawaii", 16: "Idaho", 17: "Illinois",
    18: "Indiana", 19: "Iowa", 20: "Kansas", 21: "Kentucky", 22: "Louisiana",
    23: "Maine", 24: "Maryland", 25: "Massachusetts", 26: "Michigan",
    27: "Minnesota", 28: "Mississippi", 29: "Missouri", 30: "Montana",
    31: "Nebraska", 32: "Nevada", 33: "New Hampshire", 34: "New Jersey",
    35: "New Mexico", 36: "New York", 37: "North Carolina", 38: "North Dakota",
    39: "Ohio", 40: "Oklahoma", 41: "Oregon", 42: "Pennsylvania",
    44: "Rhode Island", 45: "South Carolina", 46: "South Dakota",
    47: "Tennessee", 48: "Texas", 49: "Utah", 50: "Vermont", 51: "Virginia",
    53: "Washington", 54: "West Virginia", 55: "Wisconsin", 56: "Wyoming",
    66: "Guam", 72: "Puerto Rico", 78: "US Virgin Islands",
}

SOURCE_NOTE = "Source: CDC BRFSS 2025. Weighted to the US adult population."


def finish(fig, filename):
    """Add the source note, save the chart as a PNG and close it."""
    fig.text(0.01, -0.07, SOURCE_NOTE, fontsize=9, color=MUTED)
    CHART_DIR.mkdir(exist_ok=True)
    path = CHART_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path.name}")


def chart_age_sex():
    """Line chart: heart disease rate by age group, one line for each sex."""
    df = run_query("by_age_sex")
    fig, ax = plt.subplots(figsize=(10, 5.5))

    for sex, colour in [("Male", ORANGE), ("Female", BLUE)]:
        rows = df[df["sex"] == sex]
        ax.plot(rows["age_group"], rows["heart_disease_pct"], color=colour,
                linewidth=2, marker="o", markersize=5, label=sex)
        # Label the end of each line so you don't need the legend to read it
        last = rows.iloc[-1]
        ax.annotate(f"{sex}: {last['heart_disease_pct']}%",
                    (last["age_group"], last["heart_disease_pct"]),
                    xytext=(8, 0), textcoords="offset points",
                    va="center", color=INK, fontsize=10)

    ax.set_title("Heart disease rises steeply with age, faster for men")
    ax.set_xlabel("Age group")
    ax.set_ylabel("Ever had heart disease or a heart attack (%)")
    ax.set_ylim(bottom=0)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left")
    finish(fig, "heart_disease_by_age_sex.png")


def chart_risk_factors():
    """Paired bars: heart disease rate with vs without each risk factor."""
    df = run_query("by_risk_factor")
    has = df[df["has_factor"] == "Yes"].set_index("risk_factor")["heart_disease_pct"]
    hasnt = df[df["has_factor"] == "No"].set_index("risk_factor")["heart_disease_pct"]
    order = has.sort_values().index          # biggest rate at the top
    y = range(len(order))

    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.barh([i + 0.2 for i in y], has[order], height=0.38, color=ORANGE, label="Has this risk factor")
    ax.barh([i - 0.2 for i in y], hasnt[order], height=0.38, color=GREY, label="Doesn't")
    for i, factor in enumerate(order):
        ax.text(has[factor] + 0.3, i + 0.2, f"{has[factor]}%", va="center", fontsize=9, color=INK)
        ax.text(hasnt[factor] + 0.3, i - 0.2, f"{hasnt[factor]}%", va="center", fontsize=9, color=MUTED)

    ax.set_yticks(list(y))
    ax.set_yticklabels(order)
    ax.tick_params(axis="y", colors=INK)
    ax.set_title("Diabetes and high blood pressure show the biggest gaps")
    ax.set_xlabel("Ever had heart disease or a heart attack (%)")
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, loc="lower right")
    finish(fig, "heart_disease_by_risk_factor.png")


def chart_risk_count():
    """Bar chart: heart disease rate by number of risk factors (0 to 5)."""
    df = run_query("risk_factor_count")
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(df["num_risk_factors"], df["heart_disease_pct"], color=BLUE, width=0.7)
    for _, row in df.iterrows():
        ax.text(row["num_risk_factors"], row["heart_disease_pct"] + 0.6,
                f"{row['heart_disease_pct']}%", ha="center", fontsize=10, color=INK)

    ax.set_title("Each extra risk factor raises heart disease risk")
    ax.set_xlabel("Number of risk factors (high blood pressure, high cholesterol,\ndiabetes, smoking, no exercise)")
    ax.set_ylabel("Ever had heart disease or a heart attack (%)")
    ax.set_xticks(df["num_risk_factors"])
    ax.grid(axis="x", visible=False)
    finish(fig, "heart_disease_by_risk_count.png")


def chart_states():
    """Horizontal bars: heart disease rate for every state, highest at the top."""
    df = run_query("by_state")
    df["state"] = df["state_fips"].map(STATE_NAMES)
    df = df.sort_values("heart_disease_pct")
    overall = run_query("overall_rate")["heart_disease_pct"].iloc[0]

    fig, ax = plt.subplots(figsize=(9, 13))
    ax.barh(df["state"], df["heart_disease_pct"], color=BLUE, height=0.7)
    ax.axvline(overall, color=INK, linewidth=1, linestyle="--")
    ax.text(overall + 0.1, len(df) - 0.5, f"US overall: {overall}%", fontsize=9, color=INK, va="bottom")

    ax.set_title("Heart disease rate by state")
    ax.set_xlabel("Ever had heart disease or a heart attack (%)")
    ax.tick_params(axis="y", colors=INK, labelsize=9)
    ax.set_ylim(-0.6, len(df) + 0.4)
    ax.grid(axis="y", visible=False)
    finish(fig, "heart_disease_by_state.png")


def make_all_charts():
    """Make every chart. run_pipeline.py calls this."""
    chart_age_sex()
    chart_risk_factors()
    chart_risk_count()
    chart_states()


if __name__ == "__main__":
    make_all_charts()
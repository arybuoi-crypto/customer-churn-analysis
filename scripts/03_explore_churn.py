"""Stage 3: exploratory analysis - how does churn vary across customer groups?

Prints tables and also saves them as CSV files in outputs/tables/.
Run it from the project folder:   python scripts/03_explore_churn.py
"""

import pandas as pd

from config import SMALL_GROUP, TABLES_DIR, churn_rate_table, load_clean

TABLES_DIR.mkdir(parents=True, exist_ok=True)
df = load_clean()


def section(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def show_and_save(table: pd.DataFrame, filename: str) -> None:
    """Print a table, warn about small groups, and save it."""
    print(table.to_string(index=False))
    small = table[table["customers"] < SMALL_GROUP]
    if len(small) > 0:
        print(f"\n  WARNING: groups with fewer than {SMALL_GROUP} customers - "
              "treat their percentages with caution.")
    table.to_csv(TABLES_DIR / filename, index=False)


# --- 1. Overall churn rate ----------------------------------------------------
section("1. Overall churn")
total = len(df)
churned = int(df["churn_flag"].sum())
overall_rate = churned / total * 100
print(f"Customers: {total}")
print(f"Churned:   {churned}")
print(f"Overall churn rate: {overall_rate:.1f}%")
pd.DataFrame(
    {"customers": [total], "churned": [churned], "churn_rate_pct": [round(overall_rate, 1)]}
).to_csv(TABLES_DIR / "overall_churn.csv", index=False)

# --- 2. Churn rate by one characteristic at a time ---------------------------
# Each table answers: "Among customers in this group, what share churned?"
single_factors = [
    ("Contract", "Churn rate by contract type"),
    ("tenure_group", "Churn rate by tenure group"),
    ("charge_band", "Churn rate by monthly charge band"),
    ("InternetService", "Churn rate by internet service"),
    ("PaymentMethod", "Churn rate by payment method"),
    ("PaperlessBilling", "Churn rate by paperless billing"),
    ("TechSupport", "Churn rate by tech support"),
    ("OnlineSecurity", "Churn rate by online security"),
    ("SeniorCitizen", "Churn rate by senior citizen"),
    ("Partner", "Churn rate by partner"),
    ("Dependents", "Churn rate by dependents"),
    ("gender", "Churn rate by gender"),
]
for number, (column, title) in enumerate(single_factors, start=2):
    section(f"{number}. {title}")
    show_and_save(churn_rate_table(df, column), f"churn_by_{column}.csv")

# --- 3. Averages: churned vs stayed -------------------------------------------
section("14. Averages for customers who stayed vs churned")
averages = (
    df.groupby("Churn")[["tenure", "MonthlyCharges", "TotalCharges"]]
    .agg(["mean", "median"])
    .round(1)
)
print(averages.to_string())
averages.to_csv(TABLES_DIR / "averages_by_churn.csv")

# --- 4. Two factors together: contract x tenure -------------------------------
# WHY: contract type and tenure are probably linked (people on long contracts tend to
# have been around longer). Looking at them together shows whether one pattern might
# really be the other in disguise.
section("15. Churn rate (%) by contract type AND tenure group")
rate_grid = df.pivot_table(
    index="Contract", columns="tenure_group", values="churn_flag",
    aggfunc="mean", observed=True,
).mul(100).round(1)
count_grid = df.pivot_table(
    index="Contract", columns="tenure_group", values="churn_flag",
    aggfunc="count", observed=True,
)
print("Churn rate (%):")
print(rate_grid.to_string())
print("\nNumber of customers in each cell:")
print(count_grid.to_string())
print(f"\n  Cells with fewer than {SMALL_GROUP} customers are shaky - read them lightly.")
rate_grid.to_csv(TABLES_DIR / "churn_rate_contract_by_tenure.csv")
count_grid.to_csv(TABLES_DIR / "customers_contract_by_tenure.csv")

# --- 5. How are contract and charges related? --------------------------------
section("16. Average monthly charges and tenure by contract type")
by_contract = (
    df.groupby("Contract")[["tenure", "MonthlyCharges"]].mean().round(1)
)
print(by_contract.to_string())
by_contract.to_csv(TABLES_DIR / "avg_tenure_charges_by_contract.csv")

print("\nDone. Tables saved in outputs/tables/. Copy this output to share it.")

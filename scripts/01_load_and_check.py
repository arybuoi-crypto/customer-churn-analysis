"""Stage 1: load the raw data and run data-quality checks.

This script only LOOKS at the data. It changes nothing and saves nothing.
Run it from the project folder:   python scripts/01_load_and_check.py
"""

import pandas as pd

from config import find_raw_csv


def section(title: str) -> None:
    """Print a heading so the output is easy to scan."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


csv_path = find_raw_csv()
df = pd.read_csv(csv_path)
print(f"Loaded: {csv_path.name}")

# --- 1. Size and shape ------------------------------------------------------
section("1. Shape (rows, columns)")
print(df.shape)

# --- 2. Columns and data types ----------------------------------------------
section("2. Column names and data types")
print(df.dtypes)
# Watch for: a column that SHOULD be a number but shows as object/str (text).

# --- 3. First rows ----------------------------------------------------------
section("3. First 5 rows")
print(df.head().to_string())

# --- 4. Missing values ------------------------------------------------------
section("4. Missing values per column (real blanks only)")
print(df.isna().sum()[df.isna().sum() > 0])
if df.isna().sum().sum() == 0:
    print("No real missing values (NaN) found.")

# --- 5. Hidden missing values: blank text ----------------------------------
# A cell containing just a space is NOT counted as missing by pandas.
section("5. Blank-text cells (cells that are empty or only spaces)")
text_cols = df.select_dtypes(exclude="number").columns
blank_counts = {
    col: int(df[col].astype(str).str.strip().eq("").sum()) for col in text_cols
}
blank_counts = {col: n for col, n in blank_counts.items() if n > 0}
print(blank_counts if blank_counts else "No blank-text cells found.")

# --- 6. Is TotalCharges really numeric? -------------------------------------
section("6. TotalCharges: values that cannot be converted to a number")
if "TotalCharges" in df.columns:
    as_number = pd.to_numeric(df["TotalCharges"], errors="coerce")
    bad = df.loc[as_number.isna(), ["customerID", "tenure", "MonthlyCharges", "TotalCharges"]]
    print(f"Rows that fail conversion: {len(bad)}")
    if len(bad) > 0:
        print(bad.head(15).to_string())
        print("\ntenure values in those rows:", sorted(bad["tenure"].unique()))

# --- 7. Duplicates ----------------------------------------------------------
section("7. Duplicates")
print("Fully duplicated rows:      ", int(df.duplicated().sum()))
print("Duplicated customerID values:", int(df["customerID"].duplicated().sum()))

# --- 8. The outcome column --------------------------------------------------
section("8. Churn column: values and counts")
print(df["Churn"].value_counts(dropna=False))

# --- 9. Categories in each text column --------------------------------------
section("9. Distinct values in each text column (except customerID)")
for col in text_cols:
    if col in ("customerID", "TotalCharges"):
        continue
    print(f"\n{col}: {sorted(df[col].dropna().unique())}")

# --- 10. Numeric summary ----------------------------------------------------
section("10. Summary of numeric columns")
print(df.describe().round(2).to_string())
# Watch for: negative numbers, tenure above 72, charges that look absurd.

print("\nDone. Nothing was changed. Copy this whole output to share it.")

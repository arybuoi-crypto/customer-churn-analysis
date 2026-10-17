"""Stage 2: clean the raw data and save a new file.

The raw file in data/raw/ is NEVER modified. We read it, fix things in memory,
and write a separate file to data/processed/.
Run it from the project folder:   python scripts/02_clean_data.py
"""

import pandas as pd

from config import (
    CHARGE_BINS,
    CHARGE_LABELS,
    CLEAN_FILE,
    PROCESSED_DIR,
    TENURE_BINS,
    TENURE_LABELS,
    find_raw_csv,
)

df = pd.read_csv(find_raw_csv())
rows_at_start = len(df)
print(f"Rows in raw file: {rows_at_start}")

# --- Step 1: tidy text --------------------------------------------------------
# Remove stray spaces at the start/end of every text value.
for col in df.select_dtypes(exclude="number").columns:
    df[col] = df[col].str.strip()

# --- Step 2: fix TotalCharges -------------------------------------------------
# It should be a number, but blank text can make pandas read it as text.
# errors="coerce" turns anything unconvertible into NaN (missing) instead of crashing.
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
missing_total = df["TotalCharges"].isna().sum()
print(f"TotalCharges values that could not be converted: {missing_total}")

# DECISION: drop those rows. It is only done if the share is tiny; we print it so you
# can check. If the share were large, dropping would be a bad idea and we would need
# another approach. Mention this choice in your README.
share_missing = missing_total / rows_at_start * 100
print(f"That is {share_missing:.2f}% of all rows.")
if share_missing > 2:
    raise SystemExit("More than 2% of rows affected - stop and rethink before dropping.")
df = df.dropna(subset=["TotalCharges"])

# --- Step 3: duplicates -------------------------------------------------------
duplicates = df.duplicated(subset="customerID").sum()
print(f"Duplicate customerID rows removed: {duplicates}")
df = df.drop_duplicates(subset="customerID")

# --- Step 4: make the outcome easy to calculate with -------------------------
# churn_flag is 1 for "Yes" and 0 for "No". The MEAN of a 1/0 column is the share of 1s,
# which is exactly the churn rate.
unexpected = set(df["Churn"].unique()) - {"Yes", "No"}
if unexpected:
    raise SystemExit(f"Unexpected values in Churn: {unexpected}")
df["churn_flag"] = (df["Churn"] == "Yes").astype(int)

# --- Step 5: make SeniorCitizen readable (it is stored as 0/1) ---------------
df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

# --- Step 6: build grouped versions of tenure and monthly charges ------------
# Groups are easier to read in charts than hundreds of distinct values.
df["tenure_group"] = pd.cut(
    df["tenure"], bins=TENURE_BINS, labels=TENURE_LABELS, include_lowest=True
)
df["charge_band"] = pd.cut(
    df["MonthlyCharges"], bins=CHARGE_BINS, labels=CHARGE_LABELS, include_lowest=True
)

# Safety check: every row should have landed in a group.
assert df["tenure_group"].notna().all(), "Some tenure values fell outside the bins"
assert df["charge_band"].notna().all(), "Some charges fell outside the bins"

# --- Step 7: save ------------------------------------------------------------
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(CLEAN_FILE, index=False)

print("\n--- Summary ---")
print(f"Rows before cleaning: {rows_at_start}")
print(f"Rows after cleaning:  {len(df)}")
print(f"Rows removed:         {rows_at_start - len(df)}")
print(f"Columns now:          {df.shape[1]}")
print(f"Saved to:             {CLEAN_FILE}")
print("\nCounts per new group (check none are empty):")
print(df["tenure_group"].value_counts().sort_index().to_string())
print(df["charge_band"].value_counts().sort_index().to_string())

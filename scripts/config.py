"""Shared settings and helpers used by every script.

Keeping paths and choices in ONE place means that if you change a folder name or a
bin edge, you change it here once instead of hunting through four files.
"""

from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Folders. __file__ is this file's location, so these work no matter which
# directory you run the scripts from.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"

CLEAN_FILE = PROCESSED_DIR / "telco_churn_clean.csv"

# ---------------------------------------------------------------------------
# Analysis choices. These are DECISIONS, not facts: another analyst could pick
# different cut points. Say so in your README (see "Limitations").
# ---------------------------------------------------------------------------
# Tenure groups, in months. include_lowest=True makes the first group start at 0.
TENURE_BINS = [0, 12, 24, 48, 72]
TENURE_LABELS = ["0-12 mo", "13-24 mo", "25-48 mo", "49-72 mo"]

# Monthly charge bands, in dollars.
CHARGE_BINS = [0, 35, 70, 90, 1000]
CHARGE_LABELS = ["Under $35", "$35-70", "$70-90", "Over $90"]

# Groups smaller than this get a warning: percentages from few customers are shaky.
SMALL_GROUP = 100


def find_raw_csv() -> Path:
    """Return the one CSV file inside data/raw/, with a friendly error if not."""
    files = sorted(RAW_DIR.glob("*.csv"))
    if len(files) == 0:
        raise SystemExit(
            f"No CSV found in {RAW_DIR}\n"
            "Download the dataset (see README) and put the .csv file in data/raw/."
        )
    if len(files) > 1:
        names = [f.name for f in files]
        raise SystemExit(f"Expected exactly one CSV in {RAW_DIR}, found: {names}")
    return files[0]


def load_clean() -> pd.DataFrame:
    """Load the cleaned file made by 02_clean_data.py."""
    if not CLEAN_FILE.exists():
        raise SystemExit(
            f"{CLEAN_FILE.name} not found. Run scripts/02_clean_data.py first."
        )
    df = pd.read_csv(CLEAN_FILE)
    # Re-create the ordered group columns (CSV files forget ordering).
    df["tenure_group"] = pd.Categorical(
        df["tenure_group"], categories=TENURE_LABELS, ordered=True
    )
    df["charge_band"] = pd.Categorical(
        df["charge_band"], categories=CHARGE_LABELS, ordered=True
    )
    return df


def churn_rate_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Customers, churned customers and churn rate (%) for each value of `column`."""
    table = (
        df.groupby(column, observed=True)["churn_flag"]
        .agg(customers="count", churned="sum")
        .reset_index()
    )
    table["churn_rate_pct"] = (table["churned"] / table["customers"] * 100).round(1)
    return table

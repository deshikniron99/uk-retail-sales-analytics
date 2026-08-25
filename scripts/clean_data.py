"""
Cleaning pipeline: raw -> curated.

Takes the deliberately-imperfect raw export (data/uk_retail_orders_2023_2025.csv,
which has a few duplicate order rows, inconsistent region casing, and some
missing shipping_cost values - typical of a real POS/e-commerce export) and
produces a curated dataset used by the SQL layer, the notebook, and the
dashboard. Every step prints what it found and what it did, so the pipeline
is auditable rather than a silent fix.
"""
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "uk_retail_orders_2023_2025.csv"
CLEAN_PATH = ROOT / "data" / "uk_retail_orders_clean.csv"

CANONICAL_REGIONS = [
      "London", "South East", "North West", "Scotland", "West Midlands",
      "Yorkshire", "East of England", "South West", "Wales", "Northern Ireland",
]
REGION_LOOKUP = {r.upper(): r for r in CANONICAL_REGIONS}

df = pd.read_csv(RAW_PATH)
print(f"Loaded {len(df):,} raw rows, {df.shape[1]} columns")

# 1. Duplicate orders (same order_id inserted twice by an export glitch)
dupes = df.duplicated(subset="order_id").sum()
df = df.drop_duplicates(subset="order_id", keep="first")
print(f"Dropped {dupes} duplicate order_id rows")

# 2. Inconsistent region casing ("WALES" vs "Wales") -> canonical spelling
before_variants = df["region"].nunique()
df["region"] = df["region"].str.strip().map(lambda x: REGION_LOOKUP.get(x.upper(), x))
after_variants = df["region"].nunique()
print(f"Normalized region casing: {before_variants} -> {after_variants} distinct values")

# 3. Missing shipping_cost -> 0 for In-Store (correct, shipping doesn't apply),
#    median online shipping cost for missing Online rows (imputation, not a guess at 0)
missing_ship = df["shipping_cost"].isna().sum()
online_median_ship = df.loc[df["channel"] == "Online", "shipping_cost"].median()
df.loc[(df["channel"] == "In-Store") & (df["shipping_cost"].isna()), "shipping_cost"] = 0.0
df.loc[(df["channel"] == "Online") & (df["shipping_cost"].isna()), "shipping_cost"] = online_median_ship
print(f"Filled {missing_ship} missing shipping_cost values (0 for In-Store, median GBP {online_median_ship:.2f} for Online)")

# 4. Empty-string promo_campaign can round-trip through CSV as NaN - normalize to ''
df["promo_campaign"] = df["promo_campaign"].fillna("")

# 5. Type hygiene
df["order_date"] = pd.to_datetime(df["order_date"])
df["returned"] = df["returned"].astype(bool)

# 6. Sanity checks
assert df["order_id"].is_unique, "order_id should be unique after de-duplication"
assert (df["sales"] >= 0).all(), "sales should never be negative"
assert df["region"].isin(CANONICAL_REGIONS).all(), "unrecognised region after cleaning"

df.to_csv(CLEAN_PATH, index=False)
print(f"\nWrote {len(df):,} curated rows to {CLEAN_PATH}")

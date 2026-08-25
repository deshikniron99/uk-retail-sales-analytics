"""
Generates a synthetic-but-realistic UK e-commerce retail transactions dataset
for the portfolio project. ~3 years of daily orders (Jan 2023 - Dec 2025) with
seasonality, YoY growth, category mix, regional spread, and a promo calendar,
so the downstream SQL + pandas analysis has real patterns to find.
"""
import numpy as np
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

rng = np.random.default_rng(42)

START = date(2023, 1, 1)
END = date(2025, 12, 31)
n_days = (END - START).days + 1
dates = [START + timedelta(days=i) for i in range(n_days)]

REGIONS = {
      "London": 0.24, "South East": 0.16, "North West": 0.12, "Scotland": 0.09,
      "West Midlands": 0.09, "Yorkshire": 0.08, "East of England": 0.08,
      "South West": 0.07, "Wales": 0.04, "Northern Ireland": 0.03,
}

CATEGORIES = {
      "Electronics":        {"share": 0.22, "aov": 145, "margin": 0.18},
      "Fashion":            {"share": 0.20, "aov": 58,  "margin": 0.42},
      "Home & Garden":      {"share": 0.16, "aov": 82,  "margin": 0.35},
      "Beauty & Personal Care": {"share": 0.14, "aov": 34, "margin": 0.48},
      "Sports & Outdoors":  {"share": 0.11, "aov": 67,  "margin": 0.33},
      "Toys & Games":       {"share": 0.09, "aov": 41,  "margin": 0.30},
      "Books & Media":      {"share": 0.08, "aov": 22,  "margin": 0.25},
}

SEGMENTS = {"Consumer": 0.62, "SME": 0.26, "Corporate": 0.12}
CHANNELS = {"Online": 0.71, "In-Store": 0.29}
PAYMENTS = {"Card": 0.58, "PayPal": 0.24, "Buy Now Pay Later": 0.11, "Bank Transfer": 0.07}

def seasonality(d: date) -> float:
      # Smooth annual seasonality (winter holiday peak, summer dip) + weekday effect
      doy = d.timetuple().tm_yday
      annual = 1.0 + 0.28 * np.sin((doy - 80) / 365 * 2 * np.pi - np.pi / 2) * -1
      annual = 1.0 + 0.22 * np.cos((doy - 355) / 365 * 2 * np.pi)  # peak near late Nov/Dec
    weekday = d.weekday()
    wk = 1.15 if weekday >= 5 else 0.95  # weekends busier for consumer retail
    return annual * wk

def is_promo(d: date) -> tuple[bool, str]:
      # Black Friday / Cyber Monday week
      if d.month == 11 and 22 <= d.day <= 30:
                return True, "Black Friday"
            # Boxing Day sale
            if d.month == 12 and 26 <= d.day <= 31:
                      return True, "Boxing Day Sale"
                  # Summer sale
                  if d.month == 7 and 1 <= d.day <= 14:
                            return True, "Summer Sale"
                        return False, ""

rows = []
order_id = 100000
customer_pool_size = 6200
# give each customer a stable segment/region so segment analysis is coherent
cust_segment = rng.choice(list(SEGMENTS.keys()), size=customer_pool_size, p=list(SEGMENTS.values()))
cust_region = rng.choice(list(REGIONS.keys()), size=customer_pool_size, p=list(REGIONS.values()))

for d in dates:
      yr_growth = 1.0 + 0.16 * ((d.year - 2023) + (d.timetuple().tm_yday / 365))  # ~16% YoY growth
    base_orders = 16 * yr_growth * seasonality(d)
    promo, promo_name = is_promo(d)
    if promo:
              base_orders *= 2.6
          n_orders = max(1, int(rng.poisson(base_orders)))

    for _ in range(n_orders):
              cust_idx = rng.integers(0, customer_pool_size)
              segment = cust_segment[cust_idx]
              region = cust_region[cust_idx]
              category = rng.choice(list(CATEGORIES.keys()), p=[v["share"] for v in CATEGORIES.values()])
              cat_info = CATEGORIES[category]
              channel = rng.choice(list(CHANNELS.keys()), p=list(CHANNELS.values()))
              payment = rng.choice(list(PAYMENTS.keys()), p=list(PAYMENTS.values()))

        qty = max(1, int(rng.gamma(2.0, 1.1)))
        unit_price = max(4.0, rng.normal(cat_info["aov"] / max(qty, 1), cat_info["aov"] * 0.28 / max(qty, 1)))
        discount = 0.0
        if promo:
                      discount = round(rng.uniform(0.15, 0.40), 2)
elif rng.random() < 0.10:
            discount = round(rng.uniform(0.05, 0.20), 2)

        gross = qty * unit_price
        sales = round(gross * (1 - discount), 2)
        margin = cat_info["margin"] - (0.05 if promo else 0)
        profit = round(sales * max(margin, 0.03) * rng.uniform(0.85, 1.15), 2)
        shipping_cost = round(rng.uniform(1.5, 6.5) if channel == "Online" else 0.0, 2)

        # occasional return flag, more likely for Fashion / Electronics
        return_prob = 0.10 if category in ("Fashion", "Electronics") else 0.04
        returned = rng.random() < return_prob

        order_id += 1
        rows.append((
                      order_id, d.isoformat(), f"CUST-{cust_idx:05d}", segment, region,
                      category, channel, payment, qty, round(unit_price, 2), discount,
                      sales, profit, shipping_cost, promo_name if promo else "", returned,
        ))

df = pd.DataFrame(rows, columns=[
      "order_id", "order_date", "customer_id", "customer_segment", "region",
      "category", "channel", "payment_method", "quantity", "unit_price", "discount",
      "sales", "profit", "shipping_cost", "promo_campaign", "returned",
])

# introduce a modest chunk of light real-world messiness for the cleaning story
messy = df.sample(frac=0.015, random_state=1).index
df.loc[messy, "region"] = df.loc[messy, "region"].str.upper()
dup_rows = df.sample(frac=0.004, random_state=2)
df = pd.concat([df, dup_rows], ignore_index=True)
null_idx = df.sample(frac=0.006, random_state=3).index
df.loc[null_idx, "shipping_cost"] = np.nan

df = df.sort_values("order_date").reset_index(drop=True)
ROOT = Path(__file__).resolve().parent.parent
out_path = ROOT / "data" / "uk_retail_orders_2023_2025.csv"
df.to_csv(out_path, index=False)
print(f"Wrote {len(df):,} rows to {out_path}")
print(df.head(3).to_string())
print(df["order_date"].min(), df["order_date"].max())

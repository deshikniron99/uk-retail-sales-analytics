"""Loads the CSV into a local SQLite db and runs every query in sql/*.sql,
saving each result set to results/ as CSV (used by the notebook, the
dashboard, and the README's key-findings numbers) and printing a preview.
"""
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "retail.db"
CSV_PATH = ROOT / "data" / "uk_retail_orders_clean.csv"
SQL_DIR = ROOT / "sql"
RESULTS_DIR = ROOT / "data" / "query_results"
RESULTS_DIR.mkdir(exist_ok=True)

if not CSV_PATH.exists():
      raise SystemExit("Run scripts/clean_data.py first to produce the curated CSV.")

df = pd.read_csv(CSV_PATH)
df["promo_campaign"] = df["promo_campaign"].fillna("")

conn = sqlite3.connect(DB_PATH)
schema_sql = (SQL_DIR / "schema.sql").read_text()
conn.executescript("DROP TABLE IF EXISTS orders;")
conn.executescript(schema_sql)
df.to_sql("orders", conn, if_exists="append", index=False)
conn.commit()

query_files = sorted(f for f in SQL_DIR.glob("*.sql") if f.name != "schema.sql")
for qf in query_files:
      query = qf.read_text()
      result = pd.read_sql_query(query, conn)
      out_name = qf.stem + ".csv"
      result.to_csv(RESULTS_DIR / out_name, index=False)
      print(f"\n=== {qf.name} -> {out_name} ({len(result)} rows) ===")
      print(result.head(8).to_string(index=False))

conn.close()
print(f"\nSQLite DB written to {DB_PATH}")

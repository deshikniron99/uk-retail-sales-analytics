-- UK Retail Orders 2023-2025 - schema
-- Loaded from data/uk_retail_orders_2023_2025.csv into a local SQLite db
-- (see scripts/build_sqlite_db.py) so the queries below run against real SQL,
-- not pandas standing in for it.

CREATE TABLE IF NOT EXISTS orders (
      order_id        INTEGER PRIMARY KEY,
      order_date      TEXT NOT NULL,          -- ISO 8601 (YYYY-MM-DD)
    customer_id     TEXT NOT NULL,
      customer_segment TEXT NOT NULL,          -- Consumer | SME | Corporate
    region          TEXT NOT NULL,           -- UK region
    category        TEXT NOT NULL,
      channel         TEXT NOT NULL,           -- Online | In-Store
    payment_method  TEXT NOT NULL,
      quantity        INTEGER NOT NULL,
      unit_price      REAL NOT NULL,
      discount        REAL NOT NULL,           -- 0.0 - 0.40
    sales           REAL NOT NULL,           -- net revenue after discount
    profit          REAL NOT NULL,
      shipping_cost   REAL,
      promo_campaign  TEXT,                    -- '' when not part of a promo
    returned        INTEGER NOT NULL         -- 0/1
);

CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_category ON orders(category);
CREATE INDEX IF NOT EXISTS idx_orders_region ON orders(region);

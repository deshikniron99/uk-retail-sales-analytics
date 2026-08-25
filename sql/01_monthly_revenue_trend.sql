-- Monthly revenue, profit, and order volume, with year-over-year comparison.
-- Answers: is the business growing, and where's the seasonality?
SELECT
    strftime('%Y-%m', order_date)              AS month,
    COUNT(DISTINCT order_id)                    AS orders,
    ROUND(SUM(sales), 2)                         AS revenue,
    ROUND(SUM(profit), 2)                        AS profit,
    ROUND(SUM(profit) * 100.0 / NULLIF(SUM(sales), 0), 1) AS margin_pct,
    ROUND(SUM(sales) * 1.0 / COUNT(DISTINCT order_id), 2) AS aov
FROM orders
GROUP BY month
ORDER BY month;

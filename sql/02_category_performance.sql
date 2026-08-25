-- Revenue, profit margin, and return rate by product category.
-- Answers: which categories drive revenue vs. which drive profit?
SELECT
    category,
    COUNT(DISTINCT order_id)                                    AS orders,
    ROUND(SUM(sales), 2)                                        AS revenue,
    ROUND(SUM(sales) * 100.0 / SUM(SUM(sales)) OVER (), 1)      AS revenue_share_pct,
    ROUND(SUM(profit), 2)                                       AS profit,
    ROUND(SUM(profit) * 100.0 / NULLIF(SUM(sales), 0), 1)       AS margin_pct,
    ROUND(AVG(returned) * 100.0, 1)                             AS return_rate_pct
FROM orders
GROUP BY category
ORDER BY revenue DESC;

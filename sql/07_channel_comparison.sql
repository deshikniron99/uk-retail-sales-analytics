-- Online vs. In-Store: revenue, AOV, and margin comparison.
SELECT
    channel,
    COUNT(DISTINCT order_id)                              AS orders,
    ROUND(SUM(sales), 2)                                  AS revenue,
    ROUND(SUM(sales) * 1.0 / COUNT(DISTINCT order_id), 2) AS aov,
    ROUND(SUM(profit) * 100.0 / NULLIF(SUM(sales), 0), 1)  AS margin_pct,
    ROUND(AVG(shipping_cost), 2)                           AS avg_shipping_cost
FROM orders
GROUP BY channel
ORDER BY revenue DESC;

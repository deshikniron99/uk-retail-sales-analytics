-- Regional performance leaderboard: revenue, AOV, and customer count per UK region.
SELECT
    region,
    COUNT(DISTINCT order_id)                          AS orders,
    COUNT(DISTINCT customer_id)                        AS customers,
    ROUND(SUM(sales), 2)                                AS revenue,
    ROUND(SUM(sales) * 1.0 / COUNT(DISTINCT order_id), 2) AS aov,
    RANK() OVER (ORDER BY SUM(sales) DESC)              AS revenue_rank
FROM orders
GROUP BY region
ORDER BY revenue DESC;

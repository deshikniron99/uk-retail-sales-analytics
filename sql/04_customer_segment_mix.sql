-- Customer segment mix: how do Consumer / SME / Corporate buyers differ?
SELECT
    customer_segment,
    COUNT(DISTINCT customer_id)                          AS customers,
    COUNT(DISTINCT order_id)                              AS orders,
    ROUND(SUM(sales), 2)                                  AS revenue,
    ROUND(SUM(sales) * 1.0 / COUNT(DISTINCT order_id), 2) AS aov,
    ROUND(COUNT(DISTINCT order_id) * 1.0 / COUNT(DISTINCT customer_id), 2) AS orders_per_customer
FROM orders
GROUP BY customer_segment
ORDER BY revenue DESC;

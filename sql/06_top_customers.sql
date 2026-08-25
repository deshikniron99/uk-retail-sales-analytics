-- Top 15 customers by lifetime revenue (a lightweight RFM-style view).
SELECT
    customer_id,
    customer_segment,
    region,
    COUNT(DISTINCT order_id)                              AS orders,
    ROUND(SUM(sales), 2)                                  AS lifetime_revenue,
    MAX(order_date)                                        AS last_order_date
FROM orders
GROUP BY customer_id
ORDER BY lifetime_revenue DESC
LIMIT 15;

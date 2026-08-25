-- Promo campaign effectiveness: order volume and margin during promo windows
-- vs. a same-length non-promo baseline in the same categories.
SELECT
    CASE WHEN promo_campaign = '' OR promo_campaign IS NULL THEN 'Non-promo' ELSE promo_campaign END AS period,
    COUNT(DISTINCT order_id)                              AS orders,
    ROUND(SUM(sales), 2)                                  AS revenue,
    ROUND(AVG(discount) * 100, 1)                          AS avg_discount_pct,
    ROUND(SUM(profit) * 100.0 / NULLIF(SUM(sales), 0), 1)  AS margin_pct
FROM orders
GROUP BY period
ORDER BY revenue DESC;

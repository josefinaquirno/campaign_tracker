-- ============================================================
-- QUERY: Total Containers del site — denominador para shares
-- FILTROS A ACTUALIZAR POR CAMPAÑA:
--   {{start_date}} → fecha inicio (YYYY-MM-DD)
--   {{end_date}}   → fecha fin    (YYYY-MM-DD)
-- Sin filtro de campaña — incluye todos los containers del site.
-- ============================================================

SELECT
    DATE,
    SUM(C_UNIQUE_SESSION) AS total_sessions,
    SUM(TGMV_168HS)       AS total_nmv,
    SUM(ORDERS_168HS)     AS total_orders,
    SUM(BUYERS_168HS)     AS total_buyers

FROM `meli-bi-data.WHOWNER.DM_CONTAINERS_DEALS_ATTRIBUTION`

WHERE DATE BETWEEN "{{start_date}}" AND "{{end_date}}"
  AND SITE = 'MLA'
  AND DEAL_CONTAINER = 'container'
  AND path IN ('/promotions', '/search')

GROUP BY 1
ORDER BY 1 ASC

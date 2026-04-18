-- ============================================================
-- QUERY: Total Site — denominador para shares vs site
-- FILTROS A ACTUALIZAR POR CAMPAÑA:
--   {{start_date}} → fecha inicio (YYYY-MM-DD)
--   {{end_date}}   → fecha fin    (YYYY-MM-DD)
-- ============================================================

WITH ORDERS AS (
    SELECT DISTINCT
        ORD_CREATED_DT                                           AS date,
        SUM(ORD_ITEM.BASE_CURRENT_PRICE * ORD_ITEM.QTY)         AS tgmv_usd,
        COUNT(DISTINCT COALESCE(CRT_PURCHASE_ID, ORD_ORDER_ID)) AS transactions,
        COUNT(DISTINCT ORD_BUYER.ID)                             AS buyers,
        SUM(ORD_ITEM.QTY)                                        AS si,
        COUNT(DISTINCT ORD_ORDER_ID)                             AS orders
    FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS`
    WHERE ORD_CREATED_DT BETWEEN "{{start_date}}" AND "{{end_date}}"
      AND SIT_SITE_ID            IN ('MLA')
      AND ORD_GMV_FLG            = TRUE
      AND ORD_TGMV_FLG           = TRUE
      AND ORD_ORDER_MSHOPS_FLG   = FALSE
      AND ORD_ORDER_PROXIMITY_FLG = FALSE
      AND ORD_STATUS             = 'paid'
      AND ORD_CATEGORY.MARKETPLACE_ID = 'TM'
    GROUP BY 1
),

SESSIONS AS (
    SELECT
        TRACK_DATE                                                AS date,
        CAST(COUNT(DISTINCT CONCAT(UID, SESSION_ID)) AS INT64)   AS ts_sessions
    FROM `meli-bi-data.WHOWNER.BT_MKP_SESSIONS`
    WHERE TRACK_DATE BETWEEN "{{start_date}}" AND "{{end_date}}"
      AND BU          = 'mercadolibre'
      AND SIT_SITE_ID = 'MLA'
      AND IS_BOUNCE   = FALSE
      AND IS_CORE
    GROUP BY 1
)

SELECT
    o.date,
    o.tgmv_usd,
    s.ts_sessions,
    o.transactions,
    o.buyers,
    o.si,
    o.orders
FROM ORDERS o
LEFT JOIN SESSIONS s ON o.date = s.date
ORDER BY 1 ASC

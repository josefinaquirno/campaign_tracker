-- ============================================================
-- QUERY: Containers de campaña — performance diaria
-- FILTROS A ACTUALIZAR POR CAMPAÑA:
--   {{start_date}}       → fecha inicio (YYYY-MM-DD)
--   {{end_date}}         → fecha fin    (YYYY-MM-DD)
--   {{container_filter}} → patrón de container name (sin los %)
-- ============================================================

SELECT
    DATE,
    CONTAINER_NAME,
    C_UNIQUE_SESSION   AS sessions,
    TGMV_168HS         AS nmv,
    SI_168HS           AS nsi,
    ORDERS_168HS       AS orders,
    TRANSACTION_168HS  AS transactions,
    C_UNIQUE_USERS     AS users_container,
    V_UNIQUE_USERS     AS users_vip,
    BUYERS_168HS       AS buyers,
    CASE
        WHEN CONTAINER_NAME LIKE ('%ACC%')                                            THEN 'ACC'
        WHEN CONTAINER_NAME LIKE ('%FASHION%')                                        THEN 'FASHION'
        WHEN (CONTAINER_NAME LIKE ('%BEAUTY%') OR CONTAINER_NAME LIKE ('%BELLEZA%'))  THEN 'BEAUTY'
        WHEN (CONTAINER_NAME LIKE ('%SALUD%')  OR CONTAINER_NAME LIKE ('%HEALTH%'))   THEN 'HEALTH'
        WHEN CONTAINER_NAME LIKE ('%HE%')                                             THEN 'HE'
        WHEN CONTAINER_NAME LIKE ('%TEC%')                                            THEN 'TEC'
        WHEN CONTAINER_NAME LIKE ('%CPG%')                                            THEN 'CPG'
        WHEN CONTAINER_NAME LIKE ('%ENT%')                                            THEN 'ENT'
        WHEN CONTAINER_NAME LIKE ('%CI%')                                             THEN 'CI'
        WHEN CONTAINER_NAME LIKE ('%FH%')                                             THEN 'FH'
        WHEN CONTAINER_NAME LIKE ('%SPORTS%')                                         THEN 'SPORTS'
        WHEN (CONTAINER_NAME LIKE ('%TB BABY%') OR CONTAINER_NAME LIKE ('%TB%'))      THEN 'TB'
        WHEN CONTAINER_NAME LIKE ('%FOOD_DELIVERY%')                                  THEN 'FOOD_DELIVERY'
        WHEN CONTAINER_NAME LIKE ('%CROSS%')                                          THEN 'CROSS'
        WHEN CONTAINER_NAME LIKE ('%CBT%')                                            THEN 'CBT'
        ELSE 'OTHER'
    END AS vertical

FROM `meli-bi-data.WHOWNER.DM_CONTAINERS_DEALS_ATTRIBUTION`

WHERE DATE BETWEEN "{{start_date}}" AND "{{end_date}}"
  AND SITE = 'MLA'
  AND CONTAINER_NAME LIKE '%{{container_filter}}%'

ORDER BY 1 ASC

-- ============================================================
-- QUERY: Landing — performance diaria atribuida a la campaña
-- FILTROS A ACTUALIZAR POR CAMPAÑA:
--   {{start_date}}    → fecha inicio (YYYY-MM-DD)
--   {{end_date}}      → fecha fin    (YYYY-MM-DD)
--   {{landing_names}} → lista de nombres, ej: "landing-a","landing-b"
--                       (puede tener múltiples valores: takeover + landing principal)
-- ============================================================

SELECT
    DATE,
    LANDING_NAME,
    SESSIONS,
    TGMV_168HS        AS nmv,
    ORDERS_168HS      AS orders,
    TRANSACTIONS_168HS AS transactions,
    SI_168HS          AS nsi,
    NOT_LOG_USERS     AS users_landing,
    LISTADO_TOTAL_USERS AS users_container,
    VPP_TOTAL_USERS   AS users_vip,
    BUYERS_168HS      AS buyers

FROM `meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_CONTAINER_DEAL`

WHERE DATE BETWEEN "{{start_date}}" AND "{{end_date}}"
  AND SITE = 'MLA'
  AND landing_name IN ({{landing_names}})

ORDER BY 1 ASC

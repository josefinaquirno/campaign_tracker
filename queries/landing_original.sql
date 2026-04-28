SELECT
  DATE(DATE)        AS date,
  LANDING_NAME      AS landing_name,
  SUM(SESSIONS)           AS sessions,
  SUM(TGMV_168HS)         AS nmv,
  SUM(ORDERS_168HS)       AS orders,
  SUM(TRANSACTIONS_168HS) AS transactions,
  SUM(SI_168HS)           AS nsi,
  SUM(NOT_LOG_USERS)      AS not_logged_users,
  SUM(LISTADO_TOTAL_USERS) AS users_landing,
  SUM(VPP_TOTAL_USERS)    AS users_container,
  SUM(BUYERS_168HS)       AS buyers

FROM meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_CONTAINER_DEAL
WHERE DATE BETWEEN '2026-04-20' AND '2026-05-05'
  AND SITE = 'MLA'
  AND landing_name = 'ofertas futboleras'
GROUP BY 1, 2
ORDER BY 1 ASC

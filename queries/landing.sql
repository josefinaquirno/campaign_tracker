SELECT
  DATE_EVENT                   AS date,
  LANDING_NAME,
  SUM(TOTAL_SESSIONS)          AS sessions,
  SUM(NMV_USD_168HS_LT)        AS nmv,
  SUM(ORDERS_168HS_LT)         AS orders,
  SUM(TRANSACTIONS_168HS_LT)   AS transactions,
  SUM(SI_168HS_LT)             AS nsi,
  SUM(BUYERS_168HS_LT)         AS buyers

FROM `meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_UNIFIED`
WHERE DATE_EVENT BETWEEN '2026-04-20' AND '2026-05-05'
  AND SITE_ID = 'MLA'
  AND LANDING_NAME IN ('ofertas futboleras', '5 5 descuentos parcial')
GROUP BY DATE_EVENT, LANDING_NAME
ORDER BY 1 ASC

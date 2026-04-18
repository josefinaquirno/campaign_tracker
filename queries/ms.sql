-- ============================================================
-- QUERY: Main Slider — performance diaria de campaña
-- FILTROS A ACTUALIZAR POR CAMPAÑA:
--   {{start_date}}          → fecha inicio (YYYY-MM-DD)
--   {{end_date}}            → fecha fin    (YYYY-MM-DD)
--   {{ms_campaign_filter}}  → patrón de campaign name (sin los %)
-- ============================================================

SELECT
    m.EVENT_LOCAL_DT        AS fecha,
    m.CAMPAIGN_NAME         AS campaign_name,
    M.LINE_ITEM_NAME        AS line_item,
    SUM(m.CLICKS_QTY)       AS clicks,
    SUM(m.IMPRESSION_VIEWS_QTY) AS prints

FROM `meli-bi-data.WHOWNER.BT_ADS_DISP_METRICS_DAILY` m
INNER JOIN `meli-bi-data.WHOWNER.LK_ADS_LINE_ITEMS`  LI ON LI.LINE_ITEM_ID = M.LINE_ITEM_ID
INNER JOIN `meli-bi-data.WHOWNER.LK_ADS_ACCOUNTS`    a  ON a.account_id   = m.ACCOUNT_ID
INNER JOIN `meli-bi-data.WHOWNER.LK_ADS_CAMPAIGNS`   C  ON C.CAMPAIGN_ID  = M.CAMPAIGN_ID

WHERE m.EVENT_LOCAL_DT BETWEEN "{{start_date}}" AND "{{end_date}}"
  AND M.SIT_SITE_ID        IN ('MLA')
  AND PLACEMENT             LIKE '%MAIN-SLIDER%'
  AND ACCOUNT_TYPE          LIKE '%MARKETING%'
  AND M.CAMPAIGN_NAME       LIKE '%{{ms_campaign_filter}}%'
  AND M.LINE_ITEM_NAME  NOT LIKE '%SPLINTER%'
  AND M.CAMPAIGN_NAME   NOT LIKE '%FD%'

GROUP BY ALL
HAVING SUM(m.PRINTS_QTY) > 0
ORDER BY 1 ASC

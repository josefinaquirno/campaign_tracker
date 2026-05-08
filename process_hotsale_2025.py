"""
process_hotsale_2025.py
Extrae datos históricos de Hot Sale 2025 desde BQ y genera docs/data_hotsale_2025.json
Correr UNA SOLA VEZ: python process_hotsale_2025.py

Requisito: pip install google-cloud-bigquery
"""

from google.cloud import bigquery
import json
from datetime import datetime, date

PROJECT  = 'meli-bi-data'
START    = '2025-05-12'
END      = '2025-05-19'
SITE     = 'MLA'
OUT_FILE = 'docs/data_hotsale_2025.json'

client = bigquery.Client(project=PROJECT)

def run(sql):
    rows = client.query(sql).result()
    result = []
    for r in rows:
        row = {}
        for k, v in r.items():
            row[k] = v.isoformat() if isinstance(v, date) else v
        result.append(row)
    return result

print("⏳ Verificando nombres de landing disponibles...")
check = run(f"""
  SELECT DISTINCT LANDING_NAME
  FROM `meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_UNIFIED`
  WHERE DATE_EVENT BETWEEN '{START}' AND '{END}'
    AND SITE_ID = '{SITE}'
    AND LOWER(LANDING_NAME) LIKE '%hot%'
  ORDER BY 1
""")
print(f"  Landings encontradas: {[r['LANDING_NAME'] for r in check]}")
print("  → Si la lista está vacía o el nombre difiere de 'hot-sale', actualizalo en LANDING_NAME abajo.")

LANDING_NAME = 'hot-sale'  # <-- ajustar si el nombre real en BQ es diferente
CONTAINER_FILTER = '%MK T1 HOT SALE 2025%'

print(f"\n⏳ Extrayendo datos para {START} → {END}...")

print("  landing...")
landing = run(f"""
SELECT
  DATE_EVENT            AS date,
  LANDING_NAME          AS landing_name,
  SUM(TOTAL_SESSIONS)   AS sessions,
  SUM(NMV_USD_168HS_LT) AS nmv,
  SUM(ORDERS_168HS_LT)  AS orders,
  SUM(TRANSACTIONS_168HS_LT) AS transactions,
  SUM(SI_168HS_LT)      AS nsi,
  SUM(BUYERS_168HS_LT)  AS buyers
FROM `meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_UNIFIED`
WHERE DATE_EVENT BETWEEN '{START}' AND '{END}'
  AND SITE_ID = '{SITE}'
  AND LANDING_NAME = '{LANDING_NAME}'
GROUP BY 1, 2
ORDER BY 1
""")

print("  landing_original...")
landing_orig = run(f"""
SELECT
  DATE(DATE)               AS date,
  LANDING_NAME             AS landing_name,
  SUM(SESSIONS)            AS sessions,
  SUM(TGMV_168HS)          AS nmv,
  SUM(ORDERS_168HS)        AS orders,
  SUM(TRANSACTIONS_168HS)  AS transactions,
  SUM(SI_168HS)            AS nsi,
  SUM(LISTADO_TOTAL_USERS) AS users_landing,
  SUM(VPP_TOTAL_USERS)     AS users_container,
  SUM(BUYERS_168HS)        AS buyers
FROM `meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_CONTAINER_DEAL`
WHERE DATE BETWEEN '{START}' AND '{END}'
  AND SITE = '{SITE}'
  AND LANDING_NAME = '{LANDING_NAME}'
GROUP BY 1, 2
ORDER BY 1
""")

print("  containers...")
container = run(f"""
SELECT
  DATE                AS date,
  CONTAINER_NAME      AS container_name,
  C_UNIQUE_SESSION    AS sessions,
  TGMV_168HS          AS nmv,
  SI_168HS            AS nsi,
  ORDERS_168HS        AS orders,
  TRANSACTION_168HS   AS transactions,
  C_UNIQUE_USERS      AS users_container,
  V_UNIQUE_USERS      AS users_vip,
  BUYERS_168HS        AS buyers,
  CASE
    WHEN CONTAINER_NAME LIKE '%ACC%'                                           THEN 'ACC'
    WHEN CONTAINER_NAME LIKE '%FASHION%'                                       THEN 'FASHION'
    WHEN CONTAINER_NAME LIKE '%BEAUTY%' OR CONTAINER_NAME LIKE '%BELLEZA%'    THEN 'BEAUTY'
    WHEN CONTAINER_NAME LIKE '%SALUD%'  OR CONTAINER_NAME LIKE '%HEALTH%'     THEN 'HEALTH'
    WHEN CONTAINER_NAME LIKE '%HE%'                                            THEN 'HE'
    WHEN CONTAINER_NAME LIKE '%TEC%'                                           THEN 'TEC'
    WHEN CONTAINER_NAME LIKE '%CPG%'                                           THEN 'CPG'
    WHEN CONTAINER_NAME LIKE '%ENT%'                                           THEN 'ENT'
    WHEN CONTAINER_NAME LIKE '%SPORTS%'                                        THEN 'SPORTS'
    WHEN CONTAINER_NAME LIKE '%TB BABY%' OR CONTAINER_NAME LIKE '%TB%'        THEN 'TB'
    WHEN CONTAINER_NAME LIKE '%CROSS%'                                         THEN 'CROSS'
    ELSE 'OTHER'
  END AS vertical
FROM `meli-bi-data.WHOWNER.DM_CONTAINERS_DEALS_ATTRIBUTION`
WHERE DATE BETWEEN '{START}' AND '{END}'
  AND SITE = '{SITE}'
  AND UPPER(CONTAINER_NAME) LIKE UPPER('{CONTAINER_FILTER}')
ORDER BY 1
""")

print("  total_containers...")
total_containers = run(f"""
SELECT
  DATE                      AS date,
  SUM(C_UNIQUE_SESSION)     AS total_sessions,
  SUM(TGMV_168HS)           AS total_nmv,
  SUM(ORDERS_168HS)         AS total_orders,
  SUM(BUYERS_168HS)         AS total_buyers
FROM `meli-bi-data.WHOWNER.DM_CONTAINERS_DEALS_ATTRIBUTION`
WHERE DATE BETWEEN '{START}' AND '{END}'
  AND SITE = '{SITE}'
  AND DEAL_CONTAINER = 'container'
  AND path IN ('/promotions', '/search')
GROUP BY 1
ORDER BY 1
""")

print("  total_site...")
total_site = run(f"""
WITH ORDERS AS (
  SELECT DISTINCT
    ORD_CREATED_DT                                           AS date,
    SUM(ORD_ITEM.BASE_CURRENT_PRICE * ORD_ITEM.QTY)         AS tgmv_usd,
    COUNT(DISTINCT COALESCE(CRT_PURCHASE_ID, ORD_ORDER_ID)) AS transactions,
    COUNT(DISTINCT ORD_BUYER.ID)                            AS buyers,
    SUM(ORD_ITEM.QTY)                                       AS si,
    COUNT(DISTINCT ORD_ORDER_ID)                            AS orders
  FROM `meli-bi-data.WHOWNER.BT_ORD_ORDERS`
  WHERE ORD_CREATED_DT BETWEEN '{START}' AND '{END}'
    AND SIT_SITE_ID = '{SITE}'
    AND ORD_GMV_FLG = TRUE AND ORD_TGMV_FLG = TRUE
    AND ORD_ORDER_MSHOPS_FLG = FALSE AND ORD_ORDER_PROXIMITY_FLG = FALSE
    AND ORD_STATUS = 'paid' AND ORD_CATEGORY.MARKETPLACE_ID = 'TM'
  GROUP BY 1
),
SESSIONS AS (
  SELECT
    TRACK_DATE                                             AS date,
    CAST(COUNT(DISTINCT CONCAT(UID, SESSION_ID)) AS INT64) AS ts_sessions
  FROM `meli-bi-data.WHOWNER.BT_MKP_SESSIONS`
  WHERE TRACK_DATE BETWEEN '{START}' AND '{END}'
    AND BU = 'mercadolibre' AND SIT_SITE_ID = '{SITE}'
    AND IS_BOUNCE = FALSE AND IS_CORE
  GROUP BY 1
)
SELECT o.date, o.tgmv_usd, s.ts_sessions, o.transactions, o.buyers, o.si, o.orders
FROM ORDERS o
LEFT JOIN SESSIONS s ON o.date = s.date
ORDER BY 1
""")

data = {
    "campaign": {"name": "HOT SALE 2025", "start": START, "end": END},
    "ms": [],
    "landing": landing,
    "ctr_landing": [],
    "landing_original": landing_orig,
    "container": container,
    "total_containers": total_containers,
    "total_site": total_site,
    "targets": {},
    "refreshed_at": datetime.now().isoformat()
}

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, default=str)

print(f"\n✓ {len(landing)} días de landing | {len(container)} rows containers | {len(total_site)} días site")
print(f"✓ Guardado en {OUT_FILE}")
print(f"\nSiguiente paso: git add {OUT_FILE} && git commit -m 'data: Hot Sale 2025 historico' && git push")

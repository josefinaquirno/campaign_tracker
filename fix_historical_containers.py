"""
fix_historical_containers.py
=============================
Corrige el array 'container' de una entrada en historical.json
re-corriendo la query con el filtro correcto de container_name.

Uso:
  python fix_historical_containers.py

Editá las variables CAMPAIGN_NAME, CONTAINER_FILTER, START_DATE, END_DATE
para apuntar a la campaña a corregir.
"""

import json
import os
from google.cloud import bigquery

# ── Configuración ────────────────────────────────────────────────────────────
BILLING_PROJECT  = "meli-bi-data"
HISTORICAL_PATH  = os.path.join(os.path.dirname(__file__), "docs", "historical.json")

CAMPAIGN_NAME    = "DOUBLE DATES 04/04"          # debe coincidir exacto con historical.json
CONTAINER_FILTER = "MKP DEMAND 4 4 MARZO 2026%"  # LIKE filter para CONTAINER_NAME
START_DATE       = "2026-03-23"
END_DATE         = "2026-04-07"
# ─────────────────────────────────────────────────────────────────────────────


QUERY = f"""
SELECT
  DATE                   AS date,
  CONTAINER_NAME         AS container_name,
  C_UNIQUE_SESSION       AS sessions,
  TGMV_168HS             AS nmv,
  SI_168HS               AS nsi,
  ORDERS_168HS           AS orders,
  TRANSACTION_168HS      AS transactions,
  C_UNIQUE_USERS         AS users_container,
  V_UNIQUE_USERS         AS users_vip,
  BUYERS_168HS           AS buyers,
  CASE
    WHEN CONTAINER_NAME LIKE '%ACC%'                                            THEN 'ACC'
    WHEN CONTAINER_NAME LIKE '%FASHION%'                                        THEN 'FASHION'
    WHEN (CONTAINER_NAME LIKE '%BEAUTY%' OR CONTAINER_NAME LIKE '%BELLEZA%')   THEN 'BEAUTY'
    WHEN (CONTAINER_NAME LIKE '%SALUD%'  OR CONTAINER_NAME LIKE '%HEALTH%')    THEN 'HEALTH'
    WHEN CONTAINER_NAME LIKE '%HE%'                                             THEN 'HE'
    WHEN CONTAINER_NAME LIKE '%TEC%'                                            THEN 'TEC'
    WHEN CONTAINER_NAME LIKE '%CPG%'                                            THEN 'CPG'
    WHEN CONTAINER_NAME LIKE '%ENT%'                                            THEN 'ENT'
    WHEN CONTAINER_NAME LIKE '%CI%'                                             THEN 'CI'
    WHEN CONTAINER_NAME LIKE '%FH%'                                             THEN 'FH'
    WHEN CONTAINER_NAME LIKE '%SPORTS%'                                         THEN 'SPORTS'
    WHEN (CONTAINER_NAME LIKE '%TB BABY%' OR CONTAINER_NAME LIKE '%TB%')       THEN 'TB'
    WHEN CONTAINER_NAME LIKE '%FOOD_DELIVERY%'                                  THEN 'FOOD_DELIVERY'
    WHEN CONTAINER_NAME LIKE '%CROSS%'                                          THEN 'CROSS'
    WHEN CONTAINER_NAME LIKE '%CBT%'                                            THEN 'CBT'
    ELSE 'OTHER'
  END AS vertical
FROM `meli-bi-data.WHOWNER.DM_CONTAINERS_DEALS_ATTRIBUTION`
WHERE DATE BETWEEN '{START_DATE}' AND '{END_DATE}'
  AND SITE = 'MLA'
  AND CONTAINER_NAME LIKE '{CONTAINER_FILTER}'
ORDER BY date, container_name
"""


def to_num(v):
    """Convierte Decimal/int/float a float, None a None."""
    if v is None: return None
    try: return float(v)
    except: return v

def row_to_dict(row):
    return {
        "date":            str(row["date"]),
        "container_name":  row["container_name"],
        "sessions":        to_num(row["sessions"]),
        "nmv":             to_num(row["nmv"]),
        "nsi":             to_num(row["nsi"]),
        "orders":          to_num(row["orders"]),
        "transactions":    to_num(row["transactions"]),
        "users_container": to_num(row["users_container"]),
        "users_vip":       to_num(row["users_vip"]),
        "buyers":          to_num(row["buyers"]),
        "vertical":        row["vertical"],
    }


def main():
    with open(HISTORICAL_PATH, encoding="utf-8") as f:
        historical = json.load(f)

    entry = next((e for e in historical if e.get("name") == CAMPAIGN_NAME), None)
    if not entry:
        print(f"✗ No se encontró la entrada '{CAMPAIGN_NAME}' en historical.json")
        return

    print(f"[RUN] Corrigiendo containers de '{CAMPAIGN_NAME}' "
          f"({START_DATE} → {END_DATE}) filtro='{CONTAINER_FILTER}' ...")

    client = bigquery.Client(project=BILLING_PROJECT)
    job    = client.query(QUERY)
    rows   = list(job.result())

    if not rows:
        print("  ⚠ Query retornó 0 filas — verificá el filtro y las fechas")
        return

    entry["container"] = [row_to_dict(r) for r in rows]
    print(f"  ✓ {len(rows)} filas de containers actualizadas")

    with open(HISTORICAL_PATH, "w", encoding="utf-8") as f:
        json.dump(historical, f, ensure_ascii=False, indent=2)
    print(f"✅ historical.json actualizado")
    print(f"\nAhora corré:")
    print(f"  git add docs/historical.json")
    print(f"  git commit -m \"fix: correct container data for {CAMPAIGN_NAME}\"")
    print(f"  git push origin main")


if __name__ == "__main__":
    main()

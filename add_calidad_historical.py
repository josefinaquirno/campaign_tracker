"""
add_calidad_historical.py
=========================
Agrega calidad de oferta (riu_high, con_oferta, dto_pond) a cada entrada
del historical.json que tenga "calidad_pattern" definido pero aún no tenga "calidad".

Uso:
  python add_calidad_historical.py

Requiere:
  pip install google-cloud-bigquery

Configuración por entrada en historical.json:
  Agregá el campo "calidad_pattern" a cada entrada histórica con el patrón
  de contenedor que usaba esa campaña (igual al DATES CTE del verdi_calidad.json),
  p.ej.:  "calidad_pattern": "%MKP DEMAND 4 4%"
"""

import json
import os
from google.cloud import bigquery

# ── Configuración ────────────────────────────────────────────────────────────
BILLING_PROJECT = "meli-bi-data"
HISTORICAL_PATH = os.path.join(os.path.dirname(__file__), "docs", "historical.json")
# ─────────────────────────────────────────────────────────────────────────────


def build_light_query(pattern: str, start: str, end: str) -> str:
    """
    Query liviana que calcula solo los 3 KPIs de calidad sin breakdown por patrón.
    Evita las CTEs de exhibidos y el detalle por tipo de oferta para reducir costo y tiempo.
    """
    return f"""
WITH

FILTRO_V AS (
  SELECT DISTINCT
    SPLIT(t.CONTAINER_DEAL_ID, '-')[OFFSET(0)] AS CONTAINER_DEAL_ID
  FROM `meli-bi-data.WHOWNER.DM_ITEM_CONTAINER` t
  WHERE t.SITE = 'MLA'
    AND DATE(t.DATE_EVENT) BETWEEN '{start}' AND '{end}'
    AND LOWER(t.CONTAINER_NAME) LIKE LOWER('{pattern}')
    AND LOWER(t.CONTAINER_NAME) NOT LIKE '%ads%'
  GROUP BY 1
  HAVING SUM(COALESCE(t.UNIQUE_SESSION, 0)) > 1
),

BASE_V AS (
  SELECT
    a.VIEWED_ITEM_ID,
    DATE(a.DATE_EVENT)            AS DATE_EVENT,
    COALESCE(a.UNIQUE_SESSION, 0) AS UNIQUE_SESSION
  FROM `meli-bi-data.WHOWNER.DM_ITEM_CONTAINER` a
  JOIN FILTRO_V f
    ON SPLIT(a.CONTAINER_DEAL_ID, '-')[OFFSET(0)] = f.CONTAINER_DEAL_ID
  WHERE a.SITE = 'MLA'
    AND DATE(a.DATE_EVENT) BETWEEN '{start}' AND '{end}'
    AND LOWER(a.CONTAINER_NAME) LIKE LOWER('{pattern}')
    AND LOWER(a.CONTAINER_NAME) NOT LIKE '%ads%'
),

UNIQUE_ITEMS AS (
  SELECT DISTINCT VIEWED_ITEM_ID, DATE_EVENT
  FROM BASE_V
),

RIU AS (
  SELECT DISTINCT
    r.ITE_ITEM_ID,
    DATE(DATE_TRUNC(r.PHOTO_ID, DAY)) AS PHOTO_DATE,
    r.CATEGORY_VERIFIED
  FROM `meli-bi-data.WHOWNER.LK_BENEFITS_RIU_CLUSTER_RESULTS` r
  JOIN UNIQUE_ITEMS i
    ON r.ITE_ITEM_ID = i.VIEWED_ITEM_ID
   AND DATE(DATE_TRUNC(r.PHOTO_ID, DAY)) = DATE_SUB(i.DATE_EVENT, INTERVAL 2 DAY)
  WHERE r.SIT_SITE_ID = 'MLA'
),

OFFERS AS (
  SELECT DISTINCT
    o.ITE_ITEM_ID,
    o.DAY,
    o.CAMPAIGN_GROUP,
    SAFE_DIVIDE(o.FINAL_PRICE, o.INITIAL_PRICE) - 1 AS pct_descuento,
    o.FINAL_PRICE
  FROM `meli-sbox.PLANNINGMLA.BENEFITS_OFFERS` o
  JOIN UNIQUE_ITEMS i
    ON o.ITE_ITEM_ID = i.VIEWED_ITEM_ID
   AND o.DAY = i.DATE_EVENT
),

ENRICHED AS (
  SELECT
    b.VIEWED_ITEM_ID,
    o.CAMPAIGN_GROUP,
    r.CATEGORY_VERIFIED,
    b.UNIQUE_SESSION,
    b.UNIQUE_SESSION * COALESCE(o.pct_descuento, 0) AS DESC_PRC_SESSION,
    b.UNIQUE_SESSION * COALESCE(o.FINAL_PRICE, 0)   AS FINAL_PRICE_SESSION
  FROM BASE_V b
  LEFT JOIN RIU r
    ON b.VIEWED_ITEM_ID = r.ITE_ITEM_ID
   AND DATE_SUB(b.DATE_EVENT, INTERVAL 2 DAY) = r.PHOTO_DATE
  LEFT JOIN OFFERS o
    ON b.VIEWED_ITEM_ID = o.ITE_ITEM_ID
   AND b.DATE_EVENT = o.DAY
)

SELECT
  COUNT(DISTINCT VIEWED_ITEM_ID) AS VIEWED_ITEMS,
  COUNT(DISTINCT IF(
    CATEGORY_VERIFIED IN ('Boost','High','Mid high'), VIEWED_ITEM_ID, NULL
  )) AS HIGH_ITEMS_V,
  COUNT(DISTINCT IF(
    CAMPAIGN_GROUP IS NULL, VIEWED_ITEM_ID, NULL
  )) AS NO_OFFER_ITEMS,
  SAFE_DIVIDE(SUM(DESC_PRC_SESSION), SUM(UNIQUE_SESSION)) AS DISCOUNT_POND
FROM ENRICHED
"""


def compute_calidad_kpis(row) -> dict:
    viewed   = row["VIEWED_ITEMS"]   or 0
    high     = row["HIGH_ITEMS_V"]   or 0
    no_offer = row["NO_OFFER_ITEMS"] or 0
    disc     = row["DISCOUNT_POND"]

    riu_high   = (high / viewed * 100)               if viewed > 0 else None
    con_oferta = ((viewed - no_offer) / viewed * 100) if viewed > 0 else None
    dto_pond   = (abs(disc) * 100)                   if disc is not None else None

    return {
        "riu_high":   round(riu_high,   2) if riu_high   is not None else None,
        "con_oferta": round(con_oferta, 2) if con_oferta is not None else None,
        "dto_pond":   round(dto_pond,   2) if dto_pond   is not None else None,
    }


def main():
    with open(HISTORICAL_PATH, encoding="utf-8") as f:
        historical = json.load(f)

    client  = bigquery.Client(project=BILLING_PROJECT)
    updated = 0

    for entry in historical:
        name    = entry.get("name", "")
        pattern = entry.get("calidad_pattern")
        start   = entry.get("start")
        end     = entry.get("end")

        if not pattern:
            print(f"[SKIP] '{name}' — sin calidad_pattern")
            continue
        if entry.get("calidad"):
            print(f"[SKIP] '{name}' — ya tiene calidad")
            continue

        print(f"[RUN]  '{name}' ({start} → {end}) pattern='{pattern}' ...")
        query = build_light_query(pattern, start, end)

        try:
            job  = client.query(query)
            rows = list(job.result())
            if not rows:
                print("  ⚠ Query retornó 0 filas — verificá el pattern y las fechas")
                continue
            kpis = compute_calidad_kpis(rows[0])
            entry["calidad"] = kpis
            print(f"  ✓ riu_high={kpis['riu_high']}%  "
                  f"con_oferta={kpis['con_oferta']}%  "
                  f"dto_pond={kpis['dto_pond']}%")
            updated += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")

    if updated:
        with open(HISTORICAL_PATH, "w", encoding="utf-8") as f:
            json.dump(historical, f, ensure_ascii=False, indent=2)
        print(f"\n✅ historical.json actualizado ({updated} entradas nuevas)")
    else:
        print("\nNada que actualizar.")


if __name__ == "__main__":
    main()

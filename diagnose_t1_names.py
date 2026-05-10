"""
diagnose_t1_names.py
====================
Muestra los landing_names y container_names T1 reales en BQ
para identificar los nombres exactos a usar en la query de targets.

Uso:
  python diagnose_t1_names.py
"""
from google.cloud import bigquery

BILLING_PROJECT = "meli-bi-data"

# Fechas de campañas T1 conocidas
T1_DATE_RANGES = [
    ("2025-05-12", "2025-05-19", "HOT SALE 2025"),
    ("2025-11-03", "2025-11-11", "CYBER MONDAY 2025"),
    ("2025-11-26", "2025-12-03", "BLACK FRIDAY 2025"),
]

LANDING_QUERY = """
SELECT
  LANDING_NAME,
  COUNT(DISTINCT DATE) AS dias,
  MIN(DATE) AS primer_dia,
  MAX(DATE) AS ultimo_dia,
  ROUND(SUM(SESSIONS)) AS total_sessions
FROM `meli-bi-data.WHOWNER.DM_LANDING_ATTRIBUTION_CONTAINER_DEAL`
WHERE SITE = 'MLA'
  AND DATE BETWEEN '{start}' AND '{end}'
GROUP BY 1
HAVING total_sessions > 1000
ORDER BY total_sessions DESC
LIMIT 30
"""

CONTAINER_QUERY = """
SELECT
  CONTAINER_NAME,
  COUNT(DISTINCT DATE) AS dias,
  ROUND(SUM(C_UNIQUE_SESSION)) AS total_sessions
FROM `meli-bi-data.WHOWNER.DM_CONTAINERS_DEALS_ATTRIBUTION`
WHERE SITE = 'MLA'
  AND DATE BETWEEN '{start}' AND '{end}'
  AND (
    UPPER(CONTAINER_NAME) LIKE '%T1%'
    OR UPPER(CONTAINER_NAME) LIKE '%HOT SALE%'
    OR UPPER(CONTAINER_NAME) LIKE '%CYBER%'
    OR UPPER(CONTAINER_NAME) LIKE '%BLACK%'
    OR UPPER(CONTAINER_NAME) LIKE '%PROMO%'
  )
GROUP BY 1
ORDER BY total_sessions DESC
LIMIT 30
"""

client = bigquery.Client(project=BILLING_PROJECT)

for start, end, label in T1_DATE_RANGES:
    print(f"\n{'='*60}")
    print(f"  {label}  ({start} → {end})")
    print(f"{'='*60}")

    print("\n📍 LANDING NAMES (sessions > 1k):")
    print(f"  {'Landing Name':<45} {'Días':>5} {'Sessions':>12}")
    print("  " + "─"*65)
    rows = list(client.query(LANDING_QUERY.format(start=start, end=end)).result())
    if rows:
        for r in rows:
            print(f"  {str(r['LANDING_NAME']):<45} {int(r['dias']):>5} {int(r['total_sessions']):>12,}")
    else:
        print("  (sin resultados)")

    print("\n📦 CONTAINER NAMES (con T1/HOT/CYBER/BLACK/PROMO):")
    print(f"  {'Container Name':<55} {'Días':>5} {'Sessions':>12}")
    print("  " + "─"*75)
    rows = list(client.query(CONTAINER_QUERY.format(start=start, end=end)).result())
    if rows:
        for r in rows:
            print(f"  {str(r['CONTAINER_NAME']):<55} {int(r['dias']):>5} {int(r['total_sessions']):>12,}")
    else:
        print("  (sin resultados)")

print("\n✅ Diagnóstico completo.")

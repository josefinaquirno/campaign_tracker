"""
preview_targets_t1.py
=====================
Lee la query directamente de verdi_targets_t1.json (misma fuente que el flow),
reemplaza el TO_BASE64 por un SELECT legible y muestra los números por día.

Uso:
  python preview_targets_t1.py
"""

import json
import re
from google.cloud import bigquery

BILLING_PROJECT = "meli-bi-data"
FLOW_FILE = "verdi_targets_t1.json"

# Leer SQL del flow
with open(FLOW_FILE, encoding="utf-8") as f:
    flow = json.load(f)

raw_sql = next(
    n["parameters"]["sqlQuery"]
    for n in flow["nodes"]
    if n.get("name") == "BQ Targets T1"
)

# Reemplazar el SELECT final (TO_BASE64...) por un SELECT legible
# TARGETS_BY_DATE ya tiene todo calculado (ratio × sessions), se lee directo
READABLE_SELECT = """
SELECT
  date,
  FORMAT_DATE('%a', date) AS dia,
  ts_sessions,
  ts_nmv,
  ldg_sessions,
  ldg_usuarios,
  ldg_ses_cont,
  ldg_ses_vip,
  ldg_nsi,
  ldg_nmv,
  cnt_sessions,
  cnt_ses_vip,
  cnt_nsi,
  cnt_trx,
  cnt_nmv
FROM TARGETS_BY_DATE
ORDER BY date
"""

# Cortar el SELECT final (TO_BASE64) y reemplazarlo
query = re.sub(r"\nSELECT TO_BASE64.*", READABLE_SELECT, raw_sql, flags=re.DOTALL)

def fmt(v):
    if v is None: return "—"
    try:
        f = float(v)
        if f >= 1_000_000: return f"{f/1_000_000:.1f}M"
        if f >= 1_000:     return f"{f/1_000:.0f}k"
        return f"{f:.0f}"
    except:
        return str(v)

def main():
    print("Corriendo query T1 targets preview (desde verdi_targets_t1.json)...\n")
    client = bigquery.Client(project=BILLING_PROJECT)
    rows   = list(client.query(query).result())

    if not rows:
        print("⚠ La query no devolvió filas.")
        return

    print(f"{'Fecha':<12} {'Día':<4} {'Site Ses':>9} {'Site NMV':>10} "
          f"{'Ldg Ses':>8} {'Ldg NMV':>9} {'Ldg NSI':>8} "
          f"{'Cnt Ses':>8} {'Cnt NMV':>9} {'Cnt NSI':>8}")
    print("─" * 95)

    totals = {k: 0 for k in ['ts_sessions','ts_nmv','ldg_sessions','ldg_nmv',
                               'ldg_nsi','cnt_sessions','cnt_nmv','cnt_nsi']}
    for r in rows:
        print(f"{str(r['date']):<12} {r['dia']:<4} "
              f"{fmt(r['ts_sessions']):>9} {fmt(r['ts_nmv']):>10} "
              f"{fmt(r['ldg_sessions']):>8} {fmt(r['ldg_nmv']):>9} {fmt(r['ldg_nsi']):>8} "
              f"{fmt(r['cnt_sessions']):>8} {fmt(r['cnt_nmv']):>9} {fmt(r['cnt_nsi']):>8}")
        for k in totals:
            try: totals[k] += float(r[k] or 0)
            except: pass

    print("─" * 95)
    print(f"{'TOTAL':<12} {'':4} "
          f"{fmt(totals['ts_sessions']):>9} {fmt(totals['ts_nmv']):>10} "
          f"{fmt(totals['ldg_sessions']):>8} {fmt(totals['ldg_nmv']):>9} {fmt(totals['ldg_nsi']):>8} "
          f"{fmt(totals['cnt_sessions']):>8} {fmt(totals['cnt_nmv']):>9} {fmt(totals['cnt_nsi']):>8}")

    print("\nDetalle landing benchmark por DOW:")
    print(f"  {'DOW':<4} {'Ses':>8} {'Usuarios':>9} {'SesCont':>8} {'SesVIP':>8} {'NSI':>6} {'NMV':>9}")
    print("  " + "─" * 57)
    for r in rows:
        print(f"  {r['dia']:<4} {fmt(r['ldg_sessions']):>8} {fmt(r['ldg_usuarios']):>9} "
              f"{fmt(r['ldg_ses_cont']):>8} {fmt(r['ldg_ses_vip']):>8} "
              f"{fmt(r['ldg_nsi']):>6} {fmt(r['ldg_nmv']):>9}")

    print("\nDetalle container benchmark por DOW:")
    print(f"  {'DOW':<4} {'Ses':>8} {'SesVIP':>8} {'NSI':>6} {'NMV':>9}")
    print("  " + "─" * 38)
    for r in rows:
        print(f"  {r['dia']:<4} {fmt(r['cnt_sessions']):>8} {fmt(r['cnt_ses_vip']):>8} "
              f"{fmt(r['cnt_nsi']):>6} {fmt(r['cnt_nmv']):>9}")

if __name__ == "__main__":
    main()

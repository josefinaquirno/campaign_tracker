"""
generate_targets_t1.py
======================
Corre la query de verdi_targets_t1.json en BigQuery,
decodifica el base64 y guarda el resultado en docs/targets_t1.json.

Uso:
  python generate_targets_t1.py
"""

import json
import base64
from google.cloud import bigquery

BILLING_PROJECT = "meli-bi-data"
FLOW_FILE       = "verdi_targets_t1.json"
OUTPUT_FILE     = "docs/targets_t1.json"

# Leer SQL del flow
with open(FLOW_FILE, encoding="utf-8") as f:
    flow = json.load(f)

sql = next(
    n["parameters"]["sqlQuery"]
    for n in flow["nodes"]
    if n.get("name") == "BQ Targets T1"
)

print("Corriendo query BQ Targets T1...")
client = bigquery.Client(project=BILLING_PROJECT)
rows   = list(client.query(sql).result())

if not rows:
    print("⚠ La query no devolvió filas.")
    exit(1)

# La query devuelve una sola fila con data_b64
raw_b64 = rows[0]["data_b64"]
# Limpiar saltos de línea que BigQuery agrega al TO_BASE64
clean   = raw_b64.replace("\n", "").replace("\r", "")
decoded = base64.b64decode(clean).decode("utf-8")
data    = json.loads(decoded)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ Guardado en {OUTPUT_FILE}")
print(f"  Fechas: {data.get('dates', [])}")
print(f"  Total landing NMV: {sum(d.get('landing', {}).get('nmv', 0) for d in data.get('daily', [])):.0f}")
print(f"  Total container NMV: {sum(d.get('container', {}).get('nmv', 0) for d in data.get('daily', [])):.0f}")

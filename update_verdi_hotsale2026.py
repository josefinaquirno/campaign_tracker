"""
update_verdi_hotsale2026.py
Actualiza verdi_flow.json y verdi_calidad.json para Hot Sale 2026.
Correr cuando DD cierre (después del 5/5): python update_verdi_hotsale2026.py
Luego reimportar ambos flows en Verdi.
"""

import json, re

HS_START = '2026-05-11'
HS_END   = '2026-05-18'
HS_DATES = [f'2026-05-{d:02d}' for d in range(11, 19)]  # 11 al 18

DD_START = '2026-04-20'
DD_END   = '2026-05-05'

# ──────────────────────────────────────────────
# verdi_flow.json
# ──────────────────────────────────────────────
print("Actualizando verdi_flow.json...")
with open('verdi_flow.json', 'r', encoding='utf-8') as f:
    raw = f.read()

replacements = [
    # Fechas SQL (almacenadas como \u0027...\u0027 en el JSON)
    (r'\u0027' + DD_START + r'\u0027', r'\u0027' + HS_START + r'\u0027'),
    (r'\u0027' + DD_END   + r'\u0027', r'\u0027' + HS_END   + r'\u0027'),
    # Fechas SQL en formato literal ' (por si el archivo tiene quotes directas)
    ("'" + DD_START + "'", "'" + HS_START + "'"),
    ("'" + DD_END   + "'", "'" + HS_END   + "'"),
    # MS filter
    ('%DOUBLEDATES%', '%HOTSALE%'),
    # Landing names (formato \u0027)
    (r"\u0027ofertas futboleras\u0027, \u00275 5 descuentos parcial\u0027",
     r"\u0027hot-sale\u0027, \u0027hot-sale-parcial\u0027"),
    # Landing names (formato literal)
    ("'ofertas futboleras', '5 5 descuentos parcial'",
     "'hot-sale', 'hot-sale-parcial'"),
    # Container filter
    ("LIKE \\u0027MKP DEMAND 5 5 ABRIL 2026%\\u0027",
     "LIKE \\u0027%MKP T1 HOT SALE MAYO 2026%\\u0027"),
    ("LIKE 'MKP DEMAND 5 5 ABRIL 2026%'",
     "LIKE '%MKP T1 HOT SALE MAYO 2026%'"),
    # Nombre campaña en CONCAT (JSON escapado dentro del string SQL)
    ('\\"name\\":\\"DOUBLE DATES\\"', '\\"name\\":\\"HOT SALE\\"'),
    ('\\"start\\":\\"' + DD_START + '\\"', '\\"start\\":\\"' + HS_START + '\\"'),
    ('\\"end\\":\\"'   + DD_END   + '\\"', '\\"end\\":\\"'   + HS_END   + '\\"'),
    # Nombre campaña (formato sin escape, por si el archivo lo tiene así)
    ('"name":"DOUBLE DATES"', '"name":"HOT SALE"'),
    ('"start":"' + DD_START + '"', '"start":"' + HS_START + '"'),
    ('"end":"'   + DD_END   + '"', '"end":"'   + HS_END   + '"'),
    # Comentario al inicio del SQL
    ('CAMPAIGN TRACKER — DOUBLE DATES', 'CAMPAIGN TRACKER — HOT SALE 2026'),
    ('Fechas: 2026-04-20 → 2026-05-05', f'Fechas: {HS_START} → {HS_END}'),
]

for old, new in replacements:
    raw = raw.replace(old, new)

# Reemplazar bloque de targets (regex para capturar la sección completa)
# Targets → fechas nuevas, valores null por ahora
dates_json = json.dumps(HS_DATES)
new_targets = (
    f'"targets":{{"dates":{dates_json},'
    '"ms":{"ctr":null},'
    '"total_site":{},'
    '"landing":{},'
    '"container":{}}}'
)
# Buscar el bloque de targets en la cadena SQL (puede estar con \\" o con ")
raw = re.sub(
    r'"targets":\{"dates":\[(?:[^]]*)\].*?"container":\{[^}]*\}\}',
    new_targets,
    raw,
    flags=re.DOTALL
)

with open('verdi_flow.json', 'w', encoding='utf-8') as f:
    f.write(raw)
print("  ✓ verdi_flow.json actualizado")

# ──────────────────────────────────────────────
# verdi_calidad.json
# ──────────────────────────────────────────────
print("Actualizando verdi_calidad.json...")
with open('verdi_calidad.json', 'r', encoding='utf-8') as f:
    raw_cal = f.read()

cal_replacements = [
    # Pattern DATES CTE
    ("%MKP DEMAND 5 5%", "%MKP T1 HOT SALE MAYO 2026%"),
    (r"\u0027%MKP DEMAND 5 5%\u0027", r"\u0027%MKP T1 HOT SALE MAYO 2026%\u0027"),
    # Fechas DATES CTE (formato DATE '...')
    ("DATE \\u0027" + DD_START + "\\u0027", "DATE \\u0027" + HS_START + "\\u0027"),
    ("DATE \\u0027" + DD_END   + "\\u0027", "DATE \\u0027" + HS_END   + "\\u0027"),
    ("DATE '" + DD_START + "'", "DATE '" + HS_START + "'"),
    ("DATE '" + DD_END   + "'", "DATE '" + HS_END   + "'"),
]

for old, new in cal_replacements:
    raw_cal = raw_cal.replace(old, new)

with open('verdi_calidad.json', 'w', encoding='utf-8') as f:
    f.write(raw_cal)
print("  ✓ verdi_calidad.json actualizado")

# ──────────────────────────────────────────────
# Verificación rápida
# ──────────────────────────────────────────────
print("\n📋 Verificando cambios clave...")
checks = [
    ('verdi_flow.json', 'HOTSALE',              'MS filter'),
    ('verdi_flow.json', 'hot-sale',              'Landing filter'),
    ('verdi_flow.json', 'MKP T1 HOT SALE MAYO 2026', 'Container filter'),
    ('verdi_flow.json', HS_START,                'Fecha inicio'),
    ('verdi_calidad.json', 'MKP T1 HOT SALE MAYO 2026', 'Pattern calidad'),
    ('verdi_calidad.json', HS_START,             'Fecha calidad'),
]
all_ok = True
for fname, token, label in checks:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    ok = token in content
    if not ok:
        all_ok = False
    print(f"  {'✓' if ok else '✗'} {fname} — {label} ({token[:30]})")

if all_ok:
    print("\n✓ Todo OK. Reimportar ambos flows en Verdi.")
else:
    print("\n⚠ Algunos reemplazos no se aplicaron. Revisar manualmente los campos marcados con ✗.")

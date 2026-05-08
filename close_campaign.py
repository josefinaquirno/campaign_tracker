"""
close_campaign.py
=================
Cierra la campaña activa y activa la siguiente.

Pasos que ejecuta:
  1. Copia data.json → data_dd_0426.json  (preserva datos de DOUBLE DATES 5/5)
  2. Copia calidad.json → calidad_dd_0426.json
  3. Copia oferta.json  → oferta_dd_0426.json
  4. Actualiza campaigns.json:
       - double_dates_0426 → status=closed, apunta a sus propios archivos
       - hotsale_2026      → status=active
  5. Agrega calidad_pattern a double_dates_0426 en historical entries
     (via add_calidad_historical.py después)

Uso:
  python close_campaign.py

Después de correrlo:
  1. python add_calidad_historical.py   <- agrega KPIs calidad para 5/5
  2. python update_verdi_hotsale2026.py <- actualiza flows de Verdi
  3. git add -A && git commit -m "..." && git push
  4. Reimportar verdi_flow.json y verdi_calidad.json en Verdi/n8n
"""

import json, os, shutil

DOCS = os.path.join(os.path.dirname(__file__), "docs")

def read_json(fname):
    path = os.path.join(DOCS, fname)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def write_json(fname, data):
    path = os.path.join(DOCS, fname)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def copy_file(src, dst):
    s = os.path.join(DOCS, src)
    d = os.path.join(DOCS, dst)
    if not os.path.exists(s):
        print(f"  ⚠ No existe {src}, saltando copia")
        return False
    shutil.copy2(s, d)
    print(f"  ✓ {src} → {dst}")
    return True


def main():
    # ── 1. Copiar archivos de la campaña actual ────────────────────────────
    print("1. Archivando archivos de DOUBLE DATES 5/5...")
    copy_file("data.json",    "data_dd_0426.json")
    copy_file("calidad.json", "calidad_dd_0426.json")
    copy_file("oferta.json",  "oferta_dd_0426.json")

    # ── 2. Actualizar campaigns.json ───────────────────────────────────────
    print("\n2. Actualizando campaigns.json...")
    camps = read_json("campaigns.json")

    for c in camps:
        if c["id"] == "double_dates_0426":
            c["status"]       = "closed"
            c["data_file"]    = "data_dd_0426.json"
            c["calidad_file"] = "calidad_dd_0426.json"
            c["oferta_file"]  = "oferta_dd_0426.json"
            print(f"  ✓ {c['name']} → closed (archivos propios)")

        elif c["id"] == "hotsale_2026":
            c["status"] = "active"
            print(f"  ✓ {c['name']} → active")

    write_json("campaigns.json", camps)

    # ── 3. Agregar calidad_pattern a historical.json para 5/5 ──────────────
    print("\n3. Preparando calidad histórica de 5/5 en historical.json...")
    hist = read_json("historical.json")

    # Verificar si ya existe entrada para 5/5
    existing = next((h for h in hist if "DOUBLE DATES" in h.get("name","") and h.get("start","").startswith("2026-04")), None)
    if existing:
        print(f"  ⚠ Ya existe entrada para '{existing['name']}' — no se duplica")
    else:
        # Leer datos desde data_dd_0426.json (que acabamos de copiar)
        try:
            dd = read_json("data_dd_0426.json")
            new_entry = {
                "name":            "DOUBLE DATES 20/4",
                "start":           dd["campaign"]["start"],
                "end":             dd["campaign"]["end"],
                "calidad_pattern": "%MKP DEMAND 5 5%",
                "ms":              dd.get("ms", []),
                "landing":         dd.get("landing", []),
                "ctr_landing":     dd.get("ctr_landing", []),
                "landing_original":dd.get("landing_original", []),
                "container":       dd.get("container", []),
                "total_containers":dd.get("total_containers", []),
                "total_site":      dd.get("total_site", []),
                "targets":         dd.get("targets", {}),
            }
            hist.append(new_entry)
            write_json("historical.json", hist)
            print(f"  ✓ Entrada 'DOUBLE DATES 20/4' agregada a historical.json")
            print(f"    ms={len(new_entry['ms'])} landing={len(new_entry['landing'])} container={len(new_entry['container'])}")
        except Exception as e:
            print(f"  ✗ Error leyendo data_dd_0426.json: {e}")

    # ── Resumen ───────────────────────────────────────────────────────────
    print("""
✅ Campaña cerrada. Próximos pasos:

  1. python add_calidad_historical.py
     (agrega KPIs de calidad a DOUBLE DATES 20/4)

  2. python update_verdi_hotsale2026.py
     (actualiza verdi_flow.json y verdi_calidad.json para HOT SALE 2026)

  3. git add -A
     git commit -m "feat: close DD 5/5, open HOT SALE 2026"
     git push origin main

  4. Reimportar verdi_flow.json y verdi_calidad.json en Verdi/n8n
""")


if __name__ == "__main__":
    main()

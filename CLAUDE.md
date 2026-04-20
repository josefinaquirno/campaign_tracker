# Campaign Tracker — Contexto para Claude

## Qué es este proyecto
Dashboard de seguimiento diario de campañas comerciales de MercadoLibre Argentina.
Trackea 3 placements: Main Slider (MS), Landing, Containers.
Compara performance vs targets diarios y vs campañas históricas.

## Arquitectura
```
Verdi Flow (n8n, trigger 11:00 UTC = 8am ART)
    └── BQ query → base64 JSON → PUT GitHub API → docs/data.json

Apps Script (Code.gs)
    └── Fetch docs/data.json (base64) + docs/historical.json (plain)
    └── Merge historical → serve index.html
```

## Archivos clave
| Archivo | Rol |
|---------|-----|
| `apps_script/index.html` | Dashboard completo (~930 líneas, Chart.js) |
| `apps_script/Code.gs` | Fetches ambos JSON, sirve el web app |
| `docs/data.json` | Sobrescrito por Verdi cada mañana |
| `docs/historical.json` | Campañas cerradas — NUNCA tocado por Verdi |
| `verdi_flow.json` | Config n8n — reimportar en Verdi al hacer cambios |
| `process_bq.py` | Script manual para cerrar campaña → agregar a historical.json |

## Reglas importantes

**1. Los targets van hardcodeados en el SQL de Verdi Flow**
Verdi sobrescribe data.json completo cada día. Los targets vienen de Sheets (no de BQ),
así que deben estar embebidos como arrays literales en el CONCAT del SQL.
Si quedan como `null`, cada refresh los borra.

**2. historical.json es un archivo separado**
Nunca mover historical de vuelta a data.json. Verdi lo pisaría.
Code.gs los mergea en memoria: `data.historical = getHistoricalData()`.

**3. No usar nodo Code en Verdi**
`n8n-nodes-base.code` no está instalado en la instancia de MeLi.
Toda lógica va en BQ SQL o en Apps Script.

**4. Bash tool no funciona en este entorno**
Dar comandos PowerShell para que la usuaria los corra manualmente.

## Cómo actualizar para nueva campaña
Cambiar en `verdi_flow.json` (nodo "BQ Campaign Tracker"):

1. Fechas en todas las queries: `BETWEEN 'YYYY-MM-DD' AND 'YYYY-MM-DD'`
2. Filtro MS: `M.CAMPAIGN_NAME LIKE '%NUEVACAMPAÑA%'`
3. Filtro Landing: `landing_name IN ('landing-a', 'landing-b')`
4. Filtro Container: `CONTAINER_NAME LIKE '%MKP T2 NUEVA CAMPAÑA%'`
5. Targets en el CONCAT: reemplazar arrays de `targets.dates`, `targets.landing`, `targets.container`
6. Nombre campaña en el CONCAT: `{"name":"NOMBRE","start":"...","end":"..."}`

Reimportar el flow en Verdi. Al cerrar campaña: correr `process_bq.py` (ajustar nombre) → pushear historical.json.

## Bucket classification (Main Slider)
`getBucket(lineItem)` en index.html:
- `tachado` / `celebrity` → **PRINCIPAL**
- `alta` → **HIGH**
- `media` → **MID**

## Targets en el dashboard
- KPI cards: borde verde/naranja/rojo + `▲/▼ X% vs target`
- Charts: línea gris punteada
- Inline comparison (cuando hay histórica seleccionada): `Actual | Target | Δ Tgt | Histórico | Δ Hist`
  - Landing: Sessions tiene target
  - Container: Sessions, NMV, CVR tienen target
  - MS CTR: cuando se cargue el array en `targets.ms.ctr`

## Campaña actual: DOUBLE DATES
- Fechas: 2026-04-20 → 2026-05-05
- MS filter: `LIKE '%DOUBLEDATES%'`
- Landings: `'ofertas futboleras'`, `'5-5-descuentos-parcial'`
- Container filter: `LIKE '%MKP T2 DOUBLE DATES 5 5 ABRIL 2026%'`
- Histórica disponible: "DOUBLE DATES 04/04" (2026-03-23 → 2026-04-07)

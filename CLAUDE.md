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
| `apps_script/index.html` | Dashboard completo (Chart.js) — incluye tab Search Terms con gráfico top 10 + tabla mejorada |
| `apps_script/Code.gs` | Fetches los JSON, sirve el web app |
| `docs/data.json` | Sobrescrito por Verdi cada mañana (MS, containers, landing, total_site) |
| `docs/calidad.json` | Calidad de oferta — generado por `verdi_calidad.json` |
| `docs/oferta.json` | Métricas de oferta a nivel pattern — generado por `verdi_calidad.json` |
| `docs/search_terms.json` | Top 500 términos de búsqueda — generado por `verdi_search_terms.json` |
| `docs/historical.json` | Campañas cerradas — NUNCA tocado por Verdi |
| `verdi_flow.json` | Flow principal n8n (MS, containers, landing, total_site) |
| `verdi_calidad.json` | Flow calidad de oferta — usa patrón LIKE sobre CONTAINER_NAME |
| `verdi_search_terms.json` | Flow search terms — tabla `DM_SEARCHTERMS`, latencia ~12-14hs |
| `verdi_targets_t1.json` | Flow targets T1 |
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

## Campaña actual: HOT SALE 2026
- Fechas: 2026-05-11 → 2026-05-18
- Site: MLA · Mobile · T1
- MS filter: `LIKE '%HOTSALE%'` (sin espacio)
- Landings: `'hot-sale'`, `'hot-sale-parcial'`, `'hot-sale-tab'`
- Container filter: `LIKE '%MKP T1 HOTSALE MAYO 2026%'` ⚠️ SIN espacio entre HOT y SALE
- Calidad filter: mismo patrón `'%MKP T1 HOTSALE MAYO 2026%'` en CTE DATES de `verdi_calidad.json`
- NASP = cantidad de containers únicos activos (target día 1: 48)
- Targets T1 embebidos en SQL del flow, NO en Google Sheets

## Latencia de tablas — Hot Sale
| Tabla | Disponibilidad |
|-------|---------------|
| `DM_CONTAINERS_DEALS_ATTRIBUTION` | Mismo día, parcial desde temprano |
| `MKP_SM_CONTAINERS_ITEMS_EXHIBIDOS` | 23hs GMT (20hs ART) — no correr calidad antes |
| `LK_BENEFITS_RIU_CLUSTER_RESULTS` | Con 2 días de delay (usa `DATE_SUB(..., INTERVAL 2 DAY)`) |
| `BENEFITS_OFFERS` | ~20hs ART — % con Oferta y DTO Ponderado = 0 hasta entonces |
| `DM_SEARCHTERMS` | ~12-14hs ART — search_terms null en las primeras horas del día |
| `BT_MKP_SESSIONS` | Parcial durante el día |

## Tab Search Terms — mejoras aplicadas (2026-05-11)
- Gráfico de barras horizontal top 10 por búsquedas (amarillo Meli, mayor a menor)
- Valor en K + CVR al lado de cada barra
- Tabla: mini barra de progreso en columna búsquedas, CVR con color semántico (verde ≥4%, amarillo ≥2%), badge amarillo para top 10, color de término unificado con el resto
- Chart se destruye y re-crea al cambiar filtro de fecha (`_stBarChart` global)

## Campaña anterior: DOUBLE DATES
- Fechas: 2026-04-20 → 2026-05-05
- MS filter: `LIKE '%DOUBLEDATES%'`
- Landings: `'ofertas futboleras'`, `'5-5-descuentos-parcial'`
- Container filter: `LIKE '%MKP T2 DOUBLE DATES 5 5 ABRIL 2026%'`

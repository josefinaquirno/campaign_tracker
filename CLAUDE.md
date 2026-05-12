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

Campañas dentro del drill-down por bucket: ordenadas por **CTR descendente**.

## Targets en el dashboard
- KPI cards: borde verde/naranja/rojo + `▲/▼ X% vs target`
- Charts: línea gris punteada
- Inline comparison (cuando hay histórica seleccionada): `Actual | Target | Δ Tgt | Histórico | Δ Hist`
  - Landing: Sessions tiene target
  - Container: Sessions, NMV, CVR tienen target
  - MS CTR: cuando se cargue el array en `targets.ms.ctr`

## Métricas — fórmulas correctas (¡importante!)

**NASP** = `NMV / NSI` (no NMV/Orders). Aplicado en:
- Containers tab: `tot.nasp = tot.nsi > 0 ? tot.nmv / tot.nsi : 0`
- Summary `cont_asp`: `sum(cont_nmv) / sum(cont_nsi)` para el período (NO opAvg de ratios diarios)

**NMV Share % vs Site** = `sum(containerNMV) / sum(siteNMV)` para el período.
- Summary usa `opSum` en ambos — NO `opAvg(cont_nmvpct)`.

**Regla general**: para métricas acumuladas (share, NASP), siempre dividir sumas — nunca promediar ratios diarios. `opAvg` da resultados diferentes y es incorrecto para acumulados.

## Filtros en todas las tabs (MS, Landing, Landing Attr Acida, Containers)

**Filtro TakeOver**: helper `_toFilterHtml()`, clase `.to-filter-btn`, sincronizado globalmente. Posición: dentro de los toggles de cada tab.

**Filtro de fechas**: helper `_datePillsHtml(allDates, current, setterName)`. Clase `op-fbtn` (igual que Summary), formato `5/11`, active púrpura `#9c6ef0`. Posición: debajo del section-label, encima de los KPIs.
- MS → `MS_DATE_FILTER` / `setMSDateFilter` / `#ms-date-filter`
- Landing → `LDG_DATE_FILTER` / `setLdgDateFilter` / `#ldg-date-filter`
- Landing Attr Acida → `LDGO_DATE_FILTER` / `setLdgoDateFilter` / `#ldgo-date-filter`
- Containers → `CNT_DATE_FILTER` / `setCntDateFilter` / `#cnt-date-filter`

El filtro de fecha en **MS** requiere derivar `dateFiltered` para aplicar a KPIs, segmentación y tabla (no solo al chart). MS usa `r.fecha` (no `r.date`).

## Tabla Containers — fila de totales
`<tfoot>` en fondo `#1a1a2e` / texto `#FFE600`. CVR y NASP calculados sobre totales acumulados (no promediados por fila).

## Comparison chart timing
`renderInlineComparison(placement, containerId)` usa double `requestAnimationFrame` + `setTimeout(100)` para evitar canvas 0×0.
Placements activos: `'ms'`, `'landing'`, `'landing-orig'`, `'container'`.

## verdi_opt_landing.json — query
3 CTEs: `splinter` (DM_SPLINTER_COMPONENT) + `eshop_cpg` (DM_ESHOP_LANDING_ATTRIBUTION, Carrefour/Full Súper) + `combined` (LEFT JOIN ON LOWER(button_name) LIKE '%cpg%').

## Git en Windows — problema de encoding
Archivos pueden aparecer como modificados en Windows por diferencias de encoding (BOM/CRLF). Solución: `git restore .` antes de `git pull --rebase`.

## Campaña actual: HOT SALE 2026
- Fechas: 2026-05-11 → 2026-05-18
- Site: MLA · Mobile · T1
- MS filter: `LIKE '%HOTSALE%'` (sin espacio)
- Landings: `'hot-sale'`, `'hot-sale-parcial'`, `'hot-sale-tab'`
- Container filter: `LIKE '%MKP T1 HOTSALE MAYO 2026%'` ⚠️ SIN espacio entre HOT y SALE
- Calidad filter: mismo patrón `'%MKP T1 HOTSALE MAYO 2026%'` en CTE DATES de `verdi_calidad.json`
- Targets activos: `docs/targets_t1.json` (referenciado via `campaigns.json` → `targets_file`)
- NASP scalar en `D.targets.nasp` = 121.4 (no es array, es escalar global)
- `to_dates` en targets_t1.json: fechas con TakeOver (para filtro Con/Sin TO)
- Targets T1 en archivo JSON separado (`targets_t1.json`), NO embebidos en SQL

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

# Campaign Tracker — MLA

Seguimiento diario de campañas comerciales activas: Main Slider, Landing y Containers.

## Arquitectura

```
BigQuery → Verdi Flow (diario ~8am ART) → GitHub (docs/data.json) → Apps Script Web App → Browser
```

## Setup inicial (una sola vez)

### 1. Crear el repo en GitHub
Crear un repo público: `josefinaquirno/campaign_tracker`
(O el nombre que prefieras — actualizar las URLs en `verdi_flow.json` y `Code.gs`)

### 2. Commitear los archivos al repo
```
campaign_tracker/
├── docs/data.json     ← subir este archivo inicial al repo
└── (resto de archivos son locales)
```

### 3. Crear el Apps Script
1. Ir a https://script.google.com → Nuevo proyecto
2. Reemplazar el contenido de `Code.gs` con el archivo `apps_script/Code.gs`
3. Agregar un nuevo archivo HTML: `Archivo > Nuevo > HTML` → nombre: `index`
4. Pegar el contenido de `apps_script/index.html`
5. Deployar como web app:
   - `Implementar > Nueva implementación`
   - Tipo: **Aplicación web**
   - Ejecutar como: **Yo (mi cuenta)**
   - Quién tiene acceso: **Cualquier usuario** (o restringir a MeLi si preferís)
6. Copiar la URL del web app → compartir con el equipo

### 4. Configurar Verdi Flow
1. Abrir Verdi Flow → Importar flujo → pegar contenido de `verdi_flow.json`
2. Reemplazar `TU_GITHUB_TOKEN_ACA` con tu GitHub Personal Access Token
   (el token necesita permiso `repo` o `contents:write`)
3. Activar el flujo → se ejecutará automáticamente a las 8am ART (11:00 UTC)

---

## Iniciar nueva campaña

Al arrancar una campaña nueva, solo hay que cambiar **4 valores** en el nodo BQ de Verdi Flow:

| Campo | Ejemplo Double Dates | Qué cambiar |
|-------|---------------------|-------------|
| Fechas | `'2026-04-20'` / `'2026-05-05'` | Start y end de la nueva campaña |
| MS filter | `'%DOUBLEDATES%'` | Patrón del campaign name en ADS |
| Landing names | `'ofertas futboleras', '5-5-descuentos-parcial'` | Nombres exactos de landings |
| Container filter | `'%MKP T2 DOUBLE DATES 5 5 ABRIL 2026%'` | Patrón del container name |

También actualizar el campo `"campaign"` en el JSON que genera la query (nombre, start, end).

Y en `docs/data.json` actualizar los `targets` cuando tengas los números.

---

## Agregar campaña al histórico

Al cerrar una campaña, agregar una entrada al array `historical` en `data.json`:

```json
{
  "name": "DOUBLE DATES",
  "start": "2026-04-20",
  "end": "2026-05-05",
  "ms_clicks":    0,
  "ms_prints":    0,
  "ms_ctr":       0.0,
  "ldg_sessions": 0,
  "ldg_nmv":      0,
  "ldg_orders":   0,
  "ldg_buyers":   0,
  "ldg_cvr":      0.0,
  "ldg_nasp":     0.0,
  "cnt_sessions": 0,
  "cnt_nmv":      0,
  "cnt_orders":   0,
  "cnt_buyers":   0,
  "cnt_cvr":      0.0,
  "cnt_nasp":     0.0
}
```

Estos valores los sacás del dashboard al cierre de la campaña.
Al commitear el archivo al repo, el panel de Comparación lo mostrará disponible.

---

## Estructura de archivos

```
campaign_tracker/
├── verdi_flow.json          ← Importar en Verdi Flow. Actualizar por campaña.
├── queries/                 ← Queries SQL de referencia (con {{placeholders}})
│   ├── ms.sql
│   ├── landing.sql
│   ├── container.sql
│   ├── total_containers.sql
│   └── total_site.sql
├── apps_script/
│   ├── Code.gs              ← Copiar al proyecto Apps Script
│   └── index.html           ← Copiar al proyecto Apps Script (archivo HTML "index")
├── docs/
│   └── data.json            ← Datos actuales. Verdi Flow lo actualiza diariamente.
└── README.md
```

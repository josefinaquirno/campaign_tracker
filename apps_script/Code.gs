// ============================================================
// Campaign Tracker — Apps Script
// Fetches data.json + historical.json from GitHub and serves the dashboard.
// Deploy as: "Execute as: Me" + "Who has access: Anyone"
// ============================================================

var GITHUB_RAW_URL            = 'https://raw.githubusercontent.com/josefinaquirno/campaign_tracker/main/docs/data.json';
var GITHUB_RAW_URL_HISTORICAL = 'https://raw.githubusercontent.com/josefinaquirno/campaign_tracker/main/docs/historical.json';
var GITHUB_RAW_URL_CALIDAD    = 'https://raw.githubusercontent.com/josefinaquirno/campaign_tracker/main/docs/calidad.json';
var GITHUB_RAW_URL_OFERTA     = 'https://raw.githubusercontent.com/josefinaquirno/campaign_tracker/main/docs/oferta.json';

function doGet() {
  return HtmlService
    .createHtmlOutputFromFile('index')
    .setTitle('Campaign Tracker — MLA')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getJsonData() {
  try {
    var response = UrlFetchApp.fetch(GITHUB_RAW_URL + '?v=' + Date.now());
    var raw = response.getContentText();
    var decoded = Utilities.newBlob(Utilities.base64Decode(JSON.parse(raw))).getDataAsString();
    var data = JSON.parse(decoded);
    data.historical = getHistoricalData();
    return data;
  } catch (e) {
    // Fallback: try parsing as plain JSON (for local dev / data.json not base64-encoded)
    try {
      var response2 = UrlFetchApp.fetch(GITHUB_RAW_URL + '?v=' + Date.now());
      var data2 = JSON.parse(response2.getContentText());
      data2.historical = getHistoricalData();
      return data2;
    } catch (e2) {
      return {
        campaign: { name: '—', start: '—', end: '—' },
        ms: [], landing: [], container: [],
        total_containers: [], total_site: [], historical: [],
        targets: { ms: {}, landing: {}, container: {} },
        refreshed_at: 'error: ' + e.message
      };
    }
  }
}

function getCalidadData() {
  function decodeB64Json(raw) {
    try { return JSON.parse(Utilities.newBlob(Utilities.base64Decode(JSON.parse(raw))).getDataAsString()); }
    catch(e) { return JSON.parse(raw); }
  }

  try {
    // Intentar primero el formato combinado (calidad.json con oferta + containers)
    var calidadRaw = UrlFetchApp.fetch(GITHUB_RAW_URL_CALIDAD + '?v=' + Date.now()).getContentText();
    var calidad = decodeB64Json(calidadRaw);

    // Si calidad.json tiene oferta, es el formato combinado (viejo o transición)
    if (calidad.oferta && calidad.oferta.length > 0) {
      return calidad;
    }

    // Si no, intentar el formato split: oferta.json separado
    try {
      var ofertaRaw = UrlFetchApp.fetch(GITHUB_RAW_URL_OFERTA + '?v=' + Date.now()).getContentText();
      var oferta = decodeB64Json(ofertaRaw);
      return {
        oferta:       oferta.oferta      || [],
        containers:   calidad.containers || [],
        refreshed_at: calidad.refreshed_at || oferta.refreshed_at || ''
      };
    } catch(e2) {
      return calidad;
    }
  } catch (e) {
    return { oferta: [], containers: [], refreshed_at: '' };
  }
}

function getHistoricalData() {
  try {
    var response = UrlFetchApp.fetch(GITHUB_RAW_URL_HISTORICAL + '?v=' + Date.now());
    return JSON.parse(response.getContentText());
  } catch (e) {
    return [];
  }
}

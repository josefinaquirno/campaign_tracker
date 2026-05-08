// ============================================================
// Campaign Tracker — Apps Script
// Fetches campaign registry + data files from GitHub and serves the dashboard.
// Deploy as: "Execute as: Me" + "Who has access: Anyone"
// ============================================================

var GITHUB_RAW_BASE           = 'https://raw.githubusercontent.com/josefinaquirno/campaign_tracker/main/docs/';
var GITHUB_RAW_URL_HISTORICAL = GITHUB_RAW_BASE + 'historical.json';

function doGet() {
  return HtmlService
    .createHtmlOutputFromFile('index')
    .setTitle('Campaign Tracker — MLA')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function getCampaigns() {
  try {
    var raw = UrlFetchApp.fetch(GITHUB_RAW_BASE + 'campaigns.json?v=' + Date.now()).getContentText();
    return JSON.parse(raw);
  } catch(e) { return []; }
}

function getJsonData(dataFile, targetsFile) {
  function decodeB64Json(raw) {
    try { return JSON.parse(Utilities.newBlob(Utilities.base64Decode(JSON.parse(raw))).getDataAsString()); }
    catch(e) { return JSON.parse(raw); }
  }
  try {
    var url = GITHUB_RAW_BASE + (dataFile || 'data.json') + '?v=' + Date.now();
    var data = decodeB64Json(UrlFetchApp.fetch(url).getContentText());
    data.historical = getHistoricalData();
    // Merge dynamic targets (targets.json overrides embedded targets in data.json)
    try {
      var tf = targetsFile || 'targets.json';
      var tRaw = UrlFetchApp.fetch(GITHUB_RAW_BASE + tf + '?v=' + Date.now()).getContentText();
      var tgt = decodeB64Json(tRaw);
      if (tgt && tgt.dates && tgt.dates.length > 0) { data.targets = tgt; }
    } catch(et) { /* keep embedded targets if targets.json unavailable */ }
    return data;
  } catch (e) {
    return {
      campaign: { name: '—', start: '—', end: '—' },
      ms: [], landing: [], container: [],
      total_containers: [], total_site: [], historical: [],
      targets: { ms: {}, landing: {}, container: {} },
      refreshed_at: 'error: ' + e.message
    };
  }
}

function getCalidadData(calidadFile, ofertaFile) {
  function decodeB64Json(raw) {
    try { return JSON.parse(Utilities.newBlob(Utilities.base64Decode(JSON.parse(raw))).getDataAsString()); }
    catch(e) { return JSON.parse(raw); }
  }

  try {
    var calidadUrl = GITHUB_RAW_BASE + (calidadFile || 'calidad.json') + '?v=' + Date.now();
    var ofertaUrl  = GITHUB_RAW_BASE + (ofertaFile  || 'oferta.json')  + '?v=' + Date.now();

    var calidadRaw = UrlFetchApp.fetch(calidadUrl).getContentText();
    var calidad = decodeB64Json(calidadRaw);

    if (calidad.oferta && calidad.oferta.length > 0) {
      return calidad;
    }

    try {
      var ofertaRaw = UrlFetchApp.fetch(ofertaUrl).getContentText();
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

function getOptLandingData() {
  function decodeB64Json(raw) {
    try { return JSON.parse(Utilities.newBlob(Utilities.base64Decode(JSON.parse(raw))).getDataAsString()); }
    catch(e) { return JSON.parse(raw); }
  }
  try {
    var raw = UrlFetchApp.fetch(GITHUB_RAW_BASE + 'opt_landing.json?v=' + Date.now()).getContentText();
    return decodeB64Json(raw);
  } catch(e) {
    return { opt_landing: [], refreshed_at: '' };
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

// ============================================================
// Campaign Tracker — Apps Script
// Fetches data.json from GitHub and serves the HTML dashboard.
// Deploy as: "Execute as: Me" + "Who has access: Anyone"
// ============================================================

var GITHUB_RAW_URL = 'https://raw.githubusercontent.com/josefinaquirno/campaign_tracker/main/data.json';

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
    return JSON.parse(decoded);
  } catch (e) {
    // Fallback: try parsing as plain JSON (for local dev / data.json not base64-encoded)
    try {
      var response2 = UrlFetchApp.fetch(GITHUB_RAW_URL + '?v=' + Date.now());
      return JSON.parse(response2.getContentText());
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

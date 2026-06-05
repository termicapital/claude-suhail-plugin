/**
 * AI Workshop — Registration backend (Google Apps Script)
 * Receives form submissions from registration/index.html and appends
 * one row per registrant to the bound Google Sheet.
 *
 * Setup: see registration/README.md (≈2 minutes).
 */

var SHEET_NAME = 'Registrations';
var HEADERS = ['Timestamp', 'Name', 'Email', 'Company / Team', 'Role',
               'AI experience', 'Sessions', 'Goal', 'Source'];

function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000); // avoid race conditions on concurrent signups
  try {
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName(SHEET_NAME) || ss.insertSheet(SHEET_NAME);

    // Write header row once and freeze it.
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }

    var data = JSON.parse(e.postData.contents);
    var sessions = Array.isArray(data.sessions) ? data.sessions.join(', ') : (data.sessions || '');

    sheet.appendRow([
      new Date(),
      data.name || '',
      data.email || '',
      data.company || '',
      data.role || '',
      data.level || '',
      sessions,
      data.goal || '',
      data.page || ''
    ]);

    return json({ result: 'success' });
  } catch (err) {
    return json({ result: 'error', error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

// Lets you open the Web App URL in a browser to confirm it's live.
function doGet() {
  return json({ result: 'ok', message: 'AI Workshop registration endpoint is live.' });
}

function json(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

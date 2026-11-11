// Optional English game name (README step 6): edits the Vita's app.db (ur0:shell/db/app.db, the home screen
// takes the name from there) or Vita3K's param.sfo. Same changes as tools/rename_title.py. No page code here,
// so it runs the same in the browser and in Node (for testing).

const TITLE_ID = 'PCSG00278';
const JA = '真・ガンダム無双';
export const EN = 'Shin Gundam Musou';
const SFO_KEYS = ['TITLE', 'TITLE_00', 'STITLE', 'STITLE_00'];   // _00 = shown when the system language is Japanese
const SQLITE = 'SQLite format 3\0';
const SQLJS = 'https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.10.3/';

export class TitleError extends Error {}

const startsWith = (b, s) => [...s].every((c, i) => b[i] === c.charCodeAt(0));

/** What kind of file this is: 'appdb', 'sfo' or null. */
export function titleFileKind(bytes) {
  if (startsWith(bytes, SQLITE)) return 'appdb';
  if (startsWith(bytes, '\0PSF')) return 'sfo';
  return null;
}

/** param.sfo: replace the title strings in place (each sits in a fixed max-length slot). */
export function renameSfo(bytes) {
  const d = new Uint8Array(bytes);
  const v = new DataView(d.buffer);
  const keyTab = v.getUint32(8, true), dataTab = v.getUint32(12, true), n = v.getUint32(16, true);
  const value = new TextEncoder().encode(EN + '\0');
  let done = 0, changed = false;
  for (let i = 0; i < n; i++) {
    const e = 20 + 16 * i;
    const ko = v.getUint16(e, true), fmt = v.getUint16(e + 2, true);
    const max = v.getUint32(e + 8, true), off = dataTab + v.getUint32(e + 12, true);
    let end = keyTab + ko;
    while (d[end]) end++;
    const key = new TextDecoder().decode(d.subarray(keyTab + ko, end));
    if (!SFO_KEYS.includes(key)) continue;
    if (fmt !== 0x204 || value.length > max) throw new TitleError(`param.sfo: unexpected ${key} entry`);
    const slot = new Uint8Array(max);
    slot.set(value);
    changed ||= slot.some((b, k) => b !== d[off + k]);
    d.set(slot, off);
    v.setUint32(e + 4, value.length, true);
    done++;
  }
  if (!done) throw new TitleError('This param.sfo has no title entries.');
  return { bytes: d, changed };
}

let sqlPromise = null;

/** Load sql.js (SQLite as WebAssembly) from cdnjs, only when an app.db is chosen. */
export function loadSqlJs() {
  sqlPromise ??= new Promise((resolve, reject) => {
    const s = document.createElement('script');
    s.src = SQLJS + 'sql-wasm.js';
    s.crossOrigin = 'anonymous';
    s.onload = () => window.initSqlJs({ locateFile: (f) => SQLJS + f }).then(resolve, reject);
    s.onerror = () => reject(new TitleError('Could not load the database library. Check your connection and try again.'));
    document.head.append(s);
  }).catch((e) => { sqlPromise = null; throw e; });
  return sqlPromise;
}

/** app.db: set the 5 name entries of PCSG00278 that still hold the Japanese name. */
export function renameAppDb(SQL, bytes) {
  let db;
  try {
    db = new SQL.Database(bytes);
    const has = db.exec("SELECT count(*) FROM sqlite_master WHERE name IN ('tbl_appinfo', 'tbl_appinfo_icon')");
    if (has[0].values[0][0] !== 2) throw new TitleError('This database is not the Vita\'s app.db.');
    const found = db.exec('SELECT count(*) FROM tbl_appinfo WHERE titleId = ?', [TITLE_ID])[0].values[0][0];
    if (!found) throw new TitleError('Shin Gundam Musou (PCSG00278) is not in this app.db.');
    db.run('BEGIN');
    db.run('UPDATE tbl_appinfo SET val = ? WHERE titleId = ? AND val = ?', [EN, TITLE_ID, JA]);
    let n = db.getRowsModified();
    db.run('UPDATE tbl_appinfo_icon SET title = ? WHERE titleId = ? AND title = ?', [EN, TITLE_ID, JA]);
    n += db.getRowsModified();
    db.run('COMMIT');
    const ok = db.exec('PRAGMA integrity_check')[0].values[0][0];
    if (ok !== 'ok') throw new TitleError(`Database check failed: ${ok}`);
    return { bytes: n ? db.export() : bytes, changed: n > 0, entries: n };
  } catch (e) {
    if (e instanceof TitleError) throw e;
    throw new TitleError(`This file could not be read as app.db (${e.message ?? e}).`);
  } finally {
    db?.close();
  }
}

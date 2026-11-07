// Page code for the web patcher: file picking, status, progress and saving. Logic lives in core.js.
import { identify, patchFile, PatchError } from './core.js';
import { makeZip, crc32 } from './zip.js';

const $ = (s) => document.querySelector(s);
const SLOTS = ['eboot', 'LINKDATA.B', 'LINKDATA.C'];
const state = { manifest: null, slots: {}, busy: false, done: false };
const canPickFolder = 'showDirectoryPicker' in window;

const mb = (n) => (n < 10485760 ? (n / 1048576).toFixed(1) : Math.round(n / 1048576)) + ' MB';

async function init() {
  try {
    const r = await fetch('patcher/patches/manifest.json', { cache: 'no-cache' });
    if (!r.ok) throw new Error(r.status);
    state.manifest = await r.json();
    $('#patch-version').textContent = 'v' + state.manifest.version;
  } catch {
    showError('Could not load the patch files. Reload the page to try again.');
    return;
  }
  for (const slot of SLOTS) document.querySelector(`[data-slot="${slot}"]`).addEventListener('click', () => $('#files').click());
  $('#files').addEventListener('change', (e) => addFiles(e.target.files));
  const drop = $('#drop');
  drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', (e) => { if (!drop.contains(e.relatedTarget)) drop.classList.remove('over'); });
  drop.addEventListener('drop', (e) => { e.preventDefault(); drop.classList.remove('over'); addFiles(e.dataTransfer.files); });
  $('#patch').addEventListener('click', run);
  $('#zip').addEventListener('change', render);
  if (!canPickFolder) {                          // Firefox / Safari: zip only
    $('#zip').checked = true;
    $('#zip').disabled = true;
  }
  render();
}

async function addFiles(list) {
  if (state.busy) return;
  hideError();
  state.done = false;
  for (const file of list) {
    const row = { file, checking: true };
    const guess = /linkdata\.b$/i.test(file.name) ? 'LINKDATA.B' : /linkdata\.c$/i.test(file.name) ? 'LINKDATA.C'
      : /\.(elf|bin)$/i.test(file.name) ? 'eboot' : null;
    if (guess) { state.slots[guess] = row; render(); }
    const id = await identify(file, state.manifest);
    if (guess && state.slots[guess] === row) delete state.slots[guess];
    if (id.kind && SLOTS.includes(id.kind)) {
      // don't replace a good file with a bad one picked later
      if (id.ok || !state.slots[id.kind]?.ok) state.slots[id.kind] = { file, ...id };
    } else {
      showError(`${file.name}: ${id.message}`);
    }
    render();
  }
  $('#files').value = '';
}

function render() {
  for (const slot of SLOTS) {
    const el = document.querySelector(`[data-slot="${slot}"]`);
    const s = state.slots[slot];
    el.classList.toggle('ok', !!s?.ok);
    el.classList.toggle('bad', !!s && !s.checking && !s.ok);
    el.disabled = state.busy;
    const small = el.querySelector('small'), meta = el.querySelector('.meta');
    if (!s) { small.textContent = ''; meta.textContent = 'Choose'; }
    else if (s.checking) { small.textContent = 'Checking…'; meta.textContent = mb(s.file.size); }
    else if (s.ok) {
      small.textContent = s.entry.gameVersion ? `Game version ${s.entry.gameVersion}` : 'Decrypted original';
      meta.textContent = mb(s.file.size);
    } else { small.textContent = s.message; meta.textContent = 'Replace'; }
  }
  const zip = $('#zip').checked;
  $('#zip-note').textContent = !canPickFolder ? 'Saving to a folder needs Chrome or Edge'
    : zip ? 'On: one ~1 GB zip to unzip yourself' : 'Off: save straight into a folder you pick';
  $('#zip').disabled = state.busy || !canPickFolder;
  $('#unzip-hint').hidden = !zip;

  const ready = SLOTS.every((k) => state.slots[k]?.ok);
  $('#patch').disabled = !ready || state.busy;
  if (!state.busy && !state.done) {
    const n = SLOTS.filter((k) => state.slots[k]?.ok).length;
    setStatus(ready ? 'Ready to patch' : n ? `${n} of 3 files ready` : 'Choose your files',
      ready ? (zip ? 'Creates a zip with the rePatch folder' : 'You\'ll pick where to save it')
        : 'Drop them here or tap a row above');
  }
}

function setStatus(title, sub) { $('#status').textContent = title; $('#status-sub').textContent = sub; }
function setBar(f) { $('#bar').hidden = f == null; $('#bar i').style.width = `${Math.round((f ?? 0) * 100)}%`; }

async function run() {
  hideError();
  const mode = $('#zip').checked ? 'zip' : 'folder';
  const jobs = SLOTS.map((k) => state.slots[k]);
  const total = jobs.reduce((n, j) => n + j.entry.target.size, 0);
  let doneBefore = 0;
  state.busy = true; state.done = false;
  $('#done').hidden = true;
  render();

  try {
    let root = null;
    if (mode === 'folder') {
      setStatus('Pick a folder', 'The rePatch folder is created inside it');
      root = await window.showDirectoryPicker({ id: 'sgm-repatch', mode: 'readwrite' });
    }
    setBar(0);
    const zipEntries = [];
    for (const job of jobs) {
      const { entry } = job;
      const patch = new Uint8Array(await (await fetch('patcher/patches/' + entry.patch)).arrayBuffer());
      const sink = mode === 'folder' ? await folderSink(root, entry.target.path) : zipSink(entry.target.path, zipEntries);
      await patchFile(job.file, entry, patch, sink, (n) => {
        const f = (doneBefore + n) / total;
        setBar(f);
        setStatus(`Patching… ${Math.floor(f * 100)}%`, entry.source.name);
      });
      doneBefore += entry.target.size;
    }
    if (mode === 'zip') {
      setStatus('Preparing the zip…', 'Almost done');
      const blob = makeZip(zipEntries);
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `rePatch-PCSG00278-english-v${state.manifest.version}.zip`;
      document.body.append(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 60_000);
      setStatus('Done', 'Your browser is saving the zip');
    } else {
      setStatus('Done', `Saved into "${root.name}"`);
    }
    setBar(1);
    state.done = true;
    $('#done').hidden = false;
  } catch (err) {
    setBar(null);
    if (err?.name === 'AbortError') setStatus('Cancelled', 'Nothing was saved');
    else {
      setStatus('Patching failed', 'See the message above');
      showError(err instanceof PatchError ? err.message : `Something went wrong: ${err?.message ?? err}`);
      if (!(err instanceof PatchError)) console.error(err);
    }
    state.done = true;                           // keep this status until the files change
  } finally {
    state.busy = false;
    render();
  }
}

async function folderSink(root, path) {
  const parts = path.split('/');
  let dir = root;
  for (const p of parts.slice(0, -1)) dir = await dir.getDirectoryHandle(p, { create: true });
  const fh = await dir.getFileHandle(parts.at(-1), { create: true });
  const w = await fh.createWritable();
  return { write: (b) => w.write(b), close: () => w.close(), abort: () => w.abort().catch(() => {}) };
}

function zipSink(path, entries) {
  const e = { path, parts: [], size: 0, crc: 0 };
  return {
    write: async (b) => { e.parts.push(new Blob([b])); e.crc = crc32(e.crc, b); e.size += b.length; },
    close: async () => { entries.push(e); },
    abort: async () => {},
  };
}

function showError(msg) { $('#error').textContent = msg; $('#error-card').hidden = false; }
function hideError() { $('#error-card').hidden = true; }

init();

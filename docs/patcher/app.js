// Page code for the web patcher: file picking, status, progress and saving. Logic lives in core.js.
import { identify, patchFile, PatchError } from './core.js';
import { makeZip, crc32 } from './zip.js';

const $ = (s) => document.querySelector(s);
const SLOTS = ['eboot', 'LINKDATA.B', 'LINKDATA.C'];
const state = { manifest: null, slots: {}, busy: false };
const canPickFolder = 'showDirectoryPicker' in window;

const mb = (n) => (n / 1048576).toFixed(n < 10485760 ? 1 : 0) + ' MB';

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
  $('#pick').addEventListener('click', () => $('#files').click());
  $('#files').addEventListener('change', (e) => addFiles(e.target.files));
  const drop = $('#drop');
  drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('over'); });
  drop.addEventListener('dragleave', () => drop.classList.remove('over'));
  drop.addEventListener('drop', (e) => { e.preventDefault(); drop.classList.remove('over'); addFiles(e.dataTransfer.files); });
  $('#save-folder').addEventListener('click', () => run('folder'));
  $('#save-zip').addEventListener('click', () => run('zip'));
  if (!canPickFolder) {
    $('#save-folder').hidden = true;
    $('#folder-note').hidden = true;
  }
  render();
}

async function addFiles(list) {
  if (state.busy) return;
  hideError();
  for (const file of list) {
    const row = { file, checking: true };
    const guess = /\.(elf|bin)$/i.test(file.name) && !/linkdata/i.test(file.name) ? 'eboot'
      : /linkdata\.b$/i.test(file.name) ? 'LINKDATA.B' : /linkdata\.c$/i.test(file.name) ? 'LINKDATA.C' : null;
    if (guess) { state.slots[guess] = row; render(); }
    const id = await identify(file, state.manifest);
    if (id.kind && SLOTS.includes(id.kind)) {
      if (guess && guess !== id.kind && state.slots[guess] === row) delete state.slots[guess];
      // don't replace a good file with a bad one picked later
      if (id.ok || !state.slots[id.kind]?.ok || state.slots[id.kind] === row)
        state.slots[id.kind] = { file, ...id };
    } else {
      if (guess && state.slots[guess] === row) delete state.slots[guess];
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
    el.querySelector('.file').textContent = s ? `${s.file.name} · ${mb(s.file.size)}` : 'not chosen yet';
    el.querySelector('.msg').textContent = s ? (s.checking ? 'Checking…' : s.message) : '';
  }
  const ready = SLOTS.every((k) => state.slots[k]?.ok);
  for (const b of ['#save-folder', '#save-zip']) $(b).disabled = !ready || state.busy;
  $('#pick').disabled = state.busy;
}

async function run(mode) {
  hideError();
  state.busy = true;
  render();
  const jobs = SLOTS.map((k) => state.slots[k]);
  const total = jobs.reduce((n, j) => n + j.entry.target.size, 0);
  let doneBefore = 0;
  const progress = $('#progress'), label = $('#progress-label');
  $('#progress-box').hidden = false;
  $('#done').hidden = true;

  try {
    let root = null;
    if (mode === 'folder') {
      root = await window.showDirectoryPicker({ id: 'sgm-repatch', mode: 'readwrite' });
    }
    const zipEntries = [];
    for (const job of jobs) {
      const { entry } = job;
      label.textContent = `Patching ${entry.source.name}…`;
      const patch = new Uint8Array(await (await fetch('patcher/patches/' + entry.patch)).arrayBuffer());
      const sink = mode === 'folder' ? await folderSink(root, entry.target.path) : zipSink(entry.target.path, zipEntries);
      await patchFile(job.file, entry, patch, sink, (n) => {
        progress.value = (doneBefore + n) / total;
        label.textContent = `Patching ${entry.source.name}… ${Math.floor(((doneBefore + n) / total) * 100)}%`;
      });
      doneBefore += entry.target.size;
    }
    progress.value = 1;
    if (mode === 'zip') {
      label.textContent = 'Preparing the zip…';
      const blob = makeZip(zipEntries);
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `rePatch-PCSG00278-english-v${state.manifest.version}.zip`;
      document.body.append(a);
      a.click();
      a.remove();
      setTimeout(() => URL.revokeObjectURL(a.href), 60_000);
      label.textContent = 'Done. Your browser is saving the zip.';
    } else {
      label.textContent = `Done. Saved into the folder "${root.name}".`;
    }
    $('#done').hidden = false;
  } catch (err) {
    if (err?.name === 'AbortError') { label.textContent = 'Cancelled.'; }
    else {
      label.textContent = 'Failed.';
      showError(err instanceof PatchError ? err.message : `Something went wrong: ${err?.message ?? err}`);
      if (!(err instanceof PatchError)) console.error(err);
    }
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

function showError(msg) { const el = $('#error'); el.textContent = msg; el.hidden = false; }
function hideError() { $('#error').hidden = true; }

init();

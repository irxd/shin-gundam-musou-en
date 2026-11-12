// Patcher logic without any page code, so it runs the same in the browser and in Node (for testing).
// Files are Blob/File objects; the patches and manifest are loaded through `loadPatch(name)`.

import { applyPatch, PatchError } from './vcdiff.js';

const ELF = [0x7f, 0x45, 0x4c, 0x46];          // decrypted eboot (FAGDec "DECRYPT (ELF)")
const SELF = [0x53, 0x43, 0x45, 0x00];         // "SCE\0": eboot.bin as a SELF (encrypted, or not converted to ELF)
const LINKDATA = [0xf9, 0x7d, 0x07, 0x00];     // decrypted LINKDATA archive
const HASH_LIMIT = 64 << 20;                   // SHA-1 check for files up to 64 MB (eboot, LINKDATA.B)

export { PatchError };

const startsWith = (head, magic) => magic.every((b, i) => head[i] === b);

export async function sha1(blob) {
  const d = await crypto.subtle.digest('SHA-1', await blob.arrayBuffer());
  return [...new Uint8Array(d)].map((b) => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Work out what a file is. Returns { kind: 'eboot' | 'LINKDATA.B' | 'LINKDATA.C' | 'DLC' | null, entry, ok, message }.
 * `entry` is the manifest entry the file is the source for; ok=false means it can't be used (message says why).
 */
export async function identify(file, manifest) {
  const head = new Uint8Array(await file.slice(0, 16).arrayBuffer());
  const files = manifest.files;
  const allEboots = files.filter((f) => f.gameVersion);
  const ebootEntries = allEboots.filter((f) => !f.dlcEboot);   // the DLC variant is picked when patching

  if (startsWith(head, SELF))
    return { kind: 'eboot', ok: false, message: 'This eboot.bin is encrypted (or already patched). Decrypt the ' +
      'original with FAGDec using START DECRYPT (ELF) and choose the eboot.bin.elf it writes.' };

  if (startsWith(head, ELF)) {
    if (file.size > HASH_LIMIT) return { kind: null, ok: false, message: 'Unknown ELF file (too large for an eboot).' };
    const h = await sha1(file);
    const e = ebootEntries.find((f) => f.source.sha1 === h);
    if (e) return { kind: 'eboot', entry: e, ok: true, message: `Decrypted eboot, game version ${e.gameVersion}.` };
    if (allEboots.some((f) => f.target.sha1 === h))
      return { kind: 'eboot', ok: false, message: 'This eboot is already patched. Use the original one.' };
    return { kind: 'eboot', ok: false, message: 'Unknown eboot version (supported: ' +
      ebootEntries.map((f) => f.gameVersion).join(', ') + '). Make sure it is from Shin Gundam Musou PCSG00278 ' +
      `and not modified. (SHA-1 ${h})` };
  }

  if (startsWith(head, LINKDATA)) {
    for (const e of files.filter((f) => !f.gameVersion && !f.dlc)) {
      const kind = e.source.name;
      if (file.size === e.source.size) {
        if (file.size <= HASH_LIMIT) {           // LINKDATA.B: check it fully now
          const h = await sha1(file);
          if (h === e.target.sha1) return { kind, ok: false, message: 'This file is already patched. Use the original.' };
          if (h !== e.source.sha1) return { kind, ok: false, message: 'This file does not match the original ' +
            `${kind} (modified, or from another release).` };
        }                                        // LINKDATA.C (1 GB) is checked while patching instead
        return { kind, entry: e, ok: true, message: `Decrypted ${kind}.` };
      }
      if (file.size === e.target.size && file.size !== e.source.size)
        return { kind, ok: false, message: `This ${kind} is already patched. Use the original one.` };
    }
    return { kind: null, ok: false, message: 'A LINKDATA file, but not LINKDATA.B or LINKDATA.C of this game.' };
  }

  // DLC .BIN files (one per DLC folder): matched by size, then SHA-1
  const dlc = files.filter((f) => f.dlc);
  if (dlc.some((f) => f.source.size === file.size || f.target.size === file.size) && file.size <= HASH_LIMIT) {
    const h = await sha1(file);
    const e = dlc.find((f) => f.source.sha1 === h);
    if (e) return { kind: 'DLC', entry: e, ok: true, message: `Decrypted DLC file ${e.source.name}.` };
    if (dlc.some((f) => f.target.sha1 === h))
      return { kind: 'DLC', ok: false, message: 'This DLC file is already patched. Use the original one.' };
  }
  if (/^(DSC|DMS)\d.*\.bin$/i.test(file.name))
    return { kind: 'DLC', ok: false, message: 'This DLC file is still encrypted (or modified). Decrypt the DLC ' +
      'first with decrypt_dlc.py, see step 3 of the guide.' };

  if (/^linkdata\.[bc]$/i.test(file.name))
    return { kind: 'LINKDATA.' + file.name.slice(-1).toUpperCase(), ok: false,
      message: 'This file is still encrypted. Copy it from the game folder opened with VitaShell\'s ' +
        '"Open decrypted" over FTP, or paste it into another folder in VitaShell first if you use USB ' +
        '(or take it from Vita3K).' };
  return { kind: null, ok: false, message: 'Not a file this patcher needs.' };
}

/** The eboot entry to apply: the DLC variant (reads the patched DLC from rePatch) when DLC files are patched too. */
export function ebootEntry(entry, manifest, withDlc) {
  if (!withDlc) return entry;
  return manifest.files.find((f) => f.dlcEboot && f.gameVersion === entry.gameVersion && f.source.sha1 === entry.source.sha1)
    ?? entry;
}

/**
 * Patch one file. `sink` gets the output: { write(Uint8Array): Promise, close(): Promise, abort(): Promise }.
 * onProgress(bytesDoneForThisFile). Throws PatchError with a readable message if the source doesn't match.
 */
export async function patchFile(file, entry, patchBytes, sink, onProgress) {
  const readSource = async (pos, len) => new Uint8Array(await file.slice(pos, pos + len).arrayBuffer());
  try {
    const size = await applyPatch(patchBytes, readSource, (w) => sink.write(w), onProgress);
    if (size !== entry.target.size) throw new PatchError('patched size is wrong');
    await sink.close();
  } catch (err) {
    await sink.abort?.();
    if (err instanceof PatchError && /checksum mismatch|too short/.test(err.message))
      throw new PatchError(`${entry.source.name} doesn't match this patch. Make sure it is the original, decrypted ` +
        `file${entry.gameVersion ? ` for game version ${entry.gameVersion}` : ''} and not already patched.`);
    throw err;
  }
}

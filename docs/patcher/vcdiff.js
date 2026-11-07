// Minimal VCDIFF (RFC 3284) decoder for xdelta3 patches, streaming window by window.
//
// Supports what `xdelta3 -e -S none -A` writes: the default code table, no secondary compression,
// no application header, source windows (VCD_SOURCE) and xdelta's per-window Adler-32 (VCD_ADLER32).
// The source file is read on demand, so a 1 GB source never has to be in memory at once.

const VCD_SOURCE = 0x01, VCD_TARGET = 0x02, VCD_ADLER32 = 0x04;
const NOOP = 0, ADD = 1, RUN = 2, COPY = 3;

// RFC 3284 section 5.6: the default instruction code table, as [type1, size1, mode1, type2, size2, mode2].
const CODE_TABLE = (() => {
  const t = [[RUN, 0, 0, NOOP, 0, 0], [ADD, 0, 0, NOOP, 0, 0]];
  for (let s = 1; s <= 17; s++) t.push([ADD, s, 0, NOOP, 0, 0]);
  for (let m = 0; m <= 8; m++) {
    t.push([COPY, 0, m, NOOP, 0, 0]);
    for (let s = 4; s <= 18; s++) t.push([COPY, s, m, NOOP, 0, 0]);
  }
  for (let m = 0; m <= 5; m++)
    for (let a = 1; a <= 4; a++)
      for (let c = 4; c <= 6; c++) t.push([ADD, a, 0, COPY, c, m]);
  for (let m = 6; m <= 8; m++)
    for (let a = 1; a <= 4; a++) t.push([ADD, a, 0, COPY, 4, m]);
  for (let m = 0; m <= 8; m++) t.push([COPY, 4, m, ADD, 1, 0]);
  if (t.length !== 256) throw new Error('code table');
  return t;
})();

export class PatchError extends Error {}

class Reader {
  constructor(buf, pos = 0, end = buf.length) { this.buf = buf; this.pos = pos; this.end = end; }
  byte() {
    if (this.pos >= this.end) throw new PatchError('patch file is truncated or damaged');
    return this.buf[this.pos++];
  }
  varint() {                       // base-128, big-endian, high bit = more bytes follow
    let v = 0, b;
    do { b = this.byte(); v = v * 128 + (b & 0x7f); } while (b & 0x80);
    if (v > Number.MAX_SAFE_INTEGER) throw new PatchError('number too large in patch');
    return v;
  }
  bytes(n) {
    if (this.pos + n > this.end) throw new PatchError('patch file is truncated or damaged');
    const out = this.buf.subarray(this.pos, this.pos + n); this.pos += n; return out;
  }
}

export function adler32(buf) {
  let a = 1, b = 0;
  const n = buf.length;
  for (let i = 0; i < n;) {
    const stop = Math.min(i + 3800, n);      // keep sums below 2^31 between reductions
    for (; i < stop; i++) { a += buf[i]; b += a; }
    a %= 65521; b %= 65521;
  }
  return ((b << 16) | a) >>> 0;
}

/**
 * Apply a VCDIFF patch.
 *   patch:      Uint8Array with the whole .xdelta file
 *   readSource: async (pos, len) => Uint8Array   bytes of the original file
 *   onWindow:   async (Uint8Array) => void       receives the patched file in order, one window at a time
 *   onProgress: (doneBytes) => void              optional
 * Returns the total size of the patched file.
 */
export async function applyPatch(patch, readSource, onWindow, onProgress) {
  const r = new Reader(patch);
  if (r.byte() !== 0xd6 || r.byte() !== 0xc3 || r.byte() !== 0xc4)
    throw new PatchError('not an xdelta / VCDIFF patch');
  r.byte();                                   // version
  const hdr = r.byte();
  if (hdr & 0x01) throw new PatchError('patch uses secondary compression (unsupported; build with -S none)');
  if (hdr & 0x02) throw new PatchError('patch uses a custom code table (unsupported)');
  if (hdr & 0x04) r.bytes(r.varint());        // xdelta application header: skip

  let total = 0;
  while (r.pos < r.end) {
    const win = r.byte();
    if (win & VCD_TARGET) throw new PatchError('target-referencing windows are unsupported');
    let src = new Uint8Array(0);
    if (win & VCD_SOURCE) {
      const len = r.varint(), pos = r.varint();
      src = await readSource(pos, len);
      if (src.length !== len) throw new PatchError('original file is too short (wrong file?)');
    }
    r.varint();                               // length of the delta encoding
    const tlen = r.varint();
    const deltaInd = r.byte();
    if (deltaInd !== 0) throw new PatchError('compressed patch sections are unsupported');
    const dataLen = r.varint(), instLen = r.varint(), addrLen = r.varint();
    let want = null;
    if (win & VCD_ADLER32) {
      const c = r.bytes(4);
      want = ((c[0] << 24) | (c[1] << 16) | (c[2] << 8) | c[3]) >>> 0;
    }
    const data = new Reader(patch, r.pos, r.pos + dataLen); r.pos += dataLen;
    const inst = new Reader(patch, r.pos, r.pos + instLen); r.pos += instLen;
    const addr = new Reader(patch, r.pos, r.pos + addrLen); r.pos += addrLen;
    if (r.pos > r.end) throw new PatchError('patch file is truncated or damaged');

    const out = decodeWindow(src, tlen, data, inst, addr);
    if (want !== null && adler32(out) !== want)
      throw new PatchError('checksum mismatch: the original file does not match this patch');
    total += out.length;
    await onWindow(out);
    if (onProgress) onProgress(total);
  }
  return total;
}

function decodeWindow(src, tlen, data, inst, addr) {
  const out = new Uint8Array(tlen);
  const slen = src.length;
  const near = [0, 0, 0, 0], same = new Array(768).fill(0);
  let nextNear = 0, t = 0;

  const decodeAddr = (mode) => {
    const here = slen + t;
    let a;
    if (mode === 0) a = addr.varint();
    else if (mode === 1) a = here - addr.varint();
    else if (mode < 6) a = near[mode - 2] + addr.varint();
    else a = same[(mode - 6) * 256 + addr.byte()];
    near[nextNear] = a; nextNear = (nextNear + 1) & 3;
    same[a % 768] = a;
    return a;
  };

  const run = (type, size, mode) => {
    if (type === NOOP) return;
    if (size === 0) size = inst.varint();
    if (t + size > tlen) throw new PatchError('patch writes past the end of a window (damaged patch)');
    if (type === ADD) {
      out.set(data.bytes(size), t);
    } else if (type === RUN) {
      out.fill(data.byte(), t, t + size);
    } else {                                   // COPY
      let a = decodeAddr(mode);
      if (a >= here0()) throw new PatchError('bad copy address (damaged patch)');
      let n = size, d = t;
      if (a < slen) {                          // from the source segment
        const k = Math.min(n, slen - a);
        out.set(src.subarray(a, a + k), d);
        a += k; d += k; n -= k;
      }
      if (n > 0) {                             // from this window's output; may overlap (repeats a pattern)
        let s = a - slen;
        if (s + n <= d) out.copyWithin(d, s, s + n);
        else for (let i = 0; i < n; i++) out[d + i] = out[s + i];
      }
    }
    t += size;
  };
  const here0 = () => slen + t;

  while (inst.pos < inst.end) {
    const c = CODE_TABLE[inst.byte()];
    run(c[0], c[1], c[2]);
    run(c[3], c[4], c[5]);
  }
  if (t !== tlen) throw new PatchError('window size mismatch (damaged patch)');
  return out;
}

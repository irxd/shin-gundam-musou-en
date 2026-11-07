// Tiny "stored" (uncompressed) zip writer. Files are kept as lists of Blobs, so a 1 GB file never has to sit
// in one big ArrayBuffer; the browser can keep large Blobs on disk. No zip64: every file and the whole zip
// must stay under 4 GB, which is plenty here (the largest file is about 1 GB).

const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();

/** Running CRC-32: start with crc32(0, first), then crc32(prev, next) ... */
export function crc32(crc, buf) {
  let c = ~crc >>> 0;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  return ~c >>> 0;
}

function dosDateTime(d = new Date()) {
  const time = (d.getHours() << 11) | (d.getMinutes() << 5) | (d.getSeconds() >> 1);
  const date = ((d.getFullYear() - 1980) << 9) | ((d.getMonth() + 1) << 5) | d.getDate();
  return [time, date];
}

/** entries: [{ path: 'a/b.bin', parts: Blob[], size, crc }] -> Blob (application/zip) */
export function makeZip(entries) {
  const enc = new TextEncoder();
  const [time, date] = dosDateTime();
  const out = [], central = [];
  let offset = 0;
  for (const e of entries) {
    const name = enc.encode(e.path);
    const lh = new DataView(new ArrayBuffer(30));
    lh.setUint32(0, 0x04034b50, true);
    lh.setUint16(4, 20, true);
    lh.setUint16(6, 0x0800, true);              // UTF-8 names
    lh.setUint16(8, 0, true);                   // stored
    lh.setUint16(10, time, true);
    lh.setUint16(12, date, true);
    lh.setUint32(14, e.crc, true);
    lh.setUint32(18, e.size, true);
    lh.setUint32(22, e.size, true);
    lh.setUint16(26, name.length, true);
    lh.setUint16(28, 0, true);
    out.push(lh, name, ...e.parts);

    const ch = new DataView(new ArrayBuffer(46));
    ch.setUint32(0, 0x02014b50, true);
    ch.setUint16(4, 20, true);
    ch.setUint16(6, 20, true);
    ch.setUint16(8, 0x0800, true);
    ch.setUint16(10, 0, true);
    ch.setUint16(12, time, true);
    ch.setUint16(14, date, true);
    ch.setUint32(16, e.crc, true);
    ch.setUint32(20, e.size, true);
    ch.setUint32(24, e.size, true);
    ch.setUint16(28, name.length, true);
    ch.setUint32(42, offset, true);             // the other fields stay 0
    central.push(ch, name);
    offset += 30 + name.length + e.size;
  }
  const cdSize = central.reduce((n, p) => n + (p.byteLength ?? p.length), 0);
  const end = new DataView(new ArrayBuffer(22));
  end.setUint32(0, 0x06054b50, true);
  end.setUint16(8, entries.length, true);
  end.setUint16(10, entries.length, true);
  end.setUint32(12, cdSize, true);
  end.setUint32(16, offset, true);
  if (offset + cdSize > 0xffffffff) throw new Error('zip would be larger than 4 GB');
  return new Blob([...out, ...central, end], { type: 'application/zip' });
}

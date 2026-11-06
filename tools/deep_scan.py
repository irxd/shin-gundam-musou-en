import struct, sys, re, zlib, collections
sys.stdout.reconfigure(encoding='utf-8')
kana = {
 'utf8':  re.compile(rb'(?:\xe3[\x81-\x83][\x80-\xbf]){3,}'),
 'utf16le': re.compile(rb'(?:[\x41-\xf6]\x30){3,}'),
 'utf16be': re.compile(rb'(?:\x30[\x41-\xf6]){3,}'),
 'sjis':  re.compile(rb'(?:\x82[\x9f-\xf1]|\x83[\x40-\x96]){3,}'),
}
dec = {'utf8':'utf-8','utf16le':'utf-16-le','utf16be':'utf-16-be','sjis':'cp932'}
zhdr = re.compile(rb'\x78[\x01\x5e\x9c\xda]')
for p in sys.argv[1:]:
    f = open(p, 'rb'); magic, count, align, _ = struct.unpack('<4I', f.read(16))
    ents = [struct.unpack('<4I', f.read(16)) for _ in range(count)]
    zent = collections.Counter(); found = collections.defaultdict(list)
    for i, (off, _, sz, _) in enumerate(ents):
        if not sz: continue
        f.seek(off * align); d = f.read(sz)
        blobs = [('raw', d)]
        for m in zhdr.finditer(d):
            try:
                z = zlib.decompressobj(); out = z.decompress(d[m.start():m.start()+0x40000], 0x100000)
                if len(out) >= 64: blobs.append((f'z@{m.start():x}', out)); zent[i] += 1
            except zlib.error: pass
        for tag, b in blobs:
            for k, r in kana.items():
                ms = r.findall(b)
                if ms: found[i].append((tag, k, len(ms), ms[0][:40].decode(dec[k], 'replace')))
    print(f'#### {p}: entries with valid zlib streams: {len(zent)} (streams {sum(zent.values())}); entries with kana: {len(found)}')
    for i in list(found)[:15]:
        print(f'  [{i}] size={ents[i][2]}', found[i][:3])

import struct, sys, re
# hiragana/katakana in UTF-8 (E3 81/82/83 xx), UTF-16LE (xx 30), Shift-JIS (82 9F-F1 / 83 40-96)
pat = {
 'utf8':  re.compile(rb'(?:\xe3[\x81-\x83][\x80-\xbf]){4,}'),
 'utf16': re.compile(rb'(?:[\x41-\xf6]\x30){4,}'),
 'sjis':  re.compile(rb'(?:\x82[\x9f-\xf1]|\x83[\x40-\x96]){4,}'),
}
for p in sys.argv[1:]:
    f = open(p, 'rb'); magic, count, align, _ = struct.unpack('<4I', f.read(16))
    ents = [struct.unpack('<4I', f.read(16)) for _ in range(count)]
    tot = {k: 0 for k in pat}; ex = {}
    hits = []
    for i, (off, _, sz, _) in enumerate(ents):
        if not sz: continue
        f.seek(off * align); d = f.read(sz)
        c = {k: len(r.findall(d)) for k, r in pat.items()}
        for k in c: tot[k] += c[k]
        if any(c.values()):
            hits.append((i, sz, c, d[:8].hex()))
            for k, r in pat.items():
                if c[k] and k not in ex:
                    m = r.search(d); s = d[m.start():m.start()+60]
                    ex[k] = (i, s.decode({'utf8':'utf-8','utf16':'utf-16-le','sjis':'cp932'}[k], 'replace'))
    print(f'#### {p}: entries with kana={len(hits)} totals={tot}')
    for h in sorted(hits, key=lambda h: -sum(h[2].values()))[:12]: print('  ', h)
    for k, v in ex.items(): print('   example', k, v)

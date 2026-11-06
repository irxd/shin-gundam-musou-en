import sys, re, os, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from linkdata import LinkData
codes = [0xE38181 + k for k in range(6)]   # ぁあぃいぅう as packed UTF-8
pats = []
for fmt in ('<I', '>I'):
    for stride in range(4, 65, 4):
        gap = b'' if stride == 4 else b'.{%d}' % (stride - 4)
        pats.append((fmt, stride, re.compile(gap.join(re.escape(struct.pack(fmt, c)) for c in codes), re.S)))
# also 3-byte packed sequences with stride
for stride in range(3, 33):
    gap = b'' if stride == 3 else b'.{%d}' % (stride - 3)
    pats.append(('raw3', stride, re.compile(gap.join(re.escape(c.to_bytes(3, 'big')) for c in codes), re.S)))
def scan(name, d):
    for fmt, stride, r in pats:
        m = r.search(d)
        if m: print(f'{name} @{m.start():#x} fmt={fmt} stride={stride} size={len(d)}')
for path in sys.argv[1:]:
    if os.path.basename(path).startswith('LINKDATA.'):
        ld = LinkData(path)
        for i in range(len(ld)):
            off, sz = ld.entries[i]
            if not sz: continue
            ld.f.seek(off * ld.align)
            if ld.f.read(4) in (b'GT1G', b'_DBW', b'_HBW'): continue
            scan(f'{os.path.basename(path)}[{i}]', ld.read(i))
    else:
        scan(os.path.basename(path), open(path, 'rb').read())

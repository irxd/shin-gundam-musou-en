import sys, struct, re
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, sys.argv[3])
from linkdata import LinkData
v, p = LinkData(sys.argv[1]), LinkData(sys.argv[2])
def hdr(d, e):
    if len(d) < 8: return None
    t, c, z = struct.unpack(e + 'HHI', d[:8]); return (t, c) if z == 0 and 0 < c < 5000 and 8+4*c <= len(d) else None
def first_bytes_kind(d): return d[:4]
ok = mism = 0; bad = []
for i in range(len(v)):
    j = i if i < 112 else i + 2
    dv, dp = v.read(i), p.read(j)
    hv, hp = hdr(dv, '<'), hdr(dp, '>')
    if hv or hp:
        if hv == hp: ok += 1
        else: mism += 1; bad.append((i, j, hv, hp))
print(f'tables matching with shift(+2 from 112): {ok}, mismatched: {mism}')
for b in bad[:15]: print('  ', b)
for k in (112, 113):
    d = p.read(k); print(f'PS3 extra entry {k}: size {len(d)} head {d[:32].hex(" ")}')
    s = re.findall(rb'[ -~]{6,}', d)[:6]; print('    ascii:', s)

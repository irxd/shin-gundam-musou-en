import sys, struct, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, sys.argv[3])
from linkdata import LinkData
v, p = LinkData(sys.argv[1]), LinkData(sys.argv[2])
print('vita', len(v), v.endian, '| ps3', len(p), p.endian)
def table_hdr(d, e):
    if len(d) < 8: return None
    tid, cnt, z = struct.unpack(e + 'HHI', d[:8])
    return (tid, cnt) if z == 0 and 0 < cnt < 5000 and 8 + 4 * cnt <= len(d) else None
jp = re.compile(rb'\xe3[\x81-\x83][\x80-\xbf]')
same = diff = 0; rows = []
for i in range(max(len(v), len(p))):
    dv = v.read(i) if i < len(v) else b''; dp = p.read(i) if i < len(p) else b''
    hv, hp = table_hdr(dv, '<'), table_hdr(dp, '>')
    tv, tp = len(jp.findall(dv)), len(jp.findall(dp))
    eng = len(re.findall(rb'[A-Za-z][a-z]{3,} [A-Za-z]{2,}', dp))
    if tv or tp or eng > 5: rows.append((i, len(dv), len(dp), hv, hp, tv, tp, eng))
print(f'{"idx":>4} {"vsize":>7} {"psize":>7} vita(tid,cnt) ps3(tid,cnt) vJPchars pJPchars pEnglishPhrases')
for r in rows[:25]: print(f'{r[0]:>4} {r[1]:>7} {r[2]:>7} {str(r[3]):>14} {str(r[4]):>12} {r[5]:>8} {r[6]:>8} {r[7]:>6}')
print('...'); 
for r in rows[-8:]: print(f'{r[0]:>4} {r[1]:>7} {r[2]:>7} {str(r[3]):>14} {str(r[4]):>12} {r[5]:>8} {r[6]:>8} {r[7]:>6}')
m = sum(1 for r in rows if r[3] and r[4] and r[3] == r[4])
print(f'rows={len(rows)}  identical (tid,count) at same index: {m}')

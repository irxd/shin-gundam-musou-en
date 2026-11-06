import sys, struct, re, collections
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, 'tools')
from linkdata import LinkData
v = LinkData('decrypted/vita/LINKDATA_NGP/LINKDATA.B'); p = LinkData('decrypted/ps3/PS3_GAME/USRDIR/LINKDATA_PS3/LINKDATA.B')
jp = re.compile(rb'\xe3[\x81-\x83][\x80-\xbf]')

def parse_table(d, e):
    if len(d) < 8: return None
    tid, c = struct.unpack_from(e + 'HH', d)
    if not 0 < c < 20000 or 4 + 4 * c > len(d): return None
    offs = struct.unpack_from(e + f'{c}I', d, 4)
    base = 4 + 4 * c
    if offs[0] != 0 or any(b < a for a, b in zip(offs, offs[1:])) or base + offs[-1] > len(d): return None
    ends = list(offs[1:]) + [len(d) - base]
    return tid, [d[base + a:base + b] for a, b in zip(offs, ends)]

def tokens(rec, e):
    """Split a record into ('s', bytes) strings [u16 len][utf8][NUL] and ('b', bytes) other data."""
    out, i, raw = [], 0, b''
    while i < len(rec):
        if i + 2 <= len(rec):
            n = struct.unpack_from(e + 'H', rec, i)[0]
            s = rec[i + 2:i + 2 + n]
            if 0 < n and i + 3 + n <= len(rec) and rec[i + 2 + n] == 0 and b'\0' not in s:
                try:
                    t = s.decode('utf-8')
                    if any(ord(ch) >= 0x80 or ch.isalpha() for ch in t):
                        if raw: out.append(('b', raw)); raw = b''
                        out.append(('s', s)); i += 3 + n; continue
                except UnicodeDecodeError: pass
        raw += rec[i:i + 1]; i += 1
    if raw: out.append(('b', raw))
    return out

res = collections.Counter(); rows = []
for i in range(112, 333):
    dv, dp = v.read(i), p.read(i + 2)
    if not jp.search(dv): continue
    tv, tp = parse_table(dv, '<'), parse_table(dp, '>')
    if not tv or not tp:
        rows.append((i, 'NOT TABLE16', dv[:8].hex(), len(dv))); res['not table16'] += 1; continue
    if tv[0] != tp[0] or len(tv[1]) != len(tp[1]):
        rows.append((i, 'tid/count mismatch', tv[0], len(tv[1]), tp[0], len(tp[1]))); res['mismatch'] += 1; continue
    good = bad = 0
    for rv, rp in zip(tv[1], tp[1]):
        kv = [k for k, _ in tokens(rv, '<')]; kp = [k for k, _ in tokens(rp, '>')]
        sv = sum(k == 's' for k in kv); sp = sum(k == 's' for k in kp)
        if sv == sp: good += 1
        else: bad += 1
    res['table ok' if bad == 0 else 'table partial'] += 1
    rows.append((i, f'tid={tv[0]} recs={len(tv[1])} records with same #strings={good} differing={bad}'))
for r in rows: print(r)
print(res)

"""Build an English Vita LINKDATA.B by porting string tables from the PS3 release.

Message entries (Vita 112+ <-> PS3 +2): u32 nsec, (u32 offset, u32 size) * nsec, then sections.
A section is a string table when: u32 n, (u32 off, u32 len) * n, strings start at 4 + 8n and are
contiguous. Matching string tables (same n) are replaced with the PS3 strings (converted to LE).
All other data (script bytecode etc.) stays Vita-original.
"""
import argparse, struct, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from linkdata import LinkData, write_linkdata

PS3_SHIFT_FROM, PS3_SHIFT = 112, 2


def parse_sections(d, e):
    if len(d) < 4:
        return None
    n = struct.unpack_from(e + 'I', d)[0]
    if not 0 < n < 4096 or 4 + 8 * n > len(d):
        return None
    secs = [struct.unpack_from(e + 'II', d, 4 + 8 * i) for i in range(n)]
    pos = 4 + 8 * n
    for off, size in secs:  # sections are 4-byte aligned
        if off != (pos + 3) & ~3 or off + size > len(d):
            return None
        pos = off + size
    return [d[o:o + s] for o, s in secs] if (pos + 3) & ~3 >= len(d) >= pos else None


def parse_strtab(s, e):
    if len(s) < 4:
        return None
    n = struct.unpack_from(e + 'I', s)[0]
    if n == 0 or 4 + 8 * n > len(s):
        return None
    pos, out = 4 + 8 * n, []
    for i in range(n):
        off, ln = struct.unpack_from(e + 'II', s, 4 + 8 * i)
        if off != pos or ln == 0 or off + ln > len(s) or s[off + ln - 1] != 0:
            return None
        out.append(s[off:off + ln - 1])
        pos += ln
    return out if pos == len(s) else None


def build_strtab(strings, e='<'):
    head = struct.pack(e + 'I', len(strings))
    pos, body = 4 + 8 * len(strings), b''
    for t in strings:
        head += struct.pack(e + 'II', pos, len(t) + 1)
        body += t + b'\0'
        pos += len(t) + 1
    return head + body


def build_sections(secs, e='<'):
    pos = 4 + 8 * len(secs)
    head = struct.pack(e + 'I', len(secs))
    body = b''
    for s in secs:
        pad = (-pos) & 3
        body += b'\0' * pad
        pos += pad
        head += struct.pack(e + 'II', pos, len(s))
        body += s
        pos += len(s)
    return head + body


# ---------------------------------------------------------------------------
# "Table" entries (Vita 112-332): u16 table_id, u16 count, u32 offsets[count] (offsets[0] == 0,
# relative to data start 4 + 4*count). Each record: u16 len, bytes[len], NUL, zero-pad to 4.
# The entry is zero-padded so that it ends on a 16-byte boundary with a final 0x1A byte.

def parse_table(d, e):
    if len(d) < 8 or d[-1] != 0x1a:
        return None
    tid, c = struct.unpack_from(e + 'HH', d)
    if not 0 < c < 20000 or 4 + 4 * c > len(d):
        return None
    offs = struct.unpack_from(e + f'{c}I', d, 4)
    base = 4 + 4 * c
    if offs[0] != 0 or any(b <= a for a, b in zip(offs, offs[1:])) or base + offs[-1] >= len(d):
        return None
    recs = []
    for k, o in enumerate(offs):
        p = base + o
        n = struct.unpack_from(e + 'H', d, p)[0]
        end = base + offs[k + 1] if k + 1 < c else len(d)
        if p + 3 + n > end or d[p + 2 + n] != 0:
            return None
        recs.append(d[p + 2:p + 2 + n])
    return tid, recs


def build_table(tid, recs, e='<'):
    body, offs = b'', []
    for r in recs:
        offs.append(len(body))
        rec = struct.pack(e + 'H', len(r)) + r + b'\0'
        body += rec + b'\0' * ((-len(rec)) & 3)
    out = struct.pack(e + 'HH', tid, len(recs)) + struct.pack(e + f'{len(recs)}I', *offs) + body
    out += b'\0' * ((15 - len(out)) % 16) + b'\x1a'
    return out


def port_table(dv, dp, st):
    tv, tp = parse_table(dv, '<'), parse_table(dp, '>')
    if not tv or not tp:
        return None
    if tv[0] != tp[0] or len(tv[1]) != len(tp[1]):
        st['table: id/count mismatch (skipped)'] += 1
        return None
    recs, n = [], 0
    for rv, rp in zip(tv[1], tp[1]):
        if rp.strip(b'\0') and rp != rv:   # PS3 has real text here
            recs.append(rp); n += 1
        else:                              # PS3 placeholder/empty: keep Vita original
            recs.append(rv)
            if rv.strip(b'\0') and not rp.strip(b'\0'):
                st['table: record kept (PS3 blank)'] += 1
    st['table: strings replaced'] += n
    return build_table(tv[0], recs)


def port_node(dv, dp, st, skipped, path):
    """Recursively port a section container / string table. Returns new bytes or None if unchanged."""
    tv, tp = parse_strtab(dv, '<'), parse_strtab(dp, '>')
    if tv is not None and tp is not None:
        if len(tv) != len(tp):
            st['strtab: count mismatch (skipped)'] += 1; skipped.append((path, len(tv), len(tp)))
            return None
        st['strtab: replaced'] += 1; st['strings replaced'] += len(tp)
        return build_strtab(tp)
    vs, ps = parse_sections(dv, '<'), parse_sections(dp, '>')
    if not vs or not ps or len(vs) != len(ps):
        return None
    changed = False
    for k, (sv, sp) in enumerate(zip(vs, ps)):
        new = port_node(sv, sp, st, skipped, path + [k])
        if new is not None:
            vs[k] = new; changed = True
    if not changed:
        return None
    out = build_sections(vs)
    assert parse_sections(out, '<') == vs
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vita_b'); ap.add_argument('ps3_b'); ap.add_argument('out')
    ap.add_argument('--only', type=int, nargs='*', help='only patch these Vita entry indices')
    a = ap.parse_args()

    v, p = LinkData(a.vita_b), LinkData(a.ps3_b)
    blobs = [v.read(i) for i in range(len(v))]
    st = collections.Counter(); skipped = []
    for i in range(PS3_SHIFT_FROM, len(v)):
        if a.only and i not in a.only:
            continue
        dp = p.read(i + PS3_SHIFT)
        if parse_table(blobs[i], '<'):
            new = port_table(blobs[i], dp, st)
            if new is not None:
                blobs[i] = new; st['entry: table patched'] += 1
            continue
        if not (parse_sections(blobs[i], '<') and parse_sections(dp, '>')):
            st['entry: unknown format (untouched)'] += 1
            continue
        new = port_node(blobs[i], dp, st, skipped, [i])
        if new is not None:
            blobs[i] = new; st['entry: message patched'] += 1

    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    write_linkdata(a.out, blobs, '<', v.align)
    for k, n in sorted(st.items()):
        print(f'{k:36} {n}')
    for s in skipped[:20]:
        print('  skipped (entry, section, vita_n, ps3_n):', s)
    print('wrote', a.out)


if __name__ == '__main__':
    main()

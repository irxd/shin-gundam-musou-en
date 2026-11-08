"""Build an English Vita LINKDATA.B by porting string tables from the PS3 release.

Message entries (Vita 112+ <-> PS3 +2): u32 nsec, (u32 offset, u32 size) * nsec, then sections.
A section is a string table when: u32 n, (u32 off, u32 len) * n, strings start at 4 + 8n and are
contiguous. Matching string tables (same n) are replaced with the PS3 strings (converted to LE).
All other data (script bytecode etc.) stays Vita-original.
"""
import argparse, re, struct, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from linkdata import LinkData, write_linkdata
from textwrap_vita import Metrics, fixup, box_of

METRICS = None    # set in main(); None disables wrapping


TABLE_SENTENCE = 12.0    # table records at least this wide (in Japanese) are sentences -> may be wrapped


def english(tp, tv, st, box=None, table=False):
    """Final English bytes for one string: font fixups + pre-wrap for boxes that need it.
    tp: PS3 English bytes, tv: Vita Japanese bytes it replaces, box: (width limit, max lines) or None.
    table: record of a table entry (menus + help texts). Only sentences are wrapped there (short
    labels must stay on one line), and never narrower than the Japanese line it replaces."""
    try:
        s = fixup(tp.decode('utf-8'))
    except UnicodeDecodeError:      # binary data that happens to look like a string table
        return tp
    if table:
        s = TABLE_OVERRIDES.get(s, s)
    check_format(s, tv)
    if METRICS and box:
        ja = tv.decode('utf-8', 'replace')
        lim, lines = box
        if table:
            if '\n' not in ja and METRICS.width(ja, 5.0) < TABLE_SENTENCE:
                return s.encode('utf-8')
            lim = max(lim, METRICS.line_width(ja, 5.0))
        if '\n' in ja or METRICS.width(ja, 5.0) <= lim:      # shown in that box (not a one-line view)
            w, sc = METRICS.fit(s, lim, lines)
            if w != s:
                st['wrap: strings re-wrapped'] += 1
            if sc < 32:
                st[f'wrap: shrunk to {sc}/32'] += 1
            s = w
    return s.encode('utf-8')

PRINTF = re.compile(r'%[-+ #0]*\d*(?:\.\d+)?(?:hh|h|ll|l)?[diouxXcsfFeEgGp]')


def check_format(s, tv):
    """Some strings are printf formats filled in by the Vita eboot (e.g. '[g]%s[/] x%d'). The English must
    use the same conversions in the same order, or the game reads an int as a char* and crashes. Any other
    '%' in a format must be '%%'."""
    ja = tv.decode('utf-8', 'replace')
    want = PRINTF.findall(ja)
    if not want:
        return
    if PRINTF.findall(s) != want or '%' in PRINTF.sub('', s).replace('%%', ''):
        raise ValueError(f'printf format mismatch, add an entry to TABLE_OVERRIDES:\n'
                         f'  Japanese: {ja!r}\n  English:  {s!r}')


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


# Whole table records replaced by exact PS3 text -> new text.
TABLE_OVERRIDES = {
    # short labels too wide for their Vita slot
    'Regular Network Connection': 'Network Connection',     # Options label; auto-shrunk to unreadable
    # printf formats whose PS3 text has the arguments in another order than the Vita eboot passes them
    # (Japanese: name %s first, then count %d). Swapped order crashed the game on the reward popup.
    '[g]%d[/] of material item [g]%s[/] obtained.':
        'Material item [g]%s[/] x[g]%d[/] obtained.',
    '[g]%d[/] of material item [g]%s[/] obtained!':
        'Material item [g]%s[/]\nx[g]%d[/] obtained!',
    'Play [g]%d or more[/] times in [g]%s[/]':
        'In [g]%s[/], play [g]%d or more[/] times',
    'Play [g]%d or more[/] times with [g]%s[/]':
        'With [g]%s[/], sortie [g]%d or more[/] times',
    # a bare '%' in a printf format is undefined; it must be '%%'
    'Unlock [g]%d %[/] of Famous Scenes': 'Unlock [g]%d%%[/] of Famous Scenes',
    'Reach [g]%d %[/] of the Card Collection': 'Reach [g]%d%%[/] of the Card Collection',
}


def port_table(dv, dp, st):
    tv, tp = parse_table(dv, '<'), parse_table(dp, '>')
    if not tv or not tp:
        return None
    if tv[0] != tp[0] or len(tv[1]) != len(tp[1]):
        st['table: id/count mismatch (skipped)'] += 1
        return None
    recs, n = [], 0
    box = box_of(METRICS, [r.decode('utf-8', 'replace') for r in tv[1]]) if METRICS else None
    for rv, rp in zip(tv[1], tp[1]):
        if rp.strip(b'\0') and rp != rv:   # PS3 has real text here
            recs.append(english(rp, rv, st, box, table=True)); n += 1
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
        box = box_of(METRICS, [x.decode('utf-8', 'replace') for x in tv]) if METRICS else None
        return build_strtab([english(p, v, st, box) for v, p in zip(tv, tp)])
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


STORY_ENTRY = 171    # story/event scripts (see tools/story.py)


def port_story(dv, dp, st):
    """Replace each scene's line records with the PS3 ones (matched by line index + id)."""
    from story import parse_c, build_c, scene_lines, build_record
    iv, ip = parse_c(dv, '<'), parse_c(dp, '>')
    if not iv or not ip or len(iv) != len(ip):
        st['story: container mismatch (skipped)'] += 1
        return None
    boxes = {}
    if METRICS:    # one box size per text-section kind (dialogue / narration), from all scenes
        ja = collections.defaultdict(list)
        for a in iv:
            sa = scene_lines(a, '<')
            for t, lines in (sa[1].items() if sa else ()):
                ja[t] += [x[2].decode('utf-8', 'replace') for x in lines]
        boxes = {t: box_of(METRICS, v) for t, v in ja.items()}
        print('story boxes (width units, max lines):', boxes)
    out = []
    for a, b in zip(iv, ip):
        sa, sb = scene_lines(a, '<'), scene_lines(b, '>')
        if not sa or not sb:
            if sa: st['story: scene kept (no PS3 match)'] += 1
            out.append(a)
            continue
        secs, changed = list(sa[0]), False
        for t, lines_v in sa[1].items():
            lines_p = sb[1].get(t)
            if lines_p is None or [(x[0], x[1]) for x in lines_v] != [(x[0], x[1]) for x in lines_p]:
                st['story: text section kept (line mismatch)'] += 1
                continue
            secs[t] = build_c([build_record(idx, lid, english(text, tv, st, boxes.get(t)))
                               for (idx, lid, text), (_, _, tv) in zip(lines_p, lines_v)])
            changed = True
            st['story: text sections replaced'] += 1
            st['story: lines replaced'] += len(lines_p)
        out.append(build_c(secs) if changed else a)
    return build_c(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('vita_b'); ap.add_argument('ps3_b'); ap.add_argument('out')
    ap.add_argument('--only', type=int, nargs='*', help='only patch these Vita entry indices')
    ap.add_argument('--widths', default=str(Path(__file__).parent.parent / 'build' / 'ascii_widths.json'),
                    help='ASCII glyph widths written by build_font.py (wrapping is skipped if missing)')
    a = ap.parse_args()
    global METRICS
    if Path(a.widths).exists():
        METRICS = Metrics(a.widths)
    else:
        print('warning: no', a.widths, '- run build_font.py first; text will not be pre-wrapped')

    v, p = LinkData(a.vita_b), LinkData(a.ps3_b)
    blobs = [v.read(i) for i in range(len(v))]
    st = collections.Counter(); skipped = []
    for i in range(PS3_SHIFT_FROM, len(v)):
        if a.only and i not in a.only:
            continue
        dp = p.read(i + PS3_SHIFT)
        if i == STORY_ENTRY:
            new = port_story(blobs[i], dp, st)
            if new is not None:
                blobs[i] = new; st['entry: story patched'] += 1
            continue
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

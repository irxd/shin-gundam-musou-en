"""Build an English Vita LINKDATA.B by porting string tables from the PS3 release.

Message entries (Vita 112+ <-> PS3 +2): u32 nsec, (u32 offset, u32 size) * nsec, then sections.
A section is a string table when: u32 n, (u32 off, u32 len) * n, strings start at 4 + 8n and are
contiguous. Matching string tables (same n) are replaced with the PS3 strings (converted to LE).
All other data (script bytecode etc.) stays Vita-original.
"""
import argparse, math, re, struct, sys, collections
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from linkdata import LinkData, write_linkdata
from text_short import SHORT
from textwrap_vita import Metrics, fixup, box_of, BATTLE_TAG, SCALE_BASE, SCALE_MIN

METRICS = None    # set in main(); None disables wrapping


TABLE_SENTENCE = 12.0    # table records at least this wide (in Japanese) are sentences -> may be wrapped


def english(tp, tv, st, box=None, table=False, measured=False):
    """Final English bytes for one string: font fixups + pre-wrap for boxes that need it.
    tp: PS3 English bytes, tv: Vita Japanese bytes it replaces, box: (width limit, max lines) or None.
    table: record of a table entry (menus + help texts). Only sentences are wrapped there (short
    labels must stay on one line), and never narrower than the Japanese line it replaces, unless the
    box was measured on hardware (measured: the game wraps the Japanese itself, its lines say nothing;
    the paragraph breaks are kept, the text is shrunk instead of reflowed)."""
    try:
        s = fixup(tp.decode('utf-8'))
    except UnicodeDecodeError:      # binary data that happens to look like a string table
        return tp
    if table:
        s = TABLE_OVERRIDES.get(s, s)
    check_format(s, tv)
    tag = BATTLE_TAG.match(s)
    head = tag.group() if tag else ''
    s = head + SHORT.get(re.sub(r' *\n *', ' ', s[len(head):]), s[len(head):])     # text_short.py
    if METRICS and box == BANNER:
        return banner(s).encode('utf-8')
    if METRICS and box:
        ja = tv.decode('utf-8', 'replace')
        lim, lines, grow, fixed = (tuple(box) + (True, False)[len(box) - 2:])[:4]
        if table:
            if '\n' not in ja and METRICS.width(ja, 5.0) < TABLE_SENTENCE:
                return s.encode('utf-8')
            if not measured:
                lim = max(lim, METRICS.line_width(ja, 5.0))
        if measured or box is PANEL or '\n' in ja or METRICS.width(ja, 5.0) <= lim:  # shown in that box
            # measured boxes: a button icon ([BTN][NAME]) is drawn about one glyph wide; stand-in chars
            # (unknown to the metrics = 1.0 unit) while wrapping
            icons = BTN.findall(s) if measured else []
            for k, t in enumerate(icons):
                s = s.replace(t, chr(0xF000 + k), 1)
            w, sc = METRICS.fit(s, lim, lines, grow, reflow=not measured, fixed=fixed)
            for k, t in enumerate(icons):
                s, w = s.replace(chr(0xF000 + k), t), w.replace(chr(0xF000 + k), t)
            if w != s:
                st['wrap: strings re-wrapped'] += 1
            if sc < 32:
                st[f'wrap: shrunk to {sc}/32'] += 1
            s = w
    return s.encode('utf-8')

BTN = re.compile(r'\[BTN\]\[[A-Z0-9_]+\]')

# Battle messages ('（吉味）...', see textwrap_vita.BATTLE_TAG) show in the banner in the middle of the screen.
# The banner is one line tall and draws a second line below it, left-aligned (seen on hardware), so they
# must stay on one line. The game breaks the text itself (scaled width: the breaker reads our scale
# marker) at about 22 units, widened to 26 by the patched eboot (build_font.py BANNER_BREAK); the banner
# holds about 27 between its arrows. Long messages are shrunk to fit 25 units (and shortened in
# text_short.py when even half size is not enough).
# Orders ('（指示）') show in the green banner and also become the mission panel's objective: they are
# banner text too (one line); the panel (16.5 units wide x 2 lines) breaks the line itself, at the same scale.
# The other strings of those tables are mission objectives shown in the panel only.
BANNER = 'banner'
BANNER_W = 25.0
PANEL = (16.5, 2)


def banner(s):
    tag = BATTLE_TAG.match(s)
    head, body = (tag.group(), s[tag.end():]) if tag else ('', s)
    one = re.sub(r' *\n *', ' ', body)
    w = METRICS.width(one)
    if w <= BANNER_W:
        return head + one
    # never a line break of ours: past half size (the smallest scale), the [n:NAME] estimate may be too
    # high anyway; if the real text is still too wide, the game breaks it at half pitch (one line tall)
    return head + '\x1b' + chr(SCALE_BASE + max(SCALE_MIN, int(BANNER_W * 32 / w))) + one


def strtab_boxes(strings):
    """Wrap box per string of a string table (Japanese bytes)."""
    ja = [x.decode('utf-8', 'replace') for x in strings]
    if not METRICS:
        return [None] * len(ja)
    if any(BATTLE_TAG.match(s) for s in ja):    # battle messages + mission objectives
        return [BANNER if BATTLE_TAG.match(s) else PANEL for s in ja]
    box = box_of(METRICS, ja)
    return [box] * len(ja)

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
    # %s is a suit name: the pre-wrap guesses its width, and with long names the popup wrapped the line again
    # itself ('Selection' alone on a second line, 'screen.' on a third); break right after the name instead
    'You can now select [g]%s[/] from the Mobile Suit Selection screen.':
        'You can now select [g]%s[/]\nfrom the Mobile Suit Selection screen.',
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
    # action conditions followed by button icons (see TABLE_PAD): the icons snap to 18 px cells, so these
    # are worded to end just before a cell edge (icon a few px after the colon) within 42 bytes
    'If SP Gauge is at 2 or more:': 'If SP Gauge is 2 or more:',
    'If SP Gauge is at 1 or more, in air:': 'In air, SP Gauge 1 or more:',
    'During dash attack:': 'In a dash attack:',
    'When charge attack hits:': 'If charge attack hits:',
    'During a normal attack:': 'In a normal attack:',
    # pre-wrapped for a box narrower than the table's estimate (Plans panel ~26 units, save notice ~29)
    'There are no upgrade actions available for your current pilot level.':
        'There are no upgrade actions available\nfor your current pilot level.',
    'This game has an autosave feature.\nPlease do not remove the memory card or turn the system off during autosaves.':
        'This game has an autosave feature.\nPlease do not remove the memory card or turn\nthe system off during autosaves.',
}

# Per-table box override: tid -> function(japanese record) -> (width limit, max lines, grow) or None (use
# the table-wide estimate).
TABLE_BOXES = {
    # mission briefings (Next Battle panel): 3 lines (a 4th line is cut off at the bottom), ~22.5 units
    # wide (~311 px at 13.9 px per unit); the text types out line by line, so a shrunk text keeps 3 lines
    # at full pitch (records 594-596 are another 5-line panel and keep the table estimate)
    7: lambda ja: (22.5, 3, False) if ja.count('\n') < 3 else None,
}

# Tables whose box was measured on hardware (their Japanese lines say nothing about its width):
# tid -> (width limit, max lines, grow, fixed width). The text keeps its own line breaks, is wrapped to
# that box and shrunk if it needs more lines. fixed width: the widget breaks the text itself at the box
# width *before* the shrink is applied, so a shrunk text must still break at the full-size width (the
# shrink only fits more lines); otherwise a shrunk text may use proportionally longer lines.
TABLE_MEASURED = {
    # tutorial / help popups: the popup widget (0x812186c0) breaks at 480 px = 20 units of 24 px (~17.2 px
    # drawn), at the shrunk size too (build_font.py, BRK_APPLY); 8 lines (the longest Japanese), a 9th
    # runs into the Close button
    37: (20.0, 8, True, False),
    # area restrictions (Area screen, under the briefing): one condition per line, ~22.5 units
    26: (22.5, 3, True, False),
}

# Tables the game wraps by itself whose PS3 text has hand line breaks made for the PS3 font: where the
# Japanese has none, they are dropped (the Vita breaks elsewhere, which left short lines).
TABLE_JOIN = {10}       # character descriptions (Database > Characters)

# Field names (table 5, 256 records; also filled into battle messages as [n:FLD]). The battle HUD shows the
# current field's name in a fixed slot with an icon at about 9.5 width units, which covered the end of long
# PS3 names ('Space Battle Airs[icon]ce B'). These are shortened to fit (widest result 9.35 units).
FIELD_TABLE = (5, 256)
FIELD_SHORT = [
    (r'^(Solomon|Axis|Gryps 2|Laplace) Airspace', r'\1 Space'),
    (r'^(Space|Sea|Air) Battle Airspace', r'\1 Zone'),
    (r'^Fortress Interior', 'Inner Fortress'),
    (r'^Residential Zone', 'Residential'),
    (r'^(\d(?:st|nd|rd|th)) Protective Line', r'\1 Alert Line'),
    (r'^(East|West|South|North) (\d)(?:st|nd|rd) ?Defense Point', r'\1 Defense \2'),
    (r'^(East|West|South|North) Defense Point', r'\1 Defense'),
    (r'^(\d(?:st|nd|rd|th)) Defense Point', r'\1 Def. Point'),
    (r'^Allied Comm Facility$', 'Allied Comms'),
    (r'^Enemy Comm Facility$', 'Enemy Comms'),
    (r'^Mobile Suit Factory$', 'MS Factory'),
    (r'^Final Defense Line$', 'Final Line'),
    (r'^Orb National Defense HQ$', 'Orb Defense HQ'),
    (r'^Team Assist Point$', 'Assist Point'),
    (r'^Odessa Base Command Center$', 'Odessa HQ'),
]


def short_field_name(b):
    s = b.decode('utf-8')
    for pat, rep in FIELD_SHORT:
        s = re.sub(pat, rep, s)
    return s.encode('utf-8')

# Story box width, measured on hardware (the Japanese lines leave room at the right). section -> units
STORY_WIDTH = {2: 28.0}     # narration box: ~455 px usable (stops short of the next-page arrow)


# The action lists (Player Info > Action, Plans) draw the button icons after a condition prefix such as
# 'If SP Gauge is at 1 or more:' at an x taken from the prefix's byte length, not its drawn width
# (measured on hardware: the first icon's left edge = text start + 18 px * (bytes // 3), i.e. one
# Japanese glyph cell per 3 UTF-8 bytes). English is wider per byte, so the icons covered it. These
# records are padded with invisible ESC+'X' pairs (a 2-byte no-op for the renderer, measurer and line
# breaker) until the icons land after the text. 42 bytes = longest Japanese record of the table, tested
# safe on hardware.
TABLE_PAD = {34: range(0, 9)}       # tid -> records followed by icons (conditions ending in ':')
PAD = b'\x1bX'
PAD_MAX = 42
ICON_CELL = 18                      # px per 3 bytes
ROW_PX_PER_UNIT = 17.1              # drawn size of one width unit in these rows
ICON_GAP = 4                        # min px between the text end and the icon


def pad_icon_prefix(e, st):
    w = METRICS.width(e.decode('utf-8')) * ROW_PX_PER_UNIT
    cells = math.ceil((w + ICON_GAP - 0.5) / ICON_CELL)
    out = e + b' ' * ((3 * cells - len(e)) & 1)    # trailing space (1 byte) so the 2-byte pairs fit exactly
    while len(out) < 3 * cells:
        out += PAD
    if len(out) > PAD_MAX:
        st['table: icon prefix too long (shorten it)'] += 1
        out = e + PAD * max(0, (PAD_MAX - len(e)) // len(PAD))
    st['table: icon prefix padded'] += 1
    return out


def port_table(dv, dp, st):
    tv, tp = parse_table(dv, '<'), parse_table(dp, '>')
    if not tv or not tp:
        return None
    if tv[0] != tp[0] or len(tv[1]) != len(tp[1]):
        st['table: id/count mismatch (skipped)'] += 1
        return None
    recs, n = [], 0
    box = box_of(METRICS, [r.decode('utf-8', 'replace') for r in tv[1]]) if METRICS else None
    override = TABLE_BOXES.get(tv[0], lambda ja: None)
    measured = TABLE_MEASURED.get(tv[0])
    pad = TABLE_PAD.get(tv[0], {})
    for k, (rv, rp) in enumerate(zip(tv[1], tp[1])):
        if rp.strip(b'\0') and rp != rv:   # PS3 has real text here
            b = measured or override(rv.decode('utf-8', 'replace')) or box
            if (tv[0], len(tv[1])) == FIELD_TABLE:
                new = short_field_name(rp)
                st['table: field names shortened'] += new != rp
                rp = new
            if tv[0] in TABLE_JOIN:
                b = None                    # the game wraps these
                if b'\n' not in rv:
                    rp = re.sub(rb' *\n *', b' ', rp)
            e = english(rp, rv, st, b, table=True, measured=bool(measured))
            if k in pad and METRICS:
                e = pad_icon_prefix(e, st)
            recs.append(e); n += 1
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
        return build_strtab([english(p, v, st, b) for v, p, b in zip(tv, tp, strtab_boxes(tv))])
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
        # story text types out line by line at full line spacing: a shrunk text keeps the line count
        boxes = {t: (STORY_WIDTH.get(t, b[0]), b[1], False) for t, v in ja.items() if (b := box_of(METRICS, v))}
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

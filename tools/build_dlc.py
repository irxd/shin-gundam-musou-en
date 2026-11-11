"""English DLC (addcont) files: 17 extra scenarios (DSC) and 6 extra mobile suit packs (DMS).

Usage: build_dlc.py <decrypted addcont/PCSG00278> <Vita LINKDATA.B> <English LINKDATA.B> <out dir>
                    [--text text/dlc] [--widths build/ascii_widths.json]
Run after build_text.py (the English LINKDATA.B gives the official PS3 English for every string the DLC shares
with the base game). Every other string comes from the translations in text/dlc/*.json, which map
sha1(Japanese utf-8)[:10] -> English (no Japanese game text in the repo). Writes <out dir>/<DLC folder>/<file>
for every .BIN (unchanged ones copied). The patched eboot (tools/build_font.py dlc_path) still mounts the installed
DLC but reads its files from app0:DLC/, so <out dir> is ux0:rePatch/PCSG00278/DLC/ (rePatch's reAddcont made the
DLC disappear on hardware, even with the untouched decrypted DLC).

DSC_nnn.BIN: "size-first" container (tools/story.py): r.2 scenario title/description (string table), r.3 the
scenario's story scenes (line records, as in the base game's entry 171), r.10.* battle messages and battle
dialogue (string tables).
DMS*.BIN: u32 pack id (0x64 + pack number), u32 n, u32 offsets[n] (absolute). Three chunks are full copies of base game tables (weapon
names = entry 117, mobile suit names = entry 115, twice) plus the DLC's own records; with the DLC installed
they are loaded instead of the base tables, so they must be English too.
"""
import argparse, collections, hashlib, json, re, shutil, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import build_text as bt
from build_text import parse_sections, build_sections, parse_strtab, build_strtab, parse_table, build_table
from linkdata import LinkData
from story import parse_c, build_c, parse_record, build_record
from textwrap_vita import Metrics, box_of

JP = re.compile(rb'[\xe3-\xe9][\x80-\xbf]{2}')
STORY_ENTRY = 171
NAME_TABLES = (115, 117)      # base entries copied into every DMS pack


def key(ja):
    return hashlib.sha1(ja).hexdigest()[:10]


class Text:
    """Japanese bytes -> English bytes: own translations first, then the base game's official English."""

    def __init__(self, text_dir, base):
        self.own = {}
        for f in sorted(Path(text_dir).glob('*.json')):
            for k, v in json.load(open(f, encoding='utf-8')).items():
                if k in self.own and self.own[k] != v:
                    print(f'warning: {f.name}: {k} translated differently elsewhere')
                self.own[k] = v
        self.base, self.used, self.missing = base, set(), {}

    def get(self, ja, where):
        k = key(ja)
        if k in self.own:
            self.used.add(k)
            return self.own[k].encode('utf-8')
        if ja in self.base:
            return self.base[ja]
        self.missing.setdefault(k, (ja.decode('utf-8', 'replace'), where))
        return None


def base_pairs(vita_b, en_b):
    """Japanese -> English for every string build_text.py replaced (string tables, tables, story lines)."""
    out = {}

    def walk(a, b):
        ta, tb = parse_strtab(a, '<'), parse_strtab(b, '<')
        if ta is not None and tb is not None and len(ta) == len(tb):
            pairs = zip(ta, tb)
        elif (ta := parse_table(a, '<')) and (tb := parse_table(b, '<')) and len(ta[1]) == len(tb[1]):
            pairs = zip(ta[1], tb[1])
        else:
            sa, sb = parse_sections(a, '<'), parse_sections(b, '<')
            if sa and sb and len(sa) == len(sb):
                for x, y in zip(sa, sb):
                    walk(x, y)
            return
        for ja, en in pairs:
            if ja != en and JP.search(ja):
                # strip the wrap/scale markers of the base box: the DLC string is re-wrapped for its own box
                out.setdefault(ja, re.sub(rb'\x1b.', b'', en).replace(b'\n', b' ') if b'\n' not in ja else
                               re.sub(rb'\x1b.', b'', en))

    v, o = LinkData(vita_b), LinkData(en_b)
    for i in range(len(v.entries)):
        a, b = v.read(i), o.read(i)
        if a != b and i != STORY_ENTRY:
            walk(a, b)
    return out, v, o


# ---------------------------------------------------------------------------------------------- DSC


def translate_strtab(strings, text, st, where):
    boxes = bt.strtab_boxes(strings)
    out, changed = [], False
    for i, ja in enumerate(strings):
        box = boxes[i]
        en = text.get(ja, f'{where}:{i}') if JP.search(ja) else None
        if en is None:
            out.append(ja)
            st['kept (Japanese or no text)'] += bool(JP.search(ja))
            continue
        out.append(bt.english(en, ja, st, box)); changed = True
        st['strings translated'] += 1
    return out if changed else None


def translate_lines(recs, text, st, where, box):
    out, changed = [], False
    for idx, lid, ja in recs:
        en = text.get(ja, f'{where}:{idx}') if JP.search(ja) else None
        if en is None:
            out.append(build_record(idx, lid, ja)); st['kept (Japanese or no text)'] += bool(JP.search(ja))
            continue
        out.append(build_record(idx, lid, bt.english(en, ja, st, box))); changed = True
        st['story lines translated'] += 1
    return build_c(out) if changed else None


def port_dsc(d, text, st, boxes, where='r', depth=0):
    """Returns the translated node bytes, or None when nothing in it changed (original bytes are kept)."""
    t = parse_strtab(d, '<')
    if t is not None and build_strtab(t) == d:
        new = translate_strtab(t, text, st, where)
        return build_strtab(new) if new else None
    items = parse_c(d, '<')
    if items and len(build_c(items)) == len(d):
        recs = [parse_record(r, '<') for r in items]
        if all(recs):
            # story scene text sections: index 1 = dialogue, 2 = narration (see build_text.port_story)
            return translate_lines(recs, text, st, where, boxes.get(int(where.rsplit('.', 1)[1])))
        new = [port_dsc(x, text, st, boxes, f'{where}.{k}', depth + 1) for k, x in enumerate(items)]
        if not any(x is not None for x in new):
            return None
        return build_c([n if n is not None else x for n, x in zip(new, items)])
    secs = parse_sections(d, '<')
    if secs and len(build_sections(secs)) == len(d):
        new = [port_dsc(x, text, st, boxes, f'{where}.{k}', depth + 1) for k, x in enumerate(secs)]
        if not any(x is not None for x in new):
            return None
        return build_sections([n if n is not None else x for n, x in zip(new, secs)])
    if JP.search(d):
        st['unknown block with Japanese (untouched)'] += 1
    return None


# ---------------------------------------------------------------------------------------------- DMS


def port_dms(d, text, names, st, where):
    pack, n = struct.unpack_from('<II', d)
    assert 0x64 <= pack < 0x80 and 8 + 4 * n < len(d), 'unexpected DMS header'
    offs = list(struct.unpack_from(f'<{n}I', d, 8)) + [len(d)]
    out, changed = bytearray(d), False
    for k in range(n):
        a, b = offs[k], offs[k + 1]
        t = parse_table(d[a:b].rstrip(b'\0') if d[a:b].rstrip(b'\0').endswith(b'\x1a') else d[a:b], '<')
        if not t:
            continue
        tid, recs = t
        # the base table it copies: most records equal at the same index
        ja_base, en_base = max(names, key=lambda nb: sum(x == y for x, y in zip(recs, nb[0])))
        new = []
        for j, r in enumerate(recs):
            if j < len(ja_base) and r == ja_base[j]:
                new.append(en_base[j])
            elif JP.search(r) and (en := text.get(r, f'{where}:{k}:{j}')) is not None:
                new.append(bt.english(en, r, st)); st['names translated'] += 1
            else:
                new.append(r); st['kept (Japanese or no text)'] += bool(JP.search(r))
        nt = build_table(tid, new)
        assert len(nt) <= b - a, f'{where}: English table {k} does not fit ({len(nt)} > {b - a})'
        out[a:b] = nt + b'\0' * (b - a - len(nt))
        changed = True
        st['name tables replaced'] += 1
    return bytes(out) if changed else None


# ---------------------------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('addcont'); ap.add_argument('vita_b'); ap.add_argument('en_b'); ap.add_argument('out')
    ap.add_argument('--text', default=str(Path(__file__).parent.parent / 'text' / 'dlc'))
    ap.add_argument('--widths', default=str(Path(__file__).parent.parent / 'build' / 'ascii_widths.json'))
    ap.add_argument('--missing', help='write the untranslated strings (key, Japanese, where) to this JSON file')
    a = ap.parse_args()
    if Path(a.widths).exists():
        bt.METRICS = Metrics(a.widths)
    else:
        print('warning: no', a.widths, '- run build_font.py first; text will not be pre-wrapped')

    base, v, o = base_pairs(a.vita_b, a.en_b)
    text = Text(a.text, base)
    names = [(parse_table(v.read(i), '<')[1], parse_table(o.read(i), '<')[1]) for i in NAME_TABLES]

    # story boxes, from the base game's story scenes (same as build_text.port_story)
    boxes = {}
    if bt.METRICS:
        from story import scene_lines
        ja = collections.defaultdict(list)
        for item in parse_c(v.read(STORY_ENTRY), '<'):
            sl = scene_lines(item, '<')
            for t, lines in (sl[1].items() if sl else ()):
                ja[t] += [x[2].decode('utf-8', 'replace') for x in lines]
        boxes = {t: (bt.STORY_WIDTH.get(t, b[0]), b[1], False) for t, vals in ja.items() if (b := box_of(bt.METRICS, vals))}

    st = collections.Counter()
    root, out = Path(a.addcont), Path(a.out)
    files = 0
    # the patched eboot reads every installed DLC's files from app0:DLC/<folder>/, so every .BIN must be there,
    # changed or not (a missing folder would make that DLC's data unreadable)
    for g in sorted(root.glob('D*/*.BIN')):
        folder = g.parent
        dst = out / folder.name / g.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        d = g.read_bytes()
        where = f'{folder.name}/{g.name}'
        new = port_dsc(d, text, st, boxes, where) if g.name.startswith('DSC') else port_dms(d, text, names, st, where)
        if new is None:
            shutil.copyfile(g, dst)
        else:
            dst.write_bytes(new)
            files += 1
    for k, n in sorted(st.items()):
        print(f'{k:40} {n}')
    print(f'DLC: {files} files written to {out}; {len(text.missing)} unique strings still Japanese')
    unused = set(text.own) - text.used
    if unused:
        print(f'warning: {len(unused)} translations not used (Japanese changed?): {sorted(unused)[:5]}')
    if a.missing:
        json.dump({k: v for k, v in text.missing.items()}, open(a.missing, 'w', encoding='utf-8'),
                  ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()

"""English subtitles for the video cutscenes (FILE_NGP/MOVIE/*.mp4).

Usage: build_movies.py <ps3 LINKDATA.C> <LINKDATA.C to patch in place> [--widths build/ascii_widths.json]

The subtitles are not burned into the videos: the game draws them from one container per movie
(Vita LINKDATA.C[3014..3064] = PS3 [3016..3066]):

    u32 count (9), u32 offsets[count], zero-pad to 16; sections 16-aligned
    0: cue timing   u32 count, 3 x u32 0, count x { u32 start, u32 end, u32 0, u32 0 }  (frames)
    1: flags
    2..8: one string table per language (u32 count, count x { u32 offset, u32 len_incl_nul }, strings)
          2 = Japanese (what the Vita reads), 3 = English on PS3 ("dummy" on Vita), others "dummy"

Timings and line counts are identical on both platforms, so the PS3 English (slot 3) goes into the
Vita's Japanese slot (2), wrapped to the width of the Japanese subtitles. The English is smaller,
so each entry still fits in its 0x800-aligned space and is rewritten in place (only its size in the
LINKDATA header changes).
"""
import argparse, struct, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from linkdata import LinkData
from textwrap_vita import Metrics, fixup

FIRST, COUNT, PS3_SHIFT = 3014, 51, 2
SLOT_JA, SLOT_EN = 2, 3
WIDTH, MAX_LINES = 24.0, 2     # widest Japanese subtitle line is 23 units, at most 2 lines


def parse(d, e):
    n = struct.unpack_from(e + 'I', d)[0]
    offs = list(struct.unpack_from(f'{e}{n}I', d, 4))
    assert n == 9 and offs[0] == 0x30 and all(o % 16 == 0 for o in offs), 'not a subtitle container'
    return [d[a:b] for a, b in zip(offs, offs[1:] + [len(d)])]


def build(secs, e='<'):
    head = struct.pack(f'{e}I{len(secs)}I', len(secs), *[0] * len(secs))
    out = bytearray(head + b'\0' * (-len(head) % 16))
    offs = []
    for s in secs:
        offs.append(len(out))
        out += s + b'\0' * (-len(s) % 16)
    struct.pack_into(f'{e}{len(secs)}I', out, 4, *offs)
    return bytes(out)


def parse_strtab(b, e):
    n = struct.unpack_from(e + 'I', b)[0]
    return [b[o:o + ln - 1] for o, ln in (struct.unpack_from(e + '2I', b, 4 + 8 * k) for k in range(n))]


def build_strtab(strings, e='<'):
    head, body, pos = struct.pack(e + 'I', len(strings)), b'', 4 + 8 * len(strings)
    for t in strings:
        head += struct.pack(e + '2I', pos + len(body), len(t) + 1)
        body += t + b'\0'
    return head + body


def wrap(m, s):
    """Keep lines within WIDTH; a text that needs two lines is split where both halves are most even."""
    if m.line_width(s) <= WIDTH:
        return s
    words = s.replace('\n', ' ').split(' ')
    best = None
    for k in range(1, len(words)):
        a, b = ' '.join(words[:k]), ' '.join(words[k:])
        w = max(m.width(a), m.width(b))
        if w <= WIDTH and (best is None or w < best[0]):
            best = (w, a + '\n' + b)
    if best:
        return best[1]
    out = m.wrap(s, WIDTH, MAX_LINES)
    print(f'  warning: needs {out.count(chr(10)) + 1} lines: {s!r}')
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('ps3_c'); ap.add_argument('out_c')
    ap.add_argument('--widths', default=str(Path(__file__).parent.parent / 'build' / 'ascii_widths.json'))
    a = ap.parse_args()
    m = Metrics(a.widths)
    p, o = LinkData(a.ps3_c), LinkData(a.out_c)
    f = open(a.out_c, 'r+b')
    lines = wrapped = 0
    for vi in range(FIRST, FIRST + COUNT):
        d = o.read(vi)
        vs, ps = parse(d, '<'), parse(p.read(vi + PS3_SHIFT), '>')
        assert build(vs) == d, f'C[{vi}]: container does not round-trip'
        ja, en = parse_strtab(vs[SLOT_JA], '<'), parse_strtab(ps[SLOT_EN], '>')
        timing = lambda s, e: struct.unpack(f'{e}{len(s) // 4}I', s)
        assert timing(vs[0], '<') == timing(ps[0], '>'), f'C[{vi}]: cue timings differ from PS3'
        assert len(ja) == len(en), f'C[{vi}]: {len(ja)} Japanese vs {len(en)} English lines'
        new = []
        for s in en:
            t = fixup(s.decode('utf-8'))
            w = wrap(m, t)
            wrapped += w != t
            new.append(w.encode('utf-8'))
        lines += len(new)
        vs[SLOT_JA] = build_strtab(new)
        nd = build(vs)
        off, size = o.entries[vi]
        cap = -(-size // o.align) * o.align
        assert len(nd) <= cap, f'C[{vi}]: {len(nd)} bytes do not fit in {cap}'
        # clear the old bytes too (not up to cap: the last entry ends the file)
        f.seek(off * o.align); f.write(nd + b'\0' * max(0, size - len(nd)))
        f.seek(16 + 16 * vi + 8); f.write(struct.pack('<I', len(nd)))
    f.close()
    print(f'movie subtitles: {COUNT} cutscenes, {lines} lines in English ({wrapped} re-wrapped)')


if __name__ == '__main__':
    main()

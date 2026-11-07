"""Story/event script container (LINKDATA.B Vita entry 171 <-> PS3 entry 173).

All levels use a "size-first" container:  u32 n ; n * (u32 size, u32 offset) ; data (offsets relative to
4 + 8n, items 4-byte aligned).  Outer: 1011 items. A scene item is a container of 3 sections
(script, 4-byte, text); the text section is a container of line records:
    u16 index, u16 len (incl. NUL), u32 line_id, utf-8 text, NUL
"""
import struct


def parse_c(d, e):
    if len(d) < 4: return None
    n = struct.unpack_from(e + 'I', d)[0]
    if not 0 < n < 100000 or 4 + 8 * n > len(d): return None
    base = 4 + 8 * n
    items = []
    for k in range(n):
        size, off = struct.unpack_from(e + 'II', d, 4 + 8 * k)
        if base + off + size > len(d): return None
        items.append(d[base + off:base + off + size])
    return items


def build_c(items, e='<'):
    n = len(items)
    head = struct.pack(e + 'I', n)
    body = b''
    for it in items:
        body += b'\0' * ((-len(body)) & 3)
        head += struct.pack(e + 'II', len(it), len(body))
        body += it
    out = head + body
    return out + b'\0' * ((-len(out)) & 3)


def parse_record(r, e):
    if len(r) < 9: return None
    idx, ln, lid = struct.unpack_from(e + 'HHI', r)
    if 8 + ln != len(r) or r[-1] != 0: return None
    return idx, lid, r[8:-1]


def build_record(idx, lid, text, e='<'):
    return struct.pack(e + 'HHI', idx, len(text) + 1, lid) + text + b'\0'


def scene_lines(item, e):
    """Return (sections, {section_index: [(idx, id, text)]}) if item is a scene block, else None.
    A scene is a 3-section container; one or two sections (dialogue, narration) hold line records."""
    secs = parse_c(item, e)
    if not secs or len(secs) != 3: return None
    texts = {}
    for t in range(len(secs)):
        recs = parse_c(secs[t], e)
        if not recs: continue
        lines = [parse_record(r, e) for r in recs]
        if all(l is not None for l in lines):
            texts[t] = lines
    return (secs, texts) if texts else None

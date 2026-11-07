"""Decode G1T textures (Vita: Morton-swizzled DXT1/DXT5) to Pillow images."""
from PIL import Image
from g1t import parse_g1t
from dxt import unswizzle_blocks

FMT = {0x10: ('DXT1', 1, 8), 0x12: ('DXT5', 3, 16),    # Vita (Morton-swizzled blocks)
       0x06: ('DXT1', 1, 8), 0x08: ('DXT5', 3, 16)}    # PS3 (linear blocks)
# fmt -> (name, Pillow bcn type, bytes per block)


def tex_size(t):
    if t['fmt'] in FMT:
        return (t['w'] // 4) * (t['h'] // 4) * FMT[t['fmt']][2]
    return None


def data_start(d, t, e='<'):
    """Texture data follows the 8-byte header and, when header byte 7 is set, an extension block
    (u32 size first, e.g. 0xc)."""
    p = t['off']
    if d[p + 7]:
        import struct
        return p + 8 + struct.unpack_from(e + 'I', d, p + 8)[0]
    return p + 8


def decode_tex(d, t, vita=None):
    if t['fmt'] not in FMT:
        return None
    _, n, bs = FMT[t['fmt']]
    if vita is None:
        vita = d[:4] == b'GT1G'
    start = data_start(d, t, '<' if vita else '>')
    raw = d[start:start + tex_size(t)]
    if vita:
        raw = unswizzle_blocks(raw, t['w'], t['h'], bs)
    return Image.frombytes('RGBA', (t['w'], t['h']), raw, 'bcn', n)


def decode_all(d, vita=None):
    g = parse_g1t(d)
    return [decode_tex(d, t, vita) for t in g['textures']] if g else []

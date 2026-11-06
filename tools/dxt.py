"""DXT5 (BC3) helpers for Vita G1T textures: Morton (Z-order) block (un)swizzle + decode/encode via Pillow."""
from PIL import Image

def _morton(x, y):
    """Interleave bits: y -> even bits, x -> odd bits (Vita order)."""
    r = 0
    for i in range(16):
        r |= ((y >> i) & 1) << (2 * i) | ((x >> i) & 1) << (2 * i + 1)
    return r

def unswizzle_blocks(data, w, h, bsize=16):
    """Vita morton-ordered 4x4 blocks -> linear row-major blocks (square-power-of-2 assumption handled by min dim)."""
    bw, bh = w // 4, h // 4
    out = bytearray(len(data))
    m = min(bw, bh)
    for by in range(bh):
        for bx in range(bw):
            # for non-square textures, Vita tiles squares of size m along the longer axis
            if bw >= bh:
                tile, lx, ly = bx // m, bx % m, by
            else:
                tile, lx, ly = by // m, bx, by % m
            src = (tile * m * m + _morton(lx, ly)) * bsize
            dst = (by * bw + bx) * bsize
            out[dst:dst + bsize] = data[src:src + bsize]
    return bytes(out)

def swizzle_blocks(data, w, h, bsize=16):
    bw, bh = w // 4, h // 4
    out = bytearray(len(data)); m = min(bw, bh)
    for by in range(bh):
        for bx in range(bw):
            if bw >= bh: tile, lx, ly = bx // m, bx % m, by
            else: tile, lx, ly = by // m, bx, by % m
            dst = (tile * m * m + _morton(lx, ly)) * bsize
            src = (by * bw + bx) * bsize
            out[dst:dst + bsize] = data[src:src + bsize]
    return bytes(out)

def decode_dxt5(data, w, h):
    return Image.frombytes('RGBA', (w, h), data, 'bcn', 3)

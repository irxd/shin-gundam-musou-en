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


# ---------------------------------------------------------------- DXT5 encoder (simple, per block)
def _alpha_block(a):
    hi, lo = max(a), min(a)
    if hi == lo:
        return bytes([hi, lo]) + b'\0' * 6
    pal = [hi, lo] + [((7 - k) * hi + k * lo) // 7 for k in range(1, 7)]
    bits = 0
    for i, v in enumerate(a):
        bits |= min(range(8), key=lambda j: abs(pal[j] - v)) << (3 * i)
    return bytes([hi, lo]) + bits.to_bytes(6, 'little')


def _565(c):
    return ((c[0] >> 3) << 11) | ((c[1] >> 2) << 5) | (c[2] >> 3)


def _rgb(v):
    r, g, b = (v >> 11) & 31, (v >> 5) & 63, v & 31
    return (r << 3 | r >> 2, g << 2 | g >> 4, b << 3 | b >> 2)


def _color_block(px):
    """px: 16 (r,g,b,a). Endpoints = extremes along the luminance axis of the visible pixels."""
    vis = [p[:3] for p in px if p[3] > 0] or [p[:3] for p in px]
    lum = lambda c: c[0] * 3 + c[1] * 6 + c[2]
    c0, c1 = _565(max(vis, key=lum)), _565(min(vis, key=lum))
    if c0 < c1:
        c0, c1 = c1, c0
    if c0 == c1:
        return c0.to_bytes(2, 'little') + c1.to_bytes(2, 'little') + b'\0' * 4
    a, b = _rgb(c0), _rgb(c1)
    pal = [a, b, tuple((2 * x + y) // 3 for x, y in zip(a, b)), tuple((x + 2 * y) // 3 for x, y in zip(a, b))]
    bits = 0
    for i, p in enumerate(px):
        k = min(range(4), key=lambda j: sum((p[t] - pal[j][t]) ** 2 for t in range(3)))
        bits |= k << (2 * i)
    return c0.to_bytes(2, 'little') + c1.to_bytes(2, 'little') + bits.to_bytes(4, 'little')


def encode_dxt5_block(px):
    """px: 16 RGBA tuples, row-major -> 16-byte BC3 block."""
    return _alpha_block([p[3] for p in px]) + _color_block(px)

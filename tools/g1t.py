"""Minimal G1T (Koei Tecmo texture container) header parser. Vita = 'GT1G' little-endian, PS3 = 'G1TG' big-endian."""
import struct

def parse_g1t(d):
    if d[:4] == b'GT1G': e = '<'
    elif d[:4] == b'G1TG': e = '>'
    else: return None
    ver = d[4:8]
    fsize, toff, count, plat, extra = struct.unpack_from(e + '5I', d, 8)
    if not 0 < count < 4096 or toff + 4 * count > len(d): return None
    offs = struct.unpack_from(e + f'{count}I', d, toff)
    texs = []
    for o in offs:
        p = toff + o
        if p + 8 > len(d): return None
        b0, fmt, dims, b3 = d[p], d[p + 1], d[p + 2], d[p + 3]
        lo, hi = dims & 0xf, dims >> 4
        if e == '>':      # PS3 stores the size nibbles the other way round
            lo, hi = hi, lo
        texs.append(dict(off=p, mips=b0 >> 4, fmt=fmt, w=1 << lo, h=1 << hi, b3=b3,
                         hdr=d[p:p + 8].hex()))
    return dict(endian=e, version=ver, size=fsize, platform=plat, textures=texs)

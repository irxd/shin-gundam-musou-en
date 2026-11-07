"""Replace Japanese text sprites in Vita UI atlases with the English sprites from the PS3 release.

Usage: build_images.py <ps3 LINKDATA.C> <LINKDATA.C to patch in place>
Run after build_font.py (which writes the output LINKDATA.C). Entries keep their size, so they are
overwritten in place. Each PS3 sprite is cut out, scaled to fit the Vita sprite slot, centred, and
only the touched DXT5 blocks are re-encoded.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from PIL import Image
from linkdata import LinkData
from g1t import parse_g1t
from g1t_decode import decode_tex, data_start, tex_size
from dxt import unswizzle_blocks, swizzle_blocks, encode_dxt5_block

# (vita entry, texture, slot box in Vita atlas, ps3 entry, texture, sprite box in PS3 atlas)
SPRITES = [
    # confirmation buttons (atlas C[2611] <-> PS3 C[2612])
    (2611, 0, (12, 118, 94, 160), 2612, 0, (864, 161, 992, 215)),     # はい selected  <- YES (red)
    (2611, 0, (125, 122, 203, 162), 2612, 0, (622, 300, 731, 348)),   # はい           <- YES (grey)
    (2611, 0, (226, 118, 311, 162), 2612, 0, (770, 293, 869, 347)),   # 確認 selected  <- OK (red)
    (2611, 0, (330, 118, 426, 162), 2612, 0, (627, 351, 726, 405)),   # いいえ selected <- NO (red)
    (2611, 0, (440, 118, 536, 166), 2612, 0, (779, 358, 874, 406)),   # いいえ         <- NO (grey)
]

# whole textures replaced by the downscaled PS3 texture: (vita entry, texture, ps3 entry, texture)
WHOLE = [(i, 0, i, 0) for i in range(289, 321)]     # chapter title cards (第1話 ... / PHASE-01 ... / episode1 ...)

SCALE = 0.72     # PS3 -> Vita sprite scale (same for all, so letter heights match); squeeze if too wide


def fit(sprite, box):
    w, h = box[2] - box[0], box[3] - box[1]
    sy = min(SCALE, h / sprite.height)
    sx = min(sy, w / sprite.width)
    size = (max(1, round(sprite.width * sx)), max(1, round(sprite.height * sy)))
    return sprite.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')


def main():
    ps3_c, out_c = sys.argv[1:3]
    p, o = LinkData(ps3_c), LinkData(out_c)
    by_tex = {}
    for ve, vt, vbox, pe, pt, pbox in SPRITES:
        by_tex.setdefault((ve, vt), []).append((vbox, pe, pt, pbox))
    f = open(out_c, 'r+b')
    for (ve, vt), items in by_tex.items():
        d = o.read(ve)
        t = parse_g1t(d)['textures'][vt]
        assert t['fmt'] == 0x12, 'only DXT5 Vita textures supported'
        img = decode_tex(d, t)
        for vbox, pe, pt, pbox in items:
            pd = p.read(pe)
            src = decode_tex(pd, parse_g1t(pd)['textures'][pt]).crop(pbox)
            src = fit(src, vbox)
            img.paste((0, 0, 0, 0), vbox)
            cx, cy = (vbox[0] + vbox[2] - src.width) // 2, (vbox[1] + vbox[3] - src.height) // 2
            img.alpha_composite(src, (cx, cy))
        # re-encode the touched blocks
        start, n = data_start(d, t), tex_size(t)
        lin = bytearray(unswizzle_blocks(d[start:start + n], t['w'], t['h'], 16))
        bw = t['w'] // 4
        px = img.load()
        for vbox, *_ in items:
            for by in range(vbox[1] // 4, (vbox[3] + 3) // 4):
                for bx in range(vbox[0] // 4, (vbox[2] + 3) // 4):
                    blk = [px[bx * 4 + i % 4, by * 4 + i // 4] for i in range(16)]
                    lin[(by * bw + bx) * 16:(by * bw + bx + 1) * 16] = encode_dxt5_block(blk)
        write_tex(f, o, ve, d, t, lin)
        print(f'C[{ve}] tex {vt}: {len(items)} sprites replaced')
    for ve, vt, pe, pt in WHOLE:
        d = o.read(ve)
        t = parse_g1t(d)['textures'][vt]
        assert t['fmt'] == 0x12
        pd = p.read(pe)
        src = decode_tex(pd, parse_g1t(pd)['textures'][pt])
        img = src.convert('RGBa').resize((t['w'], t['h']), Image.LANCZOS).convert('RGBA')
        write_tex(f, o, ve, d, t, encode_image(img))
    print(f'{len(WHOLE)} whole textures replaced')
    f.close()


def encode_image(img):
    """RGBA image -> linear (row-major) DXT5 blocks."""
    px = img.load()
    out = bytearray()
    for by in range(img.height // 4):
        for bx in range(img.width // 4):
            out += encode_dxt5_block([px[bx * 4 + i % 4, by * 4 + i // 4] for i in range(16)])
    return out


def write_tex(f, o, entry, d, t, lin):
    start, n = data_start(d, t), tex_size(t)
    assert len(lin) == n
    nd = bytearray(d)
    nd[start:start + n] = swizzle_blocks(bytes(lin), t['w'], t['h'], 16)
    off, size = o.entries[entry]
    assert len(nd) == size
    f.seek(off * o.align); f.write(nd)


if __name__ == '__main__':
    main()

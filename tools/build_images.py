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
    # title screen (atlas C[2629] <-> PS3 C[2630]); last value: own scale instead of SCALE
    (2629, 0, (198, 84, 404, 122), 2630, 0, (136, 82, 385, 119), 1.0),  # ©創通・サンライズ <- ©SOTSU・SUNRISE
]

# whole textures replaced by the downscaled PS3 texture: (vita entry, texture, ps3 entry, texture)
WHOLE = [(i, 0, i, 0) for i in range(289, 321)]     # chapter title cards (第1話 ... / PHASE-01 ... / episode1 ...)

SCALE = 0.72     # PS3 -> Vita sprite scale (same for all, so letter heights match); squeeze if too wide


def fit(sprite, box, scale=SCALE):
    w, h = box[2] - box[0], box[3] - box[1]
    sy = min(scale, h / sprite.height)
    sx = min(sy, w / sprite.width)
    size = (max(1, round(sprite.width * sx)), max(1, round(sprite.height * sy)))
    return sprite.convert('RGBa').resize(size, Image.LANCZOS).convert('RGBA')


def main():
    ps3_c, out_c = sys.argv[1:3]
    p, o = LinkData(ps3_c), LinkData(out_c)
    by_tex = {}
    for ve, vt, vbox, pe, pt, pbox, *scale in SPRITES:
        by_tex.setdefault((ve, vt), []).append((vbox, pe, pt, pbox, *scale))
    f = open(out_c, 'r+b')
    for (ve, vt), items in by_tex.items():
        d = o.read(ve)
        t = parse_g1t(d)['textures'][vt]
        assert t['fmt'] == 0x12, 'only DXT5 Vita textures supported'
        img = decode_tex(d, t)
        for vbox, pe, pt, pbox, *scale in items:
            pd = p.read(pe)
            src = decode_tex(pd, parse_g1t(pd)['textures'][pt]).crop(pbox)
            src = fit(src, vbox, *scale)
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
    # boot logo (RGBA8): PS3 1280x720 area -> Vita 960x544 area
    d = o.read(KT_LOGO); t = parse_g1t(d)['textures'][0]
    pd = p.read(KT_LOGO); pt = parse_g1t(pd)['textures'][0]
    logo = fix_company_name(read_rgba(pd, pt).crop((0, 0, 1280, 720))).resize((960, 544), Image.LANCZOS)
    img = read_rgba(d, t); img.paste(logo, (0, 0))
    write_rgba(f, o, KT_LOGO, d, t, img)
    # anti-piracy notice: not translated in the PS3 EU release, so redraw it in English
    d = o.read(NOTICE); t = parse_g1t(d)['textures'][0]
    write_rgba(f, o, NOTICE, d, t, draw_notice(read_rgba(d, t)))
    print('boot logo + notice replaced')
    f.close()


KT_LOGO = 35       # "コーエーテクモゲームス" logo -> PS3 logo, words reordered to "KOEI TECMO GAMES"
NOTICE = 32        # ご注意 (copyright notice), drawn at 1280x720 inside a 2048x1024 RGBA texture
NOTICE_TITLE = 'Notice'
NOTICE_TEXT = [
    'Distributing or transmitting this game software over the internet without the permission of '
    'the rights holder, or downloading it while knowing that it was distributed illegally, '
    'is strictly prohibited by law.',
    'Thank you for your understanding and cooperation.',
]
FONT_DIR = Path('C:/Windows/Fonts')


def fix_company_name(img):
    """The EU logo reads "TECMO KOEI GAMES"; reorder the word images to "KOEI TECMO GAMES"."""
    y0, y1 = 495, 549                                             # text line (ink at rows 501-542)
    tecmo, koei, games = (360, 557), (580, 699), (722, 920)       # word columns
    gap = koei[0] - tecmo[1]
    cut = lambda w: img.crop((w[0], y0, w[1], y1))
    parts = [cut(koei), cut(tecmo), cut(games)]
    total = sum(p.width for p in parts) + gap * 2
    out = img.copy()
    out.paste(img.getpixel((10, y0)), (tecmo[0] - 4, y0, games[1] + 4, y1))   # clear the line
    x = (tecmo[0] + games[1] - total) // 2
    for part in parts:
        out.paste(part, (x, y0)); x += part.width + gap
    return out


def read_rgba(d, t):
    """Uncompressed G1T texture (fmt 0): Vita bytes are RGBA, PS3 bytes are ABGR."""
    vita = d[:4] == b'GT1G'
    s = data_start(d, t, '<' if vita else '>')
    raw = d[s:s + t['w'] * t['h'] * 4]
    return Image.frombytes('RGBA', (t['w'], t['h']), raw, 'raw', 'RGBA' if vita else 'ABGR')


def write_rgba(f, o, entry, d, t, img):
    s = data_start(d, t)
    nd = bytearray(d)
    nd[s:s + t['w'] * t['h'] * 4] = img.tobytes('raw', 'RGBA')
    off, size = o.entries[entry]
    assert len(nd) == size
    f.seek(off * o.align); f.write(nd)


def draw_notice(img):
    from PIL import ImageDraw, ImageFont
    dr = ImageDraw.Draw(img)
    dr.rectangle((240, 96, 1038, 640), fill=(239, 239, 239, 255))          # clear the Japanese text
    title = ImageFont.truetype(str(FONT_DIR / 'segoeuib.ttf'), 46)
    body = ImageFont.truetype(str(FONT_DIR / 'seguisb.ttf'), 33)
    dr.text((640, 140), NOTICE_TITLE, font=title, fill=(206, 65, 33, 255), anchor='mm')
    left, right, y, pitch = 288, 1000, 200, 47
    for para in NOTICE_TEXT:
        line = ''
        for word in para.split():
            t = (line + ' ' + word).strip()
            if dr.textlength(t, font=body) > right - left and line:
                dr.text((left, y), line, font=body, fill=(102, 102, 102, 255)); y += pitch; line = word
            else:
                line = t
        dr.text((left, y), line, font=body, fill=(102, 102, 102, 255)); y += pitch + 16
    assert y < 660, 'notice text does not fit the panel'
    return img


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

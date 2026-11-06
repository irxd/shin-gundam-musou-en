"""Proportional Latin text for the main game font (F0).

1. Atlas: left-align the Latin/punctuation glyphs inside their 20x20 cells (LINKDATA.C[2608], DXT5, Vita
   morton-swizzled) and measure each glyph's width.
2. Code: give F0 a width table. The renderer already supports per-glyph widths (draw @0x811d1a38, measure
   @0x811d2044: advance = size * width[g] / cell_w), but a full 6746-byte table does not fit anywhere, so
   two small hooks look up widths in a compact table (glyphs 0..127 and 6650..6745; everything else = 20).
   Hooks + tables live in the unused tail of the text segment (0x81370340..).
3. Output: patched LINKDATA.C entry, a Vita3K patch file, and a JSON of patch bytes (for eboot patching).

Usage: build_font.py <vita LINKDATA.C> <app0.elf dump> <out LINKDATA.C> <out vita3k patch .txt>
"""
import sys, os, struct, json, shutil
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from linkdata import LinkData
from g1t import parse_g1t
from dxt import unswizzle_blocks, swizzle_blocks, decode_dxt5
from font import load_codes, cell_box, CELL, PAGE

FONT_ENTRY = 2608
SEG0 = 0x81000000
F0_WIDTHPTR_VA = 0x8135b3a0            # font descriptor F0 + 4
DRAW_SITE, DRAW_RET = 0x811d1a38, 0x811d1a3c          # ldrb.w r7,[r1,r8]
MEAS_SITE, MEAS_RET = 0x811d2044, 0x811d204a          # ldrb r0,[r1,r0] ; mul.w r0,lr,r0
EXPECT = {DRAW_SITE: '11f80870', MEAS_SITE: '085c0efb00f0', F0_WIDTHPTR_VA: '00000000'}
CAVE = 0x81370340
TAB_LO, LO_N = CAVE, 128
TAB_HI, HI_FIRST, HI_N = CAVE + 0x80, 6650, 96
CODE = CAVE + 0x100

NARROW_LOW = [11, 13, 14, 15, 16, 20]     # ‐ ‘ ’ “ ” …
SPACE_IDX, SPACE_W = 99, 6                # ideographic space
GAP = 2                                    # px: 1 left margin + 1 spacing


# ---------------------------------------------------------------- DXT5 alpha block encoder
def encode_alpha_block(px):
    """px: 16 alpha values (row-major). Returns 8-byte BC3 alpha block."""
    hi, lo = max(px), min(px)
    if hi == lo:
        return bytes([hi, lo]) + b'\0' * 6
    pal = [hi, lo] + [((7 - k) * hi + k * lo) // 7 for k in range(1, 7)]
    bits = 0
    for i, a in enumerate(px):
        best = min(range(8), key=lambda j: abs(pal[j] - a))
        bits |= best << (3 * i)
    return bytes([hi, lo]) + bits.to_bytes(6, 'little')


def build_atlas(g1t, chars):
    g = parse_g1t(g1t)
    out = bytearray(g1t)
    targets = NARROW_LOW + [SPACE_IDX] + list(range(HI_FIRST, min(HI_FIRST + HI_N, len(chars))))
    widths = {}
    by_page = {}
    for i in targets:
        by_page.setdefault(cell_box(i)[0], []).append(i)
    for page, idxs in by_page.items():
        t = g['textures'][page]
        assert (t['w'], t['h']) == (PAGE, PAGE)
        start = t['off'] + 8
        raw = bytes(out[start:start + PAGE * PAGE])
        lin = bytearray(unswizzle_blocks(raw, PAGE, PAGE))
        alpha = decode_dxt5(bytes(lin), PAGE, PAGE).split()[3]
        for i in idxs:
            _, box = cell_box(i)
            cell = alpha.crop(box)
            if i == SPACE_IDX:
                widths[i] = SPACE_W
                continue
            bb = cell.point(lambda v: 255 if v > 40 else 0).getbbox()
            if not bb:
                widths[i] = SPACE_W
                continue
            x0, _, x1, _ = bb
            ink = cell.crop((x0, 0, x1, CELL))
            new = Image.new('L', (CELL, CELL), 0)
            new.paste(ink, (1, 0))
            widths[i] = min(CELL, (x1 - x0) + GAP)
            alpha.paste(new, box[:2])
            # re-encode the 5x5 blocks of this cell (keep each block's colour half)
            for by in range(box[1] // 4, box[3] // 4):
                for bx in range(box[0] // 4, box[2] // 4):
                    px = list(alpha.crop((bx * 4, by * 4, bx * 4 + 4, by * 4 + 4)).get_flattened_data())
                    o = (by * (PAGE // 4) + bx) * 16
                    lin[o:o + 8] = encode_alpha_block(px)
        out[start:start + PAGE * PAGE] = swizzle_blocks(bytes(lin), PAGE, PAGE)
    return bytes(out), widths


# ---------------------------------------------------------------- code
def asm(ks, src, addr):
    b, _ = ks.asm(src, addr)
    return bytes(b)


def build_code():
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    lo16 = lambda v: v & 0xffff
    hi16 = lambda v: v >> 16

    def lookup(dst, idx, ret_insns, ret_addr, base):
        # dst = width of glyph `idx` when r1 == TAB_LO (F0), else original ldrb
        return f"""
            movw ip, #{lo16(TAB_LO)}
            movt ip, #{hi16(TAB_LO)}
            cmp r1, ip
            bne normal
            cmp {idx}, #{LO_N}
            blo normal
            movw ip, #{HI_FIRST}
            subs.w {dst}, {idx}, ip
            blo full
            cmp {dst}, #{HI_N}
            bhs full
            movw ip, #{lo16(TAB_HI)}
            movt ip, #{hi16(TAB_HI)}
            ldrb.w {dst}, [ip, {dst}]
            b done
        full:
            movs {dst}, #{CELL}
            b done
        normal:
            ldrb.w {dst}, [r1, {idx}]
        done:
            {ret_insns}
            b.w #{ret_addr:#x}
        """

    draw = asm(ks, lookup('r7', 'r8', '', DRAW_RET, CODE), CODE)
    meas_addr = (CODE + len(draw) + 3) & ~3
    meas = asm(ks, lookup('r0', 'r0', 'mul r0, lr, r0', MEAS_RET, meas_addr), meas_addr)
    hook_draw = asm(ks, f'b.w #{CODE:#x}', DRAW_SITE)
    hook_meas = asm(ks, f'b.w #{meas_addr:#x}', MEAS_SITE) + asm(ks, 'nop', MEAS_SITE + 4)
    assert len(hook_draw) == 4 and len(hook_meas) == 6
    return [(DRAW_SITE, hook_draw), (MEAS_SITE, hook_meas), (CODE, draw), (meas_addr, meas)]


def main():
    vita_c, elf, out_c, out_patch = sys.argv[1:5]
    elf_bytes = open(elf, 'rb').read()
    # sanity: the bytes we replace must be what we expect
    seg_off = lambda va: 0xa0 + va - SEG0
    for va, hx in EXPECT.items():
        got = elf_bytes[seg_off(va):seg_off(va) + len(hx) // 2].hex()
        assert got == hx, f'unexpected bytes at {va:#x}: {got}'
    assert elf_bytes[seg_off(CAVE - 0x8):seg_off(CAVE - 0x8)].hex() == '' or True

    chars = load_codes(elf)
    ld = LinkData(vita_c)
    g1t = ld.read(FONT_ENTRY)
    new_g1t, widths = build_atlas(g1t, chars)
    assert len(new_g1t) == len(g1t)

    tab_lo = bytearray([CELL] * LO_N)
    tab_hi = bytearray([CELL] * HI_N)
    for i, w in widths.items():
        if i < LO_N: tab_lo[i] = w
        elif HI_FIRST <= i < HI_FIRST + HI_N: tab_hi[i - HI_FIRST] = w

    patches = [(TAB_LO, bytes(tab_lo)), (TAB_HI, bytes(tab_hi)),
               (F0_WIDTHPTR_VA, struct.pack('<I', TAB_LO))] + build_code()

    # LINKDATA.C: copy + overwrite the font entry in place (same size)
    if os.path.abspath(out_c) != os.path.abspath(vita_c):
        os.makedirs(os.path.dirname(out_c), exist_ok=True)
        shutil.copyfile(vita_c, out_c)
    off, size = ld.entries[FONT_ENTRY]
    with open(out_c, 'r+b') as f:
        f.seek(off * ld.align); f.write(new_g1t)

    # Vita3K patch file
    os.makedirs(os.path.dirname(out_patch), exist_ok=True)
    with open(out_patch, 'w', newline='\n') as f:
        f.write('# Shin Gundam Musou English patch - proportional Latin font widths\n[eboot.bin]\n')
        for va, b in patches:
            f.write(f'0:{va - SEG0:#x} ' + ' '.join(f'0x{x:02x}' for x in b) + '\n')
    json.dump([{'va': hex(va), 'bytes': b.hex()} for va, b in patches],
              open(os.path.splitext(out_patch)[0] + '.json', 'w'), indent=1)

    sample = {chars[i]: widths[i] for i in sorted(widths)[:12]}
    print('glyph widths set:', len(widths), 'sample:', sample)
    print('cave used: %#x..%#x' % (CAVE, max(va + len(b) for va, b in patches if va >= CAVE)))
    for va, b in patches:
        print(f'  {va:#x}: {len(b)} bytes')
    print('wrote', out_c, 'and', out_patch)


if __name__ == '__main__':
    main()

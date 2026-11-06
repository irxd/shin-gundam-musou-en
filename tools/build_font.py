"""Proportional Latin text for the main game font (F0).

1. Atlas: left-align the Latin/punctuation glyphs inside their 20x20 cells (LINKDATA.C[2608], DXT5, Vita
   morton-swizzled) and measure each glyph's width.
2. Code: the F0 glyph function (0x811d1434) builds a `size`-wide quad sampling a full 20px cell and returns
   `size` as the advance; the layout loop uses that return value for the pen and for line wrapping.
   Three hooks make it proportional:
     A @0x811d146c  after the glyph lookup: w = width(glyph) -> spare stack slot [sp]
     B @0x811d14b4  texture x1 = x0 + w          (was x0 + cell_w)
     C @0x811d14e4  advance/quad width = size * w / 20   (r0, also the return value)
   Width lookup uses compact tables (glyphs 0..127 and 6650..6745; everything else = 20).
   Code + tables live in the unused tail after the text segment (0x81370340..), so the eboot's segment 0
   is extended (p_filesz/p_memsz) and the eboot is rebuilt as an fself.
3. Output: patched LINKDATA.C, patched eboot.bin (fself) and the patched ELF.

Usage: build_font.py <vita LINKDATA.C> <decrypted eboot.bin.elf> <self_auth.bin> <out dir>
       out dir receives LINKDATA_NGP/LINKDATA.C, eboot.bin, eboot.bin.elf
"""
import sys, os, struct, shutil
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from keystone import Ks, KS_ARCH_ARM, KS_MODE_THUMB
from linkdata import LinkData
from g1t import parse_g1t
from dxt import unswizzle_blocks, swizzle_blocks, decode_dxt5
from font import load_codes, cell_box, CELL, PAGE
from fself import make_fself, authid_from_self_auth

FONT_ENTRY = 2608
SEG0 = 0x81000000
SEG0_LIMIT = 0x81371000                     # start of segment 1
HOOK_A, RET_A = 0x811d146c, 0x811d1472      # adds r6,r0,#0 ; ldr.w r7,[r8]
HOOK_B = 0x811d14b4                         # add.w r3,fp,sl
HOOK_C = 0x811d14e4                         # ldr.w r0,[r8,#0x44]
EXPECT = {HOOK_A: '061cd8f80070', HOOK_B: '0beb0a03', HOOK_C: 'd8f84400'}
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
    """Returns [(va, bytes)] for hooks (inside existing code) and cave code (after segment 0)."""
    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    lo16 = lambda v: v & 0xffff
    hi16 = lambda v: v >> 16
    # cave A: replicate the 2 replaced instructions, then w = width(r0) -> [sp]. Scratch: r1, ip.
    cave_a_src = f"""
        adds r6, r0, #0
        ldr.w r7, [r8]
        cmp r0, #{LO_N}
        blo low
        movw ip, #{HI_FIRST}
        subs.w r1, r0, ip
        blo full
        cmp r1, #{HI_N}
        bhs full
        movw ip, #{lo16(TAB_HI)}
        movt ip, #{hi16(TAB_HI)}
        ldrb.w r1, [ip, r1]
        b store
    low:
        movw ip, #{lo16(TAB_LO)}
        movt ip, #{hi16(TAB_LO)}
        ldrb.w r1, [ip, r0]
        b store
    full:
        movs r1, #{CELL}
    store:
        str r1, [sp]
        b.w #{RET_A:#x}
    """
    cave_a = asm(ks, cave_a_src, CODE)
    # cave C (called with bl; lr is dead here): r0 = size * w / 20  (x*3277>>16 == x/20 for our range)
    cave_c_addr = (CODE + len(cave_a) + 3) & ~3
    cave_c = asm(ks, """
        ldr.w r0, [r8, #0x44]
        ldr r1, [sp]
        muls r0, r1, r0
        movw r1, #3277
        muls r0, r1, r0
        lsrs r0, r0, #16
        bx lr
    """, cave_c_addr)
    hook_a = asm(ks, f'b.w #{CODE:#x}', HOOK_A) + asm(ks, 'nop', HOOK_A + 4)
    hook_b = asm(ks, 'ldr r3, [sp]\nadd r3, fp', HOOK_B)
    hook_c = asm(ks, f'bl #{cave_c_addr:#x}', HOOK_C)
    assert (len(hook_a), len(hook_b), len(hook_c)) == (6, 4, 4), (len(hook_a), len(hook_b), len(hook_c))
    return [(HOOK_A, hook_a), (HOOK_B, hook_b), (HOOK_C, hook_c), (CODE, cave_a), (cave_c_addr, cave_c)]


# ---------------------------------------------------------------- ELF
def patch_elf(elf: bytes, patches):
    """Apply (va, bytes) patches to segment 0, growing segment 0 into the gap before segment 1."""
    e_phoff, = struct.unpack_from('<I', elf, 28)
    e_phnum, = struct.unpack_from('<H', elf, 44)
    ph = [list(struct.unpack_from('<8I', elf, e_phoff + 32 * i)) for i in range(e_phnum)]
    p_type, off0, va0, _, fs0, ms0, _, _ = ph[0]
    assert va0 == SEG0 and fs0 == ms0
    seg0 = bytearray(elf[off0:off0 + fs0])
    end = max(va + len(b) for va, b in patches)
    assert end <= SEG0_LIMIT, 'cave overflows into segment 1'
    new_fs = max(fs0, (end - SEG0 + 3) & ~3)
    seg0 += b'\0' * (new_fs - len(seg0))
    for va, b in patches:
        o = va - SEG0
        seg0[o:o + len(b)] = b
    # rebuild file: ehdr+phdrs, seg0 (grown), then the remaining segments re-laid out after it (16-aligned)
    out = bytearray(elf[:off0])
    out += seg0
    ph[0][4] = ph[0][5] = new_fs
    for i in range(1, e_phnum):
        out += b'\0' * ((-len(out)) & 0xf)
        o, fs = ph[i][1], ph[i][4]
        data = elf[o:o + fs]
        ph[i][1] = len(out)
        out += data
    for i in range(e_phnum):
        struct.pack_into('<8I', out, e_phoff + 32 * i, *ph[i])
    return bytes(out)


def main():
    vita_c, elf_path, self_auth, out_dir = sys.argv[1:5]
    elf = open(elf_path, 'rb').read()
    seg_off = lambda va: 0xa0 + va - SEG0
    for va, hx in EXPECT.items():
        got = elf[seg_off(va):seg_off(va) + len(hx) // 2].hex()
        assert got == hx, f'unexpected bytes at {va:#x}: {got} (wrong eboot version?)'

    chars = load_codes(elf_path)
    ld = LinkData(vita_c)
    g1t = ld.read(FONT_ENTRY)
    new_g1t, widths = build_atlas(g1t, chars)
    assert len(new_g1t) == len(g1t)

    tab_lo = bytearray([CELL] * LO_N)
    tab_hi = bytearray([CELL] * HI_N)
    for i, w in widths.items():
        if i < LO_N: tab_lo[i] = w
        elif HI_FIRST <= i < HI_FIRST + HI_N: tab_hi[i - HI_FIRST] = w
    patches = [(TAB_LO, bytes(tab_lo)), (TAB_HI, bytes(tab_hi))] + build_code()

    # LINKDATA.C: copy + overwrite the font entry in place (same size)
    out_c = os.path.join(out_dir, 'LINKDATA_NGP', 'LINKDATA.C')
    os.makedirs(os.path.dirname(out_c), exist_ok=True)
    shutil.copyfile(vita_c, out_c)
    off, size = ld.entries[FONT_ENTRY]
    with open(out_c, 'r+b') as f:
        f.seek(off * ld.align); f.write(new_g1t)

    new_elf = patch_elf(elf, patches)
    open(os.path.join(out_dir, 'eboot.bin.elf'), 'wb').write(new_elf)
    fself = make_fself(new_elf, authid=authid_from_self_auth(self_auth), compress=True)
    open(os.path.join(out_dir, 'eboot.bin'), 'wb').write(fself)

    print('glyph widths set:', len(widths), {chars[i]: widths[i] for i in sorted(widths)[:10]})
    for va, b in patches:
        print(f'  {va:#x}: {len(b)} bytes')
    print(f'segment 0 grown to end at {max(va + len(b) for va, b in patches):#x}; fself {len(fself)} bytes')
    print('wrote', out_dir)


if __name__ == '__main__':
    main()

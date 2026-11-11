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
   Code lives in the small gap after the text segment (segment 0 is extended into it) and in a few spots
   of the original code that our hooks leave unused; the tables live at the end of segment 1's last page
   (segment 1's file size is extended to cover them). The eboot is rebuilt as an fself.
   Supports game versions 1.00 and 1.02 (see VERSIONS).
3. Output: patched LINKDATA.C, patched eboot.bin (fself) and the patched ELF.

Usage: build_font.py <vita LINKDATA.C> <decrypted eboot.bin.elf> <self_auth.bin> <out dir>
       out dir receives LINKDATA_NGP/LINKDATA.C, eboot.bin, eboot.bin.elf
"""
import json, sys, os, struct, shutil
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
SEG1 = 0x81371000                           # start of segment 1 (= end of the gap after segment 0)
PAGE_SIZE = 0x1000

# Supported game versions: decrypted eboot ELF sha1 -> (name, shift of the text renderer code vs 1.00).
# 1.02's renderer is the same code moved by +0xa50; all hook addresses in this file are 1.00 addresses.
VERSIONS = {
    '69e7eb06314f1f1297fe15758afadad946dbb7a0': ('1.00', 0x000),
    'a3e44c93e09b713279003ae812c313851128d04f': ('1.02', 0xa50),
}

HOOK_A, RET_A = 0x811d146c, 0x811d1472      # adds r6,r0,#0 ; ldr.w r7,[r8]
HOOK_B = 0x811d14b4                         # add.w r3,fp,sl
HOOK_C = 0x811d14e4                         # ldr.w r0,[r8,#0x44]
EXPECT = {HOOK_A: '061cd8f80070', HOOK_B: '0beb0a03', HOOK_C: 'd8f84400'}
LO_N, HI_FIRST, HI_N = 128, 6650, 96        # width tables: glyphs 0..127 and 6650..6745 (else 20)

NARROW_LOW = [11, 13, 14, 15, 16, 20]     # ‐ ‘ ’ “ ” …
SPACE_IDX, SPACE_W = 99, 6                # ideographic space
GAP = 1                                    # px: 1 left margin (ink starts at x=1); tighter fit for English


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


# ---------------------------------------------------------------- code placement
def asm(ks, src, addr):
    b, _ = ks.asm(src, addr)
    assert b, f"keystone failed to assemble at {addr:#x}"
    return bytes(b)


class Space:
    """Free code regions; place() puts each routine in the smallest region it fits (4-byte aligned)."""
    def __init__(self, ks, regions):
        self.ks, self.free, self.out = ks, [list(r) for r in regions], []

    def place(self, src_fn):
        probe = max(self.free, key=lambda r: r[1] - r[0])[0]
        size = len(asm(self.ks, src_fn(probe), probe))
        for r in sorted(self.free, key=lambda r: r[1] - r[0]):
            if r[1] - r[0] >= size:
                code = asm(self.ks, src_fn(r[0]), r[0])
                assert r[0] + len(code) <= r[1]
                self.out.append((r[0], code))
                addr = r[0]
                r[0] = (r[0] + len(code) + 3) & ~3
                return addr
        raise SystemExit(f'no room for a {size}-byte routine; free: {[(hex(a), b - a) for a, b in self.free]}')


# ---------------------------------------------------------------- line wrapping / spaces / measuring
# Pre-pass line breaker 0x811d217c copies text into a buffer and inserts '\n' when the running width
# (fixed `size` per char) exceeds the box width. Render loop 0x811d1b1e advances spaces by `size`.
# Measure function 0x811d1f3a adds `size` per char. All three get real ASCII widths, and the
# breaker gets word wrap (break at the last space on the line; original behaviour as fallback).
WRAP_ENTRY = 0x811d2188      # strd r3, r4, [sp, #0x48]
WRAP_WIDTH = 0x811d2210      # ldr.w r2, [sl, #0x44]
WRAP_OVF = 0x811d22b0        # mov r0, sl ; bl kinsoku ; ...  (overflow branch)
WRAP_EMIT = 0x811d2270       # emit current char (reloads it from [sp,#4])
WRAP_NEXT = 0x811d21e6       # loop continue (next char)
KINSOKU = 0x811d1270
RENDER_SPACE = 0x811d1c6e    # ldr.w r6, [r8, #0x44]
MEASURE_ASCII = 0x811d1ff8   # ldr.w lr, [r8, #0x44] ; add sb, lr  (only the ldr is replaced: the
                             # alternate fonts, [state+0x3c] = 1..3 e.g. the numbers right-aligned in
                             # Database > records, branch to that add with their own width in lr)
BUF_SLOT = 0x50              # unused stack slot in the breaker's frame
# Text boxes (e.g. tutorials) draw each wrapped line with a per-line char cap [state+0x58] =
# box_width / size (0x811d23a0..: argument setup + bl divide), i.e. 20 chars. Proportional lines hold
# more, so the cap becomes a constant: `movs r0,#255; b 0x811d23b4`, which also frees the 16 bytes after it
# (the stores there repeat ones made just before).
LINE_CAP, LINE_CAP_END = 0x811d23a0, 0x811d23b4
# Icon width check in the breaker (0x811d2214..0x811d2264): seven compares of the char against the icon
# codes U+E019, E01C, ... E02B (step 3), each tripling the width. Rewritten compactly with the same
# result, which frees the rest of that block for our code.
PUA_CHECK, PUA_TRIPLE, PUA_DONE = 0x811d2214, 0x811d2264, 0x811d2268
# Original instructions after our overflow hook are never reached any more (no branch targets inside).
OVF_DEAD = (0x811d22b4, 0x811d22ca)
EXPECT_WRAP = {WRAP_ENTRY: 'cde91234', WRAP_WIDTH: 'daf84420', WRAP_OVF: '5046fef7ddff0028',
               RENDER_SPACE: 'd8f84460', MEASURE_ASCII: 'd8f844e0f144',
               LINE_CAP: 'd9f83000cbf86078d8f84810cbf85ca8',
               PUA_CHECK: 'c0f2ee008142', PUA_TRIPLE: 'c2eb82029044'}


def ascii_widths(chars, widths):
    """Width (in 20px cell units) of each printable ASCII char after the game's full-width mapping."""
    idx = {c: i for i, c in enumerate(chars)}
    out = bytearray()
    for c in range(0x20, 0x7f):
        g = {0x20: '　', 0x22: '”', 0x27: '’'}.get(c, chr(0xFEE0 + c))
        out.append(widths.get(idx.get(g, -1), CELL))
    return bytes(out)


# ---------------------------------------------------------------- per-string text scale
# Box draw function 0x811d22ec(state r8, text r7, ..., box sb). At 0x811d2358 the box parameters have
# just been applied to the font state, which the function saves/restores around the draw. A string
# starting with ESC + chr(0x60 + s), 16 <= s <= 31, is drawn at s/32 size: glyph width (+0x44), height
# (+0x48) and line spacing (+0x50) are scaled. ESC + any letter except 'C' is a 2-byte no-op for the
# renderer, measurer and line breaker, so the marker itself is invisible. build_text.py adds it to
# strings that need more lines than their box holds.
# ESC + chr(0x50 + s) (0x60..0x6f) is the same scale but keeps the line pitch (+0x48 + +0x50): for boxes
# that also draw their text line by line at full pitch while it types out (story text, mission
# briefings), so the finished text has the same line spacing as the text being typed.
FIT_HOOK, FIT_RET = 0x811d2358, 0x811d235c      # ldr.w r0, [sb, #0x30]
SCALE_BASE, SCALE_MIN, SCALE_MAX = 0x60, 16, 31
SCALE_BASE_PITCH = 0x50
# The line breaker 0x811d217c is also called on its own, with a box (e.g. the tutorial popup widget
# 0x812186c0 breaks the text at the box width, then draws the lines through the box draw function). It
# applies the box to the font state at 0x811d21ae (bl APPLY), only when a box is passed, and restores the
# state on exit. Hooked there to apply the box and then the same per-string scale as the box draw, so a
# shrunk text breaks at the shrunk glyph widths. (Inside the box draw function the breaker is called
# without a box: the state is already scaled there.)
BRK_APPLY, APPLY = 0x811d21ae, 0x811d0e8c
EXPECT_FIT = {FIT_HOOK: 'd9f83000', BRK_APPLY: 'fef76dfe'}
# Center banners (battle messages, orders): the text layout methods of two sibling widget classes (same
# vtable slot, 0x811d53ac and 0x811d704a in 1.00) break the text at 480 px (`movs.w r3, #0x1e0`, the
# breaker's width argument): about 22 units, narrower than the banner (about 27 units between its arrows).
# The banner is one line tall (a second line hangs below it), so widen the limit to 572 px (26 units at
# the banner's font size); build_text.py shrinks the English to fit 25 units.
BANNER_BREAK = (0x811d56f2, 0x811d725c)
BANNER_BREAK_PX = 572
EXPECT_BANNER = {va: '5ff4f073' for va in BANNER_BREAK}


def build_code(ks, sp, d, tab_lo, tab_hi, tab_ascii):
    """All hooks + routines. d = renderer shift for this game version. Returns [(va, bytes)]."""
    A = lambda va: va + d
    lo16, hi16 = (lambda v: v & 0xffff), (lambda v: v >> 16)
    hooks = []

    # --- proportional glyphs (F0 glyph function 0x811d1434)
    # word wrap first: it is the biggest routine and only fits in the gap after segment 0
    # asciiw: r0 = char, r1 = size -> r0 = scaled width (size for non-ASCII). clobbers ip.
    asciiw = sp.place(lambda at: f"""
        sub ip, r0, #0x20
        cmp ip, #95
        bhs notascii
        movw r0, #{lo16(tab_ascii)}
        movt r0, #{hi16(tab_ascii)}
        ldrb.w r0, [r0, ip]
        mul r0, r1, r0
        movw ip, #3277
        mul r0, r0, ip
        lsrs r0, r0, #16
        bx lr
    notascii:
        mov r0, r1
        bx lr
    """)
    # overflow: word wrap. state: r6 = out ptr (current char not written yet), r8 = width incl. char,
    # sb = line count, [sp,#4] = char, [sp,#BUF_SLOT] = buffer start. r0-r3, ip, lr are free.
    ovf = sp.place(lambda at: f"""
        ldr r0, [sp, #4]
        cmp r0, #0x20
        bne scan
        movs r0, #0x0a
        strb r0, [r6], #1
        mov.w r8, #0
        add.w sb, sb, #1
        b.w #{A(WRAP_NEXT):#x}
    scan:
        ldr r2, [sp, #{BUF_SLOT}]
        mov r3, r6
    back:
        cmp r3, r2
        bls fallback
        ldrb r0, [r3, #-1]!
        cmp r0, #0x0a
        beq fallback
        cmp r0, #0x20
        bne back
        movs r0, #0x0a
        strb r0, [r3], #1
        add.w sb, sb, #1
        mov.w r8, #0
    tail:
        cmp r3, r6
        bhs tail_done
        ldrb r0, [r3], #1
        cmp r0, #0x1b
        bne not_esc
        ldrb r0, [r3]
        adds r3, #1
        cmp r0, #0x43
        bne tail
        adds r3, #1
        b tail
    not_esc:
        cmp r0, #0x80
        blo tail_ascii
        cmp r0, #0xc0
        blo tail
        ldr.w r0, [sl, #0x44]
        add r8, r0
        b tail
    tail_ascii:
        ldr.w r1, [sl, #0x44]
        bl #{asciiw:#x}
        add r8, r0
        b tail
    tail_done:
        ldr r0, [sp, #4]
        ldr.w r1, [sl, #0x44]
        bl #{asciiw:#x}
        add r8, r0
        b.w #{A(WRAP_EMIT):#x}
    fallback:
        mov r0, sl
        ldr r1, [sp, #4]
        bl #{A(KINSOKU):#x}
        cmp r0, #0
        bne do_break
        b.w #{A(WRAP_EMIT):#x}
    do_break:
        movs r0, #0x0a
        strb r0, [r6], #1
        ldr r0, [sp, #4]
        ldr.w r1, [sl, #0x44]
        bl #{asciiw:#x}
        mov r8, r0
        add.w sb, sb, #1
        b.w #{A(WRAP_EMIT):#x}
    """)
    # cave A: replicate the 2 replaced instructions, then w = width(r0) -> [sp]. Scratch: r1, ip.
    cave_a = sp.place(lambda at: f"""
        adds r6, r0, #0
        ldr.w r7, [r8]
        cmp r0, #{LO_N}
        blo low
        movw ip, #{HI_FIRST}
        subs.w r1, r0, ip
        blo full
        cmp r1, #{HI_N}
        bhs full
        movw ip, #{lo16(tab_hi)}
        movt ip, #{hi16(tab_hi)}
        ldrb.w r1, [ip, r1]
        b store
    low:
        movw ip, #{lo16(tab_lo)}
        movt ip, #{hi16(tab_lo)}
        ldrb.w r1, [ip, r0]
        b store
    full:
        movs r1, #{CELL}
    store:
        str r1, [sp]
        b.w #{A(RET_A):#x}
    """)
    # --- per-string text scale
    # r2 = font state (low register: 2-byte loads/stores, the 1.02 code gap is tiny), r3 = line pitch
    # (+0x48 glyph height + +0x50 line gap); r1 = scale/32. Pitch is scaled too, except for the
    # keep-pitch markers; the gap becomes pitch - new height. r2, r3 are free here (the box draw
    # function moved its r2/r3 arguments to sl/sb on entry).
    def scale(off):
        return f"""
        ldr r0, [r2, #{off:#x}]
        muls r0, r1, r0
        asrs r0, r0, #5
        str r0, [r2, #{off:#x}]"""
    fit = sp.place(lambda at: f"""
        ldrb r0, [r7]
        cmp r0, #0x1b
        bne done
        ldrb r1, [r7, #1]
        subs r1, #{SCALE_BASE_PITCH}
        cmp r1, #{SCALE_MIN}
        blo done
        mov r2, r8
        ldr r3, [r2, #0x48]
        ldr r0, [r2, #0x50]
        add r3, r0
        cmp r1, #{SCALE_MAX}
        bls keep
        subs r1, #{SCALE_BASE - SCALE_BASE_PITCH}
        cmp r1, #{SCALE_MAX}
        bhi done
        muls r3, r1, r3
        asrs r3, r3, #5
    keep:
        {scale(0x44)}
        {scale(0x48)}
        subs r3, r3, r0
        str r3, [r2, #0x50]
    done:
        ldr.w r0, [sb, #0x30]
        bx lr
    """)
    # breaker with a box (bl from BRK_APPLY; r0 = state, r1 = box, r4 = box, sl = state, r7 = text):
    # apply the box, then fit with r8 = state, sb = box (both set again right after the hook).
    # r0-r3 are free after it.
    brk = sp.place(lambda at: f"""
        push {{r4, lr}}
        bl #{A(APPLY):#x}
        mov r8, sl
        mov sb, r4
        bl #{fit:#x}
        pop {{r4, pc}}
    """)
    # cave C (called with bl; lr is dead here): r0 = size * w / 20  (x*3277>>16 == x/20 for our range)
    cave_c = sp.place(lambda at: """
        ldr.w r0, [r8, #0x44]
        ldr r1, [sp]
        muls r0, r1, r0
        movw r1, #3277
        muls r0, r1, r0
        lsrs r0, r0, #16
        bx lr
    """)
    # breaker char width: r1 = char (keep), r0 live (keep) -> r2
    width = sp.place(lambda at: f"""
        push {{r0, r1, lr}}
        mov r0, r1
        ldr.w r1, [sl, #0x44]
        bl #{asciiw:#x}
        mov r2, r0
        pop {{r0, r1, pc}}
    """)
    space = sp.place(lambda at: f"""
        push {{r0, r1, lr}}
        movs r0, #0x20
        ldr.w r1, [r8, #0x44]
        bl #{asciiw:#x}
        mov r6, r0
        pop {{r0, r1, pc}}
    """)
    # measurer char width (bl from MEASURE_ASCII): r2 = char -> lr = width, added by the original
    # `add sb, lr` after the hook. r0-r2 are free there.
    measure = sp.place(lambda at: f"""
        push {{lr}}
        mov r0, r2
        ldr.w r1, [r8, #0x44]
        bl #{asciiw:#x}
        pop {{r1}}
        mov lr, r0
        bx r1
    """)
    entry = sp.place(lambda at: f"""
        strd r3, r4, [sp, #0x48]
        str r1, [sp, #{BUF_SLOT}]
        bx lr
    """)
    hooks = [
        (A(HOOK_A), asm(ks, f'b.w #{cave_a:#x}', A(HOOK_A)) + asm(ks, 'nop', A(HOOK_A) + 4)),
        (A(HOOK_B), asm(ks, 'ldr r3, [sp]\nadd r3, fp', A(HOOK_B))),
        (A(HOOK_C), asm(ks, f'bl #{cave_c:#x}', A(HOOK_C))),
        (A(WRAP_ENTRY), asm(ks, f'bl #{entry:#x}', A(WRAP_ENTRY))),
        (A(WRAP_WIDTH), asm(ks, f'bl #{width:#x}', A(WRAP_WIDTH))),
        (A(WRAP_OVF), asm(ks, f'b.w #{ovf:#x}', A(WRAP_OVF))),
        (A(RENDER_SPACE), asm(ks, f'bl #{space:#x}', A(RENDER_SPACE))),
        (A(MEASURE_ASCII), asm(ks, f'bl #{measure:#x}', A(MEASURE_ASCII))),
        (A(FIT_HOOK), asm(ks, f'bl #{fit:#x}', A(FIT_HOOK))),     # returns to FIT_RET
        (A(BRK_APPLY), asm(ks, f'bl #{brk:#x}', A(BRK_APPLY))),
    ]
    assert [len(b) for _, b in hooks] == [6, 4, 4, 4, 4, 4, 4, 4, 4, 4], [len(b) for _, b in hooks]
    return hooks + sp.out


def fixed_rewrites(ks, d):
    """In-place rewrites that also free code space. Returns ([(va, bytes)], [free regions])."""
    A = lambda va: va + d
    cap = asm(ks, f'movs r0, #255\nb #{A(LINE_CAP_END):#x}', A(LINE_CAP))
    assert len(cap) == 4
    # r0 = 0x8099 here (movw just before the width hook; our width routine preserves r0/r1)
    pua = asm(ks, f"""
        movt r0, #0xee
        subs r0, r1, r0
        cmp r0, #0x12
        bhi #{A(PUA_DONE):#x}
        movw ip, #0x9249
        movt ip, #0x4
        lsr.w ip, ip, r0
        tst.w ip, #1
        bne #{A(PUA_TRIPLE):#x}
        b #{A(PUA_DONE):#x}
    """, A(PUA_CHECK))
    free = [((A(PUA_CHECK) + len(pua) + 3) & ~3, A(PUA_TRIPLE)),
            ((A(LINE_CAP) + 4 + 3) & ~3, A(LINE_CAP_END)),
            (A(OVF_DEAD[0]), A(OVF_DEAD[1]))]
    banner = [(A(va), asm(ks, f'movs.w r3, #{BANNER_BREAK_PX:#x}', A(va))) for va in BANNER_BREAK]
    assert all(len(b) == 4 for _, b in banner)
    return [(A(LINE_CAP), cap), (A(PUA_CHECK), pua)] + banner, free


# ---------------------------------------------------------------- ELF
def segments(elf):
    e_phoff, = struct.unpack_from('<I', elf, 28)
    e_phnum, = struct.unpack_from('<H', elf, 44)
    return e_phoff, [list(struct.unpack_from('<8I', elf, e_phoff + 32 * i)) for i in range(e_phnum)]


def patch_elf(elf: bytes, patches):
    """Apply (va, bytes) patches. Segment 0 may grow into the gap before segment 1. Segment 1 may hold
    data up to the end of its last page: its file size then covers its whole bss (zeros, as before)."""
    e_phoff, ph = segments(elf)
    assert ph[0][2] == SEG0 and ph[0][4] == ph[0][5] and ph[1][2] == SEG1
    placed = 0
    segs = []
    for i, p in enumerate(ph):
        data = bytearray(elf[p[1]:p[1] + p[4]])
        if i < 2:
            va = p[2]
            limit = SEG1 if i == 0 else (va + p[5] + PAGE_SIZE - 1) & ~(PAGE_SIZE - 1)
            mine = [(a, b) for a, b in patches if va <= a < limit]
            placed += len(mine)
            end = max([a + len(b) for a, b in mine], default=va)
            assert end <= limit, f'segment {i}: patch ends at {end:#x}, past {limit:#x}'
            size = max(len(data), (end - va + 3) & ~3)
            data += b'\0' * (size - len(data))
            for a, b in mine:
                data[a - va:a - va + len(b)] = b
            p[4] = len(data)
            p[5] = max(p[5], len(data))
        segs.append(data)
    assert placed == len(patches), 'patch outside segments 0/1'
    # rebuild file: ehdr+phdrs, then the segments one after another (16-aligned)
    out = bytearray(elf[:ph[0][1]])
    for i, p in enumerate(ph):
        out += b'\0' * ((-len(out)) & 0xf)
        p[1] = len(out)
        out += segs[i]
    for i in range(len(ph)):
        struct.pack_into('<8I', out, e_phoff + 32 * i, *ph[i])
    return bytes(out)


def check_sites(elf, d):
    seg_off = lambda va: 0xa0 + va - SEG0
    for va, hx in {**EXPECT, **EXPECT_WRAP, **EXPECT_FIT, **EXPECT_BANNER}.items():
        got = elf[seg_off(va + d):seg_off(va + d) + len(hx) // 2].hex()
        if got != hx:
            return f'unexpected bytes at {va + d:#x}: {got}'
    return None


def dlc_path(elf):
    """The DLC loaders mount each DLC (the ownership check stays) and then list/open 'addcont0:' + folder name.
    rePatch's reAddcont did not work for this game on hardware, so read the DLC files from app0:DLC/ instead,
    i.e. ux0:rePatch/PCSG00278/DLC/<DLC folder>/ (tools/build_dlc.py). Only these loaders use this copy of the
    string; the device table has its own 'addcont0:'."""
    ctx = b'DSC\0DMS\0%s%s\0\0\0\0addcont0:\0'
    assert elf.count(ctx) == 1, 'DLC path string not found'
    off = elf.find(ctx) + ctx.index(b'addcont0:')
    _, ph = segments(elf)
    p = next(p for p in ph[:2] if p[1] <= off < p[1] + p[4])
    new = b'app0:DLC/'
    assert len(new) == len(b'addcont0:')
    return [(p[2] + off - p[1], new)]


def detect_version(elf):
    import hashlib
    h = hashlib.sha1(elf).hexdigest()
    if h in VERSIONS:
        name, d = VERSIONS[h]
    else:   # unknown dump: accept it only if every hook site matches for exactly one known version
        ok = [v for v in VERSIONS.values() if check_sites(elf, v[1]) is None]
        assert len(ok) == 1, f'unsupported eboot (sha1 {h}); expected the decrypted 1.00 or 1.02 eboot'
        name, d = ok[0]
        print(f'warning: unknown eboot sha1 {h}; hook sites match version {name}')
    err = check_sites(elf, d)
    assert err is None, err
    return name, d


def main():
    vita_c, elf_path, self_auth, out_dir = sys.argv[1:5]
    elf = open(elf_path, 'rb').read()
    version, d = detect_version(elf)
    _, ph = segments(elf)

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
    tab_ascii = ascii_widths(chars, widths)
    # tables: right after segment 1's bss, inside its last page
    data = (ph[1][2] + ph[1][5] + 15) & ~15
    t_lo, t_hi, t_ascii = data, data + LO_N, data + LO_N + HI_N
    tables = [(t_lo, bytes(tab_lo)), (t_hi, bytes(tab_hi)), (t_ascii, bytes(tab_ascii))]

    ks = Ks(KS_ARCH_ARM, KS_MODE_THUMB)
    rewrites, free = fixed_rewrites(ks, d)
    gap = ((ph[0][2] + ph[0][4] + 3) & ~3, SEG1)
    sp = Space(ks, free + [gap])
    code = build_code(ks, sp, d, t_lo, t_hi, t_ascii)
    patches = tables + rewrites + code + dlc_path(elf)

    # LINKDATA.C: copy + overwrite the font entry in place (same size)
    out_c = os.path.join(out_dir, 'LINKDATA_NGP', 'LINKDATA.C')
    os.makedirs(os.path.dirname(out_c), exist_ok=True)
    shutil.copyfile(vita_c, out_c)
    off, size = ld.entries[FONT_ENTRY]
    with open(out_c, 'r+b') as f:
        f.seek(off * ld.align); f.write(new_g1t)

    new_elf = patch_elf(elf, patches)
    open(os.path.join(out_dir, 'eboot.bin.elf'), 'wb').write(new_elf)
    # uncompressed: keeps the release xdelta small (only our changes, not the whole recompressed eboot)
    fself = make_fself(new_elf, authid=authid_from_self_auth(self_auth), compress=False)
    open(os.path.join(out_dir, 'eboot.bin'), 'wb').write(fself)

    # ASCII advance widths for build_text.py's pre-wrapping -> build/ascii_widths.json
    wpath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build', 'ascii_widths.json')
    json.dump({chr(0x20 + i): tab_ascii[i] for i in range(len(tab_ascii))}, open(wpath, 'w'), indent=0)

    print(f'game version {version} (renderer shift {d:#x})')
    for va, b in sorted(patches):
        print(f'  {va:#x}: {len(b)} bytes')
    print('free left:', [(hex(a), b - a) for a, b in sp.free])
    print(f'fself {len(fself)} bytes')
    print('wrote', out_dir)


if __name__ == '__main__':
    main()

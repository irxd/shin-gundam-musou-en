"""Main game font (F0): glyph code list from the game ELF + atlas pages from LINKDATA.C[2608]."""
import struct, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from g1t import parse_g1t
from dxt import unswizzle_blocks, decode_dxt5

CODES_VA, CODES_COUNT = 0x813722b8, 6746        # glyph code list (segment 1; same in 1.00 and 1.02)
CELL, COLS, PER_PAGE, PAGE = 20, 51, 51 * 51, 1024

def load_codes(elf_path):
    d = open(elf_path, 'rb').read()
    e_phoff, = struct.unpack_from('<I', d, 28)
    e_phnum, = struct.unpack_from('<H', d, 44)
    for i in range(e_phnum):
        _, off, va, _, fs, _, _, _ = struct.unpack_from('<8I', d, e_phoff + 32 * i)
        if va <= CODES_VA < va + fs:
            break
    codes = struct.unpack_from(f'<{CODES_COUNT}I', d, off + CODES_VA - va)
    return [c.to_bytes((c.bit_length() + 7) // 8, 'big').decode('utf-8') for c in codes]

def load_pages(g1t_bytes):
    g = parse_g1t(g1t_bytes); pages = []
    for t in g['textures']:
        raw = g1t_bytes[t['off'] + 8:t['off'] + 8 + t['w'] * t['h']]
        pages.append(decode_dxt5(unswizzle_blocks(raw, t['w'], t['h']), t['w'], t['h']))
    return g, pages

def cell_box(index):
    page, k = divmod(index, PER_PAGE)
    r, c = divmod(k, COLS)
    return page, (c * CELL, r * CELL, c * CELL + CELL, r * CELL + CELL)

"""Minimal Python port of vitasdk's vita-make-fself (src/vita-make-fself/vita-make-fself.c).

Differences from the original tool:
  * the module NID inside sceModuleInfo is NOT rewritten (keeps the game's original NID)
  * authid can be taken from FAGDec's self_auth.bin
Output: 0x1000-byte header area, then the whole ELF (uncompressed, segments at 0x1000 + p_offset as in an
official SELF) or each segment zlib-compressed one after another (vita-make-fself layout).
"""
import struct, hashlib, zlib

HEADER_LEN = 0x1000
DIGEST_CONSTANT = bytes([0x62, 0x7C, 0xB1, 0x80, 0x8A, 0xB9, 0x38, 0xE3, 0x2C, 0x8C,
                         0x09, 0x17, 0x08, 0x72, 0x6A, 0x57, 0x9E, 0x25, 0x86, 0xE4])
SCE_SELF_TYPE_NPDRM = 8
SIZEOF = dict(header=0x80, appinfo=0x20, ehdr=0x34, phdr=0x20, seginfo=0x20, version=0x10,
              ci4=0x50, ci5=0x110, ci6=0x110, ci7=0x50)


def authid_from_self_auth(path):
    return struct.unpack_from('<Q', open(path, 'rb').read(), 0)[0]


def make_fself(elf: bytes, authid=0x2F00000000000001, compress=True, self_type=SCE_SELF_TYPE_NPDRM) -> bytes:
    e_type, = struct.unpack_from('<H', elf, 16)
    e_entry, e_phoff = struct.unpack_from('<II', elf, 24)
    e_phentsize, e_phnum = struct.unpack_from('<HH', elf, 42)
    phdrs = [bytearray(elf[e_phoff + i * e_phentsize:e_phoff + i * e_phentsize + 0x20]) for i in range(e_phnum)]
    for ph in phdrs:   # "fixup alignment"
        if struct.unpack_from('<I', ph, 28)[0] > 0x1000:
            struct.pack_into('<I', ph, 28, 0x1000)

    elf_offset = SIZEOF['header'] + SIZEOF['appinfo']
    phdr_offset = (elf_offset + SIZEOF['ehdr'] + 0xf) & ~0xf
    section_info_offset = phdr_offset + SIZEOF['phdr'] * e_phnum
    sceversion_offset = section_info_offset + SIZEOF['seginfo'] * e_phnum
    controlinfo_offset = sceversion_offset + SIZEOF['version']
    controlinfo_size = SIZEOF['ci4'] + SIZEOF['ci5'] + SIZEOF['ci6'] + SIZEOF['ci7']

    out = bytearray(HEADER_LEN)
    struct.pack_into('<QIIQQ', out, 0x80, authid, 0, self_type, 0x1000000000000, 0)          # appinfo
    myhdr = bytearray(0x34)
    myhdr[0:8] = b'\x7fELF\x01\x01\x01\x00'
    struct.pack_into('<HHIIIIIHHHHHH', myhdr, 16, e_type, 0x28, 1, e_entry, 0x34, 0, 0x05000000,
                     0x34, 0x20, e_phnum, 0, 0, 0)
    out[elf_offset:elf_offset + 0x34] = myhdr
    for i, ph in enumerate(phdrs):
        out[phdr_offset + 0x20 * i:phdr_offset + 0x20 * (i + 1)] = ph
    struct.pack_into('<IIII', out, sceversion_offset, 1, 0, 16, 0)
    p = controlinfo_offset
    ci4 = bytearray(SIZEOF['ci4']); struct.pack_into('<III', ci4, 0, 4, SIZEOF['ci4'], 1)
    ci4[0x10:0x24] = DIGEST_CONSTANT; ci4[0x24:0x44] = hashlib.sha256(elf).digest()
    ci5 = bytearray(SIZEOF['ci5']); struct.pack_into('<III', ci5, 0, 5, SIZEOF['ci5'], 1)
    ci6 = bytearray(SIZEOF['ci6']); struct.pack_into('<IIII', ci6, 0, 6, SIZEOF['ci6'], 1, 0)
    struct.pack_into('<I', ci6, 0x10, 1)                                                       # is_used
    ci7 = bytearray(SIZEOF['ci7']); struct.pack_into('<II', ci7, 0, 7, SIZEOF['ci7'])
    for ci in (ci4, ci5, ci6, ci7):
        out[p:p + len(ci)] = ci; p += len(ci)

    seginfos = []
    if not compress:
        # uncompressed: the whole ELF at HEADER_LEN, so every segment is at HEADER_LEN + p_offset, as in an
        # official SELF. Some loaders (Vita3K+ 1.4) read the segments at those offsets and crash on the
        # vita-make-fself layout (segments packed one after another).
        out += elf
        out += b'\0' * ((4 - len(out) % 4) % 4)
        for ph in phdrs:
            p_offset, p_filesz = struct.unpack_from('<I', ph, 4)[0], struct.unpack_from('<I', ph, 16)[0]
            seginfos.append((HEADER_LEN + p_offset, (p_filesz + 3) & ~3, 1, 2))
    for i, ph in enumerate(phdrs if compress else ()):
        p_offset, p_filesz = struct.unpack_from('<I', ph, 4)[0], struct.unpack_from('<I', ph, 16)[0]
        data = elf[p_offset:p_offset + p_filesz]
        offset = len(out)
        if compress:
            data = zlib.compress(data, 9); comp = 2
        else:
            comp = 1
        out += data
        pad = ((len(data) + 3) & ~3) - len(data)
        out += b'\0' * pad
        length = len(data) + pad
        seginfos.append((offset, length, comp, 2))
        if i + 1 != len(phdrs):
            out += b'\0' * ((0x10 - ((offset + length) & 0xf)) & 0xf)
    for i, si in enumerate(seginfos):
        struct.pack_into('<QQQQ', out, section_info_offset + 0x20 * i, *si)

    struct.pack_into('<IIHHIQQQQQQQQQQQQQQ', out, 0,
                     0x454353, 3, 0xC0, 1, 0x600, HEADER_LEN, len(elf), len(out), 0, 4, 0x80,
                     elf_offset, phdr_offset, 0, section_info_offset, sceversion_offset,
                     controlinfo_offset, controlinfo_size, 0)
    return bytes(out)

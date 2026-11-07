"""Extract the ELF from a decrypted (fake-signed) SELF, e.g. FAGDec's eboot.bin output.

Usage: unfself.py <eboot.bin (SCE, decrypted)> <eboot.bin.elf>

Layout (as written by vita-make-fself / tools/fself.py): SCE header, ELF header copy at elf_offset,
program headers at phdr_offset, one segment-info entry per segment (offset, length, compression 1=plain
2=zlib, encryption 2=plain).
"""
import struct, sys, zlib


def unfself(d: bytes) -> bytes:
    (magic, _, _, _, _, _, elf_size, _, _, _, _, elf_off, phdr_off, _, seginfo_off,
     *_rest) = struct.unpack_from('<IIHHIQQQQQQQQQQQQQQ', d, 0)
    assert magic == 0x454353, 'not a SELF'
    ehdr = d[elf_off:elf_off + 0x34]
    e_phoff, = struct.unpack_from('<I', ehdr, 28)
    e_phnum, = struct.unpack_from('<H', ehdr, 44)
    out = bytearray(elf_size)
    out[0:0x34] = ehdr
    for i in range(e_phnum):
        ph = d[phdr_off + 32 * i:phdr_off + 32 * (i + 1)]
        out[e_phoff + 32 * i:e_phoff + 32 * (i + 1)] = ph
        p_offset, p_filesz = struct.unpack_from('<I', ph, 4)[0], struct.unpack_from('<I', ph, 16)[0]
        off, length, comp, enc = struct.unpack_from('<4Q', d, seginfo_off + 32 * i)
        assert enc == 2, 'segment is encrypted: decrypt it first (FAGDec)'
        data = d[off:off + length]
        if comp == 2:
            data = zlib.decompress(data)
        data = data[:p_filesz]
        assert len(data) == p_filesz, f'segment {i}: {len(data)} != {p_filesz}'
        out[p_offset:p_offset + p_filesz] = data
    return bytes(out)


if __name__ == '__main__':
    src, dst = sys.argv[1:3]
    open(dst, 'wb').write(unfself(open(src, 'rb').read()))
    print('wrote', dst)

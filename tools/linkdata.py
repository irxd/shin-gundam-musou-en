"""LINKDATA archive reader/writer (PS3 = big-endian, Vita = little-endian).

Header : u32 magic (0x77df9), u32 count, u32 align (0x800), u32 0
Entries: u64 block_offset, u32 size, u32 0     (offset is in `align`-sized blocks)
Data   : each entry starts on an `align` boundary, uncompressed.
"""
import struct

MAGIC = 0x77df9


class LinkData:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        h = self.f.read(16)
        for e in '<>':
            magic, count, align, _ = struct.unpack(e + '4I', h)
            if magic == MAGIC:
                break
        else:
            raise ValueError(f'{path}: not a LINKDATA file')
        self.endian, self.align = e, align
        self.entries = [struct.unpack(e + 'QII', self.f.read(16))[:2] for _ in range(count)]

    def __len__(self):
        return len(self.entries)

    def read(self, i):
        off, size = self.entries[i]
        self.f.seek(off * self.align)
        return self.f.read(size)


def write_linkdata(path, blobs, endian='<', align=0x800):
    """Write a LINKDATA archive from a list of byte strings."""
    def pad(n):
        return (n + align - 1) // align * align

    header_size = pad(16 + 16 * len(blobs))
    table, pos = [], header_size
    for b in blobs:
        table.append((pos // align, len(b)))
        pos = pad(pos + len(b)) if b else pos
    with open(path, 'wb') as f:
        f.write(struct.pack(endian + '4I', MAGIC, len(blobs), align, 0))
        for off, size in table:
            f.write(struct.pack(endian + 'QII', off, size, 0))
        f.write(b'\0' * (header_size - f.tell()))
        for (off, size), b in zip(table, blobs):
            if not b:
                continue
            f.seek(off * align)
            f.write(b)
            f.write(b'\0' * (pad(size) - size))

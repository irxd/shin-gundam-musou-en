"""Set the game's name in sce_sys/param.sfo (LiveArea bubble / Vita3K game list).

Usage: build_sfo.py <original param.sfo> <output param.sfo>

PSF layout: header (magic '\\0PSF', version, key table, data table, count), then 16-byte index entries
(key offset u16, format u16, length u32, max length u32, data offset u32). Strings (fmt 0x204) are
NUL-terminated UTF-8 inside a fixed max-length slot, so they can be replaced in place.
"""
import struct, sys

TITLE = 'Shin Gundam Musou'
KEYS = ('TITLE', 'TITLE_00', 'STITLE', 'STITLE_00')    # _00 = shown when the system language is Japanese


def set_strings(sfo: bytes, values: dict, required=('TITLE', 'STITLE')) -> bytes:
    """Replace the given string keys that exist in the file (an update's param.sfo has no *_00 keys)."""
    d = bytearray(sfo)
    magic, _, key_tab, data_tab, n = struct.unpack_from('<4sIIII', d)
    assert magic == b'\0PSF'
    done = set()
    for i in range(n):
        ko, fmt, ln, mx, do = struct.unpack_from('<HHIII', d, 20 + 16 * i)
        key = d[key_tab + ko:d.index(b'\0', key_tab + ko)].decode()
        if key in values:
            assert fmt == 0x204
            v = values[key].encode('utf-8') + b'\0'
            assert len(v) <= mx, f'{key}: {len(v)} > {mx} bytes'
            d[data_tab + do:data_tab + do + mx] = v + b'\0' * (mx - len(v))
            struct.pack_into('<I', d, 20 + 16 * i + 4, len(v))
            done.add(key)
    assert set(required) <= done, f'missing keys: {set(required) - done}'
    return bytes(d)


def main():
    src, dst = sys.argv[1:3]
    import os
    out = set_strings(open(src, 'rb').read(), {k: TITLE for k in KEYS})
    os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
    open(dst, 'wb').write(out)
    print(f'{dst}: title set to {TITLE!r}')


if __name__ == '__main__':
    main()

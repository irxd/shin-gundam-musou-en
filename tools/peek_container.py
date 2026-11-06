"""Peek into a LINKDATA entry that is a simple container: u32 n, u32 header_size?, (u32 off, u32 size)*n ..."""
import sys, struct
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, 'tools')
from linkdata import LinkData
ld = LinkData(sys.argv[1]); i = int(sys.argv[2]); e = ld.endian
d = ld.read(i)
print(f'entry {i} size {len(d)} head {d[:64].hex(" ")}')
n = struct.unpack_from(e + 'I', d)[0]
w = struct.unpack_from(e + f'{min(2 + 2 * n, 64)}I', d)
print('u32s:', [hex(x) for x in w])

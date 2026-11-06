"""Find glyph code tables: consecutive kana U+3041..U+3046 stored as u16/u32 LE or BE with a fixed stride."""
import sys, re, os, mmap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from linkdata import LinkData
codes = [0x3041 + k for k in range(6)]
pats = []
for width, fmt in ((2, '<H'), (2, '>H'), (4, '<I'), (4, '>I')):
    import struct
    for stride in range(width, 49, 2):
        gap = b'.' * 0 if stride == width else b'.{%d}' % (stride - width)
        pat = gap.join(re.escape(struct.pack(fmt, c)) for c in codes)
        pats.append((fmt, stride, re.compile(pat, re.S)))
def scan(name, d):
    for fmt, stride, r in pats:
        for m in r.finditer(d):
            print(f'{name} @{m.start():#x} fmt={fmt} stride={stride}')
for path in sys.argv[1:]:
    if os.path.basename(path).startswith('LINKDATA.'):
        ld = LinkData(path)
        for i in range(len(ld)):
            scan(f'{os.path.basename(path)}[{i}]', ld.read(i))
    else:
        scan(os.path.basename(path), open(path, 'rb').read())

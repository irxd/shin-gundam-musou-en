"""Search all LINKDATA archives (and loose files) of a game folder for strings in several encodings."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8'); sys.path.insert(0, os.path.dirname(__file__))
from linkdata import LinkData
root, needles = sys.argv[1], sys.argv[2:]
encs = ('utf-8', 'utf-16-le', 'utf-16-be', 'cp932')
pats = [(n, e, n.encode(e)) for n in needles for e in encs]
for dp, _, fs in os.walk(root):
    for fn in fs:
        path = os.path.join(dp, fn)
        if fn.startswith('LINKDATA.'):
            ld = LinkData(path)
            for i in range(len(ld)):
                d = ld.read(i)
                for n, e, b in pats:
                    j = d.find(b)
                    if j >= 0: print(f'{os.path.relpath(path, root)}[{i}] size={len(d)} @{j:#x} {e}: {n}  head={d[:8].hex()}')
        elif os.path.getsize(path) < 200_000_000:
            d = open(path, 'rb').read()
            for n, e, b in pats:
                if b in d: print(f'{os.path.relpath(path, root)} {e}: {n}')

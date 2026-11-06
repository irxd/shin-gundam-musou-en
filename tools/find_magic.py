"""Find which LINKDATA entries contain given magic byte strings (anywhere inside)."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from linkdata import LinkData
path, magics = sys.argv[1], [m.encode('latin1') for m in sys.argv[2:]]
ld = LinkData(path)
for i in range(len(ld)):
    d = ld.read(i)
    for m in magics:
        pos, hits = 0, []
        while (pos := d.find(m, pos)) >= 0: hits.append(pos); pos += 1
        if hits: print(f'{os.path.basename(path)}[{i}] size={len(d)} {m.decode("latin1")} x{len(hits)} at {[hex(h) for h in hits[:4]]} head={d[:8].hex()}')

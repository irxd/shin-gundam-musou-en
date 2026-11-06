import struct, sys, re
sys.stdout.reconfigure(encoding='utf-8')
p, idx = sys.argv[1], [int(x) for x in sys.argv[2:]]
f = open(p, 'rb'); magic, count, align, _ = struct.unpack('<4I', f.read(16))
ents = [struct.unpack('<4I', f.read(16)) for _ in range(count)]
for i in idx:
    off, _, sz, _ = ents[i]; f.seek(off * align); d = f.read(sz)
    print(f'===== entry {i} size {sz}')
    for o in range(0, min(sz, 0x80), 16): print(f'  {o:04x}: {d[o:o+16].hex(" ")}')
    strs = [(m.start(), m.group().decode('utf-8', 'replace')) for m in re.finditer(rb'[^\x00]{2,}', d) if re.search(rb'[\x80-\xff]', m.group())]
    print(f'  {len(strs)} non-ASCII strings; first:'); [print(f'   @{o:05x} {s[:70]}') for o, s in strs[:8]]

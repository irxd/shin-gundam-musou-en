import struct, sys, collections
p = sys.argv[1]
f = open(p, 'rb')
magic, count, align, _ = struct.unpack('<4I', f.read(16))
ents = [struct.unpack('<4I', f.read(16)) for _ in range(count)]
print(f'magic={magic:#x} count={count} align={align:#x}')
for i, e in enumerate(ents[:12]): print(i, [hex(x) for x in e])
# hypothesis: (block_off, ?, size, flag)
fsz = f.seek(0, 2)
bad = 0; exts = collections.Counter(); flags = collections.Counter()
for i, (off, b, sz, fl) in enumerate(ents):
    flags[(b, fl)] += 1
    if off * align + sz > fsz: bad += 1; continue
    if sz == 0: exts['<empty>'] += 1; continue
    f.seek(off * align); h = f.read(16)
    exts[h[:4]] += 1
print('out-of-range:', bad)
print('(field1,field3) values:', flags.most_common(8))
print('first-4-byte signatures:', exts.most_common(25))

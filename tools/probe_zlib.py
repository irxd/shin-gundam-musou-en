import struct, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
for p in sys.argv[1:]:
    f = open(p, 'rb'); magic, count, align, _ = struct.unpack('<4I', f.read(16))
    ents = [struct.unpack('<4I', f.read(16)) for _ in range(count)]
    zl = 0; pos = collections.Counter(); samples = []
    for i, (off, _, sz, _) in enumerate(ents):
        if not sz: continue
        f.seek(off * align); d = f.read(min(sz, 0x400))
        for sig in (b'\x78\x9c', b'\x78\xda', b'\x78\x01', b'\x78\x5e'):
            j = d.find(sig)
            if 0 <= j < 0x200:
                zl += 1; pos[j] += 1
                if len(samples) < 4: samples.append((i, sz, j, d[:j+4].hex()))
                break
    print(f'#### {p}: {zl}/{count} entries have a zlib header in first 0x200 bytes; header offsets: {pos.most_common(6)}')
    for s in samples: print('   ', s)

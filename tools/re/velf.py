"""Minimal loader for Vita ELF dumps (Vita3K elfdumps): segments, memory reads, import tables."""
import struct
from elftools.elf.elffile import ELFFile

class VitaElf:
    def __init__(self, path):
        self.data = open(path, 'rb').read()
        elf = ELFFile(open(path, 'rb'))
        self.segs = [(s['p_vaddr'], s['p_offset'], s['p_filesz'], s['p_memsz'], s['p_flags'])
                     for s in elf.iter_segments() if s['p_type'] == 'PT_LOAD']
        self.entry = elf['e_entry']

    def off(self, va):
        for v, o, fs, ms, _ in self.segs:
            if v <= va < v + fs:
                return o + va - v
        return None

    def read(self, va, n):
        o = self.off(va)
        return None if o is None else self.data[o:o + n]

    def u32(self, va):
        b = self.read(va, 4)
        return None if not b or len(b) < 4 else struct.unpack('<I', b)[0]

    def cstr(self, va, maxlen=128):
        b = self.read(va, maxlen)
        if not b: return None
        b = b.split(b'\0')[0]
        return b.decode('latin1') if b and all(32 <= c < 127 for c in b) else None

    def imports(self):
        """Yield (lib_name, lib_nid, [(func_nid, stub_va)]) by scanning for import entries."""
        d, seen = self.data, set()
        for v, o, fs, ms, fl in self.segs:
            for p in range(o, o + fs - 0x34, 4):
                size = struct.unpack_from('<H', d, p)[0]
                if size == 0x34:
                    _, ver, attr, nf, nv, nt, _r, lnid, lname, _r2, fnids, fents = struct.unpack_from('<HHHHHHIIIIII', d, p)
                elif size == 0x24:
                    _, ver, attr, nf, nv, nt, lnid, lname, fnids, fents = struct.unpack_from('<HHHHHHIIII', d, p)
                else:
                    continue
                name = self.cstr(lname)
                if not name or not name.startswith('Sce') or not 0 < nf < 2000 or (name, lnid) in seen:
                    continue
                nids = self.read(fnids, 4 * nf); ents = self.read(fents, 4 * nf)
                if not nids or not ents: continue
                seen.add((name, lnid))
                yield name, lnid, list(zip(struct.unpack(f'<{nf}I', nids), struct.unpack(f'<{nf}I', ents)))

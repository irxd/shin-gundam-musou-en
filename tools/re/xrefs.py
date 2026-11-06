"""Linear-sweep Thumb disassembly of a Vita ELF text segment; find movw/movt-built constants (address xrefs)."""
import sys, struct, pickle, os
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
from capstone.arm import ARM_OP_IMM, ARM_OP_REG
sys.path.insert(0, os.path.dirname(__file__))
from velf import VitaElf

def build_consts(path, cache):
    if os.path.exists(cache):
        return pickle.load(open(cache, 'rb'))
    e = VitaElf(path)
    v, o, fs, _, _ = e.segs[0]
    code = e.data[o:o + fs]
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True; md.detail = True
    lo = {}; consts = []          # (insn_addr, reg, value)
    for ins in md.disasm(code, v):
        m = ins.mnemonic
        if m == 'movw' and len(ins.operands) == 2:
            r = ins.operands[0].reg; lo[r] = (ins.address, ins.operands[1].imm & 0xffff)
        elif m == 'movt' and len(ins.operands) == 2:
            r = ins.operands[0].reg
            if r in lo and ins.address - lo[r][0] < 64:
                consts.append((lo[r][0], ins.reg_name(r), lo[r][1] | ((ins.operands[1].imm & 0xffff) << 16)))
    pickle.dump(consts, open(cache, 'wb'))
    return consts

if __name__ == '__main__':
    path, cache = sys.argv[1], sys.argv[2]
    targets = [int(x, 16) for x in sys.argv[3:]]
    consts = build_consts(path, cache)
    print('movw/movt constants:', len(consts))
    for t in targets:
        hits = [(hex(a), r, hex(val)) for a, r, val in consts if t - 0x40 <= val <= t + 0x40]
        print(hex(t), hits[:20])

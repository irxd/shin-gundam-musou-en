"""Find bl/blx/b.w call sites targeting given addresses (linear Thumb sweep of seg0)."""
import sys, os
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
sys.path.insert(0, os.path.dirname(__file__))
from velf import VitaElf
e = VitaElf(sys.argv[1]); targets = {int(x, 16) for x in sys.argv[2:]}
v, o, fs, _, _ = e.segs[0]
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
for ins in md.disasm(e.data[o:o + fs], v):
    if ins.mnemonic in ('bl', 'blx', 'b.w', 'b') and ins.op_str.startswith('#'):
        t = int(ins.op_str[1:], 16)
        if t in targets: print(f'{ins.address:#x}: {ins.mnemonic} {t:#x}')

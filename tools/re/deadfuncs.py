"""Heuristic dead-function finder: function starts (push ...lr) in seg0 never referenced by any branch,
movw/movt constant, or stored pointer (addr|1) anywhere in the ELF."""
import sys, os, struct, pickle
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
sys.path.insert(0, os.path.dirname(__file__))
from velf import VitaElf
e = VitaElf(sys.argv[1]); consts = pickle.load(open(sys.argv[2], 'rb'))
v, o, fs, _, _ = e.segs[0]
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
starts, targets = [], set()
prev_end = None
for ins in md.disasm(e.data[o:o + fs], v):
    if ins.mnemonic in ('push', 'push.w') and 'lr' in ins.op_str:
        starts.append(ins.address)
    if ins.op_str.startswith('#') and (ins.mnemonic.startswith('b') or ins.mnemonic.startswith('cb')):
        try: targets.add(int(ins.op_str.split('#')[-1], 16))
        except ValueError: pass
refs = set(targets) | {c for _, _, c in consts} | {c & ~1 for _, _, c in consts}
d = e.data
for sv, so, sfs, _, _ in e.segs:
    for p in range(so, so + sfs - 3, 4):
        x = struct.unpack_from('<I', d, p)[0]
        if v <= x < v + fs: refs.add(x & ~1)
starts.sort()
dead = []
for a, b in zip(starts, starts[1:] + [v + fs]):
    # a function may begin a few instructions before its push (e.g. mov/ldr); treat any ref within 8 bytes before as a ref
    if not any((a - k) in refs for k in range(0, 10, 2)):
        dead.append((a, b - a))
dead.sort(key=lambda x: -x[1])
print('function starts:', len(starts), 'unreferenced:', len(dead))
for a, n in [x for x in dead if x[0] < int(sys.argv[3], 16)][:40]: print(f"  {a:#x} size~{n:#x}  {e.read(a, 8).hex()}")

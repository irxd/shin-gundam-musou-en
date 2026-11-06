"""Disassemble a Thumb range from a Vita ELF: dis.py ELF start_va [length]"""
import sys, os
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB
sys.path.insert(0, os.path.dirname(__file__))
from velf import VitaElf
e = VitaElf(sys.argv[1]); start = int(sys.argv[2], 16); n = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x100
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB); md.skipdata = True
for ins in md.disasm(e.read(start, n), start):
    print(f'{ins.address:08x}: {ins.bytes.hex():<10} {ins.mnemonic:8} {ins.op_str}')

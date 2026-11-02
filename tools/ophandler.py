"""Mostra o handler de um opcode do KSC: ophandler.py ../work/BOOT.BIN ../work/boot.asm 8e 70"""
import struct
import sys

b = open(sys.argv[1], "rb").read()
TABLE = 0xE01B8
asm = {}
for line in open(sys.argv[2], encoding="ascii"):
    asm[int(line[:6], 16)] = line[8:].rstrip()
for op in sys.argv[3:]:
    n = int(op, 16)
    va = struct.unpack_from("<I", b, TABLE + 0x80 + n * 4)[0]
    print(f"--- op {n:02x} @ {va:06x}")
    c = 0
    while c < 60:
        t = asm.get(va, "?")
        print(f"{va:06x} {t.split('  ;')[0]}")
        if (t.startswith("j ") or t.startswith("jr ")) and c > 0:
            print(f"{va+4:06x} {asm.get(va+4,'?').split('  ;')[0]}")
            break
        va += 4
        c += 1

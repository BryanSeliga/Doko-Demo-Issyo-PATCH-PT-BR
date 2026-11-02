"""Valida o decodificador nos 5 scripts: para no primeiro opcode desconhecido e checa alvos de salto."""
import struct
import sys

from kscdis import decode

for name in ("NEKO", "INU", "ROBO", "KAERU", "USAGI"):
    d = open(f"../work/ksc/{name}.KSC", "rb").read()
    ins, i = decode(d)
    end = 0x1C + struct.unpack("<I", d[8:12])[0]
    st = {x[0] for x in ins}
    J = []
    for s, op, l in ins:
        if op in (0x10, 0x11, 0x12, 0x21):
            J.append(int.from_bytes(d[s + 1:s + 4], "little") + 0x1C)
        elif op in (0x20, 0x28):
            J.append(int.from_bytes(d[s + 2:s + 5], "little") + 0x1C)
    bad = [t for t in J if t not in st and t < i]
    print([hex(t) for t in bad[:6]])
    print(name, "n", len(ins), "stop", hex(i), "end", hex(end), "jumps", len(J), "bad", len(bad), d[i - 10:i].hex(" "), "|", d[i:i + 16].hex(" "))

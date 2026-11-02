"""Decodificador linear do bytecode KSC (codigo comeca em 0x1C; alvos sao relativos a 0x1C)."""
import struct

CODE_BASE = 0x1C
TMPL_VAR = (0x14, 0x15, 0x17, 0x18, 0x19, 0x1A, 0x1B, 0x1C)
STR_OPS = (0x48, 0x49, 0x4A, 0x8E)
LEN = {}
for op in (0x30, 0x80, 0xA0, 0x22):
    LEN[op] = 1
for op in (0x81, 0x90, 0x91, 0x92, 0x93, 0x94, 0x95, 0x96, 0x97, 0x98, 0x99, 0x8B, 0x71, 0x72, 0x73, 0x75):
    LEN[op] = 2
for op in (0x10, 0x11, 0x12, 0x15, 0x18, 0x21, 0x82, 0x88, 0x8A):
    LEN[op] = 3
for op in (0x19, 0x83, 0x20, 0x28, 0x4E):
    LEN[op] = 4
VALID0 = {int(x, 16) for x in """03 08 23 0b 0c 0d 0e 0f 14 1a 1b 1c 31 32 38 3a 3b 40 41 43 44 4f 50 51 52 53 54 55 56 57
    5a 5b 5c 5d 5e 5f 60 61 62 63 64 65 66 67 68 69 6a 6b 6c 6d 70 78 84 85 86 87 89 8c 8d 8f b0 b1 b2 b3 b4
    b8 b9 ba bb bc bd c0 c1 c2 c3 c4 c5 c8 c9 d0 d1 d2 d4 d5 d6 d7 e0 e1 e2 e3 f0 f4 f5 fc fd""".split()}


def tmpl_end(d, i):
    """Fim da string-modelo: termina em 0; os bytes de variavel levam u16."""
    while True:
        c = d[i]
        i += 1
        if c == 0:
            return i
        if c in TMPL_VAR:
            i += 2


def callspec_end(d, i):
    """Chamada nativa (helper 6b7d0): u16 id, u8 flag, u16 opcional se flag != 0."""
    return i + 3 if d[i + 2] == 0 else i + 5


def decode(d, end=None, lens=None):
    """Gera (offset, op, bytes_totais, tipo). Tipos: op, str, case (cabecalho de switch)."""
    if end is None:
        end = CODE_BASE + struct.unpack("<I", d[8:12])[0]
    L = lens or LEN
    i = CODE_BASE
    headers = set()
    out = []
    while i < end:
        if i in headers:
            v = int.from_bytes(d[i:i + 4], "little")
            if v >> 28 == 0:
                out.append((i, -2, 4))
                i += 4
            else:
                headers.add(int.from_bytes(d[i + 4:i + 7], "little") + CODE_BASE)
                out.append((i, -1, 7))
                i += 7
            continue
        op = d[i]
        if op == 0x13:
            out.append((i, op, 1))
            i += 1
            headers.add(i)
            continue
        if op in STR_OPS:
            e = tmpl_end(d, i + 1)
        elif op == 0x25:
            e = callspec_end(d, i + 1)
        elif op == 0x24:
            e = callspec_end(d, i + 2)
        elif op in (0xF6, 0xF7):
            e = i + 2 if d[i + 1] == 0 else i + 4
        elif op in L:
            e = i + 1 + L[op]
        elif op in VALID0:
            e = i + 1
        else:
            out.append((i, op, None))
            return out, i
        out.append((i, op, e - i))
        i = e
    return out, i

"""Infere o tamanho dos operandos desconhecidos: testa candidatos e valida pelos alvos de salto."""
import collections
import struct
import sys

from kscdis import LEN, STR_OPS, VALID0, switch_end, tmpl_end

d = open(sys.argv[1], "rb").read()
csz = struct.unpack("<I", d[8:12])[0]
end = 0x1C + csz
LEN0 = set(VALID0) | {0x31, 0x1C, 0x32, 0x16, 0x17} | set(range(0, 0x0B))


def run(extra, stop_after=None):
    L = dict(LEN)
    L.update(extra)
    Z = set(LEN0) - set(extra)
    i = 0x1C
    n = 0
    st = set()
    J = []
    while i < end:
        op = d[i]
        st.add(i)
        if op == 0x13:
            i, cs = switch_end(d, i + 1)
            J += [c[3] + 0x1C for c in cs]
        elif op in STR_OPS:
            i = tmpl_end(d, i + 1)
        elif op in L:
            if op in (0x10, 0x11, 0x12, 0x21):
                J.append(int.from_bytes(d[i + 1:i + 4], "little") + 0x1C)
            if op == 0x20:
                J.append(int.from_bytes(d[i + 2:i + 5], "little") + 0x1C)
            i += 1 + L[op]
        elif op in Z:
            i += 1
        else:
            return i, op, n, st, J
        n += 1
        if stop_after and n > stop_after:
            break
    return i, None, n, st, J


extra = {}
for step in range(int(sys.argv[2])):
    i, op, n, st, J = run(extra)
    bad = sum(1 for t in J if t not in st and t < i)
    print(f"step{step} stop {i:#x} op {op if op is None else hex(op)} n={n} jumps={len(J)} bad={bad}", d[i - 6:i].hex(" "), "|", d[i:i + 14].hex(" ") if op is not None else "")
    if op is None:
        break
    print(step)
    break
    best = None
    for l in range(0, 8):
        e = dict(extra)
        e[op] = l
        ii, o2, nn, s2, J2 = run(e)
        b = sum(1 for t in J2 if t not in s2 and t < ii)
        print("   try", hex(op), l, "->", hex(ii), "bad", b)
        if best is None or (b, -ii) < (best[0], -best[1]):
            best = (b, ii, l)
    extra[op] = best[2]
print({hex(k): v for k, v in extra.items()})

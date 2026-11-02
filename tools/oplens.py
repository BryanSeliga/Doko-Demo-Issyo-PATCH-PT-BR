"""Heuristica: quanto cada handler avanca o PC do script (sw R,4($s2) com R = base + N)."""
import re
import struct

b = open("../work/BOOT.BIN", "rb").read()
asm = {}
for line in open("../work/boot.asm", encoding="ascii"):
    asm[int(line[:6], 16)] = line[8:].split("  ;")[0].rstrip()
TABLE = 0xE01B8
groups = {}
for n in range(254):
    va = struct.unpack_from("<I", b, TABLE + 0x80 + n * 4)[0]
    if va == 0x6B9B8:
        continue
    start = va
    incs = set()
    reads = 0
    jumps = []
    calls = []
    cnt = 0
    while cnt < 180:
        t = asm.get(va, "?")
        m = re.match(r"sw \$(\w+), 4\(\$s2\)", t)
        if m:
            r = m.group(1)
            for k in range(-12, 3):
                p = asm.get(va + 4 * k, "")
                mm = re.match(r"addiu \$%s, \$\w+, (\d+|0x[0-9a-f]+)$" % r, p)
                if mm:
                    incs.add(int(mm.group(1), 0))
            incs.add(-1)
        if re.match(r"lw \$\w+, 4\(\$s2\)", t):
            reads += 1
        if t.startswith("jal "):
            calls.append(t[6:])
        if t.startswith("j 0x6b9") or t.startswith("jr "):
            break
        va += 4
        cnt += 1
    key = (tuple(sorted(incs)), reads, tuple(c for c in calls if c in ("684dc", "67b54", "6b33c", "6b554", "67548", "674c0", "680a4", "680d0", "6b760", "7534c", "77404", "77224", "7537c")))
    groups.setdefault(key, []).append(f"{n:02x}")
for k, v in sorted(groups.items(), key=lambda kv: kv[1][0]):
    print(" ".join(v), "=> inc", k[0], "reads", k[1], "helpers", k[2])

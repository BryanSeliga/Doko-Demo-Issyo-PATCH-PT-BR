"""Procura trechos em Shift-JIS e UTF-16 no BOOT.BIN e em cada arquivo interno dos BPMs."""
import collections
import re
import struct
import sys

from iso_common import *

SJIS = re.compile(rb"(?:[\x81-\x84\x88-\x9f\xe0-\xea][\x40-\x7e\x80-\xfc]|[\x20-\x7e]|\n){6,}")


def is_real(run):
    try:
        s = run.decode("cp932")
    except UnicodeDecodeError:
        return None
    kana = sum(1 for c in s if "\u3040" <= c <= "\u30ff")
    return s if kana >= 3 else None


iso = Iso(sys.argv[1])
report = []
boot = iso.read(BOOT_LBA, BOOT_SIZE)
hits = [is_real(m.group()) for m in SJIS.finditer(boot)]
hits = [h for h in hits if h]
print("BOOT.BIN sjis:", len(hits), sum(map(len, hits)))
per_ext = collections.Counter()
for bpm, off, size in bpm_files(iso):
    try:
        inner = inner_files(iso, off)
    except Exception as e:
        print("ERR", bpm, e)
        continue
    for name, o, s in inner:
        ext = name.rsplit(".", 1)[-1]
        if ext in ("GIM", "AT3", "PMF", "PNG"):
            continue
        d = iso.bp(o, s)
        h = [x for x in (is_real(m.group()) for m in SJIS.finditer(d)) if x]
        if h:
            per_ext[ext] += sum(map(len, h))
            report.append((sum(map(len, h)), bpm, name, s, len(h), h[:2]))
report.sort(key=lambda r: -r[0])
print(per_ext)
for r in report[:40]:
    print(r)
with open(sys.argv[2], "w", encoding="utf-8") as out:
    for h in hits:
        out.write(h.replace("\n", "\n") + "\n")

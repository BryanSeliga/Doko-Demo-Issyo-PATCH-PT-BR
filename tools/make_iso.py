"""Monta a ISO traduzida. Uso: make_iso.py <iso_original> <iso_saida> [personagem ...]

Sem personagens, usa todos que tiverem traducao em work/trad/pt. Textos sem traducao ficam em japones.
"""
import glob
import json
import os
import re
import sys

from boot_text import patch_boot
from build_iso import build
from extract_text import collect
from fontpatch import WIDTHS_OFF, patch
from gui_render import build_all
from iso_common import BOOT_LBA, BOOT_SIZE, Iso, bpm_files, inner_files
from kscbuild import extract_inline, extract_pool, rebuild
from textfmt import to_bytes, to_text
from wrap import wrap

CHARS = {"neko": ("KSNEKO.BPM", "NEKO.KSC"), "inu": ("KSINU.BPM", "INU.KSC"), "robo": ("KSROBO.BPM", "ROBO.KSC"),
         "kaeru": ("KSKAERU.BPM", "KAERU.KSC"), "usagi": ("KSUSAGI.BPM", "USAGI.KSC")}
HERE = os.path.dirname(os.path.abspath(__file__))
PT_DIR = os.path.join(HERE, "..", "work", "trad", "pt")
# O tique verbal e inserido no fim das frases: "Que legal" + ", miau" + "!".
TIC = {"neko": {"ニャ": ", miau"}}


def load_translations(who, d):
    """Mapa texto japones -> (portugues, tipo)."""
    src = collect(d)
    pt = {}
    for path in glob.glob(os.path.join(PT_DIR, f"{who}_*.jsonl")):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                it = json.loads(line)
                pt[it["id"]] = it["pt"]
    return {it["jp"]: (pt[it["id"]], it["tipo"]) for it in src if it["id"] in pt}, len(src)


def apply_ksc(who, d, widths, amap):
    tr, total = load_translations(who, d)
    inline = {}
    for n, op, raw in extract_inline(d):
        try:
            jp = to_text(raw)
        except UnicodeDecodeError:
            continue
        if jp in tr:
            pt = tr[jp][0]
            if op == 0x48 or not (pt.startswith(" ") or pt.endswith(" ")):
                pt = wrap(pt, widths, amap)
            inline[n] = to_bytes(pt, amap)
    pool = {}
    for off, raw in extract_pool(d).items():
        try:
            jp = to_text(raw)
        except UnicodeDecodeError:
            continue
        if jp in TIC.get(who, {}):
            pool[off] = to_bytes(TIC[who][jp], amap)
        elif jp in tr:
            pool[off] = to_bytes(tr[jp][0], amap)
    print(f"{who}: {len(tr)}/{total} textos traduzidos; {len(inline)} no codigo, {len(pool)} no pool")
    return rebuild(d, inline, pool)


def main(src, dst, whos):
    iso = Iso(src)
    bpms = {n: (o, s) for n, o, s in bpm_files(iso)}
    data = {n: (o, s) for n, o, s in inner_files(iso, bpms["DATA.BPM"][0])}
    font, amap = patch(iso.bp(*data["FONT\\FONT.XFT"]))
    widths = font[WIDTHS_OFF:WIDTHS_OFF + 8192]
    ksc = {}
    for who in whos or [w for w in CHARS if glob.glob(os.path.join(PT_DIR, f"{w}_*.jsonl"))]:
        bpm, name = CHARS[who]
        inner = {n: (o, s) for n, o, s in inner_files(iso, bpms[bpm][0])}
        ksc[bpm] = {name: apply_ksc(who, iso.bp(*inner[name]), widths, amap)}
    boot = patch_boot(iso.read(BOOT_LBA, BOOT_SIZE), amap)
    print("DATA.BP ->", build(src, dst, ksc=ksc, font=font, boot=boot, inplace=build_all(iso, bpms)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

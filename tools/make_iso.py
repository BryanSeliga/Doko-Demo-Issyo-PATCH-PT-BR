"""Monta a ISO traduzida. Uso: make_iso.py <iso_original> <iso_saida> [personagem ...]

Sem personagens, usa todos que tiverem traducao em traducao/. Textos sem traducao ficam em japones.
"""
import glob
import json
import os
import re
import sys

from boot_text import patch_boot
from build_iso import build
from dic import WORDS
from dic import rebuild as rebuild_dic
from extract_text import collect
from fontpatch import WIDTHS_OFF, patch
from gui_render import build_all
from iso_common import BOOT_LBA, BOOT_SIZE, Iso, bpm_files, inner_files
from items import item_offsets, wrap_desc
from kscbuild import extract_inline, extract_pool, rebuild
from textfmt import to_bytes, to_text
import wrap as wrap_mod
from wrap import text_width, wrap

CHARS = {"neko": ("KSNEKO.BPM", "NEKO.KSC"), "inu": ("KSINU.BPM", "INU.KSC"), "robo": ("KSROBO.BPM", "ROBO.KSC"),
         "kaeru": ("KSKAERU.BPM", "KAERU.KSC"), "usagi": ("KSUSAGI.BPM", "USAGI.KSC")}
HERE = os.path.dirname(os.path.abspath(__file__))
PT_DIR = os.path.join(HERE, "..", "traducao")
# O tique verbal e inserido no fim das frases: "Que legal" + ", miau" + "!".
TIC = {"neko": {"ニャ": ", miau"}, "inu": {"わン": ", au", "わ～ン": ", au~"},
       "usagi": {"ピョン": ", pyon", "ウサ": ", usa"}, "robo": {"ロボ": ", robô"},
       "kaeru": {"オラ": "Eu", "ケロ": ", croac", "ダス": ", sô", "ハァ～": "ah~"}}


def load_translations(who, d):
    """Mapa texto japones -> (portugues, tipo)."""
    src = collect(d)
    pt = {}
    for path in glob.glob(os.path.join(PT_DIR, f"{who}_*.jsonl")):
        for line in open(path, encoding="utf-8"):
            if line.strip():
                it = json.loads(line)
                pt[it["id"]] = it["pt"]
    out = {}
    for it in src:
        if it["id"] in pt:
            text = pt[it["id"]]
            # Codigo de controle \x04 no fim (telas de comunicacao) precisa continuar no texto.
            if it["jp"].endswith("\x04") and not text.endswith("\x04"):
                if it["jp"].endswith("\n\x04") and not text.endswith("\n"):
                    text += "\n"
                text += "\x04"
            # Pedaco que termina em virgula e emendado no seguinte: em portugues precisa de espaco.
            if text.endswith(","):
                text += " "
            out[it["jp"]] = (text, it["tipo"])
    return out, len(src)


def apply_ksc(who, d, widths, amap):
    tr, total = load_translations(who, d)
    wrap_mod.TIC_WIDTH = max(text_width(t, widths, amap) for t in TIC[who].values())
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
    _, descs = item_offsets(d)
    for off, raw in extract_pool(d).items():
        try:
            jp = to_text(raw)
        except UnicodeDecodeError:
            continue
        if jp in TIC.get(who, {}):
            pool[off] = to_bytes(TIC[who][jp], amap)
        elif jp in tr:
            pt = tr[jp][0]
            if off in descs:
                pt = wrap_desc(pt, widths, amap)
            pool[off] = to_bytes(pt, amap)
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
        dic_name = name.replace(".KSC", ".DIC")
        if dic_name in WORDS:
            ksc[bpm][dic_name] = rebuild_dic(iso.bp(*inner[dic_name]), WORDS[dic_name], amap)
    boot = patch_boot(iso.read(BOOT_LBA, BOOT_SIZE), amap)
    print("DATA.BP ->", build(src, dst, ksc=ksc, font=font, boot=boot, inplace=build_all(iso, bpms)))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

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
from gim import to_gim8
from gui_render import build_all
from iso_common import BOOT_LBA, BOOT_SIZE, Iso, bpm_files, inner_files
from items import item_offsets, wrap_desc
from kscbuild import extract_inline, extract_pool, rebuild
from textfmt import to_bytes, to_text
import wrap as wrap_mod
from wrap import text_width, wrap
from xmb import icon0, patch_sfo, pic0, title_logo

# Arquivos do menu do PSP (PSP_GAME): (lba, tamanho) na ISO original.
PARAM_SFO = (2672, 472)
ICON0_PNG = (2576, 24493)
PIC0_PNG = (2688, 92891)
TITLE_LOGO = ("TITLE.BPM", "GUI\\TITLE\\TITLE.GIM")
CHARS = {"neko": ("KSNEKO.BPM", "NEKO.KSC"), "inu": ("KSINU.BPM", "INU.KSC"), "robo": ("KSROBO.BPM", "ROBO.KSC"),
         "kaeru": ("KSKAERU.BPM", "KAERU.KSC"), "usagi": ("KSUSAGI.BPM", "USAGI.KSC")}
HERE = os.path.dirname(os.path.abspath(__file__))
PT_DIR = os.path.join(HERE, "..", "traducao")
# O tique verbal e inserido no fim das frases: "Que legal" + ", " + "miau" + "!".
TIC = {"neko": {"ニャ": "miau"}, "inu": {"わン": "au", "わ～ン": "auu"},
       "usagi": {"ピョン": "pyon", "ウサ": "usa"}, "robo": {"ロボ": "robô"},
       "kaeru": {"オラ": "Eu", "ケロ": "croac", "ダス": "sô", "ハァ～": "aah"}}
# Marcadores de tique que vem depois de virgula. A ", " fica no texto, e nao no tique, para o balao
# poder quebrar a linha antes dele: palavra + tique colados nao cabem numa linha ("lugares, mia|u~").
TIC_COMMA = {"neko": ("0017",), "inu": ("0017", "0018"), "usagi": ("0017", "0018"), "robo": ("0017",),
             "kaeru": ("0019", "001a")}


def comma_tics(who, text):
    codes = "|".join(TIC_COMMA.get(who, ()))
    if not codes:
        return text
    return re.sub(r"(?<=[^\s])\{17:(%s)\}" % codes, r", {17:\1}", text)


VOWEL = "aeiouáàâãéêíóôõúüAEIOUÁÀÂÃÉÊÍÓÔÕÚÜ"


def stretch(word):
    """Estica a ultima vogal da palavra ("bom" -> "boom", "Tchau" -> "Tchauu"); sem vogal, a ultima letra."""
    for i in range(len(word) - 1, -1, -1):
        if word[i] in VOWEL:
            return word[:i + 1] + word[i].lower() + word[i + 1:]
    return word + word[-1]


def tilde(text):
    """O "~" japones (fala arrastada) vira algo que soa natural em portugues:
    palavra~ -> ultima vogal esticada; tique~ -> "!" (ou nada, se a fala for hesitante: "..."); resto -> some."""
    hesitant = "..." in text or "…" in text

    def sub(m):
        before, after = text[:m.start()], text[m.end():m.end() + 1]
        if re.search(r"\{17:[0-9a-f]{4}\}$", before):
            return "" if hesitant or (after and after in "!?♪♥") else "!"
        return ""

    out, pos = [], 0
    for m in re.finditer(r"~+", text):
        before = text[pos:m.start()]
        word = re.search(r"[^\W\d_]+$", before)
        if word and not re.search(r"\{[0-9a-f]{2}:[0-9a-f]{4}\}$|\{W\}$", before):
            before = before[:word.start()] + stretch(word.group())
            rep = ""
        else:
            rep = sub(m)
        out.append(before + rep)
        pos = m.end()
    return "".join(out) + text[pos:]


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
            text = tilde(comma_tics(who, pt[it["id"]]))
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
        elif "{17:" in jp or "、" in jp or "～" in jp:
            # Linha so de codigos (palavra + tique), fora da traducao: "Tchau" + "miau" vira "Tchau, miau".
            pt = tilde(comma_tics(who, jp.replace(" {17:", "{17:").replace("、", ", ").replace("～", "~")))
            if pt != jp:
                inline[n] = to_bytes(wrap(pt, widths, amap), amap)
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
    loose = {PARAM_SFO: patch_sfo(iso.read(*PARAM_SFO)), ICON0_PNG: icon0(), PIC0_PNG: pic0(iso.read(*PIC0_PNG))}
    # logotipo em 256 cores: a textura original tem 16 e o arquivo cresce, entao o TITLE.BPM e realocado
    logo = {n: (o, s) for n, o, s in inner_files(iso, bpms[TITLE_LOGO[0]][0])}[TITLE_LOGO[1]]
    ksc.setdefault(TITLE_LOGO[0], {})[TITLE_LOGO[1]] = to_gim8(iso.bp(*logo), title_logo(352, 75))
    print("DATA.BP ->", build(src, dst, ksc=ksc, font=font, boot=boot, inplace=build_all(iso, bpms), loose=loose))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

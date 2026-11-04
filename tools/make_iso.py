"""Monta a ISO traduzida. Uso: make_iso.py <iso_original> <iso_saida> [personagem ...]

Sem personagens, usa todos que tiverem traducao em traducao/. Textos sem traducao ficam em japones.
"""
import glob
import json
import os
import re
import sys
import unicodedata

import diary
from boot_text import patch_boot
from build_iso import build
from dic import WORDS
from dic import rebuild as rebuild_dic
from extract_text import collect
from fontpatch import WIDTHS_OFF, patch
from gim import to_gim8
from gui_render import build_all
from iso_common import BOOT_LBA, BOOT_SIZE, Iso, bpm_files, inner_files
from icon1 import build as icon1
from items import item_offsets, wrap_desc
from kscbuild import extract_inline, extract_pool, pool_uses, rebuild
from textfmt import to_bytes, to_text
import wrap as wrap_mod
from wrap import BALLOON_WIDTH, POOL_WORD_WIDTH, text_width, wrap
from xmb import icon0, patch_sfo, pic0, title_logo

# Arquivos do menu do PSP (PSP_GAME): (lba, tamanho) na ISO original.
PARAM_SFO = (2672, 472)
ICON0_PNG = (2576, 24493)
PIC0_PNG = (2688, 92891)
# Video do icone no menu do PSP: refeito em portugues (icon1.py); sem ffmpeg, e renomeado e o menu mostra o ICON0.
ICON1_PMF = (2592, 147456)
TITLE_LOGO = ("TITLE.BPM", "GUI\\TITLE\\TITLE.GIM")
# Logotipo da tela rapida (ao voltar do "Suspender"), na mesma proporcao do da tela titulo.
QUICK_LOGO = ("QUICK.BPM", "GUI\\QUICK\\Q_TITLE.GIM")
CHARS = {"neko": ("KSNEKO.BPM", "NEKO.KSC"), "inu": ("KSINU.BPM", "INU.KSC"), "robo": ("KSROBO.BPM", "ROBO.KSC"),
         "kaeru": ("KSKAERU.BPM", "KAERU.KSC"), "usagi": ("KSUSAGI.BPM", "USAGI.KSC")}
HERE = os.path.dirname(os.path.abspath(__file__))
PT_DIR = os.path.join(HERE, "..", "traducao")
# Versao curta de cada texto de placa: as placas do cenario so mostram 8 caracteres.
SIGNS_PATH = os.path.join(PT_DIR, "placas.jsonl")
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


def load_signs():
    if not os.path.exists(SIGNS_PATH):
        return {}
    rows = (json.loads(line) for line in open(SIGNS_PATH, encoding="utf-8") if line.strip())
    return {r["pt"]: r["placa"] for r in rows}


def sign_text(pt, short):
    """Texto da placa: versao curta, sem acento (as placas mostram um ponto no lugar da letra acentuada)."""
    pt = short.get(pt, pt)
    return "".join(c for c in unicodedata.normalize("NFD", pt) if not unicodedata.combining(c))


def fits_balloon(uses, is_item_name):
    """Texto do pool que so aparece em falas e no menu de opcoes."""
    return bool(uses) and uses <= {"opcao", "var", "destino"} and not is_item_name


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
    names, descs = item_offsets(d)
    uses = pool_uses(d)
    signs = load_signs()
    raw_pool = extract_pool(d)
    # paginas de diario: {offset do texto: {"$_W1": palavra traduzida, ...}}
    pages = {}
    for text_off, word_offs in diary.pages(d):
        words = pages.setdefault(text_off, {})
        for n, w in enumerate(word_offs, 1):
            if w is not None:
                words[f"$_W{n}"] = tr.get(to_text(raw_pool[w]), (to_text(raw_pool[w]),))[0]
    too_long = []
    for off, raw in raw_pool.items():
        try:
            jp = to_text(raw)
        except UnicodeDecodeError:
            continue
        if jp in TIC.get(who, {}):
            pool[off] = to_bytes(TIC[who][jp], amap)
        elif jp in tr:
            pt = tr[jp][0]
            if off in pages:
                pt = diary.wrap_page(pt, widths, amap, pages[off])
                if diary.problems(pt, widths, amap, pages[off]):
                    too_long.append(off)
            elif off in descs:
                pt = wrap_desc(pt, widths, amap)
            elif "placa" in uses.get(off, ()):
                # texto que tambem aparece nas falas fica inteiro, so sem acento
                pt = sign_text(pt, signs if uses[off] == {"placa"} else {})
            elif fits_balloon(uses.get(off), off in names) and \
                    text_width(pt, widths, amap, POOL_WORD_WIDTH) > BALLOON_WIDTH:
                # O jogo corta por letra o texto que encaixa na fala (e a opcao escolhida, que o Pokepi
                # repete no balao): quebra por palavra, ou com hifen, na largura do balao.
                pt = wrap(pt, widths, amap, var_width=POOL_WORD_WIDTH)
            pool[off] = to_bytes(pt, amap)
    print(f"{who}: {len(tr)}/{total} textos traduzidos; {len(inline)} no codigo, {len(pool)} no pool")
    if too_long:
        # a trava do BOOT corta o fim dessas paginas; ver diary_batches.py conferir
        print(f"{who}: {len(too_long)} paginas de diario passam do limite")
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
    # logotipo em 256 cores: a textura original tem 16 e o arquivo cresce, entao o pacote e realocado
    for (pack, name), size in ((TITLE_LOGO, (352, 75)), (QUICK_LOGO, (192, 41))):
        logo = {n: (o, s) for n, o, s in inner_files(iso, bpms[pack][0])}[name]
        ksc.setdefault(pack, {})[name] = to_gim8(iso.bp(*logo), title_logo(*size))
    pmf = icon1(iso.read(*ICON1_PMF))
    if pmf is not None:
        loose[ICON1_PMF] = pmf
        rename = {}
    else:
        print("ffmpeg (imageio-ffmpeg) nao encontrado: o video do icone fica desligado")
        rename = {ICON1_PMF: (b"ICON1.PMF", b"ICON1.PMX")}
    print("DATA.BP ->", build(src, dst, ksc=ksc, font=font, boot=boot, inplace=build_all(iso, bpms), loose=loose,
                               rename=rename))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])

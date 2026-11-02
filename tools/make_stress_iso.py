"""Build de teste: troca todas as falas por uma frase longa em portugues, mantendo as variaveis.

Serve para validar no emulador a estabilidade do VM, os acentos, a quebra de linha e a memoria.
Uso: make_stress_iso.py <iso_original> <iso_saida>
"""
import re
import sys

from build_iso import build
from fontpatch import patch
from iso_common import Iso, bpm_files, inner_files
from kscbuild import extract_inline, rebuild
from textfmt import TOKEN, to_bytes, to_text

CHARS = {"KSNEKO.BPM": "NEKO.KSC", "KSINU.BPM": "INU.KSC", "KSROBO.BPM": "ROBO.KSC", "KSKAERU.BPM": "KAERU.KSC", "KSUSAGI.BPM": "USAGI.KSC"}
LINE = "Olá! Esta é uma frase de teste com acentuação: coração, não, você, três, avó, Água. Será que cabe na caixa de texto?\n"
PROMPT = "Pergunta de teste com ação e coração?"


def stress_text(text, op):
    tokens = "".join(m.group(0) for m in TOKEN.finditer(text))
    return tokens + (LINE if op == 0x48 else PROMPT)


def main(src, dst):
    iso = Iso(src)
    font_off = None
    bpms = {n: (o, s) for n, o, s in bpm_files(iso)}
    data = {n: (o, s) for n, o, s in inner_files(iso, bpms["DATA.BPM"][0])}
    font, amap = patch(iso.bp(*data["FONT\\FONT.XFT"]))
    ksc = {}
    for bpm, name in CHARS.items():
        inner = {n: (o, s) for n, o, s in inner_files(iso, bpms[bpm][0])}
        d = iso.bp(*inner[name])
        repl = {}
        for n, op, raw in extract_inline(d):
            try:
                text = to_text(raw)
            except UnicodeDecodeError:
                continue
            if re.search(r"[぀-鿿]", text):
                repl[n] = to_bytes(stress_text(text, op), amap)
        out = rebuild(d, repl)
        print(name, "linhas", len(repl), "tamanho", len(d), "->", len(out))
        ksc[bpm] = {name: out}
    end = build(src, dst, ksc=ksc, font=font)
    print("DATA.BP ->", end)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

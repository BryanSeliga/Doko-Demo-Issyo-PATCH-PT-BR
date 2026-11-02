"""Itens do KSC: nome e descricao ficam na tabela de valores logo apos um marcador de array (tag 9, tamanho 0xa).

A tela de itens mostra o nome numa linha e a descricao em ate duas linhas de ITEM_WIDTH unidades.
Uso: items.py  -> lista as traducoes que nao cabem
"""
import glob
import json
import os
import struct
import sys

from kscbuild import layout
from wrap import text_width, wrap

ITEM_WIDTH = 222
ITEM_LINES = 2
NAME_WIDTH = 222


def item_offsets(d):
    """Devolve (offsets de nomes, offsets de descricoes) no pool."""
    lay = layout(d)
    n = (len(d) - lay["table"]) // 4
    t = struct.unpack_from(f"<{n}I", d, lay["table"])
    names, descs = set(), set()
    for k in range(n - 2):
        if t[k] == (9 << 28) | 0xA and t[k + 1] >> 28 == 5 and t[k + 2] >> 28 == 5:
            names.add(t[k + 1] & 0xFFFFFFF)
            descs.add(t[k + 2] & 0xFFFFFFF)
    return names, descs


def wrap_desc(text, widths, amap):
    return wrap(text.replace("\n", " "), widths, amap, ITEM_WIDTH)


def main(fix_path=None, out_path=None):
    """Sem argumentos lista o que nao cabe. Com fix_path ({id, pt} por linha), testa essas versoes no lugar
    das de traducao/. Com out_path, grava a lista {id, tipo, jp, pt, limite} do que nao cabe."""
    sys.stdout.reconfigure(encoding="utf-8")
    here = os.path.dirname(os.path.abspath(__file__))
    from extract_text import collect
    from fontpatch import WIDTHS_OFF, patch
    from kscbuild import extract_pool
    from textfmt import to_text
    d = open(os.path.join(here, "..", "work", "ksc", "NEKO.KSC"), "rb").read()
    font, amap = patch(open(os.path.join(here, "..", "work", "FONT.XFT"), "rb").read())
    widths = font[WIDTHS_OFF:WIDTHS_OFF + 8192]
    pool = extract_pool(d)
    names, descs = item_offsets(d)
    jp_of = lambda offs: {to_text(pool[o]) for o in offs}
    name_jp, desc_jp = jp_of(names), jp_of(descs)
    pt = {}
    for path in glob.glob(os.path.join(here, "..", "traducao", "neko_*.jsonl")):
        for line in open(path, encoding="utf-8"):
            it = json.loads(line)
            pt[it["id"]] = it["pt"]
    only = None
    if fix_path:
        fix = {json.loads(l)["id"]: json.loads(l)["pt"] for l in open(fix_path, encoding="utf-8") if l.strip()}
        pt.update(fix)
        only = set(fix)
    bad = []
    for it in collect(d):
        text = pt.get(it["id"])
        if text is None or (only is not None and it["id"] not in only):
            continue
        if it["jp"] in name_jp and text_width(text, widths, amap) > NAME_WIDTH:
            print("NOME", it["id"], f"largura {text_width(text, widths, amap)} > {NAME_WIDTH}:", text)
            bad.append({"id": it["id"], "tipo": "nome", "jp": it["jp"], "pt": text, "limite": "1 linha"})
        if it["jp"] in desc_jp:
            lines = wrap_desc(text, widths, amap).split("\n")
            if len(lines) > ITEM_LINES or any(text_width(l, widths, amap) > ITEM_WIDTH for l in lines):
                print("DESC", it["id"], f"{len(lines)} linhas > {ITEM_LINES}:", text)
                bad.append({"id": it["id"], "tipo": "descricao", "jp": it["jp"], "pt": text, "limite": "2 linhas"})
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            for b in bad:
                f.write(json.dumps(b, ensure_ascii=False) + "\n")
    print(len(names), "itens,", len(bad), "nao cabem")
    if not bad:
        print("OK")


if __name__ == "__main__":
    args = dict(a.split("=", 1) for a in sys.argv[1:])
    main(args.get("fix"), args.get("saida"))

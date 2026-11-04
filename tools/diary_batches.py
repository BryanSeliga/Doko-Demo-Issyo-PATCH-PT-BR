"""Separa as paginas de diario em lotes para resumir e confere os lotes resumidos.

  diary_batches.py gerar <iso_original> [tamanho]   -> work/diario/lotes/<pokepi>_NN.jsonl
  diary_batches.py conferir <iso_original> <lote>    -> confere work/diario/pt/<lote>.jsonl
  diary_batches.py aceitar <iso_original> <lote>...  -> confere e grava em traducao/

Cada linha do lote: {"id", "jp", "pt" (traducao atual), "palavras": {"$_W1": "..."}, "bytes", "linhas"}.
Os lotes tem texto do jogo: ficam em work/ e nunca vao para o repositorio.
"""
import glob
import json
import os
import sys

import diary
import make_iso
from check_batch import problems as text_problems
from extract_text import collect
from fontpatch import WIDTHS_OFF, patch
from iso_common import Iso, bpm_files, inner_files
from kscbuild import extract_pool
from textfmt import to_bytes, to_text

sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "..", "work", "diario")
PT_DIR = os.path.join(HERE, "..", "traducao")


def load(iso_path):
    iso = Iso(iso_path)
    b = {n: (o, s) for n, o, s in bpm_files(iso)}
    data = {n: (o, s) for n, o, s in inner_files(iso, b["DATA.BPM"][0])}
    font, amap = patch(iso.bp(*data["FONT\\FONT.XFT"]))
    widths = font[WIDTHS_OFF:WIDTHS_OFF + 8192]
    out = {}
    for who, (bpm, name) in make_iso.CHARS.items():
        inner = {n: (o, s) for n, o, s in inner_files(iso, b[bpm][0])}
        d = iso.bp(*inner[name])
        pool = extract_pool(d)
        ids = {it["jp"]: it["id"] for it in collect(d)}
        tr, _ = make_iso.load_translations(who, d)
        items = {}
        for text_off, word_offs in diary.pages(d):
            jp = to_text(pool[text_off])
            words = {}
            for n, off in enumerate(word_offs, 1):
                if off is not None:
                    wjp = to_text(pool[off])
                    words[f"$_W{n}"] = tr.get(wjp, (wjp,))[0]
            # a mesma pagina pode aparecer em mais de um registro, com palavras diferentes: vale a maior
            it = items.setdefault(ids[jp], {"id": ids[jp], "jp": jp, "pt": tr[jp][0], "palavras": {}})
            for k, w in words.items():
                if len(to_bytes(w, amap)) > len(to_bytes(it["palavras"].get(k, ""), amap)):
                    it["palavras"][k] = w
        out[who] = items
    return out, widths, amap


def measure(it, pt, widths, amap):
    text = diary.wrap_page(pt, widths, amap, it["palavras"])
    full = diary.expand(text, it["palavras"])
    return text, len(to_bytes(full, amap)), len(full.rstrip("\n").split("\n"))


def gerar(iso_path, size=50):
    data, widths, amap = load(iso_path)
    os.makedirs(os.path.join(WORK, "lotes"), exist_ok=True)
    os.makedirs(os.path.join(WORK, "pt"), exist_ok=True)
    for who, items in data.items():
        its = sorted(items.values(), key=lambda it: it["id"])
        n = -(-len(its) // size)
        for k in range(n):
            chunk = its[k * len(its) // n:(k + 1) * len(its) // n]
            path = os.path.join(WORK, "lotes", f"{who}_{k:02d}.jsonl")
            with open(path, "w", encoding="utf-8") as f:
                for it in chunk:
                    _, nbytes, nlines = measure(it, it["pt"], widths, amap)
                    f.write(json.dumps({**it, "bytes": nbytes, "linhas": nlines}, ensure_ascii=False) + "\n")
            print(path, len(chunk))


def conferir(data, widths, amap, lote, quiet=False):
    src = [json.loads(l) for l in open(os.path.join(WORK, "lotes", f"{lote}.jsonl"), encoding="utf-8") if l.strip()]
    path = os.path.join(WORK, "pt", f"{lote}.jsonl")
    got = {}
    for l in open(path, encoding="utf-8"):
        if l.strip():
            it = json.loads(l)
            got[it["id"]] = it["pt"]
    errors = 0
    for it in src:
        if it["id"] not in got:
            print(f"id {it['id']}: falta")
            errors += 1
            continue
        pt = got[it["id"]]
        text, nbytes, nlines = measure(it, pt, widths, amap)
        probs = text_problems(it["jp"], pt, "fala") + diary.problems(text, widths, amap, it["palavras"])
        for p in probs:
            print(f"id {it['id']}: {p}")
        errors += len(probs)
        if not quiet and not probs:
            print(f"id {it['id']}: ok ({nbytes} bytes, {nlines} linhas)")
    print("OK" if errors == 0 else f"{errors} problema(s)")
    return errors == 0, got


def aceitar(data, widths, amap, lotes):
    for lote in lotes:
        ok, got = conferir(data, widths, amap, lote, quiet=True)
        if not ok:
            print(lote, "FALHOU")
            continue
        who = lote.split("_")[0]
        done = set()
        for fn in sorted(glob.glob(os.path.join(PT_DIR, f"{who}_*.jsonl"))):
            lines = open(fn, encoding="utf-8").read().split("\n")
            hit = False
            for i, l in enumerate(lines):
                if l.strip():
                    it = json.loads(l)
                    if it["id"] in got:
                        it["pt"] = got[it["id"]]
                        lines[i] = json.dumps(it, ensure_ascii=False)
                        done.add(it["id"])
                        hit = True
            if hit:
                open(fn, "w", encoding="utf-8", newline="").write("\n".join(lines))
        print(lote, "gravado", len(done), "faltando", sorted(set(got) - done))


if __name__ == "__main__":
    cmd, iso_path = sys.argv[1], sys.argv[2]
    if cmd == "gerar":
        gerar(iso_path, *(int(x) for x in sys.argv[3:]))
    else:
        args = load(iso_path)
        if cmd == "conferir":
            ok, _ = conferir(*args, sys.argv[3])
            sys.exit(0 if ok else 1)
        aceitar(*args, sys.argv[3:])

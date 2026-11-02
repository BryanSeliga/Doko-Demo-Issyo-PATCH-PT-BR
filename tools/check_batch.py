"""Valida um lote traduzido: check_batch.py <lote_jp.jsonl> <lote_pt.jsonl>

Formato do lote traduzido: uma linha JSON por texto, {"id": n, "pt": "..."}.
Sai com codigo 0 e imprime OK se estiver tudo certo; senao lista cada problema.
"""
import collections
import json
import re
import sys

from fontpatch import ACCENTS

sys.stdout.reconfigure(encoding="utf-8")
TOKEN = re.compile(r"\{W\}|\{[0-9a-f]{2}:[0-9a-f]{4}\}|\$_[A-Z0-9]+")
ALLOWED = set(chr(c) for c in range(0x20, 0x7F)) - {"\\"} | set(ACCENTS) | {"\n", "♪", "♥"}


def tokens(s):
    return collections.Counter(TOKEN.findall(s))


def problems(jp, pt, tipo):
    out = []
    if tokens(jp) != tokens(pt):
        out.append(f"variaveis diferentes: {dict(tokens(jp))} vs {dict(tokens(pt))}")
    if jp.endswith("\n") != pt.endswith("\n"):
        out.append("o final com \\n precisa ser igual ao do japones")
    if not pt.strip():
        out.append("texto vazio")
    for label, a, b in (("inicio", jp[:1], pt[:1]), ("fim", jp.rstrip("\n")[-1:], pt.rstrip("\n")[-1:])):
        if (a == " ") != (b == " "):
            out.append(f"espaco no {label} precisa ser igual ao do japones")
    bad = sorted({c for c in TOKEN.sub("", pt) if c not in ALLOWED})
    if bad:
        out.append(f"caracteres fora da fonte: {bad}")
    if "miau" in pt.lower() and "{17:0017}" in jp and "{17:0017}" not in pt:
        out.append("use {17:0017} em vez de escrever miau")
    if tipo == "pool" and "\n" in jp.rstrip("\n"):
        for line in pt.split("\n"):
            if len(TOKEN.sub("xxxxxx", line)) > 26:
                out.append(f"linha de pool com mais de 26 caracteres: {line!r}")
    return out


def main(src, dst):
    jp = {}
    for line in open(src, encoding="utf-8"):
        it = json.loads(line)
        jp[it["id"]] = it
    seen = set()
    errors = 0
    for n, line in enumerate(open(dst, encoding="utf-8"), 1):
        if not line.strip():
            continue
        try:
            it = json.loads(line)
            i, pt = it["id"], it["pt"]
        except (ValueError, KeyError) as e:
            print(f"linha {n}: JSON invalido: {e}")
            errors += 1
            continue
        if i not in jp:
            print(f"id {i}: nao existe neste lote")
            errors += 1
            continue
        if i in seen:
            print(f"id {i}: repetido")
            errors += 1
        seen.add(i)
        for p in problems(jp[i]["jp"], pt, jp[i]["tipo"]):
            print(f"id {i}: {p}")
            errors += 1
    missing = sorted(set(jp) - seen)
    if missing:
        print(f"faltam {len(missing)} ids: {missing[:30]}")
        errors += len(missing)
    print("OK" if errors == 0 else f"{errors} problema(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

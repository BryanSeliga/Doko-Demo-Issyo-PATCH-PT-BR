"""Lista as strings de texto do BOOT.BIN com o espaco disponivel para cada uma.

Capacidade = tamanho da string + zeros seguintes, menos 1 para o terminador.
Uso: boot_strings.py <BOOT.BIN> <saida.jsonl>
"""
import json
import re
import sys

RODATA = (0xD2A38, 0xD2A38 + 0x111C0)
JP = re.compile(r"[぀-ヿ一-鿿＀-￯■-◿]")
JUNK = re.compile(r"[Ͱ-⿿-｡-ﾟ]")


def scan(b):
    out = []
    i = RODATA[0]
    while i < RODATA[1]:
        if b[i] == 0:
            i += 1
            continue
        end = b.index(b"\0", i)
        raw = b[i:end]
        cap = end
        while cap < RODATA[1] and b[cap] == 0:
            cap += 1
        text = enc = None
        for e in ("cp932", "utf-8"):
            try:
                t = raw.decode(e)
            except UnicodeDecodeError:
                continue
            if JP.search(t) and not (e == "cp932" and JUNK.search(t.replace("…", "").replace("―", "").replace("○", "").replace("●", "").replace("☆", "").replace("×", ""))):
                text, enc = t, e
                break
        if text is not None:
            out.append({"off": i, "cap": cap - i - 1, "enc": enc, "jp": text})
        i = end + 1
    return out


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    items = scan(data)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(len(items))

"""Paginas do diario: onde ficam no KSC, quebra de linha e limites da pagina.

Cada pagina e um registro de 6 valores na tabela do KSC: 9:6, 2:tipo, (0 ou b:palavra1), 5:palavra1,
(0 ou b:palavra2), 5:palavra2, 5:texto. O texto entra no save ja com as variaveis trocadas ($_W1 e $_W2
pelas palavras do registro, $_YOU, $_ME etc. pelos nomes).

Limites medidos no jogo: a pagina quebra a linha em 170 unidades e mostra 8 linhas; a trava do BOOT
(boot_text.DIARY_TEXT_MAX) corta o texto em 90 bytes de Shift-JIS, ja com as variaveis trocadas.
As duas primeiras linhas podem ir para um titulo de 40 caracteres.
"""
import re
import struct

from kscbuild import layout
from textfmt import to_bytes
from wrap import text_width, wrap

WIDTH = 160
GAME_WIDTH = 170
LINES = 8
BYTES = 88
TITLE_CHARS = 36
# Estimativa dos nomes (jogador, Pokepi, amigo): 6 letras latinas.
NAME = "Nnnnnn"
# Palavra sem registro (vem do vocabulario do Pokepi).
WORD = "Nnnnnnnnnn"
VAR = re.compile(r"\$_[A-Z0-9]+")


def pages(d):
    """Lista (offset_do_texto, [offset_palavra1 ou None, offset_palavra2 ou None]) no pool."""
    lay = layout(d)
    t = struct.unpack_from(f"<{(len(d) - lay['table']) // 4}I", d, lay["table"])
    out = []
    for k in range(len(t) - 7):
        if t[k] != (9 << 28) | 6:
            continue
        v = t[k + 1:k + 7]
        tags = [x >> 28 for x in v]
        if tags[0] == 2 and tags[1] in (0, 0xB) and tags[2] == 5 and tags[3] in (0, 0xB) and tags[4] == 5 and tags[5] == 5:
            words = [v[2] & 0xFFFFFFF if tags[1] else None, v[4] & 0xFFFFFFF if tags[3] else None]
            out.append((v[5] & 0xFFFFFFF, words))
    return out


def expand(text, words):
    """Texto com as variaveis trocadas por valores do tamanho esperado. words: {"$_W1": "Leite", ...}."""
    return VAR.sub(lambda m: words.get(m.group(), WORD if m.group().startswith("$_W") else NAME), text)


def wrap_page(text, widths, amap, words):
    """Quebra cada paragrafo na largura da pagina; as quebras do texto ficam."""
    tail = "\n" if text.endswith("\n") else ""
    body = text[:-1] if tail else text
    var_width = max([text_width(w, widths, amap) for w in words.values()] + [text_width(NAME, widths, amap)])
    return "\n".join(wrap(p, widths, amap, WIDTH, var_width) for p in body.split("\n")) + tail


def problems(text, widths, amap, words):
    """Problemas da pagina ja quebrada por wrap_page."""
    full = expand(text, words)
    lines = full.rstrip("\n").split("\n")
    out = []
    size = len(to_bytes(full, amap))
    if size > BYTES:
        out.append(f"{size} bytes (maximo {BYTES}; corte {size - BYTES})")
    # palavra do registro maior que a linha: o jogo a parte em mais de uma linha
    shown = sum(max(1, -(-text_width(l, widths, amap) // GAME_WIDTH)) for l in lines)
    if shown > LINES:
        out.append(f"{shown} linhas (maximo {LINES})")
    if len("".join(lines[:2])) > TITLE_CHARS:
        out.append(f"duas primeiras linhas com {len(''.join(lines[:2]))} letras (maximo {TITLE_CHARS})")
    return out

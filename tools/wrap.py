"""Quebra de linha por palavra para o balao de fala (largura util de 119 unidades da fonte)."""
import re

from textfmt import TOKEN

BALLOON_WIDTH = 119
# Palavras inseridas pelo jogo (vocabulario, palavras ensinadas): a maioria cabe em 90 unidades.
VAR_WIDTH = 90
# Largura do tique verbal ({17:...}); make_iso troca pela largura real do texto (", miau" = 48).
TIC_WIDTH = 48
PIECE = re.compile(r"\{W\}|\{[0-9a-f]{2}:[0-9a-f]{4}\}|\$_[A-Z0-9]+|.", re.S)


def char_width(ch, widths, amap):
    if ch in amap:
        lead, trail = amap[ch] >> 8, amap[ch] & 0xFF
        return widths[2 * 96 + trail - 0x9E] if lead == 0x81 else 16
    code = ord(ch)
    if 0x20 <= code < 0x7F:
        return widths[code - 0x20]
    return 16


def text_width(text, widths, amap):
    total = 0
    for p in PIECE.findall(text):
        if p == "{W}":
            continue
        if len(p) > 1:
            total += TIC_WIDTH if p.startswith("{17") else VAR_WIDTH
        else:
            total += char_width(p, widths, amap)
    return total


def wrap(text, widths, amap, limit=BALLOON_WIDTH):
    """Troca espacos por quebras para nenhuma linha passar do limite. Mantem o \\n final."""
    tail = "\n" if text.endswith("\n") else ""
    body = text[:-1] if tail else text
    lead = body[:len(body) - len(body.lstrip(" "))]
    trail = body[len(body.rstrip(" ")):]
    words = " ".join(body.split()).split(" ") if body.strip() else []
    lines, cur = [], ""
    space = widths[0]
    for w in words:
        if not cur:
            cur = w
        elif text_width(cur, widths, amap) + space + text_width(w, widths, amap) <= limit:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lead + "\n".join(lines) + trail + tail

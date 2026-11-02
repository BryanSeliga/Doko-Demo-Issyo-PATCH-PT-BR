"""Desenha as letras acentuadas do portugues em glifos livres do FONT.XFT.

Codigos livres do Shift-JIS mostram um ponto na fonte original. Cada letra acentuada ganha
um desses codigos de 2 bytes; o resto do texto em PT-BR usa ASCII de 1 byte.
"""
from xft import glyph_pixels, set_glyph, WIDTHS_OFF

PLACEHOLDER_IDX = 0xD0
ACCENTS = "áàâãéêíóôõúüçÁÀÂÃÉÊÍÓÔÕÚÜÇ"
BASE = {"á": "a", "à": "a", "â": "a", "ã": "a", "é": "e", "ê": "e", "í": "i", "ó": "o", "ô": "o", "õ": "o", "ú": "u", "ü": "u", "ç": "c"}
MARK = {"á": "acute", "à": "grave", "â": "circ", "ã": "tilde", "é": "acute", "ê": "circ", "í": "acute", "ó": "acute", "ô": "circ", "õ": "tilde", "ú": "acute", "ü": "diaer", "ç": "cedil"}
SPACE_WIDTH = 6

# Pixels (dx, dy, intensidade) relativos ao centro da letra; dy sobe a partir do topo dela.
SHAPES = {
    "acute": [(1, 2, 15), (0, 1, 15), (-1, 0, 9), (2, 2, 9), (1, 1, 7)],
    "grave": [(-1, 2, 15), (0, 1, 15), (1, 0, 9), (-2, 2, 9), (-1, 1, 7)],
    "circ": [(0, 2, 15), (-1, 1, 15), (1, 1, 15), (-2, 0, 13), (2, 0, 13), (-1, 2, 7), (1, 2, 7)],
    "tilde": [(-3, 0, 13), (-2, 1, 15), (-1, 1, 15), (0, 0, 13), (1, 0, 15), (2, 1, 15), (3, 1, 12), (-3, 1, 6), (0, 1, 7), (3, 0, 6)],
    "diaer": [(-2, 1, 15), (-2, 0, 15), (-3, 1, 7), (-3, 0, 7), (2, 1, 15), (2, 0, 15), (3, 1, 7), (3, 0, 7)],
}


def sjis_to_glyph(code):
    """Indice do glifo para um codigo de linha 2 do Shift-JIS (0x819F..0x81FC)."""
    assert 0x819F <= code <= 0x81FC
    return 2 * 96 + (code & 0xFF) - 0x9E


def glyph_to_sjis(idx):
    return 0x8100 | (idx - 2 * 96 + 0x9E)


def free_codes(font):
    ref = glyph_pixels(font, PLACEHOLDER_IDX)
    out = []
    for code in range(0x819F, 0x81FD):
        if code == 0x81FC:
            continue
        idx = sjis_to_glyph(code)
        if glyph_pixels(font, idx) == ref:
            out.append(code)
    return out


def accent_map(font):
    """Mapa fixo letra acentuada -> codigo Shift-JIS livre."""
    codes = free_codes(font)
    assert len(codes) >= len(ACCENTS), len(codes)
    return dict(zip(ACCENTS, codes))


def compose(font, ch):
    lower = ch.lower()
    base = BASE[lower].upper() if ch.isupper() else BASE[lower]
    rows = [list(r) for r in glyph_pixels(font, ord(base) - 0x20)]
    ys = [y for y in range(16) if any(rows[y])]
    xs = [x for y in ys for x in range(16) if rows[y][x]]
    top, bottom = ys[0], ys[-1]
    cx = (min(xs) + max(xs) + 1) // 2
    mark = MARK[lower]
    if mark == "cedil":
        # A letra encosta na ultima linha da celula: sobe para abrir espaco para o rabinho.
        shift = min(top, 2 if ch.islower() else 1, bottom - 11)
        rows = rows[shift:] + [[0] * 16 for _ in range(shift)]
        bottom -= shift
        for dx, dy, v in ((0, 1, 15), (1, 2, 15), (0, 3, 11)):
            y = bottom + dy
            if y < 16:
                rows[y][cx + dx] = max(rows[y][cx + dx], v)
        return rows, base
    if ch.isupper():
        # Maiusculas quase encostam no topo da celula: desce a letra 1 linha quando da.
        if bottom < 15 and top < 3:
            rows = [[0] * 16] + rows[:-1]
            top += 1
    gap = 1 if ch.isupper() else 2
    for dx, dy, v in SHAPES[mark]:
        y = top - gap - dy
        x = cx + dx
        if 0 <= y < 16 and 0 <= x < 16:
            rows[y][x] = max(rows[y][x], v)
    return rows, base


def patch(font_bytes):
    """Devolve (fonte_nova, mapa). A largura do espaco tambem sobe para melhorar a leitura."""
    font = bytearray(font_bytes)
    amap = accent_map(font)
    for ch, code in amap.items():
        rows, base = compose(font, ch)
        width = font[WIDTHS_OFF + ord(base) - 0x20]
        set_glyph(font, sjis_to_glyph(code), rows, width)
    font[WIDTHS_OFF] = SPACE_WIDTH
    return bytes(font), amap

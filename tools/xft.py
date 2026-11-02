"""FONT.XFT: 8192 glifos 16x16 4bpp em 32 texturas 256x256 lineares; larguras por glifo em 0x3C."""

WIDTHS_OFF = 0x3C
BITMAP_OFF = 0x2040
TEX_BYTES = 0x8000
PITCH = 128


def tex(font, n):
    """Textura n como buffer linear (pitch 128 bytes, nibble baixo = pixel esquerdo)."""
    return font[BITMAP_OFF + n * TEX_BYTES:BITMAP_OFF + (n + 1) * TEX_BYTES]


def glyph_pixels(font, idx):
    """Pixels (valores 0-15) do glifo idx como lista de 16 linhas."""
    t = tex(font, idx >> 8)
    cx, cy = (idx & 15) * 8, ((idx >> 4) & 15) * 16
    rows = []
    for y in range(16):
        row = []
        for x in range(16):
            b = t[(cy + y) * PITCH + cx + x // 2]
            row.append((b >> 4) if x & 1 else (b & 15))
        rows.append(row)
    return rows


def set_glyph(font, idx, rows, width):
    """Grava um glifo em um bytearray do XFT e sua largura."""
    base = BITMAP_OFF + (idx >> 8) * TEX_BYTES
    cx, cy = (idx & 15) * 8, ((idx >> 4) & 15) * 16
    for y in range(16):
        for xb in range(8):
            font[base + (cy + y) * PITCH + cx + xb] = (rows[y][xb * 2] & 15) | ((rows[y][xb * 2 + 1] & 15) << 4)
    font[WIDTHS_OFF + idx] = width

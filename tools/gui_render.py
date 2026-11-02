"""Redesenha rotulos GIM em portugues, no mesmo tamanho e com as cores da imagem original."""
import collections
import struct

from PIL import Image, ImageDraw, ImageFont

from gim import image_info, parse, to_rgba
from gui_text import BY_PACK, COMMON
from iso_common import inner_files

FONT_PATH = r"C:\Windows\Fonts\ARLRDBD.TTF"
SCALE = 4


def analyse(w, h, rgba):
    """Cor do texto, do contorno e do fundo da imagem original."""
    px = [tuple(rgba[i:i + 4]) for i in range(0, len(rgba), 4)]
    corners = [px[0], px[w - 1], px[(h - 1) * w], px[h * w - 1]]
    bg = None
    if sum(1 for c in corners if c[3] > 200) >= 3:
        bg = collections.Counter(c[:3] for c in corners).most_common(1)[0][0]
    solid = [p[:3] for p in px if p[3] > 110 and (bg is None or p[:3] != bg)]
    if not solid:
        return (255, 255, 255), None, bg
    lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    count = collections.Counter(solid)
    bright = sorted(count, key=lum)
    light = collections.Counter({c: n for c, n in count.items() if lum(c) >= lum(bright[len(bright) // 2])})
    dark = collections.Counter({c: n for c, n in count.items() if lum(c) < lum(bright[len(bright) // 2])})
    fill = light.most_common(1)[0][0] if light else bright[-1]
    outline = dark.most_common(1)[0][0] if dark else None
    total = sum(count.values())
    if outline is not None and (sum(dark.values()) < total * 0.05 or abs(lum(fill) - lum(outline)) < 40):
        outline = None
    return fill, outline, bg


def render(text, w, h, fill, outline, bg):
    """Texto centralizado que cabe em w x h. Reduz a fonte ate caber."""
    W, H = w * SCALE, h * SCALE
    limit = W * 9 // 10 if w > 120 else W - SCALE
    stroke = (2 if h >= 28 else 1) * SCALE if outline else 0
    size = H
    while size > 6:
        font = ImageFont.truetype(FONT_PATH, size)
        box = font.getbbox(text, stroke_width=stroke)
        if box[2] - box[0] <= limit and box[3] - box[1] <= H - SCALE:
            break
        size -= 1
    im = Image.new("RGBA", (W, H), (*(bg or (0, 0, 0)), 255 if bg else 0))
    d = ImageDraw.Draw(im)
    x = (W - (box[2] - box[0])) // 2 - box[0]
    y = (H - (box[3] - box[1])) // 2 - box[1]
    d.text((x, y), text, font=font, fill=(*fill, 255), stroke_width=stroke, stroke_fill=(*(outline or fill), 255))
    return im.resize((w, h), Image.LANCZOS)


def write_gim(data, im):
    """Grava a imagem no GIM original, mantendo formato, paleta de tamanho igual e tamanho do arquivo."""
    data = bytearray(data)
    blocks = parse(bytes(data))
    img = next(b for b in blocks if b[0] == 4)
    pal = next(b for b in blocks if b[0] == 5)
    inf = image_info(bytes(data), img[1])
    pinf = image_info(bytes(data), pal[1])
    assert inf["fmt"] in (4, 5) and inf["order"] == 0 and pinf["fmt"] == 3, inf
    w, h = inf["w"], inf["h"]
    ncol = 16 if inf["fmt"] == 4 else 256
    q = im.quantize(colors=min(ncol, pinf["w"]), method=Image.FASTOCTREE, dither=Image.NONE)
    palette = q.getpalette("RGBA")
    colors = [tuple(palette[i * 4:i * 4 + 4]) for i in range(len(palette) // 4)]
    # A paleta pode vir com cor quase transparente: garante indice 0 transparente sem mudar a imagem.
    for i in range(pinf["w"]):
        c = colors[i] if i < len(colors) else (0, 0, 0, 0)
        struct.pack_into("<4B", data, pinf["pix"] + i * 4, *c)
    stride = (w * inf["bpp"] + 7) // 8
    stride += (-stride) % 16
    px = q.load()
    for y in range(h):
        for x in range(w):
            v = px[x, y]
            if inf["fmt"] == 4:
                o = inf["pix"] + y * stride + x // 2
                if x & 1:
                    data[o] = (data[o] & 0x0F) | (v << 4)
                else:
                    data[o] = (data[o] & 0xF0) | v
            else:
                data[inf["pix"] + y * stride + x] = v
    return bytes(data)


def translate_label(data, text):
    w, h, rgba, _ = to_rgba(data)
    fill, outline, bg = analyse(w, h, rgba)
    return write_gim(data, render(text, w, h, fill, outline, bg))


def build_all(iso, bpms):
    """Devolve {(pacote, nome_interno): bytes} com todas as imagens traduzidas."""
    out = {}
    for pack, (off, size) in bpms.items():
        table = BY_PACK.get(pack, {})
        if pack.startswith(("F", "W", "E", "D", "S", "BG", "KS")) and pack not in BY_PACK and pack != "SBOARD.BPM":
            continue
        for name, o, s in inner_files(iso, off):
            if not name.endswith(".GIM"):
                continue
            base = name.split(chr(92))[-1][:-4]
            text = table.get(base) or COMMON.get(base)
            if text:
                out[(pack, name)] = translate_label(iso.bp(o, s), text)
    return out

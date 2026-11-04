"""Redesenha rotulos GIM em portugues, no mesmo tamanho e com as cores da imagem original."""
import collections
import os
import struct

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from gim import image_info, parse, to_rgba
from gui_text import BY_PACK, COMMON, PIECE_PX, PIECES, VERTICAL
from iso_common import inner_files

# M PLUS Rounded 1c (SIL OFL, ver fonts/OFL.txt): o mesmo desenho arredondado do patch em ingles.
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "MPLUSRounded1c-ExtraBold.ttf")
TRACKING = 0.06  # espaco extra entre letras, em fracao do tamanho da fonte
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


def text_box(text, font, track, stroke):
    """Caixa (x0, y0, x1, y1) do texto desenhado letra a letra com espaco extra."""
    box = font.getbbox(text, stroke_width=stroke)
    return box[0], box[1], box[2] + track * (len(text) - 1), box[3]


def draw_tracked(d, xy, text, font, track, **kw):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, **kw)
        x += font.getlength(ch) + track


def render(text, w, h, fill, outline, bg):
    """Texto centralizado que cabe em w x h. Reduz a fonte ate caber."""
    return render_hi(text, w, h, fill, outline, bg).resize((w, h), Image.LANCZOS)


def render_hi(text, w, h, fill, outline, bg, max_w=None, area=None):
    """Como render, mas devolve a imagem em SCALE vezes o tamanho final. max_w limita a largura do texto;
    area (x0, x1) e a faixa da textura que o jogo mostra, onde o texto e centralizado."""
    W, H = w * SCALE, h * SCALE
    limit = W * 9 // 10 if w > 120 else W - SCALE
    x0, x1 = (0, W) if area is None else (area[0] * SCALE, area[1] * SCALE)
    limit = min(limit, x1 - x0)
    if max_w is not None:
        limit = min(limit, max_w * SCALE)
    stroke = (2 if h >= 28 else 1) * SCALE if outline else 0
    size = H
    while size > 6:
        font = ImageFont.truetype(FONT_PATH, size)
        track = size * TRACKING
        box = text_box(text, font, track, stroke)
        if box[2] - box[0] <= limit and box[3] - box[1] <= H - SCALE:
            break
        size -= 1
    im = Image.new("RGBA", (W, H), (*(bg or (0, 0, 0)), 255 if bg else 0))
    d = ImageDraw.Draw(im)
    x = x0 + (x1 - x0 - (box[2] - box[0])) // 2 - box[0]
    y = (H - (box[3] - box[1])) // 2 - box[1]
    draw_tracked(d, (x, y), text, font, track, fill=(*fill, 255), stroke_width=stroke, stroke_fill=(*(outline or fill), 255))
    return im


def render_piece(data, text):
    """Uma silaba de titulo dividido em pedacos: letra de PIECE_PX, com a base e o centro da silaba original."""
    w, h, rgba, _ = to_rgba(data)
    fill, _, _ = analyse(w, h, rgba)
    ys, xs = np.nonzero(np.frombuffer(rgba, np.uint8).reshape(h, w, 4)[:, :, 3] > 100)
    cx, base = (xs.min() + xs.max() + 1) / 2 * SCALE, (ys.max() + 1) * SCALE
    font = ImageFont.truetype(FONT_PATH, PIECE_PX * SCALE)
    im = Image.new("RGBA", (w * SCALE, h * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x0, _, x1, _ = d.textbbox((cx, base), text, font=font, anchor="ms")
    cx -= min(0, x0) + max(0, x1 - w * SCALE)  # dentro da imagem
    d.text((cx, base), text, font=font, fill=(*fill, 255), anchor="ms")
    return write_gim(data, im.resize((w, h), Image.LANCZOS))


def render_vertical(data, text):
    """Texto girado 90 graus na faixa onde ficava o texto vertical japones."""
    w, h, _, _ = to_rgba(data)
    area = ink_area(data, None) or (0, w)
    band = (area[1] - area[0]) * SCALE
    im = Image.new("RGBA", (h * SCALE, w * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = band
    while True:
        font = ImageFont.truetype(FONT_PATH, size)
        box = d.textbbox((0, 0), text, font=font)
        if (box[2] - box[0] <= (h - 2) * SCALE and box[3] - box[1] <= band) or size <= 6 * SCALE:
            break
        size -= SCALE // 2
    d.text(((h * SCALE - (box[2] - box[0])) / 2 - box[0], area[0] * SCALE + (band - (box[3] - box[1])) / 2 - box[1]),
           text, font=font, fill=(255, 255, 255, 255))
    return write_gim(data, im.rotate(90, expand=True).resize((w, h), Image.LANCZOS))


def pack16(c, fmt):
    """Cor RGBA em paleta de 16 bits do GIM: 0 = RGB565, 1 = RGBA5551, 2 = RGBA4444."""
    r, g, b, a = c
    if fmt == 0:
        return round(r * 31 / 255) | round(g * 63 / 255) << 5 | round(b * 31 / 255) << 11
    if fmt == 1:
        return round(r * 31 / 255) | round(g * 31 / 255) << 5 | round(b * 31 / 255) << 10 | (a >= 128) << 15
    return round(r * 15 / 255) | round(g * 15 / 255) << 4 | round(b * 15 / 255) << 8 | round(a * 15 / 255) << 12


def write_gim(data, im):
    """Grava a imagem no GIM original, mantendo formato, paleta de tamanho igual e tamanho do arquivo."""
    data = bytearray(data)
    blocks = parse(bytes(data))
    img = next(b for b in blocks if b[0] == 4)
    pal = next(b for b in blocks if b[0] == 5)
    inf = image_info(bytes(data), img[1])
    pinf = image_info(bytes(data), pal[1])
    assert inf["fmt"] in (4, 5) and inf["order"] == 0 and pinf["fmt"] in (0, 1, 2, 3), inf
    w, h = inf["w"], inf["h"]
    ncol = 16 if inf["fmt"] == 4 else 256
    q = im.quantize(colors=min(ncol, pinf["w"]), method=Image.FASTOCTREE, dither=Image.NONE)
    palette = q.getpalette("RGBA")
    colors = [tuple(palette[i * 4:i * 4 + 4]) for i in range(len(palette) // 4)]
    # A paleta pode vir com cor quase transparente: garante indice 0 transparente sem mudar a imagem.
    for i in range(pinf["w"]):
        c = colors[i] if i < len(colors) else (0, 0, 0, 0)
        if pinf["fmt"] == 3:
            struct.pack_into("<4B", data, pinf["pix"] + i * 4, *c)
        else:
            struct.pack_into("<H", data, pinf["pix"] + i * 2, pack16(c, pinf["fmt"]))
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
    return write_gim(data, label_hi(data, text).resize(gim_size(data), Image.LANCZOS))


def gim_size(data):
    w, h, _, _ = to_rgba(data)
    return w, h


def label_hi(data, text, max_w=None):
    w, h, rgba, _ = to_rgba(data)
    fill, outline, bg = analyse(w, h, rgba)
    return render_hi(text, w, h, fill, outline, bg, max_w, ink_area(data, bg))


def ink_area(data, bg):
    """Faixa horizontal ocupada pelo texto original. Muitas texturas sao maiores que a parte visivel no jogo
    (a aba vizinha ou um icone cobre o resto), e o texto japones fica so na parte visivel."""
    px = rgba_array(data)
    ink = px[:, :, 3] > 60
    if bg is not None:
        ink &= np.any(px[:, :, :3] != np.array(bg, np.uint8), axis=2)
    cols = np.nonzero(ink.any(axis=0))[0]
    if len(cols) == 0:
        return None
    return max(0, int(cols[0]) - 1), min(px.shape[1], int(cols[-1]) + 2)


def rgba_array(data):
    w, h, rgba, _ = to_rgba(data)
    return np.frombuffer(bytes(rgba), np.uint8).reshape(h, w, 4)


def dilate(mask, r):
    return np.array(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(2 * r + 1))) > 0


def place(mask, shape, dx, dy):
    """Copia mask para um quadro do tamanho shape, deslocada de (dx, dy)."""
    out = np.zeros(shape, bool)
    ys, xs = np.nonzero(mask)
    ys, xs = ys + dy, xs + dx
    ok = (ys >= 0) & (ys < shape[0]) & (xs >= 0) & (xs < shape[1])
    out[ys[ok], xs[ok]] = True
    return out


def fit_base(text_alpha, base_alpha):
    """Quanto o fundo listrado engorda o texto (r) e onde fica em relacao a ele (dx, dy), medido no original."""
    best = (-1, 0, 0, 0)
    for r in (2, 3, 4, 5):
        grown = dilate(text_alpha, r)
        for dy in range(-6, 12):
            for dx in range(-6, 10):
                m = place(grown, base_alpha.shape, dx, dy)
                iou = (m & base_alpha).sum() / max(1, (m | base_alpha).sum())
                best = max(best, (iou, r, dx, dy))
    return best[1:]


def stripes(base):
    """As listras do fundo original, estendidas para os buracos entre as letras (copia a coluna coberta mais proxima)."""
    covered = base[:, :, 3] > 100
    out = base.copy()
    for y in range(base.shape[0]):
        xs = np.nonzero(covered[y])[0]
        if len(xs) == 0:
            src = np.nonzero(covered.any(axis=1))[0]
            if len(src) == 0:
                continue
            yy = src[np.abs(src - y).argmin()]
            xs, row = np.nonzero(covered[yy])[0], base[yy]
        else:
            row = base[y]
        idx = xs[np.abs(np.arange(base.shape[1])[:, None] - xs[None, :]).argmin(axis=1)]
        out[y] = row[idx]
    return out


def base_fit(base_data, old_label):
    r, dx, dy = fit_base(rgba_array(old_label)[:, :, 3] > 100, rgba_array(base_data)[:, :, 3] > 100)
    return r + 1, dx, dy  # letras latinas sao mais finas que as japonesas: mais folga, como no patch em ingles


def translate_base(base_data, new_label_hi, fit):
    """Refaz o fundo listrado no formato do texto novo, com a mesma folga e posicao do original."""
    old = rgba_array(base_data)
    r, dx, dy = fit
    hi = np.array(new_label_hi)[:, :, 3] > 100
    big = place(dilate(hi, r * SCALE), (old.shape[0] * SCALE, old.shape[1] * SCALE), dx * SCALE, dy * SCALE)
    alpha = np.array(Image.fromarray(big.astype(np.uint8) * 255).resize((old.shape[1], old.shape[0]), Image.BOX))
    out = stripes(old)
    out[:, :, 3] = alpha
    return write_gim(base_data, Image.fromarray(out, "RGBA"))


def build_all(iso, bpms):
    """Devolve {(pacote, nome_interno): bytes} com todas as imagens traduzidas."""
    out = {}
    for pack, (off, size) in bpms.items():
        table = BY_PACK.get(pack, {})
        if pack.startswith(("F", "W", "E", "D", "S", "BG", "KS")) and pack not in BY_PACK and pack != "SBOARD.BPM":
            continue
        files = {n.split(chr(92))[-1][:-4]: (n, o, s) for n, o, s in inner_files(iso, off) if n.endswith(".GIM")}
        for key, text in VERTICAL.get(pack, {}).items():
            name, o, s = files[key]
            out[(pack, name)] = render_vertical(iso.bp(o, s), text)
        for key, text in PIECES.get(pack, {}).items():
            name, o, s = files[key]
            out[(pack, name)] = render_piece(iso.bp(o, s), text)
        for key, (name, o, s) in files.items():
            text = table.get(key) or COMMON.get(key)
            if not text:
                continue
            data = iso.bp(o, s)
            # fundo listrado dos menus (MENU_BASE1 atras de MENU1): segue o formato das letras
            base = key.replace("MENU", "MENU_BASE", 1) if key.startswith(("MENU", "SMENU")) else None
            if base not in files:
                hi = label_hi(data, text)
            else:
                bname, bo, bs = files[base]
                bdata = iso.bp(bo, bs)
                fit = r, dx, _ = base_fit(bdata, data)
                w, bw = gim_size(data)[0], gim_size(bdata)[0]
                # o texto e centralizado: os dois lados, com a folga do fundo, tem que caber na textura do fundo
                hi = label_hi(data, text, min(2 * (bw - dx - r - 1) - w, w + 2 * (dx - r - 1)))
                out[(pack, bname)] = translate_base(bdata, hi, fit)
            out[(pack, name)] = write_gim(data, hi.resize(gim_size(data), Image.LANCZOS))
    return out

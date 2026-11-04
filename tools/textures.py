"""Texturas 3D com japones (enfeites de estacao do quarto e cenario): apaga a escrita e desenha o portugues.

Cada entrada diz onde esta a escrita (caixas e regra da tinta), com que cor preencher o lugar (ou None para
recompor com os vizinhos) e os textos novos. As texturas sao pequenas (16 a 128 px): o texto e desenhado 4x
maior e reduzido, e a imagem volta para o GIM original com a paleta de 16 cores (gui_render.write_gim).
A mesma textura pode estar repetida em outros pacotes (variantes de noite e neve, objetos do quarto): todas as
copias identicas sao trocadas. As entradas do cenario ficam em textures_*.py, uma por grupo de lugares.

Formato de uma entrada, chave (pacote, caminho interno do GIM):
  "erase": lista de (caixa (x0, y0, x1, y1), regra da tinta)
      regras: ("redder", d)  vermelho acima do verde e do azul por mais de d
              ("dark", v)    canal mais claro abaixo de v
              ("light", v)   canal mais escuro acima de v
              ("near", (r, g, b), d)  distancia ate a cor menor que d
              ("all",)       a caixa inteira
  "fill": None (recompoe com os vizinhos), "rows" (cor mais comum da linha, para papel liso),
      (r, g, b) ou (r, g, b, 0) para transparente
  "texts": lista de {"lines": [...], "box": (x0, y0, x1, y1), "color": (r, g, b)} com opcionais
      "vertical": True (letras empilhadas), "turned": 90 ou -90 (a textura aparece girada no modelo 3D,
      90 = sentido horario; o texto e desenhado em pe na orientacao da tela), "outline": (r, g, b)
"""
import importlib
import pkgutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from gim import to_rgba
from gui_render import FONT_PATH, write_gim
from iso_common import inner_files

SCALE = 4

SPECS = {
    # saquinho de "chitose-ame" (doce do Shichi-Go-San), pendurado no quarto em novembro; fica em pe com a textura
    # girada, e o texto vai em letras empilhadas como os kanji do original
    ("BG_ROOM.BPM", "SEASON20\\GIM\\SEASON_11_01_01.GIM"): {
        "erase": [((31, 10, 59, 21), ("redder", 60))], "fill": (241, 241, 241),
        "texts": [{"lines": ["DOCE"], "box": (31, 10, 59, 21), "color": (211, 30, 40), "turned": 90, "vertical": True}]},
    # "gashou" (feliz ano novo), quadro do Ano Novo; a tinta e as bordas suavizadas puxam para o vermelho
    ("BG_ROOM.BPM", "SEASON07\\GIM\\SEASON_01_01.GIM"): {
        "erase": [((0, 0, 64, 64), ("redder", 22))], "fill": None,
        "texts": [{"lines": ["FELIZ", "ANO", "NOVO"], "box": (4, 4, 60, 60), "color": (120, 0, 0)}]},
    # "koori" (raspadinha de gelo), bandeirinha do verao
    ("BG_ROOM.BPM", "SEASON17\\GIM\\SEASON_07_02_01.GIM"): {
        "erase": [((0, 0, 64, 48), ("redder", 30))], "fill": (252, 252, 252),
        "texts": [{"lines": ["RASPA", "DINHA"], "box": (3, 8, 61, 44), "color": (161, 14, 27)}]},
    # "matsuri" (festa), lanterna da festa de verao; a moldura vermelho-escura (r bem maior que g) fica
    ("BG_ROOM.BPM", "SEASON19\\GIM\\KABE_U04.GIM"): {
        "erase": [((0, 0, 32, 32), lambda r, g, b, a: r - g < 45 and max(r, g, b) < 150)], "fill": None,
        "texts": [{"lines": ["FESTA"], "box": (1, 9, 31, 23), "color": (28, 22, 20)}]},
    # grito de festa em katakana, na faixa branca da esquerda
    ("BG_ROOM.BPM", "SEASON19\\GIM\\KABE_U04_02.GIM"): {
        "erase": [((9, 2, 16, 27), lambda r, g, b, a: r + g + b < 480)], "fill": None,
        "texts": [{"lines": ["OBA"], "box": (9, 3, 16, 26), "color": (100, 20, 10), "vertical": True}]},
    # "meri kurisumasu" (feliz natal), faixinha branca sobre fundo transparente
    ("BG_ROOM.BPM", "SEASON06\\GIM\\SEASON_12_01_01.GIM"): {
        "erase": [((0, 0, 32, 8), ("all",))], "fill": (0, 0, 0, 0),
        "texts": [{"lines": ["NATAL"], "box": (0, 0, 32, 8), "color": (253, 253, 253)}]},
}


def load_specs():
    """SPECS mais as entradas de cada textures_*.py."""
    specs = dict(SPECS)
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for mod in pkgutil.iter_modules([here]):
        if mod.name.startswith("textures_"):
            specs.update(importlib.import_module(mod.name).SPECS)
    return specs


def ink_rule(rule):
    if callable(rule):
        return rule
    kind = rule[0]
    if kind == "redder":
        return lambda r, g, b, a: r - max(g, b) > rule[1]
    if kind == "dark":
        return lambda r, g, b, a: max(r, g, b) < rule[1]
    if kind == "light":
        return lambda r, g, b, a: min(r, g, b) > rule[1]
    if kind == "near":
        c, d = rule[1], rule[2]
        return lambda r, g, b, a: (r - c[0]) ** 2 + (g - c[1]) ** 2 + (b - c[2]) ** 2 < d * d
    if kind == "all":
        return lambda r, g, b, a: True
    raise ValueError(rule)


def inpaint(px, mask):
    """Preenche os pixels marcados com a media dos vizinhos ja conhecidos, de fora para dentro."""
    px = px.astype(float)
    known = ~mask
    h, w = mask.shape
    while not known.all():
        acc = np.zeros_like(px)
        cnt = np.zeros((h, w))
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)):
            sk = np.zeros_like(known)
            sp = np.zeros_like(px)
            ys, yd = (slice(max(dy, 0), h + min(dy, 0)), slice(max(-dy, 0), h + min(-dy, 0)))
            xs, xd = (slice(max(dx, 0), w + min(dx, 0)), slice(max(-dx, 0), w + min(-dx, 0)))
            sk[yd, xd] = known[ys, xs]
            sp[yd, xd] = px[ys, xs]
            acc += sp * sk[:, :, None]
            cnt += sk
        new = ~known & (cnt > 0)
        if not new.any():
            break
        px[new] = acc[new] / cnt[new][:, None]
        known = known | new
    return px.astype(np.uint8)


def fill_rows(px, mask, boxes):
    """Pinta cada pixel apagado com a cor mais comum dos pixels que ficaram na mesma linha da caixa
    (papel liso ou em degrade vertical, onde recompor pelos vizinhos borra)."""
    px = px.copy()
    h, w = mask.shape
    for x0, y0, x1, y1 in boxes:
        last = None
        for y in range(y0, min(y1, h)):
            keep = [tuple(px[y, x]) for x in range(x0, min(x1, w)) if not mask[y, x]]
            if keep:
                last = max(set(keep), key=keep.count)
            if last is not None:
                for x in range(x0, min(x1, w)):
                    if mask[y, x]:
                        px[y, x] = last
    return px


def draw_text(size, lines, box, color, vertical=False, outline=None):
    """Camada RGBA com o texto no maior tamanho que cabe na caixa, centralizado."""
    x0, y0, x1, y1 = (v * SCALE for v in box)
    bw, bh = x1 - x0, y1 - y0
    layer = Image.new("RGBA", (size[0] * SCALE, size[1] * SCALE), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if vertical:
        lines = list(lines[0])
    stroke = SCALE if outline else 0
    px = bh
    while px > 4:
        font = ImageFont.truetype(FONT_PATH, px)
        boxes = [d.textbbox((0, 0), t, font=font, stroke_width=stroke) for t in lines]
        step = max(b[3] - b[1] for b in boxes) * (1.0 if vertical else 1.12)
        if max(b[2] - b[0] for b in boxes) <= bw and step * len(lines) <= bh:
            break
        px -= 1
    top = y0 + (bh - step * len(lines)) / 2
    for k, (t, b) in enumerate(zip(lines, boxes)):
        d.text((x0 + (bw - (b[2] - b[0])) / 2 - b[0], top + k * step - b[1]), t, font=font, fill=(*color[:3], 255),
               stroke_width=stroke, stroke_fill=(*(outline or color)[:3], 255))
    return layer.resize(size, Image.LANCZOS)


def text_layer(w, h, t):
    turned = t.get("turned", 0)
    if not turned:
        return draw_text((w, h), t["lines"], t["box"], t["color"], t.get("vertical", False), t.get("outline"))
    bx0, by0, bx1, by1 = t["box"]
    if turned == 90:  # tela = textura girada no sentido horario
        box = (h - by1, bx0, h - by0, bx1)
    else:
        box = (by0, w - bx1, by1, w - bx0)
    layer = draw_text((h, w), t["lines"], box, t["color"], t.get("vertical", False), t.get("outline"))
    return layer.rotate(turned, expand=True)


def translate(data, spec):
    w, h, rgba, _ = to_rgba(data)
    px = np.frombuffer(rgba, np.uint8).reshape(h, w, 4).copy()
    mask = np.zeros((h, w), bool)
    for (x0, y0, x1, y1), rule in spec["erase"]:
        ink = ink_rule(rule)
        for y in range(y0, min(y1, h)):
            for x in range(x0, min(x1, w)):
                mask[y, x] |= ink(*(int(v) for v in px[y, x]))
    fill = spec["fill"]
    if fill is None:
        px = inpaint(px, mask)
    elif fill == "rows":
        px = fill_rows(px, mask, [box for box, _ in spec["erase"]])
    else:
        px[mask] = fill if len(fill) == 4 else (*fill, 255)
    im = Image.fromarray(px, "RGBA")
    for t in spec["texts"]:
        im.alpha_composite(text_layer(w, h, t))
    return write_gim(data, im)


def build_all(iso, bpms, specs=None):
    """{(pacote, nome): bytes} para as texturas das entradas e todas as copias identicas delas."""
    originals = {}
    for (pack, name), spec in (specs or load_specs()).items():
        files = {n: (o, s) for n, o, s in inner_files(iso, bpms[pack][0])}
        data = iso.bp(*files[name])
        originals[data] = translate(data, spec)
    out = {}
    sizes = {len(d) for d in originals}
    for pack, (off, _) in bpms.items():
        for n, o, s in inner_files(iso, off):
            if s in sizes and n.endswith(".GIM"):
                data = iso.bp(o, s)
                if data in originals:
                    out[(pack, n)] = originals[data]
    return out

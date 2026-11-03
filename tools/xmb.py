"""Arte em portugues: titulo no PARAM.SFO, icone e descricao do menu do PSP e logotipo da tela titulo.

As imagens-fonte ficam em art/ (feitas pelo autor do patch) e sao reduzidas aqui ao tamanho de cada arquivo.
"""
import io
import os
import struct

from PIL import Image

TITLE = "Doko Demo Issyo"
ART = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "art")


def patch_sfo(sfo, title=TITLE):
    """Troca o TITLE do PARAM.SFO no lugar (o campo tem tamanho maximo fixo)."""
    sfo = bytearray(sfo)
    _, _, keys, data, n = struct.unpack_from("<4sIIII", sfo, 0)
    for i in range(n):
        ko, fmt, _, mx, do = struct.unpack_from("<HHIII", sfo, 20 + i * 16)
        if sfo[keys + ko:sfo.index(b"\0", keys + ko)] == b"TITLE":
            raw = title.encode("utf-8") + b"\0"
            assert len(raw) <= mx
            struct.pack_into("<I", sfo, 20 + i * 16 + 4, len(raw))
            sfo[data + do:data + do + mx] = raw + b"\0" * (mx - len(raw))
            return bytes(sfo)
    raise KeyError("TITLE")


def png(im):
    out = io.BytesIO()
    im.save(out, "PNG", optimize=True)
    return out.getvalue()


def icon0():
    """ICON0.PNG: 144x80, opaco."""
    return png(Image.open(os.path.join(ART, "icon.png")).convert("RGB").resize((144, 80), Image.LANCZOS))


def pic0(original):
    """PIC0.PNG: 310x180. Fora da moldura fica transparente como no original, para o fundo do menu aparecer."""
    im = Image.open(os.path.join(ART, "pic0.png")).convert("RGBA").resize((310, 180), Image.LANCZOS)
    outside = Image.open(io.BytesIO(original)).convert("RGBA").getchannel("A").point(lambda a: 255 if a else 0)
    im.putalpha(outside)
    # com 256 cores o PNG cabe nos setores do original
    return png(im.quantize(256, method=Image.Quantize.FASTOCTREE))


def title_logo(w, h):
    """Logotipo da tela titulo no tamanho da textura, centralizado e com fundo transparente."""
    logo = Image.open(os.path.join(ART, "logo.png")).convert("RGBA")
    logo = logo.crop(logo.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox())
    scale = min(w / logo.width, h / logo.height)
    logo = logo.resize((round(logo.width * scale), round(logo.height * scale)), Image.LANCZOS)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(logo, ((w - logo.width) // 2, (h - logo.height) // 2))
    return out

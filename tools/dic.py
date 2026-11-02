"""Vocabulario inicial do Pokepi (arquivo .DIC dentro do KS*.BPM).

Formato: u32 0x9000_0000|n, n u32 0xB000_0000|offset de cada registro. Cada registro: u32 0x9000_0013 e 19 valores
de 4 bytes (tag no nibble alto), seguidos de duas strings: a palavra e a leitura em kana. Os valores 1 e 2 (tag 6)
sao offsets absolutos dessas strings; o valor 3 e o tamanho da palavra em caracteres.

As palavras traduzidas ficam aqui, na ordem do arquivo. A leitura em kana fica igual: o jogo a usa para agrupar
as palavras na lista e no shiritori.
"""
import struct

from textfmt import to_bytes

NEKO = [
    "Gato", "Mangaká", "Professor", "Espião", "Sushiman", "Apostador", "Musa", "Modelo", "Piloto", "Perdedor",
    "Megera", "Otaku", "Paparazzo", "Bêbado", "Besouro", "Caracol", "Baleia", "Leão", "ET", "Pulga-d'água",
    "Barata", "Cupim", "Lagostim", "Sushi", "Atum", "Ouriço", "Ovas", "Sundae", "Natto", "Pudim",
    "Tataki", "Maionese", "Wasabi", "Cebola", "Casca", "Alho", "Gengibre", "Picles", "Mentaiko", "Mostarda",
    "Pimenta", "Gelatina", "Missô", "Chá gelado", "Suco", "Leite quente", "Refri", "Chá oolong", "Shoyu", "Molho",
    "Trem-bala", "Triciclo", "Roda-gigante", "Carrossel", "Viatura", "Ambulância", "Caminhão", "Limpa-fossa", "Carrinho", "Rosto",
    "Olho", "Pinta", "Rabo", "Clavícula", "Costas", "Tanquinho", "Cintura", "Umbigo", "Tornozelo", "Frieira",
    "Cólica", "Rinite", "Ressaca", "Dor de amor", "Olá", "Tchau", "Passeio", "Banho de sol", "Praia", "Soneca",
    "Agito", "Cartomancia", "Bocha", "Skate", "Karaokê", "Videogame", "Mahjong", "Romance", "Diário a dois", "Paixão",
    "Encontro", "Simpatia", "Promessa", "Almofadada", "Luta livre", "Estudo", "Esquecimento", "Beisebol", "Esforço", "Trabalho",
    "Noitada", "Briga", "Faxina", "Lavar WC", "Lavar roupa", "Acordar cedo", "Telefonema", "Declaração", "Amor", "Presente",
    "Amor secreto", "Massagem", "Cafuné", "Beijo", "Tapinhas", "Spa", "Fofoca", "Traição", "Ciúme", "Mandinga",
    "Peteleco", "Travessura", "Infantilizar", "Vacina", "Mercadinho", "Sushiaria", "Videokê", "Posto policial", "Biblioteca", "Bombeiros",
    "Delegacia", "Templo", "Parquinho", "Shinjuku", "Harajuku", "Asakusa", "Escola", "Hotel cápsula", "Torre Tóquio", "Festa Nebuta",
    "Havaí", "Anisong", "Enka", "Yodel", "Heavy metal", "Frigideira", "Toalha", "Travesseiro", "Fita adesiva", "Máscara",
    "Chinelo", "Vestido", "Vídeo", "Micro-ondas", "Escova", "Touca", "Batom", "Papelão", "Computador", "Despertador",
    "Prendedor", "Ábaco",
]
WORDS = {"NEKO.DIC": NEKO}


def records(d):
    n = struct.unpack_from("<I", d, 0)[0] & 0xFFFFFFF
    return [x & 0xFFFFFFF for x in struct.unpack_from(f"<{n}I", d, 4)]


def cstr(d, p):
    return d[p:d.index(b"\0", p)]


def rebuild(d, words, amap):
    """Troca a palavra de cada registro (None mantem a original). Remonta o arquivo com os novos offsets."""
    recs = records(d)
    assert len(recs) == len(words), (len(recs), len(words))
    out = bytearray(d[:4 + 4 * len(recs)])
    for i, (r, word) in enumerate(zip(recs, words)):
        head = struct.unpack_from("<I", d, r)[0]
        assert head == 0x90000013, hex(head)
        vals = list(struct.unpack_from("<19I", d, r + 4))
        old_word, reading = cstr(d, vals[1] & 0xFFFFFFF), cstr(d, vals[2] & 0xFFFFFFF)
        new_word = old_word if word is None else to_bytes(word, amap)
        start = len(out)
        struct.pack_into("<I", out, 4 + 4 * i, 0xB0000000 | start)
        if word is not None:
            vals[3] = (vals[3] & 0xF0000000) | len(word)
        vals[1] = 0x60000000 | (start + 80)
        vals[2] = 0x60000000 | (start + 80 + len(new_word) + 1)
        out += struct.pack("<20I", head, *vals) + new_word + b"\0" + reading + b"\0"
    return bytes(out)

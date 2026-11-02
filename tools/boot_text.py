"""Textos do BOOT.BIN: offset no arquivo -> portugues. Cada um precisa caber no espaco original."""
from textfmt import to_bytes

# Textos em Shift-JIS desenhados com a fonte do jogo (acentos pelo mapa da fonte).
SJIS = {
    0xD8194: "Fem", 0xD8198: "Mas", 0xD819C: "A", 0xD81A0: "B", 0xD81A8: "O",
    0xD8334: "Toro", 0xD833C: "Suzuki", 0xD8344: "Jun", 0xD834C: "Pierre", 0xD8358: "Ricky", 0xD8364: "Kuro",
    0xD8370: "Mas", 0xD8374: "Fem", 0xD8378: "A", 0xD8380: "B", 0xD8388: "AB", 0xD8390: "O",
    0xD8398: "Áries", 0xD83A4: "Touro", 0xD83B0: "Gêmeos", 0xD83BC: "Câncer", 0xD83C4: "Leão", 0xD83CC: "Virgem",
    0xD83D8: "Libra", 0xD83E4: "Escorpião", 0xD83F0: "Sagit.", 0xD83F8: "Capric.", 0xD8400: "Aquário", 0xD840C: "Peixes",
    0xD8B10: "Toro", 0xD8B18: "Suzuki", 0xD8B20: "Jun", 0xD8B28: "Pierre", 0xD8B34: "Ricky", 0xD8B54: "Aiko",
    0xD8BAC: "Para salvar são precisos 800 KB livres.",
    0xD8BE4: "                                O: OK",
    0xD8C28: '"Memory Stick" mal encaixado.',
    0xD8C64: '"Memory Stick" sem espaço livre.',
    0xD8EA4: "Salvando...",
    0xD9D70: "Detalhes", 0xD9D7C: "Cancelar", 0xD9D88: "Apagar amigo", 0xD9D98: "É esta pessoa?", 0xD9DA8: "Apagar mesmo?",
    0xD9DBC: "%2d", 0xD9DC4: "%2d", 0xD9DCC: "%4d/%2d/%2d", 0xD9DDC: "%2d/%2d",
    0xD9EF0: "Corrigir", 0xD9EFC: "Cancelar", 0xD9F08: "Apagar", 0xD9F20: "Apagar mesmo?",
    0xDA0D0: '"Memory Stick" sem espaço livre.',
    0xDA104: "Para salvar são precisos 800 KB livres.",
    0xDA13C: "                                O: OK",
    0xDA168: 'Achamos um save de "Doko Demo Issyo".',
    0xDA19C: "Substituir este save apaga o Pokepi atual, mas as palavras e os amigos passam para o novo.",
    0xDA218: "Deseja continuar?",
    0xDA230: "A hora do save difere da hora do PSP.",
    0xDA268: "Acerte o relógio do PSP.",
    0xDA2B4: "Está tudo certo?",
    0xDA30C: "%4d", 0xDA314: "%2d", 0xDA31C: "%2d",
    0xDA42C: "Carregando",
    0xDA56C: "Testando...\n",
    0xDA580: "Aplicar as opções?",
    0xDA638: "Oferecer", 0xDA644: "Cancelar", 0xDA650: "Presentear", 0xDA668: "Jogar fora",
    0xDA674: "Pôr no quarto", 0xDA684: "Guardar", 0xDA694: "Oferecer mesmo?", 0xDA6AC: "Jogar fora mesmo?",
    0xDA6D8: "%2d", 0xDA6E0: "%2d", 0xDBA68: "%2d/%2d",
    0xDBCB0: "Substituir?", 0xDBCCC: "Sem dados", 0xDBCD8: "%d/%d", 0xDBCE8: "%2d/%2d",
    0xDBF8C: "%d", 0xDC064: "%2d/%2d", 0xDC2A0: "Jogad.", 0xDC2A8: "%d", 0xDC2B0: "Rodada", 0xDC2B8: "%dx",
    0xDD9D0: "Conectando...\nAguarde um pouco.",
}

# Textos em UTF-8 mostrados pelas janelas do sistema do PSP.
UTF8 = {
    0xDD33C: "Doko Demo Issyo",
    0xDD358: "Toro (gato), Jun (coelho), Ricky (sapo), Pierre (cachorro) e Suzuki (robô): cinco Pokepis cheios de personalidade. Leve-os com você e converse em qualquer hora e lugar.",
    0xDDBA0: "A conexão com o anfitrião caiu.",
    0xDDBD8: "Não restou nenhum jogador.",
    0xDDC0C: "Anfitrião não encontrado.",
    0xDDC40: "Erro de comunicação.",
    0xDDC68: "A conexão com o outro jogador caiu.",
    0xDDC9C: "Outro jogador não encontrado.",
    0xDDCD0: "Conectando...\n\nAguarde um pouco.",
    0xDDD0C: "O interruptor de rede sem fio\nestá desligado. Para conectar,\nligue o interruptor.",
    0xDDDB0: "Falha na conexão.\nTentar de novo?",
}


def capacity(boot, off):
    end = boot.index(b"\0", off)
    while boot[end] == 0:
        end += 1
    return end - off - 1


def patch_boot(boot, amap):
    """Devolve o BOOT.BIN traduzido; falha se algum texto nao couber."""
    out = bytearray(boot)
    for table, enc in ((SJIS, lambda t: to_bytes(t, amap)), (UTF8, lambda t: t.encode("utf-8"))):
        for off, text in table.items():
            raw = enc(text)
            cap = capacity(boot, off)
            assert len(raw) <= cap, (hex(off), text, len(raw), cap)
            out[off:off + cap + 1] = raw + b"\0" * (cap + 1 - len(raw))
    return bytes(out)

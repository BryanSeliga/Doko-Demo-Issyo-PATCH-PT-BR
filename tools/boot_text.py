"""Textos do BOOT.BIN: offset no arquivo -> portugues. Cada um precisa caber no espaco original."""
import struct

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
    # Creditos finais: so os cargos; nomes de pessoas e lojas ficam como no original.
    0xDDE34: "Doko Demo Issyo: equipe", 0xDDE50: "Criação", 0xDDE68: "Game design",
    0xDDE90: "Design de personagens", 0xDDEB0: "Programação", 0xDDF2C: "Diálogos",
    0xDDF5C: "Programação script", 0xDDF80: "Gráficos", 0xDDFBC: "Animação", 0xDDFD8: "Design de fonte",
    0xDDFEC: "Diário", 0xDE000: "Assistente", 0xDE01C: "Gerente de projeto", 0xDE038: "Apoio às fotos",
    0xDE15C: "Música", 0xDE188: "Efeitos sonoros", 0xDE19C: "Sistema de som", 0xDE1C0: "& suporte",
    0xDE1EC: "Gestão de som", 0xDE210: "Coordenação da caixa", 0xDE260: "Design caixa e manual",
    0xDE284: "Manual", 0xDE2A0: "Gestão de QA", 0xDE2C0: "Equipe QA", 0xDE370: "Promoção",
    0xDE3A4: "Marketing", 0xDE3D8: "Agradecimentos", 0xDE46C: "Direção", 0xDE488: "Produção",
    0xDE4B0: "Produção executiva", 0xDE4E8: "Supervisão",
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


# Pagina do diario: o jogo copia o texto da pagina (em UTF-16, com as quebras que ele insere) para um espaco
# de 100 caracteres, sem limite; texto maior apaga os dados do diario e o PSP desliga. Antes da copia, um zero
# no byte 90 do texto (pagina com ate 90 caracteres + quebras inseridas, que tem no maximo 1 por 13 letras).
# Endereco virtual -> (instrucao original, nova). Nenhuma delas tem relocacao.
DIARY_TEXT_MAX = 90
NAME_MAX = 7

CODE = {
    # Diario, pagina comum: v0 = registro da pagina, texto em +0x170.
    0x39A24: (0x24420170, 0x24460170),  # addiu v0, v0, 0x170 -> addiu a2, v0, 0x170
    0x39A28: (0x00403021, 0xA4400170 + DIARY_TEXT_MAX),  # move a2, v0 -> sh zero, 0x170+90(v0)
    # Divisor das duas linhas de titulo (diario e memorias): a2 = texto. A copia de a2 em v0 so e
    # devolvida quando pedem 0 linhas, e os dois chamadores pedem 2.
    0x14D34: (0x00C01021, 0xA4C00000 + DIARY_TEXT_MAX),  # move v0, a2 -> sh zero, 90(a2)
    # Memorias: s0 = registro da pagina, texto em +0x1E8. "s2 = v1 ou 1" vira movn e libera uma instrucao.
    0x3E19C: (0x14600002, 0x24120001),  # bnez v1, +2 -> addiu s2, zero, 1
    0x3E1A0: (0x00609021, 0x0063900B),  # move s2, v1 -> movn s2, v1, v1
    0x3E1A4: (0x24120001, 0xA60001E8 + DIARY_TEXT_MAX),  # addiu s2, zero, 1 -> sh zero, 0x1E8+90(s0)
    # Teclado (aberto em 0x1FD80 com o tipo do campo: 0 palavras, 1 nome, 2 e 3 telefone). Nos tipos 1 a 3 o
    # byte +0x21 tira a conversao para kanji e prende o teclado na primeira pagina, entao os nomes so aceitavam
    # hiragana. A troca de pagina (cursor alem da borda) e o desenho das teclas passam a olhar +0x23, que so vale
    # no telefone: os nomes ganham a pagina ABC/abc e continuam sem conversao.
    0x2133C: (0x92220021, 0x92220023),  # lbu v0, 0x21(s1) -> 0x23(s1): pagina, cursor para a direita
    0x2144C: (0x92220021, 0x92220023),  # o mesmo para a esquerda
    0x218C0: (0x92020021, 0x92020023),  # lbu v0, 0x21(s0) -> 0x23(s0): faces das teclas da pagina
    0x1FF2C: (0x92250021, 0x92250023),  # setas laterais e tecla Num acesas (antes so no tipo 0)
    # Tecla Num: no modo restrito so era aceita no tipo 2 (+0x22); passa a ser recusada so no telefone
    0x21614: (0x92220022, 0x92220023),  # lbu v0, 0x22(s1) -> 0x23(s1)
    0x217FC: (0x1440FF87, 0x1040FF87),  # bnez v0 -> beqz v0 (aceita quando nao e telefone)
    # Pagina inicial (+0x44): 1 = ABC/abc nos tipos 0 e 1 (palavras e nomes), 0 = kana/numeros nos outros.
    # O "sw zero, 0x110" do delay slot sobra: o memset(+0x48, 0, 0xd4) logo depois ja zera +0x110.
    0x1FE20: (0xAE200044, 0x2E430002),  # sw zero, 0x44(s1) -> sltiu v1, s2, 2
    0x1FE2C: (0xAE200110, 0xAE230044),  # sw zero, 0x110(s1) -> sw v1, 0x44(s1)
    # Limite do nome em caracteres. O nome vai para blocos de 16 bytes: 7 cabem mesmo em kana (14 + NUL).
    0x200B4: (0x24020004, 0x24020000 + NAME_MAX),  # addiu v0, zero, 4 -> NAME_MAX
}
# o segmento de codigo comeca no byte 0x80 do arquivo, no endereco virtual 0
CODE_FILE_OFFSET = 0x80


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
    for va, (old, new) in CODE.items():
        off = va + CODE_FILE_OFFSET
        assert struct.unpack_from("<I", boot, off)[0] == old, hex(va)
        struct.pack_into("<I", out, off, new)
    return bytes(out)

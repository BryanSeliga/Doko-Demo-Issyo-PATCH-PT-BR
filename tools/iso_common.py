"""Leitura somente-leitura da ISO original e do indice do DATA.BP."""
import struct

SECTOR = 2048
DATA_BP_LBA = 7760
DATA_BP_SIZE = 406898688
BOOT_LBA = 704
BOOT_SIZE = 1341110
EBOOT_LBA = 32
EBOOT_SIZE = 1341456


class Iso:
    def __init__(self, path):
        self.f = open(path, "rb")

    def read(self, lba, size):
        self.f.seek(lba * SECTOR)
        return self.f.read(size)

    def bp(self, offset, size):
        self.f.seek(DATA_BP_LBA * SECTOR + offset)
        return self.f.read(size)


def parse_bp_table(data):
    """Tabela hash do BP: cabecalho (buckets, total, tam_nomes, tam_tabela), entradas
    (nome, offset, tamanho, proximo) e tabela de nomes. Offsets sao relativos ao DATA.BP."""
    buckets, total, names_size, table_size = struct.unpack_from("<4I", data, 0)
    names_at = 16 + total * 16
    out = []
    for i in range(total):
        name_off, off, size, nxt = struct.unpack_from("<4I", data, 16 + i * 16)
        if name_off == 0xFFFFFFFF:
            continue
        end = data.index(b"\0", names_at + name_off)
        out.append((data[names_at + name_off:end].decode("ascii"), off, size, i, nxt))
    return out, (buckets, total, names_size, table_size)


TOP_DATA = 0x6000


def bpm_files(iso):
    """Lista (nome_bpm, offset_absoluto_no_BP, tamanho)."""
    ents, _ = parse_bp_table(iso.bp(0, TOP_DATA))
    return sorted(((e[0], TOP_DATA + e[1], e[2]) for e in ents), key=lambda e: e[1])


def inner_files(iso, bpm_off):
    """Lista (nome, offset_absoluto_no_BP, tamanho) de um BPM."""
    head = iso.bp(bpm_off, 16)
    total, table_size = struct.unpack_from("<I", head, 4)[0], struct.unpack_from("<I", head, 12)[0]
    ents, _ = parse_bp_table(iso.bp(bpm_off, table_size))
    return sorted(((e[0], bpm_off + table_size + e[1], e[2]) for e in ents), key=lambda e: e[1])

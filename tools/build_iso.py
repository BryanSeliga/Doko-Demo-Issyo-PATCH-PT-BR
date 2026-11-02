"""Monta a ISO traduzida a partir da original, sem alterar a original.

DATA.BP e o ultimo arquivo do disco: BPMs modificados vao para o fim dele e so o indice muda.
A fonte muda de conteudo sem mudar de tamanho, entao e gravada no lugar.
O EBOOT.BIN criptografado e trocado pelo BOOT.BIN, que e o mesmo executavel sem criptografia.
"""
import shutil
import struct

from iso_common import (BOOT_LBA, BOOT_SIZE, DATA_BP_LBA, DATA_BP_SIZE, EBOOT_LBA, EBOOT_SIZE, SECTOR, TOP_DATA, Iso,
                        bpm_files, inner_files, parse_bp_table)


def find_dir_record(f, name_lba_size):
    """Procura em todo o sistema de arquivos o registro com (lba, tamanho) e devolve a posicao dele."""
    lba, size = name_lba_size
    needle = struct.pack("<I", lba) + struct.pack(">I", lba) + struct.pack("<I", size) + struct.pack(">I", size)
    f.seek(0)
    head = f.read(DATA_BP_LBA * SECTOR)
    pos = head.find(needle)
    assert pos > 0, (lba, size)
    return pos - 2


def set_record_size(f, rec, size):
    f.seek(rec + 10)
    f.write(struct.pack("<I", size) + struct.pack(">I", size))


def build(src, dst, ksc=None, font=None, boot=None):
    """ksc: {nome_bpm: {nome_arquivo: bytes}} com novos arquivos; font/boot: bytes de mesmo tamanho."""
    iso = Iso(src)
    shutil.copyfile(src, dst)
    bp_base = DATA_BP_LBA * SECTOR
    with open(dst, "r+b") as f:
        bpms = {n: (o, s) for n, o, s in bpm_files(iso)}
        top, _ = parse_bp_table(iso.bp(0, TOP_DATA))
        top_index = {e[0]: e[3] for e in top}
        end = DATA_BP_SIZE
        for bpm_name, files in (ksc or {}).items():
            off, size = bpms[bpm_name]
            head = iso.bp(off, 16)
            table_size = struct.unpack_from("<I", head, 12)[0]
            blob = bytearray(iso.bp(off, size))
            ents, _ = parse_bp_table(bytes(blob[:table_size]))
            by_name = {e[0]: e for e in ents}
            for name, data in files.items():
                e = by_name[name]
                blob += b"\0" * ((-len(blob)) % 16)
                struct.pack_into("<2I", blob, 16 + e[3] * 16 + 4, len(blob) - table_size, len(data))
                blob += data
            end += (-end) % SECTOR
            f.seek(bp_base + end)
            f.write(blob)
            i = top_index[bpm_name]
            f.seek(bp_base + 16 + i * 16 + 4)
            f.write(struct.pack("<2I", end - TOP_DATA, len(blob)))
            end += len(blob)
        if font is not None:
            data_off = bpms["DATA.BPM"][0]
            x = {n: (o, s) for n, o, s in inner_files(iso, data_off)}["FONT\\FONT.XFT"]
            assert len(font) == x[1]
            f.seek(bp_base + x[0])
            f.write(font)
        boot_bytes = boot if boot is not None else iso.read(BOOT_LBA, BOOT_SIZE)
        assert len(boot_bytes) == BOOT_SIZE
        f.seek(BOOT_LBA * SECTOR)
        f.write(boot_bytes)
        assert BOOT_SIZE <= EBOOT_SIZE
        rec = find_dir_record(f, (EBOOT_LBA, EBOOT_SIZE))
        f.seek(EBOOT_LBA * SECTOR)
        f.write(boot_bytes + b"\0" * (EBOOT_SIZE - BOOT_SIZE))
        set_record_size(f, rec, BOOT_SIZE)
        # tamanho do DATA.BP e do volume: so crescem se algum BPM foi para o fim do arquivo
        if end != DATA_BP_SIZE:
            rec = find_dir_record(f, (DATA_BP_LBA, DATA_BP_SIZE))
            set_record_size(f, rec, end)
        total = bp_base + end
        total += (-total) % SECTOR
        f.seek(0, 2)
        cur = f.tell()
        if total > cur:
            f.truncate(total)
            sectors = total // SECTOR
            f.seek(16 * SECTOR + 80)
            f.write(struct.pack("<I", sectors) + struct.pack(">I", sectors))
    return end

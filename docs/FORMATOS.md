# Formatos do Doko Demo Issyo (PSP, UCJS10002)

Notas de engenharia reversa usadas pelas ferramentas em `tools/`.

## ISO

- `PSP_GAME/SYSDIR/EBOOT.BIN` é criptografado; `BOOT.BIN` é o mesmo executável em ELF/PRX sem criptografia.
  O patch grava o `BOOT.BIN` traduzido no lugar do `EBOOT.BIN`.
- `PSP_GAME/USRDIR/data/DATA.BP` (LBA 7760) é o último arquivo do disco e guarda todo o conteúdo do jogo.

## DATA.BP e BPM

Os dois usam a mesma tabela hash:

| Campo | Tipo | Significado |
|---|---|---|
| buckets, total, tam_nomes, tam_tabela | 4 × u32 | cabeçalho |
| nome, offset, tamanho, próximo | 4 × u32 × `total` | `nome = 0xFFFFFFFF` indica bucket vazio |
| nomes | bytes | strings terminadas em NUL |

Offsets são relativos ao fim da tabela. Um arquivo novo pode ir para o fim do pacote: basta atualizar offset e tamanho.

## KSC (scripts de diálogo)

```
0x00 "KSC\0", versão, u32 entrada, u32 início_pool, u32 tam_pool, u16, u16, u16, u16
0x1C código | stub de entrada | pool de strings | tabela de valores marcados
```

VM de pilha com despacho em `0x6B9A4` no BOOT (tabela de opcodes em `0xE01B8`).
Endereços de código são relativos a `0x1C`. A lista de operandos fica em `tools/kscdis.py`.

| Opcode | Operandos | Função |
|---|---|---|
| `48` | string terminada em NUL | fala em balão |
| `8e` | string terminada em NUL | empilha string (perguntas) |
| `88` | u24 | empilha string do pool |
| `10 11 12 21` | u24 | saltos |
| `20 28` | u8, u24 | chamadas |
| `24 25` | u8 (só 24), chamada nativa | u16, u8, u16 se o u8 for diferente de 0 |
| `13` | cabeçalhos de `case` no meio do código | `switch`: u32 valor, u24 próximo cabeçalho; termina com tag 0 |
| `8a 15 18` | u24 | ponteiros de código |
| `f6 f7` | u8, u16 se o u8 for diferente de 0 | |

Dentro das strings, os bytes `14 15 17 18 19 1a 1b 1c` são seguidos de um u16 e inserem variáveis. O byte `16` delimita palavras variáveis.

Valores marcados têm o tipo nos 4 bits altos: `2` inteiro, `5` string, `7` código, `9` array, `b` referência.
Ao mudar o tamanho do código, só código e tag 7 precisam ser refeitos: strings são relativas ao pool, e as novas vão para o fim do arquivo.

## Fonte (FONT.XFT, em DATA.BPM)

- 8192 glifos 16×16, 4 bpp, em 32 texturas lineares de 256×256 (nibble baixo = pixel à esquerda).
- Tabela de largura por glifo em `0x3C`; bitmaps em `0x2040`; paleta de 16 cores em `0x102040`.
- ASCII usa 1 byte. Códigos de 2 bytes viram `glifo = linha × 96 + célula` (ver `0x4078` no BOOT).
- Bytes `0xA1–0xDF` isolados não funcionam: o decodificador sempre consome 2 bytes quando o bit alto está ligado.
- Os acentos usam códigos livres do Shift-JIS em `0x81AD–0x81D6`, definidos em `tools/fontpatch.py`.

## Balão de fala

Largura útil de cerca de 119 unidades da tabela de larguras, com 4 linhas visíveis. O texto rola sozinho e quebra por caractere, então as quebras antes de cada palavra precisam ser inseridas pela ferramenta.

O código `0x8540` não existe no Shift-JIS padrão: na fonte do jogo é um coração. As ferramentas o representam como `♥`.

Strings do pool também vão parar no balão: as guardadas em variável (op `84`) entram no meio das falas, e a opção escolhida no menu de opções (chamada `8b 21 NN`, com `NN` opções) é repetida pelo Pokepi. A caixa de opções aceita `\n` e mostra a opção em duas linhas. `kscbuild.pool_uses` classifica cada string, e `make_iso` quebra na largura do balão as que só aparecem nesses lugares.

## Placas do cenário

Os textos de placas, faixas e dirigíveis ficam na tabela de valores, em listas logo depois de um registro que termina em `2:0 2:6 2:20 2:3 2:5 2:N`. As placas mostram um ponto no lugar das letras acentuadas e só os 8 primeiros caracteres, então esses textos entram na ISO sem acento e na versão curta de `traducao/placas.jsonl` (até 8 caracteres; com `$_WORD`, no máximo 3 fixos).

## Vídeo do ícone (PSP_GAME/ICON1.PMF)

- PSMF: cabeçalho de `0x800` bytes (tamanho dos dados em `0x0C`, sem mapa de pontos de entrada) e MPEG-PS em pacotes de 2048 bytes.
- H.264 Main 2.1, 144×80, 300 quadros a 29,97, CABAC, sem quadros B, 1 referência, IDR a cada 30, AUD e SEI de tempo em todo quadro.
- Cada grupo de 30 quadros começa num pacote novo, com o cabeçalho de sistema e um pacote `0xBF` que lista o tamanho de cada quadro do grupo. O PES que começa um quadro leva PTS e DTS (PTS = DTS + 3003).
- `tools/icon1.py` refaz o vídeo com o ffmpeg do pacote `imageio-ffmpeg`: o logotipo vira o ICON0 traduzido e a legenda japonesa fica coberta, com o texto em português por cima.

## Diário

- Cada página é um registro na tabela de valores do KSC: `9:6`, `2:tipo`, `0`/`b:palavra1`, `5:palavra1`, `0`/`b:palavra2`, `5:palavra2`, `5:texto` (`tools/diary.py`).
- Quando a página é escrita, o texto vai para o save já com as variáveis trocadas (`$_W1`, `$_YOU`...), num registro de `0xDC` bytes (28 registros; texto a partir do byte 8). Trocar a tradução não muda páginas que já estão num save.
- Ao abrir a página, o jogo converte o texto para UTF-16 e quebra as linhas em 170 unidades (rotina em `0x14AD0`), num espaço de 100 caracteres sem limite: na tela Diário fica em `+0x38` da estrutura (global `0x896B8`), e logo depois vêm os dados da tela. Texto maior desliga o PSP.
- No leiaute com título, as duas primeiras linhas vão para um espaço de 40 caracteres (`+0x100`; rotina em `0x14D2C`).
- O texto só é desenhado se o byte de estado do registro (`+0x168`) não for 0.
- A página mostra 8 linhas. `boot_text.CODE` corta o texto em 90 bytes antes da cópia, nas telas Diário e Memórias, e as traduções ficam em até 88 bytes (`diary_batches.py conferir`).

## Itens

Nome e descrição de cada item ficam na tabela de valores do KSC, logo depois de um marcador de array `9:0xa`: o primeiro valor de tag 5 é o nome, e o segundo é a descrição. A tela de itens mostra o nome numa linha e a descrição em até duas linhas, de cerca de 222 unidades cada. `tools/items.py` lista o que não cabe.

## Vocabulário inicial (*.DIC, nos KS*.BPM)

- `u32 0x9000_0000 | n`, seguido de `n` valores `0xB000_0000 | offset` com a posição de cada registro.
- Cada registro tem `0x9000_0013` e 19 valores de 4 bytes, seguidos de duas strings terminadas em NUL: a palavra e a leitura em kana.
- Os valores 1 e 2 (tag 6) são os offsets absolutos dessas strings. O valor 3 é o tamanho da palavra em caracteres.
- A leitura em kana agrupa as palavras na lista e serve ao shiritori; o patch só troca a palavra (`tools/dic.py`).

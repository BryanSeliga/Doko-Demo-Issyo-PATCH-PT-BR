# Doko Demo Issho — Patch de tradução PT-BR (PSP)

Tradução de fã para português brasileiro de **Doko Demo Issho** (どこでもいっしょ) para PSP, o bichinho virtual falante do Toro.

> Este repositório tem **só o patch** e as ferramentas usadas para fazê-lo. Nenhum arquivo do jogo é distribuído aqui. Você precisa ter a sua própria cópia do jogo.

## O que está traduzido

- Menus, botões e telas (cadastro, opções, dados, diário, cartões, presentes e afins).
- Mensagens do sistema (salvar, carregar, erros, signos, tipos sanguíneos).
- **Todas as falas do Toro**, mais de 13 mil textos, e as palavras que ele já sabe.
- Nomes e descrições dos itens do Toro.
- Fonte com acentos do português (á à â ã é ê í ó ô õ ú ü ç).

Ainda em japonês: as falas dos outros quatro Pokepi (Pierre, Ricky, Suzuki e Jun), as letras do teclado na página de kana, o minijogo de shiritori (que depende da língua japonesa), os créditos e o logotipo. **Escolha o Toro** ao começar um jogo novo.

## O que você precisa

- A ISO japonesa do jogo: `Doko Demo Issho (Japan).iso`, código **UCJS-10002**.
  - SHA-1: `d5561bfb9362a47357aa070d8665ea22fdc83084`
- O arquivo do patch (`.xdelta`), na página de **Releases** deste repositório.
- Um programa que aplique patches xdelta, por exemplo:
  - [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher) (Windows, Linux, Mac)
  - [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (no navegador)
  - ou o aplicador em Python deste repositório (veja abaixo)

## Como aplicar

1. Confira se a sua ISO é a certa (SHA-1 acima). Uma ISO diferente não vai funcionar.
2. Abra o programa de patch, escolha a ISO original e o arquivo `.xdelta`.
3. Gere a ISO nova, por exemplo `Doko Demo Issho (PT-BR).iso`. A original não é alterada.

Com Python 3 instalado, também dá para aplicar pelo terminal:

```
python tools/vcdiff.py aplicar "Doko Demo Issho (Japan).iso" "Doko Demo Issho PT-BR.xdelta" "Doko Demo Issho (PT-BR).iso"
```

## Onde jogar

- **PPSSPP** (PC, Android, iOS): testado e funcionando.
- **PSP de verdade**: precisa de firmware customizado, porque o patch usa o executável sem criptografia. Ainda não foi testado em aparelho.

## Dicas

- Quando o Toro fala ", miau" no fim das frases, é o jeitinho dele (o original usa "nya").
- O teclado abre na página de letras japonesas. Para escrever com letras latinas (ABC, DEF…), vá com o direcional até a borda direita do teclado e aperte → mais uma vez.
- Se algo aparecer cortado ou estranho, abra uma *issue* com um print e, se puder, o que estava acontecendo no jogo.

## Para quem quer mexer

- `tools/`: ferramentas em Python para ler e remontar os arquivos do jogo (scripts KSC, pacotes BP/BPM, fonte XFT, imagens GIM) e gerar o patch.
- `traducao/`: os textos traduzidos, um JSON por linha (`{"id", "pt"}`). O texto japonês não fica no repositório; ele é extraído da sua ISO com `tools/extract_text.py`.
- `docs/FORMATOS.md`: como os formatos do jogo funcionam.
- `docs/GUIA_TRADUCAO.md`: guia de estilo da tradução.

Para montar a ISO traduzida a partir da sua cópia e gerar o patch:

```
cd tools
python make_iso.py "<iso original>" "<iso traduzida>" neko
python make_patch.py "<iso original>" "<iso traduzida>" "Doko Demo Issho PT-BR.xdelta"
```

`make_patch.py` confere o resultado aplicando o patch de volta.

## Aviso

Projeto de fã, sem fins lucrativos e sem ligação com a Sony. *Doko Demo Issho* e seus personagens pertencem aos seus donos. Compre o jogo original.

<p align="center"><img src="docs/img/logo.png" alt="Doko Demo Issyo — Tradução Brasileira" width="560"></p>

<p align="center">
  Tradução de fã de <b>Doko Demo Issyo</b> (どこでもいっしょ) para o português do Brasil, no PSP<br>
  <a href="../../releases/latest"><b>Baixar o patch mais recente</b></a>
</p>

<p align="center">
  <img src="docs/img/shot_title.png" width="400" alt="Tela título">
  <img src="docs/img/shot_toro.png" width="400" alt="Toro falando em português">
</p>

# Doko Demo Issyo — Tradução Brasileira (PSP)

Tradução de fã de **Doko Demo Issyo**, o jogo de bichinho virtual falante do Toro, para o português do Brasil (PT-BR).

> Este repositório tem **só o patch** e as ferramentas usadas para fazê-lo. Nenhum arquivo do jogo é distribuído aqui. Você precisa ter a sua própria cópia do jogo.

## O que está traduzido

- **Todas as falas dos cinco Pokepi** (Toro, Pierre, Jun, Suzuki e Ricky), mais de 52 mil textos, e as palavras que eles já sabem.
- Menus, botões e títulos das telas, redesenhados com uma fonte arredondada parecida com a original e com o destaque listrado dos menus no formato das palavras em português.
- Logotipo novo na tela título, e ícone, nome e descrição novos no menu do PSP.
- Mensagens do sistema (salvar, carregar, erros, signos, tipos sanguíneos).
- Nomes e descrições dos itens.
- Os cargos da equipe nos créditos finais.
- A fonte do jogo, ampliada com os acentos do português (á à â ã é ê í ó ô õ ú ü ç).

Continua em japonês: as letras da página kana do teclado (use a página latina para ensinar palavras), o minijogo shiritori (ele depende da língua japonesa), os nomes da equipe nos créditos e os subtítulos escritos à mão em letras latinas ao lado dos títulos das telas (como "Pokepi Sentaku"), que foram mantidos como no original.

## Imagens

<p align="center">
  <img src="docs/img/shot_select.png" width="400" alt="Escolha do Pokepi">
  <img src="docs/img/shot_profile.png" width="400" alt="Nome do Pokepi">
  <img src="docs/img/shot_toro2.png" width="400" alt="Fala do Toro">
  <img src="docs/img/shot_items.png" width="400" alt="Tela de itens">
</p>

<p align="center">
  <img src="docs/img/shot_menu.png" width="400" alt="Menu do quarto">
  <img src="docs/img/psp_menu.png" width="400" alt="Simulação do jogo no menu do PSP">
</p>
<p align="center"><sub>À direita: simulação do ícone e da descrição novos sobre o fundo do jogo no menu do PSP.</sub></p>

## O que você precisa

- A ISO japonesa do jogo: `Doko Demo Issho (Japan).iso`, código **UCJS-10002**.
  - SHA-1: `d5561bfb9362a47357aa070d8665ea22fdc83084`
- O arquivo do patch (`.xdelta`), na página **Releases** deste repositório.
- Um programa que aplique patches xdelta, por exemplo:
  - [Delta Patcher](https://github.com/marco-calautti/DeltaPatcher) (Windows, Linux, Mac)
  - [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) (no navegador)
  - ou o aplicador em Python deste repositório (veja abaixo)

## Como aplicar

1. Confira se a sua ISO é a certa (SHA-1 acima). Uma ISO diferente não funciona.
2. Abra o programa de patch e escolha a ISO original e o arquivo `.xdelta`.
3. Gere a ISO nova, por exemplo `Doko Demo Issyo (PT-BR).iso`. A original não é alterada.
4. Opcional: confira a ISO nova. O SHA-1 dela está nas notas de cada versão.

Desde a v1.3 o patch tem um checksum em cada bloco. Se o download vier corrompido ou a ISO original não for a certa, o Delta Patcher, o xdelta e o aplicador em Python param com erro em vez de gerar uma ISO quebrada.

Com o Python 3 instalado, dá para aplicar pela linha de comando:

```
python tools/vcdiff.py aplicar "Doko Demo Issho (Japan).iso" "Doko Demo Issyo PT-BR.xdelta" "Doko Demo Issyo (PT-BR).iso"
```

## Onde jogar

- **PPSSPP** (PC, Android, iOS): testado e funcionando.
- **PSP de verdade**: precisa de firmware customizado, porque o patch usa o executável sem criptografia. Em teste num PSP-3000; se tiver algum problema, avise.

## Dicas

- No quarto, o menu principal abre com o **direcional para a direita**.
- Os Pokepi terminam as frases com o seu tique, como no original: o Toro diz ", miau", o Pierre ", au", a Jun ", pyon", o Suzuki ", robô" e o Ricky ", croac" ou ", sô" (no original, "nya", "wan", "pyon", "robo", "kero" e "dasu").
- O teclado abre na página japonesa. Para digitar com letras latinas (ABC, DEF…), leve o cursor até a borda direita do teclado e aperte → mais uma vez.
- Se algo aparecer cortado ou estranho, abra uma *issue* com um print e, se puder, o que estava acontecendo no jogo.

## Para quem quiser contribuir

- `tools/`: ferramentas em Python para ler e remontar os arquivos do jogo (scripts KSC, pacotes BP/BPM, fonte XFT, imagens GIM) e para gerar o patch.
- `traducao/`: os textos traduzidos, um objeto JSON por linha (`{"id", "pt"}`). O texto japonês não fica no repositório: ele é extraído da sua própria ISO com `tools/extract_text.py`.
- `art/`: as imagens-fonte do logotipo da tela título, do ícone e da descrição do menu do PSP.
- `docs/FORMATOS.md`: como funcionam os formatos de arquivo do jogo.
- `docs/GUIA_TRADUCAO.md`: o guia de estilo da tradução.

Para montar a ISO traduzida a partir da sua cópia e gerar o patch:

```
cd tools
python make_iso.py "<iso original>" "<iso traduzida>"
python make_patch.py "<iso original>" "<iso traduzida>" "Doko Demo Issyo PT-BR.xdelta"
```

O `make_patch.py` confere o resultado aplicando o patch de volta.

## Créditos

- Tradução, ferramentas e arte: [BryanSeliga](https://github.com/BryanSeliga).

## Aviso

Projeto de fã, sem fins comerciais e sem ligação com a Sony ou a BeXide. *Doko Demo Issyo* e seus personagens pertencem aos seus donos. Compre o jogo original.

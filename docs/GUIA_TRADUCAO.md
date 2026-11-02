# Guia de tradução PT-BR

Traduza do japonês para **português brasileiro natural**, como se o jogo tivesse sido feito aqui. Não traduza palavra por palavra.

## O jogo

*Doko Demo Issho* é um bichinho virtual falante. Pokepi são bichinhos que sonham em virar humanos; quem joga ensina palavras, e eles usam essas palavras nas conversas.

Texto leve, fofo e engraçado, com público de todas as idades. Humor e carinho importam mais que a literalidade: adapte piadas e trocadilhos para funcionarem em português.

## Personagens e voz

| Japonês | PT-BR | Voz |
|---|---|---|
| トロ | Toro | Gatinho branco, personagem principal. Doce, curioso e ingênuo, um pouco criança. Fala informal e carinhosa. Quer muito virar humano. |
| ピエール | Pierre | Cachorro |
| リッキー | Ricky | Sapo |
| スズキ | Suzuki | Robô |
| ジュン | Jun | Coelho |
| クロ | Kuro | Gato preto de boina vermelha, amigo do Toro |
| ポケピ | Pokepi | |
| 人間 | humano / gente | |
| ことば / コトバ | palavra | |

Fale com quem joga usando **você**, sem gíria datada ou palavrão. Prefira frases curtas, com cara de fala. Mantenha os alongamentos e a alegria do original: "Sim~!", "Eba!", "Hmm...".

## Regras obrigatórias

**1. Variáveis são intocáveis.** Mantenha exatamente a mesma quantidade de cada marcador; pode mudar a ordem para a frase soar natural.

- `{W}{14:0001}{W}`: palavra inserida pelo jogo, muitas vezes ensinada por quem joga. Mantenha o trio inteiro.
- `{14:0000}`, `{14:000b}` e semelhantes: número ou texto inserido pelo jogo.
- `$_YOU`, `$_WORD`, `$_W1`, `$_OPP` e outros começados por `$_`: nome de quem joga, palavras e afins. Mantenha sem alteração.
- `{17:0017}`: **tique verbal do personagem**, por padrão ", miau". Coloque-o no final da frase, antes da pontuação, como em `Que legal{17:0017}!`. Isso aparece como "Que legal, miau!". Não escreva "miau" à mão quando houver esse marcador.

**2. As variáveis podem ser qualquer palavra.** Não se sabe o gênero nem o número. Não coloque artigo antes delas (`o {W}…`) nem concorde com elas. Reescreva a frase para ficar neutra: "Gosto de {W}…{W}", "Isso de {W}…{W} é legal".

**3. Quem joga pode ser menino ou menina.** Evite formas com gênero para essa pessoa. Em vez de "Você está cansado?", use "Você parece sem energia?". Em vez de "obrigado por vir", use "que bom que você veio".

**4. Mantenha a estrutura de cada texto.**

- Se o japonês termina com `\n`, o português também termina com `\n`. Se não termina, também não termina.
- Espaço no início ou no fim do japonês indica que o texto é um pedaço de frase que será colado a outro. Mantenha esse espaço.
- Quebras de linha **no meio** de `fala` e `pergunta` podem ser removidas, pois a ferramenta quebra as linhas sozinha. Em textos do tipo `pool` com várias linhas, como páginas de diário, mantenha as quebras e linhas com até 26 caracteres.
- Textos seguidos no arquivo costumam ser a mesma conversa, e um pensamento pode continuar no próximo. Leia os vizinhos antes de traduzir.
- Textos do tipo `pool` curtos são opções de resposta, palavras ou nomes de itens: traduza de forma enxuta.

**5. Só estes caracteres existem na fonte:** ASCII comum e `á à â ã é ê í ó ô õ ú ü ç` (e maiúsculas), mais `♪` e `♥`.

- Use `...` em vez de `…`, `!` em vez de `！`, `?` em vez de `？`, `~` em vez de `～`.
- Use aspas retas `"` em vez de `「」`. Nunca use barra invertida, travessão longo ou emoji.
- Não deixe nenhum japonês na tradução, exceto se for mesmo necessário manter um nome como 
  está. Nesse caso, escreva em letras latinas.

**6. Palavras japonesas.** Traduza ou adapte comidas e costumes quando houver equivalente natural (おフロ = banho). Mantenha nomes japoneses conhecidos em letras latinas (sushi, Tóquio). Quando o assunto é a própria língua ou a escrita japonesa, como leitura de kanji, adapte para falar de "como se escreve" ou "como se fala".

**7. Detalhes recorrentes.**

- Quando `ニャ` ou `にゃ` aparecer escrito no texto, sem ser o marcador, use ", miau" no fim da frase.
- `♪` e `♥` aparecem no jogo como coraçãozinhos: mantenha onde o japonês tiver esses símbolos.
- Mantenha honoríficos em letras latinas quando forem parte do nome (-san, -chan). Sem nome, adapte: 先生 = "Prof."
- Número variável pode ser 1 ou mais: use uma forma que sirva aos dois, como "palavra(s) nova(s)".
- `{14:0000}` dentro de datas e períodos pode ser estação do ano ou mês. Escreva de um jeito que sirva aos dois: "na época de {14:0000}".

## Exemplos

| Japonês | Português |
|---|---|
| `何を おしえて くれるの{17:0017}？\n` | `O que você vai me ensinar{17:0017}?\n` |
| `{W}{14:0003}{W}は {W}{14:0002}{W} なの{17:0017}～\n` | `{W}{14:0003}{W} é {W}{14:0002}{W}{17:0017}~\n` |
| `大きな おフロって イイよね～\n` | `Banho de banheira grandona é bom demais, né~?\n` |
| `だからね！\n` | `Então, é isso!\n` |
| `そうかな？` (pool) | `Será?` |

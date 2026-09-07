# Continuar daqui

Arquivo de retomada. Se a conversa com o assistente for reiniciada, **leia este
arquivo primeiro**: ele diz exatamente onde o trabalho parou, sem precisar
reconstruir o histórico.

Regra: atualizar este arquivo a cada notebook concluído, no mesmo commit.

---

## Objetivo desta etapa

Um exemplo **aprofundado** para cada uma das 9 bases do PySUS, além de
notebooks que **cruzam bases**. Os exemplos existentes (16, na pasta de cada
base) são a porta de entrada; estes novos são material de pesquisa.

Cada notebook aprofundado deve:

- responder a uma pergunta de pesquisa real, não demonstrar uma função;
- usar indicadores reconhecidos (ICSAP, mortalidade prematura por DCNT,
  mortalidade infantil evitável, adequação do pré-natal…), para que o
  resultado seja comparável com a literatura;
- rodar dentro da memória do Colab gratuito, usando SQL sobre os arquivos
  quando a base for grande;
- conferir o resultado contra uma fonte oficial, no próprio notebook.

## Situação

| # | Base | Notebook | Estado |
|---|------|----------|--------|
| 1 | IBGE | `IBGE/populacao-denominadores-e-piramides.ipynb` | **pronto** — 16 células, validado |
| 2 | SIM | `SIM/mortalidade-prematura-por-dcnt.ipynb` | **pronto** — 18 células, validado |
| 3 | SINASC | `SINASC/nascimentos-prematuridade-e-pre-natal.ipynb` | **pronto** — 21 células, validado |
| 4 | SIH | `SIH/internacoes-sensiveis-a-atencao-primaria.ipynb` | **pronto** — 19 células, validado |
| 5 | CNES | `CNES/rede-assistencial-e-leitos-por-habitante.ipynb` | **pronto** — 18 células, validado |
| 6 | SINAN | `SINAN/arboviroses-dengue-chikungunya-zika.ipynb` | **pronto** — 16 células, validado |
| 7 | PNI | `PNI/cobertura-vacinal-e-anos-incompletos.ipynb` | **pronto** — 12 células, validado |
| 8 | SIA | `SIA/alta-complexidade-oncologia-e-dialise.ipynb` | **pronto** — 14 células, validado |
| 9 | CIHA | `CIHA/o-que-o-ciha-acrescenta-ao-sih.ipynb` | **pronto** — 13 células, validado |
| 10 | cruzamento | `cruzamentos/mortalidade-infantil-e-numeros-pequenos.ipynb` | **pronto** — 15 células, validado |
| 11 | cruzamento | `cruzamentos/painel-do-municipio.ipynb` | **pronto** — 11 células, validado |

**Etapa concluída.** As nove bases do PySUS têm exemplo aprofundado, mais dois
cruzamentos. Próximos passos possíveis, se houver interesse:

- notebooks temáticos (saúde da mulher, oncologia, saúde mental, saúde indígena);
- aplicar ao aplicativo os aprendizados que ainda estão pendentes;
- mapas, que exigiriam malhas geográficas fora do PySUS.

## Última correção — 07/09/2026, `cruzamentos/frio-e-coracao-replicando-um-estudo.ipynb`

O notebook publicava **7.571.377 óbitos** onde o correto são **275.485** — 27,5
vezes mais. A célula da seção 3 lia *todos* os caminhos que `sim(uf, ANOS)`
devolve, e o `state=` da PySUS não filtra: a consulta em
`pysus/api/ducklake/models.py` é `state IN (...) OR state IS NULL`, e o arquivo
**nacional** de cada ano não tem estado no catálogo — então vem junto com o
estadual. Para nove anos, dezoito arquivos em vez de nove.

A prova de que era isso: a diferença entre publicado e correto era **idêntica
nos quatro estados** — 1.823.973 óbitos, a contribuição do arquivo nacional
somada a cada coluna.

| | publicado (errado) | correto | fator |
|---|---:|---:|---:|
| Total | 7.571.377 | 275.485 | 27,5 |
| RS | 1.945.873 | 121.900 | 16,0 |
| SC | 1.883.040 | 59.067 | 31,9 |
| CE | 1.902.757 | 78.784 | 24,2 |
| AM | 1.839.707 | 15.734 | 116,9 |
| Inverno/verão no RS | 1,161 | 1,355 | |
| Inverno/verão no AM | 1,147 | 1,021 | |

O **texto** do notebook já estava certo — "cerca de um terço mais" no RS e "2%"
no AM batem com os números corretos. Foram as **saídas** que foram regeradas
contaminadas. Corrigimos o código e reexecutamos; o texto ficou como estava.

O que mudou:

- a célula da seção 3 ganhou `arquivos_da_uf()`, a mesma defesa que
  `mortalidade-infantil-e-numeros-pequenos.ipynb` já tinha: escolhe o arquivo
  pelo nome (`DO` + UF + ano) e **levanta erro** se faltar o ano de algum
  estado. A seção 2 já fazia isso para o SIH (prefixo `RD`) — só esta ficou de
  fora, e foi por onde o Brasil entrou;
- o item 4 da verificação de sanidade passou a **conferir**, e não só imprimir.
  Ele recebeu 7.571.377 e não disse nada, porque a referência ("cerca de 400 mil
  óbitos circulatórios por ano no Brasil") não estava ligada a faixa nenhuma.
  Agora compara com os 540 mil esperados para 15% da população em nove anos e
  exige entre 35% e 75% — o correto dá 51%, o contaminado dava 1.402%.

Pendências que este commit **não** fecha:

- `VALIDACAO.md` e `_ferramentas/sentinelas.json` continuam sendo os da
  rodada de 01/09/2026. O `validar_todos.py` se recusa, de propósito, a
  reescrever os dois numa rodada com filtro, e a rodada completa dos 36
  notebooks não foi feita — este notebook passou pelo validador sozinho.
  Consequência esperada: a próxima rodada completa vai acusar deriva aqui
  (`1.16 contra 1.15` virou `1.35 contra 1.02`, e o item 4 ganhou linha).
  É a correção aparecendo, não defeito novo.
- o item 3 da mesma verificação ("sazonalidade maior no Sul que no Norte")
  aprovou 1,16 contra 1,15 durante a contaminação. Comparação sem margem
  nenhuma: continua frouxa, e vale apertar quando alguém voltar aqui.
- a seção 2 imprime "180 meses de internações publicados entre 2010 e 2024, de
  174 possíveis (103%)" e logo abaixo chama isso de lacuna. O catálogo do SIH
  encheu desde que o texto foi escrito; a narrativa da seção 2 e a tabela da
  seção "o que dá e o que não dá para replicar" envelheceram e precisam de uma
  revisão de texto.

## Aprendizados para o aplicativo

Ficam em `_ferramentas/APRENDIZADOS-KERNEL.md`, com o estado de cada um
(pendente / aplicado na versão X).

## Como retomar

1. Ler este arquivo e `_ferramentas/APRENDIZADOS-KERNEL.md`.
2. Ler `GUIA-DE-ESTILO.md`.
3. Pegar a primeira linha "a fazer" da tabela e continuar.


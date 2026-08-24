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

## Aprendizados para o aplicativo

Ficam em `_ferramentas/APRENDIZADOS-KERNEL.md`, com o estado de cada um
(pendente / aplicado na versão X).

## Como retomar

1. Ler este arquivo e `_ferramentas/APRENDIZADOS-KERNEL.md`.
2. Ler `GUIA-DE-ESTILO.md`.
3. Pegar a primeira linha "a fazer" da tabela e continuar.


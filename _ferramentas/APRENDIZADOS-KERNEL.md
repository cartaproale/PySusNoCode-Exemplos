# Aprendizados para o kernel do PySusNoCode

Cada linha aqui nasceu de um erro real ao construir os exemplos. O que vale
para o aplicativo vira lição embutida (`pysusnocode/lessons.py`), regra do
prompt (`pysusnocode/prompts.py`) ou correção no kernel (`pysusnocode/kernel.py`).

Estado: **pendente** = descoberto, ainda não aplicado; **v1.x.y** = já embarcado.

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 1 | `nest_asyncio.apply()` é obrigatório: sem ele o download trava dentro de qualquer notebook | prompt + lição | v1.7.2 |
| 2 | `group` é obrigatório no CNES, proibido no SIH/SIM/SINASC/SIA e precisa ser `None` no CIHA | lição | v1.8.0 |
| 3 | Período inexistente devolve tabela vazia **em silêncio** — sempre conferir `len()` | lição | v1.8.0 |
| 4 | Base nacional inteira estoura a memória (dengue de um ano ≈ 29 GB) | prompt + kernel | v1.8.0 |
| 5 | Morte do Python precisa ser detectada na hora, não no fim do tempo limite | kernel | v1.8.0 |
| 6 | `GROUP BY` no duckdb exige o nome original da coluna, não o apelido | lição | v1.8.0 |
| 7 | Tabelas do DATASUS têm dezenas a centenas de colunas: o pandas precisa de largura maior | kernel | v1.8.0 |

## Descobertas ao construir os exemplos aprofundados (agosto de 2026)

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 8 | `display.float_format` global arredondava tudo para 2 casas: `0,0886` virava `0,09`. A mesma célula mostrava números diferentes no aplicativo e no Colab — quebra a promessa do produto | kernel | pendente |
| 9 | As barras de progresso do PySUS (stderr com retorno de carro) viram uma parede de lixo quando salvas. Precisam ser colapsadas na exibição | kernel/interface | pendente |
| 10 | Os arquivos de população municipal de **2022 e 2023 vêm truncados na origem** (só PR e só RN). Taxas municipais desses anos saem erradas sem aviso | lição | pendente |
| 11 | O PySUS devolve o caminho de um **arquivo** `.parquet`, não de uma pasta: `read_parquet('arquivo.parquet')`, sem `/**/*.parquet` | lição | pendente |
| 12 | A idade no SIM é codificada (primeiro dígito = unidade). Tratar `IDADE` como número dá idades de 400 anos | lição | pendente |
| 13 | Comparar taxas brutas entre lugares de estruturas etárias diferentes inverte conclusões. Ao comparar regiões, o assistente deveria oferecer padronização por idade | prompt | pendente |
| 14 | Formatar milhar com `f"{n:,}".replace(",", ".")` **corrompe as vírgulas do texto em volta** dentro do mesmo f-string. Usar uma função que formata só o número | lição | pendente |
| 15 | Códigos do DATASUS (ESC2010, RACACOR, GESTACAO…) não podem ser adivinhados: os rótulos saíram deslocados e a tabela inteira ficou errada, sem nenhum erro de execução. Conferir a distribuição real antes de rotular | prompt | pendente |
| 16 | Cruzar escolaridade com idade da morte dá resultado invertido (quem não estudou "vive mais"), porque escolaridade carrega a geração. Ao estratificar por escolaridade, fixar a faixa etária e comparar composição, não taxa | prompt | pendente |


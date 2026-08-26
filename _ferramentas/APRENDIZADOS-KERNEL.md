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
| 8 | `display.float_format` global arredondava tudo para 2 casas: `0,0886` virava `0,09`. A mesma célula mostrava números diferentes no aplicativo e no Colab — quebra a promessa do produto | kernel | v1.8.1 |
| 9 | As barras de progresso do PySUS (stderr com retorno de carro) viram uma parede de lixo quando salvas. Precisam ser colapsadas na exibição | ferramenta do repositório | feito |
| 10 | Os arquivos de população municipal de **2022 e 2023 vêm truncados na origem** (só PR e só RN). Taxas municipais desses anos saem erradas sem aviso | lição + prompt | v1.8.1 |
| 11 | O PySUS devolve o caminho de um **arquivo** `.parquet`, não de uma pasta: `read_parquet('arquivo.parquet')`, sem `/**/*.parquet` | lição | v1.8.1 |
| 12 | A idade no SIM é codificada (primeiro dígito = unidade). Tratar `IDADE` como número dá idades de 400 anos | lição + prompt | v1.8.1 |
| 13 | Comparar taxas brutas entre lugares de estruturas etárias diferentes inverte conclusões. Ao comparar regiões, o assistente deveria oferecer padronização por idade | prompt | v1.8.1 |
| 14 | Formatar milhar com `f"{n:,}".replace(",", ".")` **corrompe as vírgulas do texto em volta** dentro do mesmo f-string. Usar uma função que formata só o número | lição | v1.8.1 |
| 15 | Códigos do DATASUS (ESC2010, RACACOR, GESTACAO…) não podem ser adivinhados: os rótulos saíram deslocados e a tabela inteira ficou errada, sem nenhum erro de execução. Conferir a distribuição real antes de rotular | lição | v1.8.1 |
| 16 | Cruzar escolaridade com idade da morte dá resultado invertido (quem não estudou "vive mais"), porque escolaridade carrega a geração. Ao estratificar por escolaridade, fixar a faixa etária e comparar composição, não taxa | lição | v1.8.1 |
| 17 | `sih(uf, ano, mes)` devolve **uma lista** e o primeiro arquivo costuma ser o SP (serviços profissionais, um registro por ato), não o RD (uma linha por internação). Escolher pelo nome do arquivo, nunca por `[0]` | lição | v1.8.1 |
| 18 | A cobertura do RD do SIH no espelho do PySUS é esburacada: no Paraná há 1 ou 2 meses por ano recente, contra 12 do SP. Conferir no catálogo antes de prometer uma análise anual | lição | v1.8.1 |
| 19 | O PNI no PySUS termina em 2019 (grupos CPNI e DPNI); pedir 2020 ou depois devolve lista vazia | lição | v1.8.1 |
| 20 | Ao afirmar que um resultado "confirma" algo, verificar se confirma mesmo. O índice de Kotelchuck não ordena pelo número de consultas, e eu quase publiquei uma confirmação que a tabela contrariava | prompt | pendente |
| 21 | A idade no SIH usa dois campos: `IDADE` e `COD_IDADE` (unidade). Um recém-nascido de 3 dias aparece como idade 3 | lição | v1.8.1 |
| 22 | O grupo PF do CNES tem uma linha por **vínculo**, não por pessoa: 351 mil vínculos para 226 mil profissionais no PR. Contar linhas infla "médicos por mil habitantes" em 3,6 vezes. Contar `DISTINCT CPF_PROF` | lição | v1.8.1 |
| 23 | `REGSAUDE` do CNES vem escrito de várias formas para a mesma região (`2ª`, `02`, `002`). Sem normalizar, 22 regiões viram 40 | lição | v1.8.1 |
| 24 | "Leito complementar" (`TP_LEITO=3`) não é sinônimo de UTI: inclui unidades intermediárias. Chamar de UTI infla o indicador | lição | v1.8.1 |
| 25 | Os arquivos do SINAN **não têm as mesmas colunas** entre agravos (`HOSPITALIZ` existe na dengue e na chikungunya, não no zika; zika tem 38 colunas contra 121 da dengue). Perguntar ao arquivo antes de montar a consulta | lição | v1.8.1 |
| 26 | As datas do SINAN vêm como **texto**: `strftime` e `date_diff` falham. Usar `TRY_CAST(col AS DATE)` | lição | v1.8.1 |
| 27 | O código de descarte do `CLASSI_FIN` **muda de agravo para agravo**: 8 na dengue, 5 na chikungunya, 2 no zika. Uma regra única conta descartados como casos e infla a chikungunya em 60%. O jeito de achar o código sem a tabela: é aquele em que ninguém morre | lição | v1.8.1 |
| 28 | Campos numéricos do SINAN têm strings vazias: `CAST` quebra a consulta inteira, `TRY_CAST` não | lição | v1.8.1 |
| 29 | Em base com competência mensal, **contar os meses antes de somar o ano**: o PNI de 2019 tem 4 meses e a cobertura despenca de 87% para 30% — um ano incompleto é idêntico a uma catástrofe de saúde pública | prompt | pendente |
| 30 | No SIA, a atenção básica aparece com valor aprovado **zero**: ela é paga por bloco de financiamento, não por procedimento. Concluir que a atenção primária é barata é erro de leitura | lição | pendente |
| 31 | O código do procedimento do SIGTAP é estruturado (2 dígitos = grupo, 4 = subgrupo). Dá para classificar milhões de linhas sem tabela auxiliar | lição | pendente |
| 32 | Campo pronto nem sempre é confiável: o `COBERT` do PNI vem fora de escala no nível municipal. Quando os ingredientes estão no arquivo (doses e população), recalcular | prompt | pendente |
| 33 | O catálogo do PySUS é **um único arquivo duckdb** (`~/pysus/ducklake/catalog.duckdb`) e não aceita dois processos ao mesmo tempo: "O arquivo já está sendo usado por outro processo". Duas janelas do aplicativo baixando ao mesmo tempo quebram uma delas | kernel | pendente |
| 34 | SIM e SINASC fecham em anos diferentes (no PR, SIM até 2024 e SINASC até 2022). Ao cruzar bases, usar a interseção dos anos — nunca o ano mais recente de uma delas | lição | v1.8.2 |
## Revisão "estado da arte" da PySUS 2.10 (26 de agosto de 2026)

A biblioteca saltou de **20 para 99 nomes públicos** entre a 2.9 e a 2.10 — uma
mudança grande que passou despercebida. Tudo abaixo foi **testado**, não lido:
a documentação promete mais do que a biblioteca entrega, e é exatamente esse o
risco de aproveitar exemplo de terceiro sem verificar.

**Funciona e é útil**

| Função | O que faz |
|---|---|
| `info()` / `info_table()` | Lista os 34 conjuntos de dados, com origem e descrição |
| `load_column_metadata(base)` | Nome e descrição das colunas de 6 bases |
| `missing_values(df)`, `column_stats(df)` | Perfil de completude e tipos |
| `set_cache()`, `cache_status()`, `clear_cache()` | Gestão do cache |

**Anunciado, mas vazio** — `info()` lista 34 bases, mas só as **9 de origem
FTP** têm arquivos. As 19 de origem "Saude" (`ATENCAOPRIMARIA`, `SISVAN`,
`ARBOVIROSES`, `SISAGUA`, `VACINACAO`…) devolvem **zero arquivos**; as 6 de
"DadosGov" exigem autenticação. Inclusive `atencao_primaria()`, que parecia
resolver a pendência do [[esus-aps-sisab-viabilidade]] — não resolve.

**Funciona mas engana** — o mais importante desta revisão:

| # | Achado | Estado |
|---|---|---|
| 36 | `quality_score()` dá **nota 100 de 100** a um arquivo do SIH cheio de campos em branco, porque mede nulos e o DATASUS grava vazio como string vazia | v1.8.8 |
| 37 | `validate_data()` aprova a coluna `IDADE` do SIH pela regra "0 a 120", sem saber que ela depende de `COD_IDADE` para significar alguma coisa | v1.8.8 |
| 38 | `to_english()` traduz **parte** dos nomes e devolve tabela metade em português, metade em inglês (`IDADE` vira `age`, mas `COD_IDADE` fica — justamente a armadilha) | v1.8.8 |
| 39 | `disable_progress_bars()` existe, promete o que queríamos e **não tem efeito** (testado na 2.10.3): as barras continuam em stderr | v1.8.8 |
| 40 | `load_column_metadata()` documenta nomes, mas quase não traz tabelas de código: **0 das 14 dificuldades** que tivemos ao construir os exemplos teriam sido resolvidas por ele | v1.8.8 |
| 41 | A máquina de desenvolvimento ficou na 2.9 enquanto instalações novas já vinham com a 2.10 — daí o piso `pysus>=2.10` no requirements | v1.8.8 |

**Conclusão da revisão:** as 41 lições que construímos testando continuam sendo
o ativo. A biblioteca ganhou ferramentas de conveniência, não conhecimento
sobre o DATASUS.

## Teste sistemático da origem "Saude" e da atenção primária (26/08/2026)

A revisão anterior concluiu que as 19 bases de origem "Saude" **estavam
vazias**. Estava errada — e o erro foi meu, não da fonte. `get_files()` devolve
zero porque essas bases **não são arquivos de FTP**: são o portal
`dadosabertos.saude.gov.br` (Next.js sobre CKAN) mais a API REST DEMAS
(`apidadosabertos.saude.gov.br`). Os dados existem, estão atualizados e são
baixáveis. O que não funciona são as funções de conveniência da biblioteca.

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 42 | Base de origem "Saude" com **0 arquivos não quer dizer sem dados**. Antes de declarar uma fonte vazia, verificar por qual caminho ela é servida | prompt + lição | pendente |
| 43 | `atencao_primaria()` devolve vazio por erro de chave: o mapa interno tem `ATENCAOPRIMARIA`, a função procura `ATENCAO_PRIMARIA`, não acha, e cai no slug `atencao_primaria` — que o portal não reconhece. Atinge as **11 funções de nome composto** (`assistencia_saude`, `saude_indigena`, `vigilancia_meio_ambiente`…). O parâmetro `group=` existe mas é ignorado: não há como contornar pela API pública | lição | pendente |
| 44 | `sisvan()` aponta para o grupo **errado** (`saude-indigena`); o SISVAN está em `atencao-primaria`. Pior que vazio: devolveria outra base sem avisar | lição | pendente |
| 45 | Mesmo com o slug certo não baixaria nada: a função só aceita recurso cuja URL termina em `.csv`, e no portal quase tudo é `.csv.zip` | lição | pendente |
| 46 | O caminho que funciona é `SaudeClient` (`list_groups` → `list_datasets` → `fetch_dataset`) ou a URL do S3 direto. Medido: **189 recursos CSV em 26 datasets**, 89 deles de atenção primária | prompt + lição | pendente |
| 47 | Os indicadores MGDI têm **esquema único de 25 colunas** — uma receita serve para todos. As somas fecham: `_mun` bate exatamente com `_rs`, `_ms`, `_uf`, `_reg` e `_br` (verificado em 4 arquivos) | lição | pendente |
| 48 | `vl_indicador_calculado_al` é a **Amazônia Legal** — 773 municípios, exatamente as 9 UFs. Preenchido só nas linhas desses municípios, zero nas demais. O nome não diz isso em lugar nenhum. Confirmado em 3 de 4 arquivos; no 4º a própria fonte diverge 0,23% | lição | pendente |
| 49 | A periodicidade **varia por indicador**: eMulti é série mensal (28 competências), saúde bucal é dezembro de cada ano mais a competência corrente (11). `co_anomes` no formato AAAAMM não garante série mensal — conferir os meses presentes antes de plotar | lição | pendente |
| 50 | `aggregate_by_age_group()` aceita **qualquer** coluna numérica como se fosse idade. Passei o código da UF e ela devolveu "faixas etárias" 0-5, 5-15, 15-30, sem um aviso | lição | pendente |
| 51 | `detect_units()` classificou **todas** as colunas numéricas como `'kg'` (confiança 0,5), inclusive o código da UF e uma contagem de equipes | lição | pendente |
| 52 | `aggregate_by_period()` com a coluna de data em texto devolve **0 linhas e nenhum erro** | lição | pendente |
| 53 | `to_geojson()` num DataFrame sem coordenadas grava um `FeatureCollection` **vazio** e devolve sucesso | lição | pendente |
| 54 | `to_sql()` não grava banco nenhum: devolve o **texto** do `CREATE TABLE` | lição | pendente |
| 55 | `search_columns()` só tem conteúdo para `sinan` (120 colunas para "idade"); `sih`, `sim` e `sinasc` devolvem 0. `get_aliases()` devolve `[]` para SIH/IDADE, SIM/IDADE e SINASC/IDADEMAE | lição | pendente |
| 56 | O que funciona de verdade e vale ensinar: `query_parquet` + `to_df`/`to_arrow`/`stream_parquet` (175 mil linhas em 0,1 s, com projeção de colunas), `mask_data`/`unmask_data` (Fernet, reversível com a chave), `column_stats`, `profile_report`, `diff_dfs`, `link_datasets`, `to_csv`/`to_excel`/`export`, e `list_files` para as bases de FTP | prompt + lição | pendente |
| 57 | **Previne Brasil / SISAB está acessível** por REST com filtros de `uf`, `competencia`, `quadrimestre` e `codigo_municipio` — e o helper `pysus.api.saude.rest.iter_rows` funciona (1.188 linhas do AC em 1,0 s) | lição | pendente |
| 58 | O `offset` da API DEMAS é **linha**, não página, apesar de a própria documentação dizer "Número da página". Verificado: `offset=10` com `limit=10` não repete nada do `offset=0` | lição | pendente |
| 59 | A API DEMAS **cai**: ficou fora do ar por mais de uma hora durante este teste (timeout e 502) enquanto o portal e o S3 continuavam de pé. Notebook que dependa só dela quebra sem culpa do usuário — o S3 é o caminho estável | prompt + lição | pendente |
| 60 | Os códigos de indicador do Previne Brasil (10, 20, 30, 40, 50, 70) **não são documentados** no swagger, e a coluna `percentual` passa de 100 em alguns — não é numerador/denominador. Vale a lição 15: não adivinhar rótulo de código | lição | pendente |

**Conclusão do teste:** a atenção primária é a maior lacuna da nossa base de
exemplos e ela **é viável** — mas por fora das funções de conveniência da
pysus, que estão quebradas justamente aí.

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 35 | **O outro lado do `nest_asyncio`**: dentro de notebook ele é obrigatório, mas num script `.py` comum é desnecessário **e impede o Python de encerrar** — o processo termina o trabalho, imprime tudo e fica parado para sempre. Medido: com `nest_asyncio` o script trava; sem ele, encerra em 3,9 s. Não afeta o aplicativo (o `shutdown()` mata o kernel à força — verificado), mas afeta scripts gerados para rodar sozinhos | lição | pendente |








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

## A regressão do `state=` (26/08/2026) — a mais grave até hoje

Descoberta por acaso, ao cruzar o Previne Brasil com o SINASC: os quatro
estados devolveram **o mesmo total de nascimentos**. O `state=` não filtra
nada — e três exemplos **já publicados** passaram a mostrar o Brasil inteiro
com o rótulo do Paraná.

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 61 | **`state=` não filtra o resultado.** Ele diz onde procurar; desde 2026 o catálogo publica um arquivo **nacional** ao lado do arquivo de cada estado, e a PySUS devolve os dois. Medido: SINASC PR/2022 passou de 140.637 para **2.702.559 linhas (19×)**, com o próprio PR contado duas vezes. Atingiu `perfil-dos-nascimentos`, `causas-de-obito` e `mortalidade-infantil` | prompt + lição | pendente |
| 62 | `drop_duplicates()` **não** conserta: as linhas do arquivo nacional e do estadual não são idênticas, e as 281.274 continuam 281.274 | lição | pendente |
| 63 | Procurar a sigla da UF no nome do arquivo é armadilha: **`DO23OPEN` contém "PE"**. Quem filtrar por substring mantém o arquivo nacional achando que é de Pernambuco | lição | pendente |
| 64 | O catálogo sabe distinguir: em `list_files()` o arquivo nacional vem com `state` **vazio** e caminho `.../BR/...`; o do estado vem com a sigla. É por aí que se escolhe | lição | pendente |
| 65 | Nem todo ano tem arquivo estadual: **SINASC 2023 só tem o nacional**. Nesse caso é preciso filtrar as linhas pelo código do IBGE — e dizer ao usuário que filtrou | lição | pendente |
| 66 | `sih(state=...)` sem `group` escolhe **tabelas diferentes conforme o estado**: AC → `RJ` (AIH *rejeitada*), SP → `SP` (serviços profissionais), RR → `SP`. Contar "internações" no arquivo errado dá outro número e outro significado | lição | pendente |
| 67 | `pni(state=..., year=2023)` devolve **0 arquivos**, e `ciha(state="RR")` também. Zero arquivo não é erro: é resultado vazio em silêncio | lição | pendente |
| 68 | **A validação precisa conferir ordem de grandeza, não só execução.** Os três notebooks quebrados continuaram rodando e imprimindo sem um único erro — só que o número virou outro. Executar sem exceção não é prova de que está certo | ferramenta do repositório | pendente |
| 69 | `validar_todos.py` executa mas **não regrava as saídas**. Foi por isso que a regressão ficou invisível: o GitHub continuava exibindo os números certos da validação antiga ao lado de um código que já devolvia outra coisa. Criado o `reexecutar.py` para fechar essa brecha | ferramenta do repositório | feito |

## O que a 2.10.4 (lançada em 26/08/2026) muda — testado em ambiente limpo

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 70 | **`pip install pysus==2.10.4` num ambiente limpo não importa**: `ModuleNotFoundError: No module named 'yaml'`. O PyYAML continua sem ser declarado, o mesmo defeito que pegamos ao montar o instalador offline da 1.8.3. Nosso `requirements.txt` já contorna com `pyyaml>=6.0` | requirements | v1.8.3 |
| 71 | A 2.10.4 **não corrige** a regressão do `state=`: `sinasc("PR", 2022)` continua devolvendo `SINASC_2022` + `DNPR2022`, e `atencao_primaria()` continua vazia (a chave `ATENCAO_PRIMARIA` segue ausente do mapa) | lição | pendente |
| 72 | Na 2.10.4 `sisvan()` passou a devolver **2 arquivos** — mas ainda do grupo `saude-indigena`. Piorou: antes vinha vazio, agora vem dado errado com cara de certo | lição | pendente |
| 73 | **O espelho do SIH é muito incompleto.** Para PR/2024 o catálogo tem 12 arquivos: **RD só em agosto**, `RJ` em dezembro e `SP` nos outros dez meses. Nosso exemplo de internações só está certo porque calhou de pegar agosto. Trocar o mês devolve outra tabela, com outro significado | lição + prompt | pendente |
| 74 | Não dá para escolher a tabela: `sih(..., group="RD")` devolve **lista vazia**, e a coluna `group` do `list_files()` vem `None` mesmo para `RDPR2408`. O jeito é ler o prefixo do nome do arquivo | lição | pendente |
| 75 | Cinco versões em três dias (2.10.0 a 2.10.4). Para trabalho reprodutível o piso `pysus>=2.10` é arriscado: o certo é **fixar a versão** | requirements | pendente |

## Construindo o exemplo do Previne Brasil (26/08/2026)

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 76 | **A paginação por `offset` da API DEMAS é instável.** Ela pagina por deslocamento de linha sobre um resultado sem ordenação garantida: entre uma página e a próxima as linhas se movem. Três coletas seguidas do PR devolveram 21.546 linhas cada, mas **14.071, 16.137 e 12.829 registros distintos** — união de 20.800. Cada passada perde de 22% a 38% e preenche o buraco repetindo outras linhas. **O total sempre bate; o conteúdo, nunca** | prompt + lição | pendente |
| 77 | A saída é **não paginar**: particionar o pedido até caber numa resposta só. Por `codigo_municipio`, cada pedido traz ~54 linhas, e o estado inteiro sai estável em 14 s com 8 pedidos em paralelo — 21.546 registros únicos, idênticos entre execuções | lição | pendente |
| 78 | Correção de um erro meu: a "cobertura irregular" que eu tinha anotado (município que não reportaria certos indicadores) **era artefato da paginação**. A base é completa e retangular: 399 municípios × 3 competências × 6 indicadores × 3 visões | — | corrigido |
| 79 | No Previne Brasil, **`percentual` não é o resultado do indicador**: é cobertura de cadastro (identificados ÷ estimados do IBGE), por isso passa de 100 em metade das linhas. O resultado é `percentual_quadrimestre` (numerador ÷ denominador utilizado). Ambas conferidas em 100% das linhas | lição | pendente |
| 80 | Quando um código não tem tabela em lugar nenhum, dá para identificá-lo **pela evidência**: os três indicadores de gestante compartilham denominador idêntico em 100% dos municípios, o que os isola sem precisar adivinhar. É a lição 15 aplicada de forma construtiva | prompt + lição | pendente |
| 81 | Nos indicadores MGDI, **zero não quer dizer ausência do serviço**: cada arquivo mede uma modalidade. Dos 502 municípios com zero equipes de Saúde Bucal 40h, **147 (29%) têm equipe na modalidade de carga horária diferenciada**, contada em outro arquivo | prompt + lição | pendente |
| 82 | **Nem todo indicador é somável.** Equipes, polos e centros pertencem a um município só e a soma bate com o total nacional. Já "pessoas atendidas pela Farmácia Popular" **não fecha** (12.008.228 somando municípios contra 11.942.618 declarados): a mesma pessoa pode ser atendida em mais de um município. Antes de somar, olhe a unidade de medida | prompt + lição | pendente |
| 83 | Os indicadores MGDI têm **calendários diferentes** entre si: dos seis usados no painel, só existe **uma competência em comum**. Pegar "o mais recente de cada um" compara retratos de meses diferentes | lição | pendente |
| 84 | O código do município tem **7 dígitos no IBGE** e **6 no MGDI**. E o arquivo de população envelhece: Boa Esperança do Norte (MT) existe no indicador e não existe no denominador | lição | pendente |
| 85 | As barras de progresso da PySUS saem pelos **dois** canais — o FTP manda por stderr, o download do IBGE por stdout. O filtro do repositório só limpava stderr | ferramenta do repositório | feito |
| 86 | No cadastro de UBS, `LATITUDE`/`LONGITUDE` vêm como **texto com vírgula e ponto misturados no mesmo arquivo**. Sem `str.replace(",", ".")` viram `NaN` e o mapa sai vazio sem erro. 4% das 47.910 unidades não têm coordenada nenhuma | lição | pendente |
| 87 | **O retângulo "do Brasil" reprova dados bons**: as três UBS de Fernando de Noronha (IBGE 260545) ficam a leste de −34° de longitude. Qualquer conferência geográfica precisa incluir o arquipélago | lição | pendente |
| 88 | A coluna `UF` do cadastro de UBS guarda o **código numérico do IBGE** (41 = PR), não a sigla. Filtrar por `"PR"` devolve zero linha sem erro | lição | pendente |
| 89 | `to_geojson()` é útil quando as colunas existem (2.291 pontos do PR, com propriedades) — mas quando não existem grava **coleção vazia e devolve sucesso**. Confira sempre o número de pontos depois de exportar | lição | pendente |
| 90 | **83 municípios não têm nenhuma UBS cadastrada, e 67 deles (81%) têm equipe de saúde bucal custeada.** Ausência no arquivo não é ausência de rede — o maior deles, Araruama (RJ), tem 137 mil habitantes | prompt + lição | pendente |
| 91 | Quando a mesma base tem API paginada e arquivo publicado, **prefira o arquivo**: vem inteiro, de uma vez, igual para todos. A regra vale para UBS e para tudo que o portal publica em `.csv.zip` | prompt + lição | pendente |

## Varredura sistemática da 2.10.4 (27/08/2026)

A 2.10.4 é a última publicada e nada entrou no `main` depois dela. Comparei as
duas versões nome a nome, assinatura a assinatura.

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 92 | **A 2.10.4 não muda nada de observável para nós.** Superfície pública idêntica à 2.10.3: 99 nomes, 95 módulos, zero assinaturas alteradas, `_SAUDE_GROUP_MAP` inalterado. A única mudança de código são +866 caracteres no arquivo de bancos do FTP. Não há razão para mover o pino `pysus==2.10.3` | requirements | verificado |
| 93 | O que a 2.10.4 acrescentou foram cinco **rótulos** de grupo do SIA (`AB`, `AC`, `AT`, `PS`, `SA`) — mas os arquivos **já eram alcançáveis na 2.10.3**: `sia(state="PR", year=2024, month=1, group="AT")` devolve o mesmo `ATDPR2401.parquet` nas duas versões, e a coluna `group` do `list_files()` continua `None` nas duas | lição | pendente |
| 94 | **Os rótulos novos do SIA não descrevem o conteúdo.** Testado pelo procedimento principal (`AP_PRIPAL`), com o grupo `AM` como controle (100% medicamentos especializados, como o rótulo promete): `AT` ("Atenção") é **100% subgrupo 0305, nefrologia/diálise**; `AC` ("Alta Complexidade") é um único procedimento cirúrgico (0418010030); `AB` ("Atenção Básica") é 100% subgrupo 0301 **com a coluna `AB_PROCAIH` preenchida em todas as linhas**, apontando para uma cirurgia do aparelho digestivo | prompt + lição | pendente |
| 95 | **`group="AB"` não é atenção básica.** No Paraná, janeiro de 2024: `AB` tem **615 linhas** e a produção ambulatorial de verdade (`PA`) tem **3.246.596** — 0,02%. Quem procurar atenção primária no SIA pelo rótulo vai concluir que ela é minúscula. A produção da atenção primária está em `PA` e `BI` | prompt + lição | pendente |
| 96 | **Achado aproveitável: o grupo `AT` (arquivos `ATD`) é a APAC de diálise, com dado individual e exames.** No PR, jan/2024: 6.813 APACs, 6.669 pacientes distintos, 42 estabelecimentos, 413 municípios de residência, R$ 20,9 milhões no mês, série mensal completa de 2015 a 2024. Traz identificador do paciente (`AP_CNSPCN`), acesso vascular, situação quanto a transplante, sorologias e exames laboratoriais (`ATD_HB`, `ATD_ALBUMI`, `ATD_FOSFOR`, `ATD_PTH`, `ATD_KTVSEM`) | exemplo novo | proposto |
| 97 | Nos campos do `ATD`, os **categóricos vêm 100% preenchidos** (acesso vascular, transplante, HIV, HCV) mas os **laboratoriais variam muito por estado**: no PR de 42% a 71%, no AC de 12% a 13%. Não dá para tirar conclusão nacional desses exames sem antes medir o preenchimento em cada UF | lição | pendente |
| 98 | No `ATD`, `AP_CIDPRI` (diagnóstico principal) vem **vazio em 100% das linhas** nos dois estados testados. Um campo existir na tabela não significa que ele tenha conteúdo | lição | pendente |
| 99 | Ainda no `ATD`: **45% dos pacientes do PR se tratam fora do município onde moram** (26% no AC). Como a diálise é três vezes por semana, isso é deslocamento recorrente — uma pergunta de acesso que a base responde sozinha, cruzando `AP_MUNPCN` com `AP_UFMUN` | exemplo novo | proposto |

| # | Aprendizado | Onde entra | Estado |
|---|-------------|-----------|--------|
| 35 | **O outro lado do `nest_asyncio`**: dentro de notebook ele é obrigatório, mas num script `.py` comum é desnecessário **e impede o Python de encerrar** — o processo termina o trabalho, imprime tudo e fica parado para sempre. Medido: com `nest_asyncio` o script trava; sem ele, encerra em 3,9 s. Não afeta o aplicativo (o `shutdown()` mata o kernel à força — verificado), mas afeta scripts gerados para rodar sozinhos | lição | pendente |








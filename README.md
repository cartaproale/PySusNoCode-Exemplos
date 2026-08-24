# PySusNoCode · Exemplos

Notebooks prontos para analisar dados públicos de saúde do **DATASUS**, feitos
para profissionais de saúde que **não programam**. Abra no Google Colab, mude o
estado e o ano, execute.

> ⚠️ **Este não é o repositório da biblioteca PySUS.** A biblioteca é mantida
> pelo AlertaDengue/Fiocruz e fica em
> [AlertaDengue/PySUS](https://github.com/AlertaDengue/PySUS), com documentação
> em [pysus.readthedocs.io](https://pysus.readthedocs.io/pt/latest/).
> Aqui ficam apenas exemplos de uso.

---

## Como as três peças se encaixam

| Projeto | O que faz | De quem é |
|---|---|---|
| [AlertaDengue/PySUS](https://github.com/AlertaDengue/PySUS) | A **biblioteca** que acessa os dados do DATASUS | AlertaDengue / Fiocruz |
| [PySusNoCode](https://github.com/cartaproale/PySusNoCode) | O **aplicativo** que escreve e testa os notebooks conversando em português | Kraemer Academy |
| **Este repositório** | Os **exemplos** prontos, todos validados | Kraemer Academy |

---

## Comece por aqui

| Notebook | O que você aprende |
|---|---|
| [`_comece-aqui/01-primeiros-passos.ipynb`](_comece-aqui/01-primeiros-passos.ipynb) | Instalar, baixar o primeiro conjunto de dados e fazer uma primeira conta |
| [`_comece-aqui/02-descobrir-dados-disponiveis.ipynb`](_comece-aqui/02-descobrir-dados-disponiveis.ipynb) | Descobrir que bases, estados e períodos existem antes de baixar |
| [`_comece-aqui/03-mapa-completo-das-bases.ipynb`](_comece-aqui/03-mapa-completo-das-bases.ipynb) | **Referência:** tudo o que a biblioteca oferece, base por base e grupo por grupo |

## Uma análise para cada base

Todas as nove bases da biblioteca estão cobertas:

| Notebook | Pergunta que responde | Base |
|---|---|---|
| [`SINAN/dengue-por-estado-e-mes.ipynb`](SINAN/dengue-por-estado-e-mes.ipynb) | Como a dengue se distribuiu entre estados e meses? | SINAN |
| [`SINAN/serie-historica-tuberculose.ipynb`](SINAN/serie-historica-tuberculose.ipynb) | Como as notificações evoluíram ao longo dos anos? | SINAN |
| [`SIM/causas-de-obito.ipynb`](SIM/causas-de-obito.ipynb) | Quais as principais causas de óbito no estado? | SIM |
| [`SINASC/perfil-dos-nascimentos.ipynb`](SINASC/perfil-dos-nascimentos.ipynb) | Cesáreas, peso ao nascer e pré-natal | SINASC |
| [`SIH/internacoes-por-causa.ipynb`](SIH/internacoes-por-causa.ipynb) | Por que se interna pelo SUS, por quanto tempo e a que custo? | SIH |
| [`SIA/producao-ambulatorial.ipynb`](SIA/producao-ambulatorial.ipynb) | Quais procedimentos ambulatoriais o SUS mais realiza? | SIA |
| [`CNES/leitos-por-municipio.ipynb`](CNES/leitos-por-municipio.ipynb) | Quais municípios têm mais leitos e quantos são do SUS? | CNES |
| [`CNES/profissionais-de-saude.ipynb`](CNES/profissionais-de-saude.ipynb) | Quantos profissionais, de quais ocupações e onde? | CNES |
| [`PNI/cobertura-vacinal.ipynb`](PNI/cobertura-vacinal.ipynb) | Quantas doses foram aplicadas e qual a cobertura? | PNI |
| [`CIHA/atendimentos-ciha.ipynb`](CIHA/atendimentos-ciha.ipynb) | O que acontece nos atendimentos além do SUS? | CIHA |

## Indicadores que combinam bases

| Notebook | Pergunta que responde | Bases |
|---|---|---|
| [`indicadores/mortalidade-infantil.ipynb`](indicadores/mortalidade-infantil.ipynb) | Quantas crianças morrem antes de 1 ano, e do quê? | SIM + SINASC |
| [`indicadores/populacao-e-taxas.ipynb`](indicadores/populacao-e-taxas.ipynb) | Como comparar estados de tamanhos diferentes (taxas por 100 mil)? | IBGE + SINAN |

## Para quem já se sentir à vontade

| Notebook | O que ensina |
|---|---|
| [`avancado/arquivos-grandes-e-sql.ipynb`](avancado/arquivos-grandes-e-sql.ipynb) | Analisar milhões de linhas sem travar: colunas selecionadas e consultas SQL |

Todos trazem uma célula de **parâmetros** no início: mude a sigla do estado e o
ano, e a análise inteira se ajusta.

---

## Análises aprofundadas

Os exemplos acima são a porta de entrada. Estes respondem a **perguntas de
pesquisa**, com indicadores reconhecidos internacionalmente, e servem de
material de trabalho — não de demonstração.

| Notebook | A pergunta que responde | Base |
|---|---|---|
| [`IBGE/populacao-denominadores-e-piramides.ipynb`](IBGE/populacao-denominadores-e-piramides.ipynb) | Como obter um denominador confiável e comparar lugares sem enganação (padronização por idade) | IBGE |
| [`SIM/mortalidade-prematura-por-dcnt.ipynb`](SIM/mortalidade-prematura-por-dcnt.ipynb) | Qual a probabilidade de morrer entre 30 e 70 anos por doença crônica — a meta 3.4 da ONU | SIM |
| [`SINASC/nascimentos-prematuridade-e-pre-natal.ipynb`](SINASC/nascimentos-prematuridade-e-pre-natal.ipynb) | Prematuridade, adequação do pré-natal e cesáreas pela classificação de Robson | SINASC |
| [`SIH/internacoes-sensiveis-a-atencao-primaria.ipynb`](SIH/internacoes-sensiveis-a-atencao-primaria.ipynb) | Quantas internações a atenção primária poderia ter evitado, e quanto custam | SIH |
| [`CNES/rede-assistencial-e-leitos-por-habitante.ipynb`](CNES/rede-assistencial-e-leitos-por-habitante.ipynb) | Leitos e médicos por habitante, por município e por região de saúde | CNES |
| [`SINAN/arboviroses-dengue-chikungunya-zika.ipynb`](SINAN/arboviroses-dengue-chikungunya-zika.ipynb) | Como as três arboviroses diferem em sazonalidade, idade e gravidade | SINAN |
| [`PNI/cobertura-vacinal-e-anos-incompletos.ipynb`](PNI/cobertura-vacinal-e-anos-incompletos.ipynb) | Quanto da queda de cobertura vacinal é real e quanto é arquivo incompleto | PNI |
| [`SIA/alta-complexidade-oncologia-e-dialise.ipynb`](SIA/alta-complexidade-oncologia-e-dialise.ipynb) | Para onde vai o dinheiro do ambulatório, e quanto se anda para se tratar | SIA |
| [`CIHA/o-que-o-ciha-acrescenta-ao-sih.ipynb`](CIHA/o-que-o-ciha-acrescenta-ao-sih.ipynb) | O que existe além do SUS — e por que essa base exige cautela | CIHA + SIH |
| [`cruzamentos/mortalidade-infantil-e-numeros-pequenos.ipynb`](cruzamentos/mortalidade-infantil-e-numeros-pequenos.ipynb) | Quando a criança morre, e por que taxas municipais anuais quase sempre são ruído | SIM + SINASC |
| [`cruzamentos/painel-do-municipio.ipynb`](cruzamentos/painel-do-municipio.ipynb) | Como está a saúde da minha cidade, comparada com o estado | Seis bases |

Cada um deles termina com uma seção **"o que vale levar"**: as funções
reaproveitáveis e as armadilhas que o notebook resolveu no caminho.

---

## Como usar no Google Colab

1. Clique no notebook desejado aqui no GitHub;
2. Copie o endereço da página;
3. Abra [colab.research.google.com](https://colab.research.google.com), escolha
   **GitHub** e cole o endereço — ou baixe o arquivo `.ipynb` e use **Upload**;
4. Execute as células na ordem (`Shift + Enter`).

Não é preciso instalar nada no seu computador.

---

## Compromisso deste repositório

**Nenhum notebook é publicado sem ter sido executado do início ao fim, com
dados reais do DATASUS.** A validação é feita por
[`_ferramentas/validar_todos.py`](_ferramentas/validar_todos.py), que roda cada
célula e falha se qualquer uma der erro. O resultado fica registrado em
[`VALIDACAO.md`](VALIDACAO.md), com a data.

Além disso, uma [rotina automática](.github/workflows/validar.yml) reexecuta
todos os notebooks **todo mês**. Se a biblioteca mudar e algum exemplo parar de
funcionar, abre-se uma issue automaticamente — antes que alguém trave na
primeira célula.

Os resultados também são conferidos contra a realidade, não apenas contra a
ausência de erro. Cada notebook aprofundado termina com uma seção de
**verificações de sanidade**, e os números batem com as fontes oficiais:

- mortalidade infantil de 10,3 por mil no Paraná em 2022;
- 6.022.283 casos prováveis e 6.337 óbitos por dengue no Brasil em 2024, na
  maior epidemia da série histórica;
- 2,77 médicos por mil habitantes no Paraná, contra os 2,8 que o Conselho
  Federal de Medicina apura;
- população do Brasil de 212.583.750 em 2024, idêntica pelas duas fontes do
  IBGE.

Quando um resultado **não** confirmou o que estava escrito, o texto foi
corrigido — não o resultado. Está registrado nos commits.

Isso existe porque o contrário é fácil de acontecer: a biblioteca muda, os
exemplos param de funcionar e ninguém percebe até um usuário travar na primeira
célula.

---

## Armadilhas que estes notebooks já resolvem

Foram descobertas testando, e nenhuma delas está documentada de forma óbvia:

1. **`nest_asyncio` é obrigatório.** As funções da PySUS falham dentro de
   qualquer notebook sem ele (`asyncio.run() cannot be called from a running
   event loop`). Todos os exemplos começam aplicando-o.
2. **O parâmetro `group` se comporta de três formas diferentes:**
   - **CNES:** essencial — sem ele vêm 33 mil linhas e 362 colunas misturadas;
   - **SIH, SIM, SINASC, SIA:** usá-lo devolve **zero linhas**, sem erro;
   - **CIHA:** o valor padrão (`"CIHA"`) devolve zero — é preciso passar
     `group=None` explicitamente.
3. **Período inexistente devolve tabela vazia, não erro.** A cobertura do
   catálogo é irregular por base, estado e mês: no Paraná, por exemplo, só um
   mês de 2024 tem internações publicadas. Por isso todo notebook consulta
   `list_files` antes e confere `len(tabela)` depois — e o de internações
   **descobre sozinho** um mês com dados.
4. **Bases nacionais são enormes.** A dengue de 2024 tem 6,5 milhões de linhas
   (~29 GB carregada inteira) e um mês do SIA tem 3,6 milhões. Os notebooks
   dessas bases leem apenas as colunas necessárias — e o
   [notebook avançado](avancado/arquivos-grandes-e-sql.ipynb) mostra como
   consultar com SQL sem carregar nada.
5. **Arquivos que vêm incompletos, sem avisar.** A população municipal do IBGE
   de 2022 traz **só o Paraná** e a de 2023 **só o Rio Grande do Norte**; o PNI
   de 2019 tem quatro dos doze meses. Em cada caso, a conta roda normalmente e
   entrega um resultado errado. Os notebooks conferem antes de dividir.
6. **O mesmo campo muda de significado entre agravos.** No SINAN, o código de
   "descartado" é 8 na dengue, 5 na chikungunya e 2 no zika. Usar um só nas três
   infla a chikungunya em mais de 60%.
7. **`sih()` devolve vários arquivos, e o primeiro é o errado.** O grupo SP tem
   uma linha por ato médico; o RD, uma por internação. Quem pega o primeiro da
   lista acha que tem um milhão de internações quando tem um milhão de
   procedimentos.
8. **Contar linhas não é contar pessoas.** O cadastro de profissionais do CNES
   tem uma linha por vínculo: no Paraná, 351 mil vínculos para 226 mil pessoas.
   O indicador "médicos por mil habitantes" sai 3,6 vezes maior se ninguém
   perceber.

A lista completa, com o que cada descoberta gerou no aplicativo, está em
[`_ferramentas/APRENDIZADOS-KERNEL.md`](_ferramentas/APRENDIZADOS-KERNEL.md).

---

## Sobre os dados

Os dados vêm do **DATASUS / Ministério da Saúde**, são públicos e não
identificam pessoas. São dados administrativos, sujeitos a revisão pelas
secretarias de saúde: o mesmo período consultado em datas diferentes pode
apresentar números um pouco distintos.

Este projeto é independente e não possui vínculo com o Ministério da Saúde.

## Licença

Código sob licença MIT. A biblioteca PySUS, usada como dependência, é
licenciada sob GPL-3.0 pelo AlertaDengue — este repositório não incorpora nem
modifica o código dela.

---

*Um produto [Kraemer Academy](https://kraemeracademy.net).*

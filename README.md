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
ausência de erro: a taxa de mortalidade infantil calculada aqui (10,3 por mil
no Paraná em 2022) coincide com a estatística oficial, e a série de tuberculose
mostra a queda de 2020 pela subnotificação da pandemia.

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

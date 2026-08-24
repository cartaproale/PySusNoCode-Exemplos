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

## Análises prontas

| Notebook | Pergunta que responde | Base |
|---|---|---|
| [`CNES/leitos-por-municipio.ipynb`](CNES/leitos-por-municipio.ipynb) | Quais municípios têm mais leitos e quantos são do SUS? | CNES |
| [`SINAN/dengue-por-estado-e-mes.ipynb`](SINAN/dengue-por-estado-e-mes.ipynb) | Como a dengue se distribuiu entre estados e meses? | SINAN |
| [`SIM/causas-de-obito.ipynb`](SIM/causas-de-obito.ipynb) | Quais as principais causas de óbito no estado? | SIM |
| [`SINASC/perfil-dos-nascimentos.ipynb`](SINASC/perfil-dos-nascimentos.ipynb) | Cesáreas, peso ao nascer e pré-natal | SINASC |

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

Isso existe porque o contrário é fácil de acontecer: a biblioteca muda, os
exemplos param de funcionar e ninguém percebe até um usuário travar na primeira
célula.

---

## Três armadilhas que estes notebooks já resolvem

Foram descobertas testando, e valem para qualquer análise sua:

1. **`nest_asyncio` é obrigatório.** As funções da PySUS falham dentro de
   qualquer notebook sem ele (`asyncio.run() cannot be called from a running
   event loop`). Todos os exemplos começam aplicando-o.
2. **O parâmetro `group` só vale para o CNES.** No SIH, SIM, SINASC e SIA, usá-lo
   faz a consulta devolver **zero linhas** — sem erro nenhum. No CNES, ao
   contrário, ele é essencial: sem `group`, vêm 33 mil linhas e 362 colunas.
3. **Período inexistente devolve tabela vazia, não erro.** A cobertura do
   catálogo é irregular por base, estado e mês. Por isso todo notebook consulta
   `list_files` antes e confere `len(tabela)` depois.

E uma quarta, específica do SINAN: a base de dengue de 2024 tem **6,5 milhões de
linhas** e ocupa cerca de **29 GB** se carregada inteira — o suficiente para
travar o Colab. O notebook de dengue mostra como fazer a mesma análise com
1 GB, lendo apenas as colunas necessárias.

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

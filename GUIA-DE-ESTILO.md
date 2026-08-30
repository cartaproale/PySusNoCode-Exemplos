# Guia de estilo dos notebooks

Regras para manter todos os exemplos consistentes e confiáveis. Quem contribuir
com um notebook novo deve segui-las.

## As duas regras que não se negociam

**1. Nenhum notebook entra sem passar por `_ferramentas/validar_todos.py`**, que
o executa do início ao fim com dados reais. Não vale "deve funcionar".

**2. Todo notebook termina com uma verificação de sanidade** — uma célula que
confere se o resultado faz sentido e diz em voz alta quando não faz: ordem de
grandeza contra uma referência externa, soma das partes contra o total, `len()`
maior que zero, UF única quando se pediu uma UF.

O motivo é a versão da PySUS estar fixa (`pysus==2.10.6`). O pino garante que o
notebook publicado roda com a biblioteca contra a qual foi validado — mas não
protege contra o catálogo do servidor mudar, que está fora do nosso controle. A
verificação de sanidade é o que transforma essa mudança em **aviso na tela** em
vez de número errado com cara de certo.

Por que isso importa aqui: uma mudança de catálogo já fez três exemplos
devolverem o Brasil inteiro rotulado como Paraná, sem erro nenhum. Falhar alto
é incômodo; acertar o formato e errar o número vira decisão errada.

## Notebooks-alternativa

Alguns problemas têm dois caminhos que valem a pena manter vivos ao mesmo
tempo — hoje é o caso de "arquivos grandes", que existe com **duckdb direto** e
com as **ferramentas da PySUS**. Não é redundância por descuido: é seguro contra
o imponderável. A camada de conveniência da PySUS mudou seis vezes em cinco dias
em agosto de 2026; o duckdb pode um dia não estar disponível num ambiente. Ter
os dois testados significa que, se um cair, o outro já está pronto.

Quando criar um par assim:

- **Diga qual é o recomendado**, no cabeçalho dos dois e no README. Um par sem
  hierarquia deixa o leitor escolhendo no escuro.
- **Explique por que o outro existe** — a razão é redundância, e dizer isso
  evita que alguém "limpe" o repositório apagando o que parece duplicado.
- **Os dois calculam o mesmo número**, e a verificação de sanidade de cada um
  confere contra o outro caminho quando for possível.
- **Os dois são validados** como qualquer outro notebook. Um plano B que não
  roda não é plano B.

## Estrutura de cada notebook

1. **Título e cabeçalho** — a pergunta que o notebook responde, a fonte dos
   dados e o tempo estimado.
2. **Preparação** — sempre estas duas células:
   ```python
   %pip install pysus==2.10.6 nest_asyncio -q
   ```
   ```python
   import nest_asyncio
   nest_asyncio.apply()
   ```
3. **Parâmetros** — uma célula isolada com `UF`, `ANO`, `MES`… tudo o que o
   leitor pode querer trocar, com comentário explicando.
4. **Conferência do catálogo** — `list_files(...)` antes de baixar.
5. **Download** — com recorte pequeno por padrão.
6. **Verificação** — `len(tabela)` e, quando for usar colunas específicas,
   conferir `tabela.columns`.
7. **Análise e gráfico.**
8. **"Como adaptar"** — o que mudar para outro estado, período ou recorte.
9. **Rodapé** com os créditos.

## Escrita

- Português do Brasil, dirigido a quem **não programa**.
- Explique o *porquê* antes do código, não depois.
- Nada de jargão sem explicação: "DataFrame" vira "tabela".
- Comentários no código apenas quando esclarecem uma decisão.

## Código

- Converta antes de contar: `pd.to_numeric(col, errors="coerce")`.
- Nunca use `asyncio.run()` — o `nest_asyncio` já resolve.
- **`group` em CNES, SIA e SIH; nunca em SIM e SINASC.** Medido em 30/08/2026:
  `sia(..., group="PA")` devolve só `PAPR2401` (sem ele vêm dez arquivos, uma
  família diferente cada) e `sih(..., group="RD")` devolve só `RDPR2401` (sem
  ele vêm quatro, e o de serviços profissionais tem 14x mais linhas que o de
  internações). Já `sinasc(..., group="DN")` devolve `SINASC_2022`, que é o
  arquivo **nacional**, e `sim(..., group="DO")` devolve `DO22OPEN`, também
  nacional — ali o `group` não filtra o estado, entrega o Brasil com cara de
  acerto. Em SIM e SINASC escolha o arquivo pelo **nome** (`DO`/`DN` + UF), e
  prefira um ano que tenha arquivo estadual: 2025 e 2026 só têm o nacional.
- SINAN: `as_dataframe=False` + `pd.read_parquet(caminho, columns=[...])`.
- Gráficos com matplotlib, títulos e eixos em português, `plt.tight_layout()`.

## Nomes de arquivo

Minúsculas, sem acentos, palavras separadas por hífen:
`leitos-por-municipio.ipynb`. **Nada de espaços ou caracteres invisíveis** —
um arquivo com espaço de largura zero no nome não abre no Colab.

## Saídas

Os notebooks são publicados **com as saídas salvas**, para que possam ser lidos
no GitHub sem executar. As saídas vêm da validação, então refletem dados reais.

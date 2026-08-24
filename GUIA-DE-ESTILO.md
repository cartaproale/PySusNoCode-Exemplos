# Guia de estilo dos notebooks

Regras para manter todos os exemplos consistentes e confiáveis. Quem contribuir
com um notebook novo deve segui-las.

## A regra que não se negocia

**Nenhum notebook entra sem passar por `_ferramentas/validar_todos.py`**, que o
executa do início ao fim com dados reais. Não vale "deve funcionar".

## Estrutura de cada notebook

1. **Título e cabeçalho** — a pergunta que o notebook responde, a fonte dos
   dados e o tempo estimado.
2. **Preparação** — sempre estas duas células:
   ```python
   %pip install pysus nest_asyncio -q
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
- CNES **com** `group`; SIH, SIM, SINASC e SIA **sem** `group`.
- SINAN: `as_dataframe=False` + `pd.read_parquet(caminho, columns=[...])`.
- Gráficos com matplotlib, títulos e eixos em português, `plt.tight_layout()`.

## Nomes de arquivo

Minúsculas, sem acentos, palavras separadas por hífen:
`leitos-por-municipio.ipynb`. **Nada de espaços ou caracteres invisíveis** —
um arquivo com espaço de largura zero no nome não abre no Colab.

## Saídas

Os notebooks são publicados **com as saídas salvas**, para que possam ser lidos
no GitHub sem executar. As saídas vêm da validação, então refletem dados reais.

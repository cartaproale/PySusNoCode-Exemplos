"""Monta o exemplo 'Arquivos grandes pelas ferramentas da PySUS'.

Companheiro de `avancado/arquivos-grandes-e-sql.ipynb`, que faz o mesmo
trabalho com duckdb direto. Os dois existem de proposito: se um caminho parar
de funcionar, o outro continua. O de duckdb segue sendo o recomendado.
"""
from pathlib import Path

from montar_notebook import code, construir, md

DESTINO = Path(__file__).resolve().parents[1] / "avancado" / \
    "arquivos-grandes-pelas-ferramentas-da-pysus.ipynb"

CELULAS = [
    md("""
# Arquivos grandes pelas ferramentas da PySUS

**A pergunta:** dá para consultar um arquivo de milhões de linhas sem carregá-lo
na memória, usando só o que a própria PySUS oferece?

**Fonte:** SIA/SUS (produção ambulatorial), pela biblioteca PySUS.

**Tempo estimado:** 2 a 5 minutos.

> ### Leia isto antes
>
> Este notebook é o **caminho alternativo**. O recomendado é
> `avancado/arquivos-grandes-e-sql.ipynb`, que resolve o mesmo problema com
> **duckdb direto**.
>
> Por que o duckdb é o recomendado: ele é uma ferramenta estável e de uso
> geral, e o que você aprender lá serve fora da PySUS. Já a camada de
> conveniência da PySUS muda rápido — foram **seis versões em cinco dias** em
> agosto de 2026, e várias funções auxiliares dessa camada devolvem resultado
> vazio ou errado sem avisar.
>
> Por que este notebook existe mesmo assim: **redundância**. Se um dia o
> duckdb não estiver disponível no seu ambiente, ou se a PySUS ganhar algo que
> o duckdb não faz, aqui está o mesmo trabalho pelo outro caminho, testado.
"""),

    code("%pip install pysus==2.10.6 nest_asyncio -q"),

    code("""
import nest_asyncio
nest_asyncio.apply()

import time
import pandas as pd
import pysus

print("PySUS", pysus.__version__)
"""),

    code("""
# ---- O que você pode trocar -------------------------------------------
UF = "AC"      # estado pequeno para o exemplo rodar rápido
ANO = 2025
MES = 1
"""),

    md("""
## O problema, em números

Um mês do SIA de um estado grande tem milhões de linhas. Carregar tudo com
`pd.read_parquet()` consome dezenas de vezes o tamanho do arquivo em disco —
e é assim que o Python é encerrado no meio da análise.
"""),

    code("""
from pysus import sia

caminhos = sia(UF, ANO, MES, group="PA")
caminho = str(caminhos[0]).replace("\\\\", "/")

import os
tamanho_mb = os.path.getsize(caminho) / 1024**2
print(f"Arquivo: {os.path.basename(caminho)}")
print(f"Tamanho em disco: {tamanho_mb:.1f} MB")
"""),

    md("""
## Técnica 1 — `query_parquet`: agregar sem carregar

`pysus.query_parquet(caminho, sql)` entrega uma consulta pronta sobre o arquivo,
e `pysus.to_df()` materializa **apenas o resultado**. O arquivo inteiro nunca
entra na memória.

A tabela se chama `data` dentro da consulta.
"""),

    code("""
inicio = time.time()

consulta = pysus.query_parquet(caminho, '''
    SELECT
      substr(PA_PROC_ID, 1, 4) AS subgrupo,
      count(*)                                   AS registros,
      sum(TRY_CAST(PA_QTDAPR AS BIGINT))         AS quantidade_aprovada
    FROM data
    GROUP BY 1
    ORDER BY quantidade_aprovada DESC
    LIMIT 10
''')
top = pysus.to_df(consulta)

tempo_consulta = time.time() - inicio
memoria_kb = top.memory_usage(deep=True).sum() / 1024
print(f"{tempo_consulta:.2f}s | resultado ocupa {memoria_kb:.1f} KB")
top
"""),

    md("""
Repare nas duas colunas: **registros** e **quantidade aprovada** são números
diferentes, e a diferença não é pequena. No SIA, uma linha pode representar
várias realizações do mesmo procedimento — contar linhas subestima a produção.
É a razão de a consulta somar `PA_QTDAPR` em vez de só contar.
"""),

    md("""
## Técnica 2 — `stream_parquet`: percorrer em pedaços

Quando você precisa das **linhas**, e não de um resumo, `stream_parquet` entrega
o arquivo em blocos, e `columns=` descarta as colunas que não interessam antes
de qualquer coisa chegar à memória.
"""),

    code("""
inicio = time.time()
linhas = 0
soma = 0
pico_mb = 0

for pedaco in pysus.stream_parquet(caminho, chunk_size=100_000,
                                   columns=["PA_PROC_ID", "PA_QTDAPR"]):
    linhas += len(pedaco)
    pico_mb = max(pico_mb, pedaco.memory_usage(deep=True).sum() / 1024**2)
    soma += pd.to_numeric(pedaco["PA_QTDAPR"], errors="coerce").sum()

tempo_stream = time.time() - inicio
print(f"{tempo_stream:.2f}s | {linhas:,} linhas percorridas")
print(f"Maior pedaço na memória: {pico_mb:.0f} MB")
print(f"Quantidade aprovada no mês: {soma:,.0f}")
"""),

    md("""
## Técnica 3 — o que NÃO fazer, para ter a comparação

Carregar o arquivo inteiro. Fazemos aqui só para medir; num estado grande esta
célula derrubaria o Python.
"""),

    code("""
inicio = time.time()
tudo = pd.read_parquet(caminho)
tempo_tudo = time.time() - inicio
memoria_gb = tudo.memory_usage(deep=True).sum() / 1024**3

print(f"{tempo_tudo:.2f}s | {len(tudo):,} linhas, {len(tudo.columns)} colunas")
print(f"Memória: {memoria_gb:.2f} GB  ({memoria_gb * 1024:.0f} MB)")
print(f"\\nO arquivo tem {tamanho_mb:.0f} MB em disco e ocupa "
      f"{memoria_gb * 1024 / tamanho_mb:.0f}x isso na memória.")

del tudo
"""),

    code("""
comparacao = pd.DataFrame([
    {"Técnica": "query_parquet (agrega)", "Tempo (s)": round(tempo_consulta, 2),
     "Memória": f"{memoria_kb:.0f} KB"},
    {"Técnica": "stream_parquet (percorre)", "Tempo (s)": round(tempo_stream, 2),
     "Memória": f"{pico_mb:.0f} MB por pedaço"},
    {"Técnica": "read_parquet (tudo)", "Tempo (s)": round(tempo_tudo, 2),
     "Memória": f"{memoria_gb * 1024:.0f} MB"},
])
comparacao
"""),

    md("""
## Verificação de sanidade

Toda análise deste repositório termina conferindo o próprio resultado. Aqui a
conferência é direta: as duas técnicas que não carregam o arquivo devem chegar
**ao mesmo número** que a que carrega. Se divergirem, alguma delas está lendo
o arquivo errado — ou a biblioteca mudou de comportamento.
"""),

    code("""
conferencia = pysus.to_df(pysus.query_parquet(caminho, '''
    SELECT count(*) AS linhas,
           sum(TRY_CAST(PA_QTDAPR AS BIGINT)) AS quantidade
    FROM data
'''))
linhas_sql = int(conferencia["linhas"].iloc[0])
soma_sql = int(conferencia["quantidade"].iloc[0])

print("Verificações\\n")
iguais_linhas = linhas_sql == linhas
iguais_soma = abs(soma_sql - soma) < 1
print(f"1. Linhas: query_parquet {linhas_sql:,} x stream_parquet {linhas:,}")
print(f"   {'confere' if iguais_linhas else 'ATENÇÃO: divergem'}")
print(f"2. Quantidade aprovada: {soma_sql:,} x {soma:,.0f}")
print(f"   {'confere' if iguais_soma else 'ATENÇÃO: divergem'}")
print(f"3. A soma é maior que a contagem de linhas?")
print(f"   {soma_sql:,} > {linhas_sql:,} — "
      f"{'confere (uma linha pode valer várias realizações)' if soma_sql > linhas_sql else 'ATENÇÃO: inesperado no SIA'}")

if not (iguais_linhas and iguais_soma):
    print("\\nATENÇÃO: os caminhos discordam. Não use este resultado antes de "
          "descobrir por quê.")
"""),

    md("""
## Quando usar cada caminho

| Situação | Use |
|---|---|
| Resumo, contagem, agrupamento | `query_parquet` + `to_df` |
| Precisa das linhas, uma passada | `stream_parquet` com `columns=` |
| Arquivo pequeno e você quer tudo | `pd.read_parquet` mesmo |

E entre este notebook e o `arquivos-grandes-e-sql.ipynb`: **prefira aquele**.
O duckdb direto é mais estável e o conhecimento serve fora da PySUS. Este aqui
é o plano B — e existe justamente para que haja um.

## Como adaptar

- **Outro estado ou período:** troque `UF`, `ANO` e `MES` no topo. Comece
  pequeno: um estado grande num mês já passa de três milhões de linhas.
- **Outra base:** o mesmo funciona para SIH, SIM, SINASC e SINAN — troque a
  função de download e as colunas da consulta.
- **Outra pergunta:** o SQL do `query_parquet` é SQL comum. `GROUP BY`,
  `WHERE`, `JOIN` entre arquivos, tudo vale.

---

*Exemplo do PySusNoCode — [kraemeracademy.net](https://kraemeracademy.net).
Dados públicos do DATASUS via PySUS.*
"""),
]

if __name__ == "__main__":
    print("resumo:", construir(DESTINO, CELULAS, timeout=900))

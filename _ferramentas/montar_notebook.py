"""Monta e valida notebooks de exemplo.

Regra do repositório: nenhum notebook entra sem ter sido executado de verdade,
baixando dados reais do DATASUS. Este módulo constrói o .ipynb a partir de uma
lista de células e usa o mesmo motor de execução do PySusNoCode para rodá-las,
guardando as saídas no arquivo final.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Reaproveita o kernel do aplicativo (mesmo motor que valida as células lá).
APP = Path(__file__).resolve().parents[2] / "PySusNoCodeForWindows"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from pysusnocode.kernel import NotebookKernel  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]

# As barras de progresso do PySUS são escritas em stderr com retorno de carro.
# Ao vivo elas ajudam; salvas no notebook viram uma parede de lixo ilegível.
RUIDO = ("file/s]", "it/s]", "?file/s", "?it/s")


def limpar_saidas(saidas: list[dict]) -> list[dict]:
    """Remove barras de progresso, preservando avisos de verdade."""
    limpas = []
    for saida in saidas:
        if saida.get("output_type") != "stream" or saida.get("name") != "stderr":
            limpas.append(saida)
            continue
        texto = "".join(saida.get("text", ""))
        # guarda só as linhas que não são quadro de barra de progresso
        sobra = "\n".join(
            linha for linha in texto.replace("\r", "\n").split("\n")
            if linha.strip() and not any(marca in linha for marca in RUIDO)
        ).strip()
        if sobra:
            saida = dict(saida, text=sobra + "\n")
            limpas.append(saida)
    return limpas


def md(texto: str) -> tuple[str, str]:
    return ("markdown", texto.strip("\n"))


def code(texto: str) -> tuple[str, str]:
    return ("code", texto.strip("\n"))


def construir(caminho: Path, celulas: list[tuple[str, str]], executar: bool = True,
              timeout: int = 900) -> dict:
    """Cria o notebook, executa cada célula e grava com as saídas.

    Devolve um resumo: células executadas, tempo e erros encontrados.
    """
    import nbformat
    from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

    kernel = NotebookKernel()
    nb_celulas = []
    erros: list[str] = []
    inicio = time.time()

    if executar:
        kernel.start()

    try:
        contador = 0
        for tipo, fonte in celulas:
            if tipo == "markdown":
                nb_celulas.append(new_markdown_cell(fonte))
                continue

            celula = new_code_cell(fonte)
            if executar:
                contador += 1
                print(f"    célula {contador}… ", end="", flush=True)
                marco = time.time()
                resultado = kernel.execute(fonte, timeout=timeout)
                print(f"{time.time() - marco:.1f}s "
                      f"{'OK' if resultado.ok else 'ERRO'}")
                celula["execution_count"] = resultado.execution_count
                saidas = []
                for saida in resultado.outputs:
                    try:
                        saidas.append(nbformat.from_dict(saida))
                    except Exception:  # noqa: BLE001
                        pass
                celula["outputs"] = limpar_saidas(saidas)
                if not resultado.ok:
                    erros.append(f"célula {contador}: {resultado.error_summary[-300:]}")
            nb_celulas.append(celula)
    finally:
        if executar:
            kernel.shutdown()

    nb = new_notebook(
        cells=nb_celulas,
        metadata={
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "colab": {"provenance": []},
        },
    )
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        nbformat.write(nb, fh)

    return {
        "arquivo": str(caminho.relative_to(RAIZ)),
        "celulas_codigo": contador if executar else 0,
        "segundos": round(time.time() - inicio, 1),
        "erros": erros,
    }

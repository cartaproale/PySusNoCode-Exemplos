"""Reexecuta um notebook existente e **grava as saídas de volta**.

Por que isto existe: `validar_todos.py` executa e diz se deu erro, mas não
regrava as saídas. Quando uma célula é corrigida à mão, o notebook fica com
código novo ao lado de saída velha — e quem lê no GitHub vê um número que já
não é o que o código produz. Foi assim que a regressão do `state=` ficou
invisível: os três notebooks continuavam mostrando os números certos da
validação antiga enquanto o código passado a devolver o Brasil inteiro.

Uso:
    python _ferramentas/reexecutar.py SINASC/perfil-dos-nascimentos.ipynb
    python _ferramentas/reexecutar.py SIM            # a pasta inteira
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
if str(AQUI) not in sys.path:
    sys.path.insert(0, str(AQUI))

APP = Path(__file__).resolve().parents[2] / "PySusNoCodeForWindows"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from pysusnocode.kernel import NotebookKernel  # noqa: E402

from montar_notebook import limpar_saidas  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
TEMPO_LIMITE = 1800


def reexecutar(caminho: Path) -> tuple[bool, list[str]]:
    """Executa o notebook do começo ao fim e grava saídas e contadores."""
    import nbformat

    doc = nbformat.read(caminho, as_version=4)
    kernel = NotebookKernel()
    kernel.start()
    erros: list[str] = []
    inicio = time.time()

    try:
        contador = 0
        for celula in doc.cells:
            if celula.get("cell_type") != "code":
                continue
            fonte = "".join(celula.get("source", ""))
            if not fonte.strip():
                continue
            contador += 1
            print(f"    célula {contador}… ", end="", flush=True)
            marco = time.time()
            resultado = kernel.execute(fonte, timeout=TEMPO_LIMITE)
            print(f"{time.time() - marco:.1f}s {'OK' if resultado.ok else 'ERRO'}")

            celula["execution_count"] = resultado.execution_count
            saidas = []
            for saida in resultado.outputs:
                try:
                    saidas.append(nbformat.from_dict(saida))
                except Exception:  # noqa: BLE001
                    pass
            celula["outputs"] = limpar_saidas(saidas)
            if not resultado.ok:
                erros.append(
                    f"célula {contador}: "
                    f"{resultado.error_summary.strip().splitlines()[-1][:160]}"
                )
    finally:
        kernel.shutdown()

    nbformat.write(doc, caminho)
    print(f"    {contador} células em {time.time() - inicio:.0f}s — "
          f"saídas regravadas")
    return not erros, erros


def alvos(argumentos: list[str]) -> list[Path]:
    if not argumentos:
        return sorted(p for p in RAIZ.rglob("*.ipynb")
                      if "_ferramentas" not in str(p))
    # Um por um, e nao so o primeiro: a versao anterior lia sys.argv[1] e jogava
    # fora o resto CALADA. Pedir dois notebooks rodava um, dizia "1 de 1 sem
    # erro", e o segundo ficava por reexecutar sem ninguem saber.
    reunidos: list[Path] = []
    for argumento in argumentos:
        for achado in um_alvo(argumento):
            if achado not in reunidos:
                reunidos.append(achado)
    return reunidos


def um_alvo(argumento: str) -> list[Path]:
    caminho = RAIZ / argumento
    if caminho.is_file():
        return [caminho]
    if caminho.is_dir():
        # rglob, e nao glob: 'reexecutar.py .' devolvia ZERO notebooks em
        # silencio, porque a raiz nao tem .ipynb solto. Zero calado e o defeito
        # que este repositorio inteiro existe para ensinar a evitar.
        achados = sorted(caminho.rglob("*.ipynb"))
        achados = [a for a in achados if "_ferramentas" not in str(a)]
        if not achados:
            raise SystemExit(f"nenhum notebook em {argumento}")
        return achados
    raise SystemExit(f"não encontrei: {argumento}")


def conferir_sintaxe(caminho: Path) -> None:
    # json puro: o nbformat so e importado dentro de reexecutar(), e aqui a
    # conferencia roda ANTES de qualquer kernel subir.
    doc = json.loads(caminho.read_text(encoding="utf-8"))
    n = 0
    for celula in doc["cells"]:
        if celula["cell_type"] != "code":
            continue
        n += 1
        fonte = "".join(celula["source"])
        if fonte.lstrip().startswith(("!", "%")):
            continue
        try:
            compile(fonte, str(caminho), "exec")
        except SyntaxError as erro:
            raise SystemExit(
                f"{caminho.relative_to(RAIZ)}, célula de código {n}: "
                f"{erro.msg} (linha {erro.lineno}). Corrija antes de reexecutar."
            )


def main() -> int:
    escolhidos = alvos(sys.argv[1:])

    # Sintaxe antes do kernel: compilar as 400 celulas leva menos de um segundo,
    # e um f-string quebrado so aparecia depois de minutos de download.
    for nb in escolhidos:
        conferir_sintaxe(nb)

    print(f"Reexecutando {len(escolhidos)} notebook(s) com dados reais.\n")
    falhas = []
    for nb in escolhidos:
        print(f"→ {nb.relative_to(RAIZ)}")
        ok, erros = reexecutar(nb)
        if not ok:
            falhas.append((nb, erros))
            for e in erros:
                print(f"      {e}")
    print("\n" + "=" * 60)
    print(f"{len(escolhidos) - len(falhas)} de {len(escolhidos)} sem erro")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())

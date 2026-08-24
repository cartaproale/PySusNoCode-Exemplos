"""Mostra as saídas gravadas nos notebooks, para conferência humana.

Executar sem erro não basta: um notebook pode "funcionar" e mesmo assim
devolver uma tabela vazia ou um número absurdo. Este script imprime o que cada
célula produziu.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def resumir(caminho: Path, limite_linhas: int = 6) -> None:
    nb = json.loads(caminho.read_text(encoding="utf-8"))
    print(f"\n{'=' * 78}\n{caminho.relative_to(RAIZ)}\n{'=' * 78}")

    n = 0
    for celula in nb["cells"]:
        if celula.get("cell_type") != "code":
            continue
        n += 1
        fonte = "".join(celula.get("source", [])).strip()
        primeira = fonte.splitlines()[0] if fonte else ""
        print(f"\n[{n}] {primeira[:70]}")

        saidas = celula.get("outputs", [])
        if not saidas:
            print("     (sem saída)")
            continue

        for saida in saidas:
            tipo = saida.get("output_type")
            if tipo == "stream":
                for linha in "".join(saida.get("text", "")).strip().splitlines()[:limite_linhas]:
                    print(f"     {linha}")
            elif tipo in ("execute_result", "display_data"):
                dados = saida.get("data", {})
                if "image/png" in dados:
                    tamanho = len(dados["image/png"]) * 3 // 4
                    print(f"     [gráfico gerado: {tamanho // 1024} KB]")
                elif "text/plain" in dados:
                    texto = "".join(dados["text/plain"]).strip()
                    for linha in texto.splitlines()[:limite_linhas]:
                        print(f"     {linha[:100]}")
            elif tipo == "error":
                print(f"     ❌ {saida.get('ename')}: {str(saida.get('evalue'))[:90]}")


if __name__ == "__main__":
    alvos = sys.argv[1:] or [str(p) for p in sorted(RAIZ.rglob("*.ipynb"))]
    for alvo in alvos:
        resumir(Path(alvo))

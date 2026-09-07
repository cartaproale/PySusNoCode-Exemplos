"""Sela a fonte de cada célula que já tem saída gravada.

Serve uma vez só, para os notebooks que já estavam validados entrarem no
regime do selo sem precisar de uma rodada inteira de reexecução. Daqui em
diante quem sela é o `reexecutar.py`, no momento em que grava a saída.

Só rode isto logo depois de uma rodada completa aprovada: o selo afirma que a
saída ali gravada veio daquele código, e essa afirmação precisa ser verdade.

    python _ferramentas/selar.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

for _fluxo in (sys.stdout, sys.stderr):
    if hasattr(_fluxo, "reconfigure"):
        _fluxo.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parents[1]


def selar(caminho: Path) -> int:
    doc = json.loads(caminho.read_text(encoding="utf-8"))
    seladas = 0
    for celula in doc.get("cells", []):
        if celula.get("cell_type") != "code":
            continue
        fonte = "".join(celula.get("source", ""))
        if not fonte.strip() or not celula.get("outputs"):
            continue
        selo = hashlib.sha1(fonte.encode("utf-8")).hexdigest()[:12]
        celula.setdefault("metadata", {})["fonte_selada"] = selo
        seladas += 1
    if seladas:
        caminho.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                           encoding="utf-8")
    return seladas


def main() -> int:
    total = 0
    for caminho in sorted(RAIZ.rglob("*.ipynb")):
        if "_ferramentas" in str(caminho) or ".claude" in str(caminho):
            continue
        quantas = selar(caminho)
        total += quantas
        print(f"  {quantas:3} células — {caminho.relative_to(RAIZ)}")
    print(f"\n{total} células seladas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

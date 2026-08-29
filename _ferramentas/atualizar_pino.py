"""Sobe o pino da PySUS em todos os lugares de uma vez.

O repositório fixa a versão da PySUS de propósito: o notebook publicado precisa
rodar com a biblioteca contra a qual foi validado. O preço disso é que o número
aparece em muitos lugares — 33 notebooks, o guia de estilo, o requirements do
aplicativo, o prompt de sistema e este próprio script. Subir na mão é convite a
esquecer um.

Uso:
    python _ferramentas/atualizar_pino.py 2.10.7          # aplica
    python _ferramentas/atualizar_pino.py 2.10.7 --ver    # só mostra

Depois de aplicar, REVALIDE:
    python _ferramentas/validar_todos.py

Trocar o pino sem revalidar quebra a única garantia que o repositório dá.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
APP = RAIZ.parent / "PySusNoCodeForWindows"

# Arquivos de texto onde o pino aparece, e o padrão que o encontra.
ALVOS_TEXTO = [
    (RAIZ / "GUIA-DE-ESTILO.md", r"pysus==\d+\.\d+\.\d+"),
    (RAIZ / "_ferramentas" / "construir_sisab_ubs.py", r"pysus==\d+\.\d+\.\d+"),
    (APP / "requirements.txt", r"pysus==\d+\.\d+\.\d+"),
    (APP / "pysusnocode" / "prompts.py", r"pysus==\d+\.\d+\.\d+"),
    (APP / "pysusnocode" / "lessons.py", r"pysus==\d+\.\d+\.\d+"),
]


def versao_valida(texto: str) -> str:
    if not re.fullmatch(r"\d+\.\d+\.\d+", texto):
        raise SystemExit(f"versão inválida: {texto!r} (esperado algo como 2.10.7)")
    return texto


def atualizar_notebooks(nova: str, aplicar: bool) -> list[str]:
    """Troca o pino na célula de instalação de cada notebook."""
    alvo = re.compile(r"pysus==\d+\.\d+\.\d+")
    mudados = []
    for nb in sorted(RAIZ.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(nb):
            continue
        dados = json.loads(nb.read_text(encoding="utf-8"))
        tocou = False
        for celula in dados["cells"]:
            if celula["cell_type"] != "code":
                continue
            novas = [alvo.sub(f"pysus=={nova}", linha) for linha in celula["source"]]
            if novas != celula["source"]:
                celula["source"] = novas
                tocou = True
        if tocou:
            mudados.append(str(nb.relative_to(RAIZ)))
            if aplicar:
                nb.write_text(json.dumps(dados, ensure_ascii=False, indent=1) + "\n",
                              encoding="utf-8")
    return mudados


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    nova = versao_valida(sys.argv[1])
    aplicar = "--ver" not in sys.argv

    print(f"Pino alvo: pysus=={nova}")
    print("Modo:", "APLICANDO" if aplicar else "só mostrando (--ver)")
    print()

    mudados = atualizar_notebooks(nova, aplicar)
    print(f"Notebooks: {len(mudados)}")
    for m in mudados[:5]:
        print(f"   {m}")
    if len(mudados) > 5:
        print(f"   ... e mais {len(mudados) - 5}")

    print("\nOutros arquivos:")
    for caminho, padrao in ALVOS_TEXTO:
        if not caminho.exists():
            print(f"   AUSENTE  {caminho}")
            continue
        texto = caminho.read_text(encoding="utf-8")
        quantos = len(re.findall(padrao, texto))
        if not quantos:
            print(f"   sem pino {caminho.name}")
            continue
        if aplicar:
            caminho.write_text(re.sub(padrao, f"pysus=={nova}", texto),
                               encoding="utf-8")
        print(f"   {quantos}x       {caminho.name}")

    # Uma checagem final: nao pode sobrar pino antigo em lugar nenhum.
    if aplicar:
        sobrou = []
        for nb in RAIZ.rglob("*.ipynb"):
            if ".ipynb_checkpoints" in str(nb):
                continue
            t = nb.read_text(encoding="utf-8")
            if "pysus==" in t and f"pysus=={nova}" not in t:
                sobrou.append(nb.name)
        print("\nPino antigo remanescente:", sobrou or "nenhum")
        print("\nAGORA REVALIDE — o pino sem revalidação não vale nada:")
        print("   python _ferramentas/validar_todos.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

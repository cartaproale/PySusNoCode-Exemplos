"""Gera o catálogo de exemplos (exemplos.json) lido pelo aplicativo.

O PySusNoCode mostra esta lista para quem abre o programa e não sabe por onde
começar, e baixa daqui o notebook escolhido. Como o catálogo sai dos próprios
arquivos, ele nunca fica desatualizado em relação ao repositório.

Uso:
    python _ferramentas/gerar_catalogo.py
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "exemplos.json"
REPOSITORIO = "cartaproale/PySusNoCode-Exemplos"
RAMO = "main"

# Rótulos em negrito que abrem a descrição do notebook, na ordem de preferência.
ROTULOS = (
    "A pergunta:",
    "Pergunta que este notebook responde:",
    "O que você vai fazer:",
    "O que este notebook faz:",
)

NOMES_DE_GRUPO = {
    "_comece-aqui": "Comece por aqui",
    "cruzamentos": "Cruzando bases",
    "indicadores": "Indicadores",
    "avancado": "Para quem já se sente à vontade",
}


def primeiro_markdown(nb: dict) -> str:
    for celula in nb.get("cells", []):
        if celula.get("cell_type") == "markdown":
            return "".join(celula.get("source", []))
    return ""


def extrair(texto: str, rotulo: str) -> str:
    """Parágrafo que vem depois de um rótulo em negrito, já sem o rótulo.

    Alguns cabeçalhos põem um rótulo por linha, sem linha em branco entre
    eles. Por isso o corte acontece no primeiro dos dois: fim de parágrafo ou
    início do próximo rótulo — senão a descrição sai com o "Tempo estimado"
    grudado no fim.
    """
    marca = f"**{rotulo}**"
    if marca not in texto:
        return ""
    trecho = texto.split(marca, 1)[1]
    trecho = trecho.split("\n\n", 1)[0]
    linhas = []
    for linha in trecho.splitlines():
        if linhas and linha.lstrip().startswith("**"):
            break
        linhas.append(linha)
    return " ".join(" ".join(linhas).split()).strip()


def limpar_markdown(texto: str) -> str:
    """Tira a marcação para o texto caber numa lista da interface."""
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)   # links
    texto = texto.replace("**", "").replace("`", "")
    texto = re.sub(r"(?<!\w)\*(?!\s)([^*]+?)\*(?!\w)", r"\1", texto)   # itálico
    return " ".join(texto.split()).strip()


def descrever(nb: dict) -> tuple[str, str, str, bool]:
    """Título, descrição, tempo estimado e se é um exemplo aprofundado."""
    cabecalho = primeiro_markdown(nb)
    titulo = ""
    for linha in cabecalho.splitlines():
        if linha.startswith("# "):
            titulo = limpar_markdown(linha[2:])
            break

    descricao = ""
    for rotulo in ROTULOS:
        descricao = limpar_markdown(extrair(cabecalho, rotulo))
        if descricao:
            break
    if not descricao:
        # sem rótulo conhecido: usa o primeiro parágrafo depois do título
        corpo = cabecalho.split("\n", 1)[1] if "\n" in cabecalho else ""
        descricao = limpar_markdown(corpo.strip().split("\n\n", 1)[0])

    # Os rótulos terminam em dois-pontos e a frase segue em minúscula
    # ("A pergunta: quantos casos..."). Fora do cabeçalho ela vira uma
    # descrição solta, e aí precisa começar como frase.
    if descricao:
        descricao = descricao[0].upper() + descricao[1:]

    tempo = limpar_markdown(extrair(cabecalho, "Tempo estimado:")).rstrip(".")
    # Os exemplos aprofundados são os que entregam funções reaproveitáveis, e
    # todos trazem esta seção no cabeçalho.
    aprofundado = "O que você leva daqui:" in cabecalho
    return titulo, descricao, tempo, aprofundado


VALIDACAO = RAIZ / "VALIDACAO.md"


def ler_validacao() -> tuple[dict, dict]:
    """Resumo e situação por notebook, direto do VALIDACAO.md.

    O catálogo é o que o aplicativo mostra ao usuário na hora de escolher um
    exemplo — e a validação faz parte da escolha. Quem lê "reprovado na última
    validação" ANTES de abrir não perde tempo com um notebook que o próprio
    repositório sabe que está quebrado (quase sempre por defeito a montante,
    como o catálogo duplicado da dengue em 31/08/2026).
    """
    resumo: dict = {}
    por_arquivo: dict = {}
    if not VALIDACAO.is_file():
        return resumo, por_arquivo
    texto = VALIDACAO.read_text(encoding="utf-8")
    m = re.search(r"\*\*Última validação:\*\* *(\S+)", texto)
    if m:
        resumo["data"] = m.group(1)
    m = re.search(r"\*\*Resultado:\*\* *(\d+) de (\d+)", texto)
    if m:
        resumo["funcionando"] = int(m.group(1))
        resumo["total"] = int(m.group(2))
    m = re.search(r"\*\*Versão da PySUS usada no teste:\*\* *(\S+)", texto)
    if m:
        resumo["versao_pysus"] = m.group(1)
    for linha in texto.splitlines():
        m = re.match(r"\| `([^`]+)` \| \d+ \| \d+ \| \S+ \| (.+?) \|\s*$", linha)
        if not m:
            continue
        arquivo, situacao = m.group(1), m.group(2).strip()
        if situacao.startswith("✅"):
            por_arquivo[arquivo] = {"situacao": "ok"}
        elif situacao.startswith("⚠️"):
            por_arquivo[arquivo] = {"situacao": "alerta",
                                    "detalhe": situacao.lstrip("⚠️ ").strip()[:160]}
        else:
            por_arquivo[arquivo] = {"situacao": "falha",
                                    "detalhe": situacao.lstrip("❌ ").strip()[:160]}
    return resumo, por_arquivo


def main() -> int:
    resumo_val, situacao_val = ler_validacao()
    exemplos = []
    for caminho in sorted(RAIZ.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(caminho):
            continue
        relativo = caminho.relative_to(RAIZ).as_posix()
        nb = json.loads(caminho.read_text(encoding="utf-8"))
        titulo, descricao, tempo, aprofundado = descrever(nb)
        pasta = relativo.split("/")[0]
        celulas = sum(1 for c in nb.get("cells", []) if c.get("cell_type") == "code")
        graficos = sum(
            1
            for c in nb.get("cells", [])
            for s in c.get("outputs", [])
            if "image/png" in s.get("data", {})
        )
        exemplos.append({
            "arquivo": relativo,
            "titulo": titulo or caminho.stem,
            "descricao": descricao,
            "grupo": NOMES_DE_GRUPO.get(pasta, pasta),
            "base": "" if pasta in NOMES_DE_GRUPO else pasta,
            "aprofundado": aprofundado,
            "celulas": celulas,
            "graficos": graficos,
            "tempo": tempo,
            "validacao": situacao_val.get(relativo, {}),
        })

    # Comece por aqui primeiro; depois os aprofundados; o resto em seguida.
    def ordem(item):
        if item["grupo"] == "Comece por aqui":
            return (0, item["arquivo"])
        return (1 if item["aprofundado"] else 2, item["grupo"], item["titulo"])

    exemplos.sort(key=ordem)

    catalogo = {
        "gerado_em": str(date.today()),
        "repositorio": REPOSITORIO,
        "ramo": RAMO,
        "total": len(exemplos),
        "validacao": resumo_val,
        "exemplos": exemplos,
    }
    DESTINO.write_text(
        json.dumps(catalogo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )

    sem_descricao = [e["arquivo"] for e in exemplos if not e["descricao"]]
    print(f"{len(exemplos)} exemplos catalogados em {DESTINO.name}")
    for e in exemplos[:5]:
        print(f"  · {e['titulo'][:70]}")
    if sem_descricao:
        print("\nSem descrição (revise o cabeçalho):")
        for a in sem_descricao:
            print("  !", a)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

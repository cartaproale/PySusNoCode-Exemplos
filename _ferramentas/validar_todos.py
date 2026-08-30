"""Executa todos os notebooks do repositório e gera o relatório de validação.

Este script é a garantia do repositório: nenhum notebook é publicado como
funcional sem passar por aqui. Ele executa cada célula de verdade, baixando
dados reais do DATASUS, e falha se qualquer uma der erro.

Uso:
    python _ferramentas/validar_todos.py            # valida tudo
    python _ferramentas/validar_todos.py SINAN      # só uma pasta
"""

from __future__ import annotations

import json
import sys
import time
from datetime import date
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "PySusNoCodeForWindows"
if str(APP) not in sys.path:
    sys.path.insert(0, str(APP))

from pysusnocode.kernel import NotebookKernel  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
RELATORIO = RAIZ / "VALIDACAO.md"
TEMPO_LIMITE = 1800


def versao_pysus() -> str:
    """Versão da PySUS contra a qual esta validação foi feita."""
    try:
        import pysus

        return pysus.get_version()
    except Exception:  # noqa: BLE001
        try:
            from importlib.metadata import version

            return version("pysus")
        except Exception:  # noqa: BLE001
            return "não identificada"


def executar(caminho: Path) -> dict:
    """Roda todas as células de código do notebook num kernel novo."""
    nb = json.loads(caminho.read_text(encoding="utf-8"))
    kernel = NotebookKernel()
    kernel.start()
    inicio = time.time()
    erros: list[str] = []
    alertas: list[str] = []
    executadas = 0
    graficos = 0

    try:
        for celula in nb["cells"]:
            if celula.get("cell_type") != "code":
                continue
            fonte = "".join(celula.get("source", []))
            if not fonte.strip():
                continue
            executadas += 1
            resultado = kernel.execute(fonte, timeout=TEMPO_LIMITE)
            for saida in resultado.outputs:
                if "image/png" in saida.get("data", {}):
                    graficos += 1
            # A verificacao de sanidade nao levanta excecao: ela IMPRIME. Se o
            # validador so olhasse resultado.ok, um notebook cuja propria
            # conferencia esta gritando passaria como funcionando — e passou,
            # por meses, em dois deles.
            texto = "".join("".join(s.get("text", [])) for s in resultado.outputs)
            for linha in texto.splitlines():
                if "ATENÇÃO" in linha:
                    alertas.append(f"célula {executadas}: {linha.strip()[:150]}")
            if not resultado.ok:
                erros.append(f"célula {executadas}: {resultado.error_summary.strip().splitlines()[-1][:160]}")
                break   # as seguintes dependeriam desta
    finally:
        kernel.shutdown()

    return {
        "arquivo": str(caminho.relative_to(RAIZ)).replace("\\", "/"),
        "celulas": executadas,
        "graficos": graficos,
        "segundos": round(time.time() - inicio, 1),
        "erros": erros,
        "alertas": alertas,
    }


def main() -> int:
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    notebooks = sorted(
        p for p in RAIZ.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in str(p) and filtro in str(p.relative_to(RAIZ))
    )
    if not notebooks:
        print("Nenhum notebook encontrado.")
        return 1

    print(f"Validando {len(notebooks)} notebook(s) com dados reais do DATASUS.\n")
    resultados = []
    for caminho in notebooks:
        print(f"→ {caminho.relative_to(RAIZ)}")
        r = executar(caminho)
        resultados.append(r)
        # ALERTA e um estado proprio: a verificacao de sanidade nao levanta
        # excecao, ela imprime. Sem isto o notebook passava como OK enquanto
        # a propria conferencia dele gritava — e passou, por meses.
        if r["erros"]:
            estado = "FALHOU"
        elif r["alertas"]:
            estado = "ALERTA"
        else:
            estado = "OK"
        print(f"  {estado} — {r['celulas']} células, {r['graficos']} gráfico(s), {r['segundos']}s")
        for a in r["alertas"]:
            print(f"    ! {a}")
        for e in r["erros"]:
            print(f"    ! {e}")

    aprovados = [r for r in resultados if not r["erros"]]
    reprovados = [r for r in resultados if r["erros"]]
    com_alerta = [r for r in resultados if not r["erros"] and r["alertas"]]

    linhas = [
        "# Validação dos notebooks",
        "",
        "Gerado automaticamente por `_ferramentas/validar_todos.py`. Cada notebook",
        "é executado do início ao fim, baixando dados reais do DATASUS.",
        "",
        f"**Última validação:** {date.today():%d/%m/%Y}  ",
        f"**Resultado:** {len(aprovados)} de {len(resultados)} notebooks funcionando"
        + (f", {len(com_alerta)} com alerta da própria verificação"
           if com_alerta else "") + "  ",
        # A versão da biblioteca importa: um exemplo pode passar numa versão e
        # falhar na seguinte, e sem esse registro não dá para saber contra o
        # que o "funcionando" foi apurado.
        f"**Versão da PySUS usada no teste:** {versao_pysus()}",
        "",
        "| Notebook | Células | Gráficos | Tempo | Situação |",
        "|---|---:|---:|---:|---|",
    ]
    for r in resultados:
        if r["erros"]:
            estado = f"❌ {r['erros'][0][:60]}"
        elif r["alertas"]:
            estado = f"⚠️ a própria verificação alertou: {r['alertas'][0][:45]}"
        else:
            estado = "✅ funcionando"
        linhas.append(
            f"| `{r['arquivo']}` | {r['celulas']} | {r['graficos']} | "
            f"{r['segundos']:.0f}s | {estado} |"
        )
    linhas += ["", "> Um notebook só é listado como funcionando depois de executar",
               "> todas as suas células sem erro, com dados reais."]
    print(f"\n{'=' * 60}")
    print(f"{len(aprovados)} de {len(resultados)} notebooks funcionando")
    if com_alerta:
        print(f"{len(com_alerta)} com a PRÓPRIA verificação de sanidade alertando:")
        for r in com_alerta:
            print(f"   {r['arquivo']}")
        print("Isso não é aviso decorativo: ou o dado mudou, ou a conferência")
        print("está mal calibrada. Nos dois casos, alguém precisa olhar.")

    # Uma rodada com filtro NÃO reescreve o relatório. O VALIDACAO.md é a
    # garantia do repositório: ele afirma que TODOS os notebooks foram
    # executados. Uma rodada parcial que o sobrescreve transforma essa garantia
    # em mentira — e já transformou. O repositório chegou a publicar 33
    # exemplos acompanhados de um relatório que cobria três, porque a última
    # rodada tinha sido só na pasta SIA.
    if filtro:
        print(f"Rodada parcial (filtro {filtro!r}): {RELATORIO.name} NÃO foi "
              "atualizado.")
        print("Rode sem filtro para regerar o relatório completo.")
        return 0 if not (reprovados or com_alerta) else 1

    RELATORIO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Relatório: {RELATORIO.relative_to(RAIZ)}")
    return 0 if not (reprovados or com_alerta) else 1


if __name__ == "__main__":
    raise SystemExit(main())

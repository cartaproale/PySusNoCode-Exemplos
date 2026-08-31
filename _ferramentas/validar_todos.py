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
import re
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


CABECALHO_DE_EXCECAO = re.compile(r"^([A-Za-z_][\w.]*(?:Error|Exception|Warning|"
                                  r"Interrupt|Exit|[A-Z]\w*)): (.+)$")


def diagnostico(resumo: str, largura: int = 200) -> str:
    """Extrai a linha que DIAGNOSTICA o erro, e nao a ultima linha qualquer.

    Pegar splitlines()[-1] funciona para "NameError: name 'x' is not defined",
    e falha justamente nos erros que alguem se deu ao trabalho de escrever bem:
    o notebook do SISAB levanta uma excecao com quatro paragrafos explicando
    que o servidor do Ministerio caiu e que a culpa nao e do usuario, e o
    relatorio mostrava so o rabo dela — "abra no navegador: https:", cortado no
    meio da URL. A informacao existia e foi jogada fora na hora de exibir.

    Entao: varremos de baixo para cima ate achar o CABECALHO da excecao, que e
    onde mora o diagnostico.
    """
    linhas = [l.rstrip() for l in resumo.strip().splitlines() if l.strip()]
    if not linhas:
        return "erro sem mensagem"
    for linha in reversed(linhas):
        achado = CABECALHO_DE_EXCECAO.match(linha.strip())
        if achado:
            classe, mensagem = achado.groups()
            return f"{classe}: {mensagem}"[:largura]
    # O duckdb usa cabecalho de erro com ESPACOS ("Invalid Input Error: ...")
    # e termina com um marcador de posicao ("      ^") — que era exatamente o
    # que aparecia no relatorio: "célula 4: ^". Segunda passada, mais frouxa.
    for linha in reversed(linhas):
        l = linha.strip()
        if re.search(r"(Error|Exception)\b.*\S", l) and len(l) > 8:
            return l[:largura]
    return linhas[-1][:largura]


# ---------------------------------------------------------------------------
# Sentinelas: a memória entre validações.
#
# Cada notebook imprime duas coisas que valem guardar: as linhas de PERÍODO
# ("Ano do SINASC: 2022", "Período do SIH: ano de 2025...") e as linhas da
# VERIFICAÇÃO DE SANIDADE ("4. ICSAP entre 5% e 35%? 15.7% (sim)"). Guardamos
# as linhas INTEIRAS, sem tentar interpretar os números: deriva é linha que
# mudou, e quem lê a diferença é gente.
#
# A regra que importa: valor que muda SEM o período mudar merece um olhar.
# Não é reprovação — o DATASUS retifica arquivo publicado, e isso é rotina —
# mas também pode ser uma fórmula que alguém quebrou. A memória existe para
# que a mudança nunca passe em silêncio.
# ---------------------------------------------------------------------------
SENTINELAS = RAIZ / "_ferramentas" / "sentinelas.json"

PADROES_PERIODO = [
    re.compile(r"^Ano d[oe] \S+: *\d{4}"),
    re.compile(r"^Per[íi]odo (do|analisado|da)\b.*\d{4}"),
    re.compile(r"^Compet[êe]ncia.*\d{2}/\d{4}"),
    re.compile(r"^Vamos usar .*\d{4}"),
    re.compile(r"\(o mais recente com arquivo"),
    re.compile(r"^Estado: .+ — \d{4}"),
]
# Uma linha de sanidade é uma linha NUMERADA que carrega um veredito. Os 36
# notebooks falam dois dialetos — "...: confere", "...? 15.7% (sim)", e o mapa
# ainda escreve "— confere (é o estado conhecido...)". O que é comum a todos:
# começa com "N." e contém confere/sim/ATENÇÃO.
PADRAO_SANIDADE = re.compile(
    r"^\d+\.\s.*(confere|\(sim\)|ATENÇÃO)|\((sim|ATENÇÃO)\)\s*$")


def extrair_sentinelas(textos: list[str]) -> dict:
    """Colhe linhas de período e de sanidade das saídas de um notebook."""
    periodos: list[str] = []
    sanidade: list[str] = []
    for texto in textos:
        # O tqdm termina a barra de progresso com \r sem \n; sem esta troca, a
        # barra cola na linha seguinte ("Downloading...|Nascimentos: ano 2022")
        # e o período vira outro texto — foi um falso positivo real.
        for linha in texto.replace("\r", "\n").splitlines():
            limpa = re.sub(r"\s+", " ", linha).strip()[:160]
            if not limpa:
                continue
            if PADRAO_SANIDADE.search(limpa) and limpa not in sanidade:
                sanidade.append(limpa)
            elif any(p.search(limpa) for p in PADROES_PERIODO) and limpa not in periodos:
                periodos.append(limpa)
    return {"periodos": periodos, "sanidade": sanidade}


def comparar_sentinelas(arquivo: str, memoria: dict, atual: dict) -> list[str]:
    """Compara com a validação anterior. Devolve linhas de relato (vazio = estável)."""
    antiga = memoria.get(arquivo)
    if antiga is None:
        return []          # primeira vez na memória: nada com que comparar
    relato: list[str] = []
    if antiga.get("periodos") != atual["periodos"]:
        relato.append("período mudou — diferença nos valores é esperada:")
        for l in antiga.get("periodos", []):
            if l not in atual["periodos"]:
                relato.append(f"  − {l}")
        for l in atual["periodos"]:
            if l not in antiga.get("periodos", []):
                relato.append(f"  + {l}")
        return relato
    sumiram = [l for l in antiga.get("sanidade", []) if l not in atual["sanidade"]]
    surgiram = [l for l in atual["sanidade"] if l not in antiga.get("sanidade", [])]
    if sumiram or surgiram:
        relato.append("DERIVA: valor mudou sem o período mudar — olhe:")
        for l in sumiram:
            relato.append(f"  − {l}")
        for l in surgiram:
            relato.append(f"  + {l}")
    return relato


def semear() -> int:
    """Cria a memória de sentinelas a partir das SAÍDAS SALVAS, sem executar.

    Para o primeiro uso, ou depois de uma mudança intencional já validada.
    As saídas salvas vêm da última validação completa, então a memória nasce
    dizendo a verdade sobre o estado publicado.
    """
    memoria: dict = {}
    for caminho in sorted(RAIZ.rglob("*.ipynb")):
        if ".ipynb_checkpoints" in str(caminho):
            continue
        nb = json.loads(caminho.read_text(encoding="utf-8"))
        textos = ["".join(s.get("text", []))
                  for c in nb.get("cells", []) for s in c.get("outputs", [])]
        rel = str(caminho.relative_to(RAIZ)).replace("\\", "/")
        memoria[rel] = {"data": f"{date.today():%d/%m/%Y}",
                        **extrair_sentinelas(textos)}
    SENTINELAS.write_text(json.dumps(memoria, ensure_ascii=False, indent=1) + "\n",
                          encoding="utf-8")
    com_algo = sum(1 for v in memoria.values() if v["periodos"] or v["sanidade"])
    print(f"Memória semeada das saídas salvas: {len(memoria)} notebooks, "
          f"{com_algo} com sentinelas.")
    return 0


def executar(caminho: Path) -> dict:
    """Roda todas as células de código do notebook num kernel novo."""
    nb = json.loads(caminho.read_text(encoding="utf-8"))
    kernel = NotebookKernel()
    kernel.start()
    inicio = time.time()
    erros: list[str] = []
    alertas: list[str] = []
    textos: list[str] = []
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
            # Cada saida vai SEPARADA para as sentinelas: o tqdm termina a
            # barra sem newline, e juntar tudo numa string so cola a barra na
            # linha seguinte ("...file/s]Nascimentos: ano 2022") — dois falsos
            # positivos de deriva vieram exatamente dai.
            pedacos = ["".join(s.get("text", [])) for s in resultado.outputs]
            textos.extend(pedacos)
            texto = "\n".join(pedacos)
            for linha in texto.splitlines():
                if "ATENÇÃO" in linha:
                    alertas.append(f"célula {executadas}: {linha.strip()[:150]}")
            if not resultado.ok:
                erros.append(f"célula {executadas}: {diagnostico(resultado.error_summary)}")
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
        "sentinelas": extrair_sentinelas(textos),
    }


# Notebooks que precisam rodar ANTES dos outros, e por que.
#
# 03-mapa-completo-das-bases varre onze conjuntos do portal de dados abertos do
# Ministerio, e medimos em 30/08/2026 que isso derruba o acesso ao
# sisab.saude.gov.br por mais de UMA HORA — reproduzido em teste A/B. Duas
# validacoes completas foram reprovadas por isso, sempre no mesmo notebook, e a
# culpa nunca foi dele. Espacar as chamadas foi testado e nao resolveu (a
# rajada e interna a pysus).
#
# Entao a ordem alfabetica, que punha o mapa antes do SISAB, deixa de valer:
# quem depende do SISAB roda primeiro. Nao e conserto do bloqueio, e desvio.
PRIMEIRO = ("AtencaoPrimaria/producao-da-ubs-no-sisab-equipe-por-equipe.ipynb",)


def ordenar(notebooks: list[Path]) -> list[Path]:
    def chave(p: Path) -> tuple[int, str]:
        rel = p.relative_to(RAIZ).as_posix()
        return (PRIMEIRO.index(rel) if rel in PRIMEIRO else len(PRIMEIRO), rel)
    return sorted(notebooks, key=chave)


def main() -> int:
    if "--semear" in sys.argv[1:]:
        return semear()
    filtro = sys.argv[1] if len(sys.argv) > 1 else ""
    notebooks = ordenar(sorted(
        p for p in RAIZ.rglob("*.ipynb")
        if ".ipynb_checkpoints" not in str(p) and filtro in str(p.relative_to(RAIZ))
    ))
    if not notebooks:
        print("Nenhum notebook encontrado.")
        return 1

    print(f"Validando {len(notebooks)} notebook(s) com dados reais do DATASUS.\n")
    try:
        memoria = json.loads(SENTINELAS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        memoria = {}
        print("(sem memória de sentinelas — rode --semear depois de validar)\n")
    derivas: dict[str, list[str]] = {}
    resultados = []
    for caminho in notebooks:
        print(f"→ {caminho.relative_to(RAIZ)}")
        r = executar(caminho)
        resultados.append(r)
        # Notebook que FALHOU nao entra na comparacao: a sanidade nem rodou,
        # e o retrato pela metade so geraria "sumiu tudo" — o erro ja conta.
        relato = ([] if r["erros"] else
                  comparar_sentinelas(r["arquivo"], memoria, r["sentinelas"]))
        if relato:
            derivas[r["arquivo"]] = relato
            for linha in relato:
                print(f"    ~ {linha}")
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
            estado = f"❌ {r['erros'][0][:120]}"
        elif r["alertas"]:
            estado = f"⚠️ a própria verificação alertou: {r['alertas'][0][:45]}"
        else:
            estado = "✅ funcionando"
        linhas.append(
            f"| `{r['arquivo']}` | {r['celulas']} | {r['graficos']} | "
            f"{r['segundos']:.0f}s | {estado} |"
        )
    if derivas:
        linhas += ["", "## Sentinelas: o que mudou desde a validação anterior", ""]
        for arquivo, relato in derivas.items():
            linhas.append(f"**`{arquivo}`**")
            linhas += [f"- {l}" for l in relato]
            linhas.append("")
        linhas += ["> Deriva não reprova: o DATASUS retifica arquivos publicados, e",
                   "> isso é rotina. Mas valor que muda sem o período mudar merece",
                   "> um olhar antes do próximo commit."]
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

    # A memória só avança em rodada completa — pela mesma razão do relatório:
    # uma parcial que a sobrescrevesse apagaria a referência dos outros 30.
    # E notebook que FALHOU mantém a memória antiga: as sentinelas de uma
    # execução interrompida no meio são um retrato pela metade, e gravá-las
    # apagaria justamente a referência boa com que a próxima rodada compara.
    nova_memoria = {}
    for r in resultados:
        if r["erros"] and r["arquivo"] in memoria:
            nova_memoria[r["arquivo"]] = memoria[r["arquivo"]]
        else:
            nova_memoria[r["arquivo"]] = {"data": f"{date.today():%d/%m/%Y}",
                                          **r["sentinelas"]}
    SENTINELAS.write_text(json.dumps(nova_memoria, ensure_ascii=False, indent=1)
                          + "\n", encoding="utf-8")
    print(f"Memória de sentinelas atualizada: {SENTINELAS.relative_to(RAIZ)}")
    return 0 if not (reprovados or com_alerta) else 1


if __name__ == "__main__":
    raise SystemExit(main())

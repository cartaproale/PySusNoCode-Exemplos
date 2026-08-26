"""Saiu versão nova da PySUS? Ela conserta o que nos afeta?

A biblioteca teve cinco lançamentos em três dias. Este script responde de um
golpe: qual é a última versão no PyPI, e se os três defeitos que quebram o
nosso trabalho continuam de pé.

As sondas (cada uma nasceu de um problema real, documentado em
APRENDIZADOS-KERNEL.md):

  1. PyYAML  — a PySUS importa `yaml` sem declarar a dependência. Instalação
     limpa não consegue nem `import pysus` (lição 70).
  2. state=  — o catálogo devolve o arquivo NACIONAL junto com o do estado, e
     o `state=` não filtra. Três exemplos nossos passaram a mostrar o Brasil
     rotulado como Paraná (lição 61).
  3. atencao_primaria() — devolve vazio por um erro de chave interno; atinge
     as 11 funções de nome composto da origem "Saude" (lição 43).

Uso:
    python _ferramentas/vigiar_pysus.py              # sonda a PySUS instalada
    python _ferramentas/vigiar_pysus.py --nova       # instala a última do PyPI
                                                     # num ambiente isolado e
                                                     # sonda lá, sem mexer no
                                                     # seu aplicativo
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

PACOTE = "pysus"
UF_TESTE, ANO_TESTE = "PR", 2022


# --------------------------------------------------------------- PyPI
def ultima_do_pypi() -> tuple[str, list[str]]:
    """Versão mais recente publicada e a lista de dependências declaradas."""
    url = f"https://pypi.org/pypi/{PACOTE}/json"
    with urllib.request.urlopen(url, timeout=60) as resposta:
        dados = json.load(resposta)
    return dados["info"]["version"], dados["info"].get("requires_dist") or []


def instalada() -> str | None:
    try:
        import pysus

        return pysus.__version__
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------- sondas
def sonda_pyyaml() -> tuple[bool, str]:
    """A PySUS declara o PyYAML entre as dependências dela?"""
    from importlib.metadata import requires

    exigidas = requires(PACOTE) or []
    declarado = any(d.lower().startswith(("pyyaml", "yaml")) for d in exigidas)
    if declarado:
        return True, "PyYAML declarado nas dependências"
    return False, ("PyYAML NÃO declarado — `pip install pysus` num ambiente "
                   "limpo falha no `import pysus`")


def sonda_state() -> tuple[bool, str]:
    """`state=` devolve só o estado pedido, ou vem o arquivo nacional junto?"""
    import pysus

    catalogo = pysus.list_files(dataset="sinasc", state=UF_TESTE, year=ANO_TESTE)
    do_estado = {
        Path(str(n)).name
        for n in catalogo.loc[catalogo["state"] == UF_TESTE, "name"]
    }
    caminhos = pysus.sinasc(state=UF_TESTE, year=ANO_TESTE)
    nomes = [Path(str(p)).name for p in caminhos]
    intrusos = [n for n in nomes if n not in do_estado]

    if not intrusos:
        return True, f"state= devolveu só o {UF_TESTE}: {nomes}"
    return False, (f"veio arquivo nacional junto: {intrusos} — "
                   f"quem confiar no state= recebe o Brasil")


def sonda_atencao_primaria() -> tuple[bool, str]:
    """A função da atenção primária voltou a encontrar os dados?"""
    import pysus

    resultado = pysus.atencao_primaria()
    quantos = len(resultado)
    if quantos:
        return True, f"atencao_primaria() devolveu {quantos} item(ns)"
    return False, "atencao_primaria() continua vazia (erro de chave interno)"


SONDAS = [
    ("PyYAML declarado", sonda_pyyaml),
    ("state= filtra", sonda_state),
    ("atencao_primaria()", sonda_atencao_primaria),
]


def rodar_sondas() -> int:
    versao = instalada()
    print(f"PySUS sondada: {versao}\n")
    consertados = 0
    for rotulo, sonda in SONDAS:
        try:
            ok, detalhe = sonda()
        except Exception as erro:  # noqa: BLE001
            texto = str(erro).lower()
            if "ducklake" in texto or "being used by another" in texto or (
                    "ioexception" in texto and "catalog" in texto):
                print(f"  [PULOU] {rotulo:20s} o catálogo do DATASUS está aberto "
                      f"por outro programa")
                print(f"  {'':28s} feche o PySusNoCode (ou espere a validação "
                      f"terminar) e rode de novo")
            else:
                print(f"  [ERRO ] {rotulo:20s} {type(erro).__name__}: "
                      f"{str(erro)[:90]}")
            continue
        marca = "OK   " if ok else "FALHA"
        print(f"  [{marca}] {rotulo:20s} {detalhe}")
        consertados += ok
    print(f"\n{consertados} de {len(SONDAS)} defeitos corrigidos nesta versão.")
    return consertados


# ------------------------------------------------- ambiente isolado
def python_com_venv() -> str | None:
    """Um Python capaz de criar ambiente isolado.

    O Python que vem embutido no PySusNoCode é enxuto e **não traz o módulo
    `venv`**. Nesse caso procuramos outro instalado na máquina.
    """
    candidatos = [sys.executable]
    if sys.platform == "win32":
        for versao in ("3.12", "3.13", "3.11"):
            candidatos.append(f"py -{versao}")
    candidatos.append("python3")

    for candidato in candidatos:
        comando = candidato.split() + ["-c", "import venv"]
        try:
            pronto = subprocess.run(comando, capture_output=True, timeout=60)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if pronto.returncode == 0:
            return candidato
    return None


def sondar_em_ambiente_isolado(versao: str) -> int:
    """Instala a versão pedida num venv temporário e roda as sondas lá."""
    interpretador = python_com_venv()
    if interpretador is None:
        print("Não achei um Python capaz de criar ambiente isolado.")
        print("O Python embutido do aplicativo não traz o módulo `venv`.")
        print("Instale o Python 3.12 (python.org) e rode este script por ele.")
        return 1

    base = Path(tempfile.mkdtemp(prefix="vigia-pysus-"))
    venv = base / "venv"
    print(f"Criando ambiente isolado em {venv} (com {interpretador})…")
    subprocess.run(interpretador.split() + ["-m", "venv", str(venv)], check=True)

    python = venv / "Scripts" / "python.exe"
    if not python.exists():                      # Linux / macOS
        python = venv / "bin" / "python"

    print(f"Instalando {PACOTE}=={versao} (só ele: é assim que a sonda 1 mede)…")
    subprocess.run([str(python), "-m", "pip", "install", "-q",
                    f"{PACOTE}=={versao}"], check=True)

    # a instalação sozinha importa? se não, a sonda 1 já está respondida —
    # mas as outras duas precisam da biblioteca de pé para dizer alguma coisa.
    checagem = subprocess.run([str(python), "-c", "import pysus"],
                              capture_output=True, text=True)
    if checagem.returncode != 0:
        falta = checagem.stderr.strip().splitlines()[-1][:100]
        print(f"  instalação limpa NÃO importa: {falta}")
        print("  instalando o que falta só para poder rodar as outras sondas…")
        subprocess.run([str(python), "-m", "pip", "install", "-q", "pyyaml"],
                       check=True)

    print("Rodando as sondas no ambiente isolado:\n" + "-" * 60)
    concluido = subprocess.run([str(python), str(Path(__file__).resolve()),
                                "--somente-sondas"])
    return concluido.returncode


def main() -> int:
    if "--somente-sondas" in sys.argv:
        rodar_sondas()
        return 0

    try:
        versao_pypi, dependencias = ultima_do_pypi()
    except Exception as erro:  # noqa: BLE001
        print(f"Não consegui consultar o PyPI: {type(erro).__name__}: {erro}")
        versao_pypi, dependencias = None, []

    versao_local = instalada()
    print("=" * 60)
    print("VIGIA DA PYSUS")
    print("=" * 60)
    print(f"  instalada aqui : {versao_local or '(não instalada)'}")
    print(f"  última no PyPI : {versao_pypi or '(não consultada)'}")
    if versao_pypi and versao_local and versao_pypi != versao_local:
        print("  >>> VERSÃO NOVA DISPONÍVEL")
    if dependencias:
        tem_yaml = any(d.lower().startswith(("pyyaml", "yaml")) for d in dependencias)
        print(f"  PyYAML declarado no pacote publicado: "
              f"{'sim' if tem_yaml else 'NÃO'}")
    print()

    if "--nova" in sys.argv:
        if not versao_pypi:
            print("Sem versão do PyPI para testar.")
            return 1
        return sondar_em_ambiente_isolado(versao_pypi)

    rodar_sondas()
    if versao_pypi and versao_local and versao_pypi != versao_local:
        print(f"\nPara sondar a {versao_pypi} sem mexer no seu aplicativo:")
        print("    python _ferramentas/vigiar_pysus.py --nova")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

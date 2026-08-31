"""Recontagem independente dos indicadores — a segunda conta.

Cada notebook calcula seus indicadores de um jeito (pandas, avg(CASE...)).
Este auditor recalcula os mesmos indicadores por OUTRO caminho — numerador e
denominador explícitos, count() em SQL — a partir dos mesmos arquivos do
cache, e compara com o que o notebook gravou nas suas saídas. Se as duas
contas chegam ao mesmo número por caminhos distintos, o erro precisa estar
nos dois lugares ao mesmo tempo para passar.

Ele também confronta os números com o arquivo de VALORES-OURO
(_ferramentas/valores_ouro.json): totais conferidos uma única vez contra uma
fonte EXTERNA (TABNET, SIDRA/IBGE), gravados com data e nunca recalculados
por este programa. A regra do ouro: se a recontagem bate com o notebook mas
os dois discordam do ouro, o defeito é nosso duas vezes.

O auditor NÃO baixa nada: só lê o cache local e as saídas salvas. Ele roda
DEPOIS da validação, não no lugar dela.

Uso:
    python _ferramentas/auditar.py                    # audita os três
    python _ferramentas/auditar.py painel icsap mi    # escolhendo
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parents[1]
CACHE = Path.home() / "pysus" / "downloads" / "ducklake"
OURO = RAIZ / "_ferramentas" / "valores_ouro.json"

MUNICIPIO6 = "411370"        # Londrina — o mesmo do painel
UF_PREFIXO = "41"

PASSOU: list[str] = []
DIVERGIU: list[str] = []


# ---------------------------------------------------------------------------
# infraestrutura comum
# ---------------------------------------------------------------------------
def caminho_cache(subpasta: str, nome: str) -> str:
    achados = glob.glob(str(CACHE / subpasta / nome))
    if not achados:
        raise SystemExit(f"faltou no cache: {subpasta}/{nome} — valide antes de auditar")
    return sorted(achados)[-1].replace(os.sep, "/")


def saidas_salvas(relativo: str) -> str:
    nb = json.loads((RAIZ / relativo).read_text(encoding="utf-8"))
    pedacos = []
    for c in nb["cells"]:
        for o in c.get("outputs", []):
            pedacos.append("".join(o.get("text", [])))
            pedacos.append("".join(o.get("data", {}).get("text/plain", [])))
    return "\n".join(pedacos)


def numero_gravado(texto: str, padrao: str, rotulo: str) -> float:
    m = re.search(padrao, texto)
    if not m:
        raise SystemExit(f"não achei nas saídas salvas: {rotulo} (padrão {padrao!r})")
    bruto = m.group(1)
    # Dois formatos convivem nas saídas: "1.101.298" (mil() do notebook, ponto
    # de milhar) e "1,451" (f"{:,}", vírgula de milhar). Um "10.32" é decimal.
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", bruto):
        return float(re.sub(r"[.,]", "", bruto))
    return float(bruto.replace(",", ""))


def conferir(rotulo: str, gravado: float, recalculado: float,
             numerador: float, denominador: float,
             observacao: str = "", casas: int = 1) -> None:
    """Compara o valor do notebook com a recontagem, mostrando N e D."""
    arredondado = round(recalculado, casas)
    ok = abs(arredondado - gravado) < 10 ** (-casas) / 2 + 1e-9
    marca = "PASS" if ok else "FAIL"
    (PASSOU if ok else DIVERGIU).append(rotulo)
    extra = f"   [{observacao}]" if observacao else ""
    print(f"  {marca}  {rotulo:46} notebook {gravado:>12,}  "
          f"reconta {arredondado:>12,}  = {numerador:,.0f} / {denominador:,.0f}{extra}")


def conferir_ouro(chave: str, nosso: float) -> None:
    """Compara um total nosso com o valor-ouro externo, se houver."""
    try:
        ouro = json.loads(OURO.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return
    registro = ouro.get("valores", {}).get(chave)
    if registro is None:
        return
    valor = registro["valor"]
    tolerancia = registro.get("tolerancia", 0)
    ok = abs(nosso - valor) <= tolerancia
    marca = "OURO" if ok else "FAIL"
    (PASSOU if ok else DIVERGIU).append(f"ouro:{chave}")
    print(f"  {marca}  {chave:46} externo  {valor:>12,}  "
          f"nosso   {nosso:>12,.0f}   [{registro['fonte']}, {registro['data']}]")


# ---------------------------------------------------------------------------
# painel do município (Londrina, 5 bases)
# ---------------------------------------------------------------------------
ICSAP_PREFIXOS_PAINEL = [
    "A33", "A34", "A35", "A36", "A37", "A95", "B05", "B06", "B16", "B26",
    "B77", "A19", "E86", "A00", "A01", "A02", "A03", "A04", "A05", "A06",
    "A07", "A08", "A09", "D50", "H66", "J00", "J01", "J02", "J03", "J06",
    "J31", "J13", "J14", "J18", "J45", "J46", "J20", "J21", "J40", "J41",
    "J42", "J43", "J44", "J47", "I10", "I11", "I20", "I50", "J81", "I63",
    "I64", "I65", "I66", "I67", "I69", "G45", "G46", "E10", "E11", "E12",
    "E13", "E14", "G40", "G41", "N10", "N11", "N12", "N30", "N34", "A46",
    "L01", "L02", "L03", "L04", "L08", "N70", "N71", "N72", "N73", "N75",
    "N76", "K25", "K26", "K27", "K28", "O23", "A50",
]


def valores_do_quadro() -> dict[str, float]:
    nb = json.loads((RAIZ / "cruzamentos" / "painel-do-municipio.ipynb")
                    .read_text(encoding="utf-8"))
    for celula in nb["cells"]:
        for saida in celula.get("outputs", []):
            texto = "".join(saida.get("data", {}).get("text/plain", []))
            if "Município" in texto and "Mortalidade geral" in texto:
                gravados = {}
                for linha in texto.splitlines():
                    m = re.match(r"(.+?)\s{2,}(-?[\d.]+)\s+(-?[\d.]+)", linha)
                    if m:
                        gravados[m.group(1).strip()] = float(m.group(2))
                return gravados
    raise SystemExit("não achei o quadro de indicadores nas saídas do painel")


def auditar_painel(con) -> None:
    g = valores_do_quadro()
    print(f"### painel-do-municipio — Londrina, {len(g)} indicadores gravados\n")

    pop = caminho_cache("ibge", "POPTBR24.parquet")
    hab, hab_uf = con.execute(f"""
        SELECT sum(CASE WHEN CAST(MUNIC_RES AS VARCHAR) LIKE '{MUNICIPIO6}%'
                        THEN TRY_CAST(POPULACAO AS BIGINT) END),
               sum(CASE WHEN CAST(MUNIC_RES AS VARCHAR) LIKE '{UF_PREFIXO}%'
                        THEN TRY_CAST(POPULACAO AS BIGINT) END)
        FROM read_parquet('{pop}')""").fetchone()
    conferir("População", g["População"], hab, hab, 1, casas=0)
    conferir_ouro("populacao_londrina_2024", hab)
    conferir_ouro("populacao_pr_2024", hab_uf)

    dn = caminho_cache("sinasc", "DNPR2022.parquet")
    n = con.execute(f"""
        SELECT count(*) AS nasc,
               count(CASE WHEN PARTO IN ('1','2') THEN 1 END) AS parto_valido,
               count(CASE WHEN PARTO = '2' THEN 1 END) AS cesareas,
               count(CASE WHEN TRY_CAST(PESO AS INT) BETWEEN 200 AND 7000 THEN 1 END) AS peso_valido,
               count(CASE WHEN TRY_CAST(PESO AS INT) BETWEEN 200 AND 2499 THEN 1 END) AS baixo_peso,
               count(CASE WHEN TRY_CAST(SEMAGESTAC AS INT) BETWEEN 15 AND 45 THEN 1 END) AS ig_valida,
               count(CASE WHEN TRY_CAST(SEMAGESTAC AS INT) BETWEEN 15 AND 36 THEN 1 END) AS prematuros,
               count(CASE WHEN TRY_CAST(CONSPRENAT AS INT) BETWEEN 0 AND 30 THEN 1 END) AS pren_valido,
               count(CASE WHEN TRY_CAST(CONSPRENAT AS INT) BETWEEN 6 AND 30 THEN 1 END) AS pren_6mais,
               count(CASE WHEN TRY_CAST(IDADEMAE AS INT) BETWEEN 10 AND 55 THEN 1 END) AS idade_valida,
               count(CASE WHEN TRY_CAST(IDADEMAE AS INT) BETWEEN 10 AND 19 THEN 1 END) AS maes_jovens
        FROM read_parquet('{dn}')
        WHERE CODMUNRES = '{MUNICIPIO6}'""").df().iloc[0]
    conferir("Nascidos vivos", g["Nascidos vivos"], n["nasc"], n["nasc"], 1, casas=0)
    conferir_ouro("nascidos_vivos_londrina_2022", n["nasc"])
    conferir("Cesáreas", g["Cesáreas"], 100 * n["cesareas"] / n["parto_valido"],
             n["cesareas"], n["parto_valido"],
             f"{n['nasc'] - n['parto_valido']} parto ignorado fora da conta")
    conferir("Baixo peso ao nascer", g["Baixo peso ao nascer"],
             100 * n["baixo_peso"] / n["peso_valido"],
             n["baixo_peso"], n["peso_valido"],
             f"{n['nasc'] - n['peso_valido']} sem peso válido")
    conferir("Prematuridade", g["Prematuridade"],
             100 * n["prematuros"] / n["ig_valida"], n["prematuros"], n["ig_valida"],
             f"{n['nasc'] - n['ig_valida']} sem semanas válidas")
    conferir("Pré-natal com 6+ consultas", g["Pré-natal com 6+ consultas"],
             100 * n["pren_6mais"] / n["pren_valido"], n["pren_6mais"], n["pren_valido"])
    conferir("Mães com menos de 20 anos", g["Mães com menos de 20 anos"],
             100 * n["maes_jovens"] / n["idade_valida"], n["maes_jovens"], n["idade_valida"])

    do = caminho_cache("sim", "DOPR2022.parquet")
    o = con.execute(f"""
        SELECT count(*) AS obitos,
               count(CASE WHEN substr(IDADE,1,1) IN ('0','1','2','3')
                           AND TIPOBITO = '2' THEN 1 END) AS infantis,
               count(CASE WHEN substr(CAUSABAS,1,1) = 'I' THEN 1 END) AS circ,
               count(CASE WHEN substr(CAUSABAS,1,1) = 'C' THEN 1 END) AS cancer,
               count(CASE WHEN substr(CAUSABAS,1,1) IN ('V','W','X','Y') THEN 1 END) AS ext,
               count(CASE WHEN substr(CAUSABAS,1,1) = 'R' THEN 1 END) AS mal
        FROM read_parquet('{do}')
        WHERE CODMUNRES = '{MUNICIPIO6}'""").df().iloc[0]
    conferir("Óbitos", g["Óbitos"], o["obitos"], o["obitos"], 1, casas=0)
    conferir_ouro("obitos_londrina_2022", o["obitos"])
    conferir("Mortalidade geral", g["Mortalidade geral"],
             1000 * o["obitos"] / hab, o["obitos"], hab,
             "óbitos de 2022 sobre população de 2024 — mistura de safra do notebook")
    conferir("Mortalidade infantil", g["Mortalidade infantil"],
             1000 * o["infantis"] / n["nasc"], o["infantis"], n["nasc"])
    conferir_ouro("obitos_infantis_londrina_2022", o["infantis"])
    for chave, rotulo in [("circ", "Óbitos por causa circulatória (%)"),
                          ("cancer", "Óbitos por câncer (%)"),
                          ("ext", "Óbitos por causas externas (%)"),
                          ("mal", "Óbitos por causa mal definida (%)")]:
        conferir(rotulo, g[rotulo], 100 * o[chave] / o["obitos"], o[chave], o["obitos"])

    lt = caminho_cache("cnes", "LTPR2406.parquet")
    leitos = con.execute(f"""
        SELECT sum(TRY_CAST(QT_EXIST AS INT)) FROM read_parquet('{lt}')
        WHERE CODUFMUN = '{MUNICIPIO6}'""").fetchone()[0]
    conferir("Leitos por mil habitantes", g["Leitos por mil habitantes"],
             1000 * leitos / hab, leitos, hab, casas=2)
    pf = caminho_cache("cnes", "PFPR2406.parquet")
    medicos = con.execute(f"""
        SELECT count(DISTINCT CPF_PROF) FROM read_parquet('{pf}')
        WHERE CODUFMUN = '{MUNICIPIO6}' AND CBO LIKE '225%'""").fetchone()[0]
    conferir("Médicos por mil habitantes", g["Médicos por mil habitantes"],
             1000 * medicos / hab, medicos, hab, casas=2)

    rd25 = sorted(glob.glob(str(CACHE / "sih" / "RDPR25*.parquet")))
    if len(rd25) != 12:
        raise SystemExit(f"esperava 12 RDPR25xx no cache, achei {len(rd25)}")
    lista = "[" + ", ".join("'" + a.replace(os.sep, "/") + "'" for a in rd25) + "]"
    prefixos = ", ".join(f"'{p}'" for p in ICSAP_PREFIXOS_PAINEL)
    s = con.execute(f"""
        SELECT count(*) AS internacoes,
               count(CASE WHEN substr(DIAG_PRINC,1,3) IN ({prefixos}) THEN 1 END) AS icsap,
               count(CASE WHEN MUNIC_RES <> MUNIC_MOV THEN 1 END) AS fora,
               count(CASE WHEN MORTE = '1' THEN 1 END) AS obitos_hosp,
               sum(TRY_CAST(DIAS_PERM AS BIGINT)) AS dias,
               count(TRY_CAST(DIAS_PERM AS BIGINT)) AS com_dias
        FROM read_parquet({lista})
        WHERE substr(DIAG_PRINC,1,1) <> 'O' AND MUNIC_RES = '{MUNICIPIO6}'""").df().iloc[0]
    conferir("Internações sensíveis à atenção primária",
             g["Internações sensíveis à atenção primária"],
             100 * s["icsap"] / s["internacoes"], s["icsap"], s["internacoes"])
    conferir("Internações fora do município de residência",
             g["Internações fora do município de residência"],
             100 * s["fora"] / s["internacoes"], s["fora"], s["internacoes"])
    conferir("Letalidade hospitalar", g["Letalidade hospitalar"],
             100 * s["obitos_hosp"] / s["internacoes"],
             s["obitos_hosp"], s["internacoes"], casas=2)
    conferir("Permanência média", g["Permanência média"],
             s["dias"] / s["com_dias"], s["dias"], s["com_dias"],
             f"{s['internacoes'] - s['com_dias']:.0f} sem DIAS_PERM")


# ---------------------------------------------------------------------------
# internações sensíveis (PR inteiro, lista Portaria com códigos de 3 E 4 dígitos)
# ---------------------------------------------------------------------------
ICSAP_GRUPOS = {
    "1": ["A33", "A34", "A35", "A36", "A37", "A95", "B05", "B06", "B16",
          "B26", "B77", "G000", "A170", "A19"],
    "2": ["E86"] + [f"A0{i}" for i in range(10)],
    "3": ["D50"],
    "4": [f"E4{i}" for i in range(0, 7)] + [f"E{i}" for i in range(50, 65)],
    "5": ["H66", "J00", "J01", "J02", "J03", "J06", "J31"],
    "6": ["J13", "J14", "J153", "J154", "J158", "J159", "J181"],
    "7": ["J45", "J46"],
    "8": ["J20", "J21", "J40", "J41", "J42", "J43", "J44", "J47"],
    "9": ["I10", "I11"],
    "10": ["I20"],
    "11": ["I50", "J81"],
    "12": ["I63", "I64", "I65", "I66", "I67", "I69", "G45", "G46"],
    "13": ["E10", "E11", "E12", "E13", "E14"],
    "14": ["G40", "G41"],
    "15": ["N10", "N11", "N12", "N30", "N34", "N390"],
    "16": ["A46", "L01", "L02", "L03", "L04", "L08"],
    "17": ["N70", "N71", "N72", "N73", "N75", "N76"],
    "18": ["K25", "K26", "K27", "K28", "K920", "K921", "K922"],
    "19": ["O23", "A50", "P350"],
}


def auditar_icsap(con) -> None:
    texto = saidas_salvas("SIH/internacoes-sensiveis-a-atencao-primaria.ipynb")
    g_total = numero_gravado(texto, r"Internações no período:\s+([\d.]+)", "internações")
    g_obst = numero_gravado(texto, r"Partos e causas obstétricas:\s+([\d.]+)", "obstétricas")
    g_den = numero_gravado(texto, r"Denominador \(sem partos\):\s+([\d.]+)", "denominador")
    g_sens = numero_gravado(texto, r"Sensíveis à atenção primária:\s+([\d.]+)", "sensíveis")
    g_prop = numero_gravado(texto, r"PROPORÇÃO DE ICSAP — PR, \d{4}:\s+([\d.]+)%", "proporção")
    print(f"\n### internacoes-sensiveis — PR inteiro, ano completo\n")

    todos = sorted({c for lista in ICSAP_GRUPOS.values() for c in lista})
    c4 = [c for c in todos if len(c) == 4]
    c3 = [c for c in todos if len(c) == 3]
    # A regra do notebook: o código de 4 dígitos decide primeiro, depois o de 3.
    # Como nenhum código de 4 da lista contradiz um de 3 (J153 entra e J15 não
    # está na lista), a união dos dois testes reproduz a mesma classificação.
    em4 = ", ".join(f"'{c}'" for c in c4)
    em3 = ", ".join(f"'{c}'" for c in c3)
    rd25 = sorted(glob.glob(str(CACHE / "sih" / "RDPR25*.parquet")))
    lista = "[" + ", ".join("'" + a.replace(os.sep, "/") + "'" for a in rd25) + "]"
    r = con.execute(f"""
        SELECT count(*) AS total,
               count(CASE WHEN upper(DIAG_PRINC) LIKE 'O%' THEN 1 END) AS obstetricas,
               count(CASE WHEN substr(upper(DIAG_PRINC),1,4) IN ({em4})
                            OR substr(upper(DIAG_PRINC),1,3) IN ({em3})
                          THEN 1 END) AS sensiveis,
               count(CASE WHEN upper(DIAG_PRINC) NOT LIKE 'O%'
                            OR substr(upper(DIAG_PRINC),1,4) IN ({em4})
                            OR substr(upper(DIAG_PRINC),1,3) IN ({em3})
                          THEN 1 END) AS elegiveis
        FROM read_parquet({lista})""").df().iloc[0]
    conferir("Internações no período (PR)", g_total, r["total"], r["total"], 1, casas=0)
    conferir("Partos e causas obstétricas", g_obst, r["obstetricas"],
             r["obstetricas"], 1, casas=0)
    conferir("Denominador (sem partos)", g_den, r["elegiveis"], r["elegiveis"], 1,
             "obstétrica que É sensível (O23...) fica no denominador", casas=0)
    conferir("Sensíveis à atenção primária", g_sens, r["sensiveis"],
             r["sensiveis"], 1, casas=0)
    conferir("Proporção de ICSAP (%)", g_prop,
             100 * r["sensiveis"] / r["elegiveis"], r["sensiveis"], r["elegiveis"])
    # O total do SIH NÃO se compara com o TABNET por igualdade: semânticas de
    # período diferentes (competência × mês de internação). A medição completa
    # está em valores_ouro.json, na seção de referências sem comparação.


# ---------------------------------------------------------------------------
# mortalidade infantil (PR, definição DO PRÓPRIO notebook: sem TIPOBITO)
# ---------------------------------------------------------------------------
def auditar_mi(con) -> None:
    texto = saidas_salvas("indicadores/mortalidade-infantil.ipynb")
    g_inf = numero_gravado(texto, r"Óbitos de menores de 1 ano:\s+([\d,]+)", "infantis")
    g_nasc = numero_gravado(texto, r"Nascidos vivos:\s+([\d,]+)", "nascidos")
    g_taxa = numero_gravado(texto, r"Taxa de mortalidade infantil: ([\d.]+)", "taxa")
    print(f"\n### mortalidade-infantil — PR 2022\n")

    do = caminho_cache("sim", "DOPR2022.parquet")
    dn = caminho_cache("sinasc", "DNPR2022.parquet")
    infantis = con.execute(f"""
        SELECT count(*) FROM read_parquet('{do}')
        WHERE substr(IDADE,1,1) IN ('0','1','2','3')""").fetchone()[0]
    nasc = con.execute(f"SELECT count(*) FROM read_parquet('{dn}')").fetchone()[0]
    conferir("Óbitos de menores de 1 ano (PR)", g_inf, infantis, infantis, 1, casas=0)
    conferir("Nascidos vivos (PR)", g_nasc, nasc, nasc, 1, casas=0)
    conferir_ouro("nascidos_vivos_pr_2022", nasc)
    conferir_ouro("obitos_infantis_pr_2022", infantis)
    conferir("Taxa de mortalidade infantil", g_taxa, 1000 * infantis / nasc,
             infantis, nasc, casas=2)
    # A definição deste notebook NÃO filtra TIPOBITO; a do painel filtra ('2',
    # não fetal). A diferença medida fica registrada aqui de propósito:
    com_tipo = con.execute(f"""
        SELECT count(*) FROM read_parquet('{do}')
        WHERE substr(IDADE,1,1) IN ('0','1','2','3') AND TIPOBITO = '2'""").fetchone()[0]
    if com_tipo != infantis:
        print(f"        nota: com TIPOBITO='2' (regra do painel) seriam "
              f"{com_tipo:,} — diferença de {infantis - com_tipo} registro(s)")


def main() -> int:
    escolha = [a for a in sys.argv[1:] if not a.startswith("-")] or ["painel", "icsap", "mi"]
    con = duckdb.connect()
    if "painel" in escolha:
        auditar_painel(con)
    if "icsap" in escolha:
        auditar_icsap(con)
    if "mi" in escolha:
        auditar_mi(con)
    print(f"\n{'=' * 74}")
    print(f"{len(PASSOU)} conferências reproduzidas, {len(DIVERGIU)} divergentes")
    for r in DIVERGIU:
        print(f"   DIVERGIU: {r}")
    return 1 if DIVERGIU else 0


if __name__ == "__main__":
    sys.exit(main())

"""Monta o exemplo 'Compartilhar dados sem expor identificadores'.

Usa mask_data/unmask_data da PySUS sobre o CNS do profissional no SIA, que e
dado pessoal presente em arquivo publico. O notebook mostra os tres metodos e,
principalmente, onde cada um engana.
"""
from pathlib import Path

from montar_notebook import code, construir, md

DESTINO = Path(__file__).resolve().parents[1] / "avancado" / \
    "compartilhar-dados-sem-expor-identificadores.ipynb"

CELULAS = [
    md("""
# Compartilhar dados sem expor identificadores

**A pergunta:** preciso mandar um recorte da produção ambulatorial para um
colega analisar. Como tiro de lá quem atendeu, sem estragar a análise?

**Fonte:** SIA/SUS (produção ambulatorial), pela biblioteca PySUS.

**Tempo estimado:** 3 a 6 minutos.

> ### Por que isto é um problema de verdade
>
> Os arquivos do DATASUS são públicos, mas **não são anônimos**. A produção
> ambulatorial traz o `PA_CNSMED` — o Cartão Nacional de Saúde do profissional
> que executou o procedimento. É um número que identifica uma pessoa.
>
> Baixar é uma coisa; **repassar adiante** é outra. A LGPD trata dado de saúde
> como dado pessoal sensível, e o fato de a origem ser pública não transfere a
> responsabilidade de quem redistribui.
>
> A PySUS traz `mask_data` para isso. Este notebook mostra como usar — e mostra
> os três lugares onde ela engana quem confia sem conferir.
"""),

    md("""
## Preparação

Atenção a esta célula: `mask_data` precisa da biblioteca `cryptography`, que a
PySUS **não declara como dependência**. Ela é importada só na hora de usar, então
o erro não aparece na instalação — aparece no meio da sua análise. Instale junto.
"""),

    code("%pip install pysus==2.10.6 cryptography nest_asyncio -q"),

    code("""
import nest_asyncio
nest_asyncio.apply()

import pandas as pd
import pysus
from pysus.api.transform.masking import mask_data, unmask_data

print("PySUS", pysus.__version__)
"""),

    code("""
# ---- O que você pode trocar -------------------------------------------
UF = "AC"      # estado pequeno, para o exemplo rodar rápido
ANO = 2025
MES = 1
LINHAS = 20000  # tamanho da amostra usada na demonstração
"""),

    md("""
## 1. O identificador existe mesmo?

Antes de proteger, confira que há o que proteger. Vamos olhar o `PA_CNSMED`
sem carregar o arquivo inteiro.
"""),

    code("""
from pysus import sia

caminho = str(sia(UF, ANO, MES, group="PA")[0]).replace("\\\\", "/")

perfil = pysus.to_df(pysus.query_parquet(caminho, '''
    SELECT count(*)                        AS linhas,
           count(DISTINCT PA_CNSMED)       AS profissionais_distintos,
           sum(CASE WHEN PA_CNSMED IS NULL OR trim(PA_CNSMED) = ''
                    THEN 1 ELSE 0 END)     AS sem_cns
    FROM data
'''))
perfil
"""),

    md("""
Cada linha carrega o CNS de um profissional. Não é um campo vazio herdado de
sistema antigo: está preenchido, e identifica pessoas reais.

## 2. A primeira armadilha: deixar a biblioteca escolher as colunas

`mask_data(df)` sem `columns=` tenta **adivinhar** quais colunas são sensíveis,
procurando pedaços de texto no nome da coluna: `CPF`, `NOME`, `NASC`, `RG`,
`ENDERECO`, `TELEFONE`, `EMAIL`, `CEP`.

Procurar pedaço de nome erra dos dois lados. Vamos ver nos dados reais.
"""),

    code("""
from pysus.api.transform.masking import _detect_sensitive_columns
import pyarrow.parquet as pq

colunas_sia = pq.read_schema(caminho).names
detectadas = _detect_sensitive_columns(pd.DataFrame(columns=colunas_sia))

print("Colunas do SIA/PA:", len(colunas_sia))
print("O que a auto-detecção marcaria como sensível:", detectadas)
print()
print("PA_CNSMED (o CNS do profissional) foi detectado?",
      "SIM" if "PA_CNSMED" in detectadas else "NÃO")
"""),

    md("""
Dois erros de uma vez:

- **`PA_INCURG` foi marcada** — é o incremento de urgência, um valor
  administrativo. Entrou porque as letras `RG` aparecem no meio de `INCURG`.
  Criptografar essa coluna estraga a análise sem proteger ninguém.
- **`PA_CNSMED` não foi marcada** — o identificador de verdade ficou de fora,
  porque `CNS` não está na lista de padrões.

O resultado é o pior dos dois mundos: você entrega o arquivo achando que está
protegido, e ele continua trazendo o profissional.

No SINASC é ainda mais claro. Vamos olhar as colunas de lá.
"""),

    code("""
import os
from pysus import sinasc

# Atenção: state= diz ONDE PROCURAR, não filtra o resultado — a consulta traz
# também o arquivo nacional. Escolhemos o do estado pelo nome do arquivo.
arquivos = [str(a) for a in sinasc(state=UF, year=2022, as_dataframe=False)]
do_estado = [a for a in arquivos
             if os.path.basename(a).upper().startswith('DN' + UF)]

colunas_sinasc = pq.read_schema(do_estado[0].replace(chr(92), '/')).names
print('Arquivo:', os.path.basename(do_estado[0]))
print('Detectadas:', _detect_sensitive_columns(pd.DataFrame(columns=colunas_sinasc)))
"""),

    md("""
`CODMUNNASC` (município de nascimento), `LOCNASC` (se nasceu em hospital, em
casa, no caminho) e `TPNASCASSI` (quem assistiu o parto) são **as colunas da
análise**. A auto-detecção as pegou porque todas contêm `NASC`.

Aceitar `columns=None` no SINASC criptografa o município de nascimento e depois
você tenta agrupar por ele.

> **A regra:** sempre diga quais colunas mascarar. Olhe a lista, decida você.
"""),

    md("""
## 3. Os três métodos, e o que cada um faz com a sua análise

`mask_data` aceita `method=` com três valores. A diferença entre eles não é
"mais forte" e "mais fraco" — é **o que sobra para analisar depois**.
"""),

    code("""
amostra = pd.read_parquet(caminho, columns=["PA_CNSMED", "PA_PROC_ID",
                                            "PA_QTDAPR"]).head(LINHAS)
distintos_originais = amostra["PA_CNSMED"].nunique()
print(f"Amostra: {len(amostra):,} linhas, "
      f"{distintos_originais:,} profissionais distintos")
"""),

    code("""
resultados = []
guardado = {}

for metodo in ["encrypt", "hash", "redact"]:
    mascarada, chave = mask_data(amostra, columns=["PA_CNSMED"], method=metodo)
    guardado[metodo] = (mascarada, chave)
    resultados.append({
        "método": metodo,
        "vira": str(mascarada["PA_CNSMED"].iloc[0])[:28] + "…",
        "profissionais distintos": mascarada["PA_CNSMED"].nunique(),
        "conta certo?": "sim" if mascarada["PA_CNSMED"].nunique() ==
                        distintos_originais else "NÃO",
        "reversível?": "com a chave" if metodo == "encrypt" else "não",
    })

comparacao = pd.DataFrame(resultados)
print(f"(o original tem {distintos_originais:,} profissionais distintos)\\n")
comparacao
"""),

    md("""
## 4. A segunda armadilha: `encrypt` inventa profissionais

Olhe a coluna "profissionais distintos" acima. O `encrypt` transformou os
profissionais da amostra em **um valor diferente por linha**.

O motivo é técnico e tem uma boa razão: a criptografia usada (Fernet) embaralha
com um ingrediente aleatório a cada chamada, para que o mesmo valor não gere
sempre o mesmo resultado — é assim que ela impede que alguém compare dois
arquivos e descubra quem se repete.

O efeito colateral é que **o mesmo profissional vira vários**. Se o seu colega
receber esse arquivo e contar quantos profissionais atenderam, ele vai contar
linhas achando que conta pessoas — e o número sai alto, sem erro nenhum na tela.
É a mesma armadilha de contar em vez de somar, disfarçada de segurança.
"""),

    code("""
mascarada, chave = guardado["encrypt"]
print(f"Profissionais distintos, de verdade: {distintos_originais:,}")
print(f"Profissionais distintos, no arquivo criptografado: "
      f"{mascarada['PA_CNSMED'].nunique():,}")
print(f"Linhas da amostra: {len(amostra):,}")
print("\\nA criptografia não preserva agrupamento. Quem receber esse arquivo "
      "não consegue\\ncontar profissionais, nem juntar com outra tabela pelo CNS.")
"""),

    md("""
Em compensação, **é o único método que volta atrás**. Guarde a chave em lugar
separado do arquivo — quem tem os dois tem o dado original.
"""),

    code("""
recuperada = unmask_data(mascarada, ["PA_CNSMED"], chave)
voltou_igual = recuperada["PA_CNSMED"].equals(amostra["PA_CNSMED"])


# Mostra o CNS sem publicá-lo: três primeiros e dois últimos dígitos.
def so_as_pontas(cns):
    cns = str(cns)
    return f"{cns[:3]}{'•' * (len(cns) - 5)}{cns[-2:]}"


print("Com a chave, o CNS original volta?", "sim" if voltou_igual else "NÃO")
print("Primeiro CNS, antes :", so_as_pontas(amostra["PA_CNSMED"].iloc[0]))
print("Primeiro CNS, depois:", so_as_pontas(recuperada["PA_CNSMED"].iloc[0]))
print()
print("Repare que nem aqui o número aparece inteiro. Este notebook é "
      "publicado no GitHub")
print("com as saídas salvas — imprimir o CNS de alguém seria fazer "
      "exatamente o que")
print("ele ensina a evitar.")
"""),

    md("""
## 5. `hash`: preserva a análise — e é menos protegido do que parece

O `hash` é determinístico: o mesmo CNS vira sempre o mesmo código. Por isso a
contagem de profissionais fica **certa**, e o seu colega ainda consegue juntar
duas tabelas pelo profissional sem nunca saber quem ele é.

Só que a mesma propriedade que faz isso funcionar abre uma porta. O hash não
leva nenhum ingrediente secreto: quem tiver **a lista de CNS possíveis** — o
CNES publica os profissionais — pode passar a lista pela mesma conta e comparar.

Não é teoria. Vamos fazer o ataque aqui.
"""),

    code("""
import hashlib
import time

mascarada_hash, _ = guardado["hash"]

# O atacante não precisa do seu arquivo original: basta conhecer o universo de
# CNS possíveis. Aqui simulamos esse universo com os CNS da própria amostra.
universo = amostra["PA_CNSMED"].astype(str).unique()

inicio = time.time()
dicionario = {hashlib.sha256(c.encode()).hexdigest(): c for c in universo}
recuperados = mascarada_hash["PA_CNSMED"].map(dicionario)
segundos = time.time() - inicio

print(f"Universo testado: {len(universo):,} CNS")
print(f"Tempo do ataque: {segundos:.2f}s")
print(f"Hashes revertidos: {recuperados.notna().mean() * 100:.1f}%")
print()
print("O hash é PSEUDONIMIZAÇÃO, não anonimização: ele esconde o número de quem")
print("olha por cima, e devolve o número para quem sabe o que procurar.")
"""),

    md("""
Isso não torna o `hash` inútil — torna-o adequado a um cenário específico:
**colega de confiança que precisa agrupar por profissional**. Para publicação
aberta, ele não serve.

## 6. `redact`: o único que não tem volta

Substitui tudo por `***`. Perde a análise por profissional inteira, e nem com
chave se recupera — `unmask_data` levanta erro se você tentar.
"""),

    code("""
redigida, chave_redact = guardado["redact"]
print("Como fica:", redigida["PA_CNSMED"].iloc[0])
print("Valores distintos que sobraram:", redigida["PA_CNSMED"].nunique())

try:
    unmask_data(redigida, ["PA_CNSMED"], chave_redact)
    print("\\nATENÇÃO: o unmask não falhou — verifique a versão da biblioteca.")
except Exception as erro:
    print(f"\\nTentar reverter falha, como esperado: {type(erro).__name__}")
    print("Se você redigir sem guardar o original, o dado acabou.")
"""),

    md("""
## 7. Qual escolher

| Você vai… | Use | Porque |
|---|---|---|
| Publicar aberto, sem análise por profissional | `redact` | Não há o que reverter |
| Mandar para colega que precisa agrupar por profissional | `hash` | Preserva contagem e junção; pseudonimiza |
| Precisar recuperar o original depois | `encrypt` + chave guardada à parte | Único reversível — mas **não conta profissionais** |

E em qualquer um dos três: **passe `columns=` explicitamente**.
"""),

    md("""
## Verificação de sanidade

As afirmações deste notebook são todas verificáveis. A célula abaixo confere
cada uma e reclama alto se alguma deixar de valer — por exemplo, se uma versão
nova da PySUS mudar o comportamento.
"""),

    code("""
print("Verificações\\n")
falhas = []

# 1. o identificador está de fato preenchido
ok1 = int(perfil["profissionais_distintos"].iloc[0]) > 1
print(f"1. O arquivo traz identificador real: "
      f"{int(perfil['profissionais_distintos'].iloc[0]):,} CNS distintos — "
      f"{'confere' if ok1 else 'ATENÇÃO'}")
falhas += [] if ok1 else ["identificador"]

# 2. a auto-detecção erra dos dois lados
ok2 = "PA_CNSMED" not in detectadas and len(detectadas) > 0
print(f"2. A auto-detecção ignora o PA_CNSMED e marca outras: {detectadas} — "
      f"{'confere' if ok2 else 'ATENÇÃO: mudou, reveja o texto acima'}")
falhas += [] if ok2 else ["auto-deteccao"]

# 3. encrypt não preserva agrupamento; hash preserva; redact colapsa
d_enc = guardado["encrypt"][0]["PA_CNSMED"].nunique()
d_hash = guardado["hash"][0]["PA_CNSMED"].nunique()
d_red = guardado["redact"][0]["PA_CNSMED"].nunique()
ok3 = d_enc > distintos_originais and d_hash == distintos_originais and d_red == 1
print(f"3. Distintos — original {distintos_originais:,} | encrypt {d_enc:,} | "
      f"hash {d_hash:,} | redact {d_red} — "
      f"{'confere' if ok3 else 'ATENÇÃO'}")
falhas += [] if ok3 else ["metodos"]

# 4. o encrypt é reversível com a chave
print(f"4. unmask_data devolve o original: "
      f"{'confere' if voltou_igual else 'ATENÇÃO'}")
falhas += [] if voltou_igual else ["reversao"]

# 5. o hash cai para dicionário
ok5 = recuperados.notna().mean() > 0.99
print(f"5. O hash é revertido por dicionário "
      f"({recuperados.notna().mean() * 100:.0f}%) — "
      f"{'confere (é pseudonimização)' if ok5 else 'ATENÇÃO'}")
falhas += [] if ok5 else ["dicionario"]

print()
if falhas:
    print("ATENÇÃO: falhou em", falhas,
          "— não use este notebook como referência antes de investigar.")
else:
    print("Tudo confere. As cinco afirmações do notebook valem nesta versão.")
"""),

    md("""
## Como adaptar

- **Outras colunas:** no SIA, `PA_CNPJCPF` também identifica. No SIH, olhe
  `CNS_PAC` e `CPF_AUT`. Liste as colunas do seu arquivo e decida uma a uma —
  não deixe a biblioteca decidir.
- **Outro estado ou período:** troque `UF`, `ANO` e `MES` no topo.
- **Guardar a chave:** `chave` é `bytes`. Grave em arquivo separado, fora da
  pasta que você vai compartilhar. Chave junto do dado é o mesmo que não ter
  mascarado.
- **Antes de repassar:** confira que a coluna original não sobrou em nenhuma
  outra parte do arquivo, e lembre que combinações de colunas comuns
  (município + data + procedimento raro) podem reidentificar mesmo sem o CNS.

---

*Exemplo do PySusNoCode — [kraemeracademy.net](https://kraemeracademy.net).
Dados públicos do DATASUS via PySUS.*
"""),
]

if __name__ == "__main__":
    print("resumo:", construir(DESTINO, CELULAS, timeout=900))

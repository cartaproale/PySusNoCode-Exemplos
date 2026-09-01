# Validação dos notebooks

Gerado automaticamente por `_ferramentas/validar_todos.py`. Cada notebook
é executado do início ao fim, baixando dados reais do DATASUS.

**Última validação:** 01/09/2026  
**Resultado:** 32 de 36 notebooks funcionando  
**Versão da PySUS usada no teste:** 2.10.6

| Notebook | Células | Gráficos | Tempo | Situação |
|---|---:|---:|---:|---|
| `AtencaoPrimaria/producao-da-ubs-no-sisab-equipe-por-equipe.ipynb` | 11 | 1 | 32s | ✅ funcionando |
| `AtencaoPrimaria/painel-da-aps-programas-do-municipio.ipynb` | 14 | 1 | 8s | ✅ funcionando |
| `AtencaoPrimaria/previne-brasil-indicadores-da-aps.ipynb` | 14 | 2 | 244s | ✅ funcionando |
| `AtencaoPrimaria/ubs-no-mapa-e-o-que-o-cadastro-esconde.ipynb` | 11 | 1 | 5s | ✅ funcionando |
| `CIHA/atendimentos-ciha.ipynb` | 9 | 1 | 7s | ✅ funcionando |
| `CIHA/o-que-o-ciha-acrescenta-ao-sih.ipynb` | 13 | 2 | 88s | ✅ funcionando |
| `CNES/leitos-por-municipio.ipynb` | 10 | 1 | 7s | ✅ funcionando |
| `CNES/profissionais-de-saude.ipynb` | 9 | 1 | 7s | ✅ funcionando |
| `CNES/rede-assistencial-e-leitos-por-habitante.ipynb` | 17 | 3 | 12s | ✅ funcionando |
| `IBGE/populacao-denominadores-e-piramides.ipynb` | 18 | 4 | 113s | ✅ funcionando |
| `PNI/cobertura-vacinal-e-anos-incompletos.ipynb` | 12 | 3 | 62s | ✅ funcionando |
| `PNI/cobertura-vacinal.ipynb` | 8 | 1 | 7s | ✅ funcionando |
| `SIA/alta-complexidade-oncologia-e-dialise.ipynb` | 15 | 3 | 16s | ✅ funcionando |
| `SIA/dialise-o-caminho-do-paciente-renal.ipynb` | 15 | 1 | 86s | ✅ funcionando |
| `SIA/producao-ambulatorial.ipynb` | 10 | 1 | 13s | ✅ funcionando |
| `SIH/internacoes-por-causa.ipynb` | 10 | 1 | 7s | ✅ funcionando |
| `SIH/internacoes-sensiveis-a-atencao-primaria.ipynb` | 18 | 3 | 39s | ✅ funcionando |
| `SIM/causas-de-obito.ipynb` | 9 | 1 | 9s | ✅ funcionando |
| `SIM/mortalidade-prematura-por-dcnt.ipynb` | 19 | 4 | 110s | ✅ funcionando |
| `SINAN/arboviroses-dengue-chikungunya-zika.ipynb` | 4 | 0 | 25s | ❌ célula 4: Error: TProtocolException: Invalid data |
| `SINAN/decodificar-os-codigos-do-sinan.ipynb` | 14 | 1 | 8s | ✅ funcionando |
| `SINAN/dengue-por-estado-e-mes.ipynb` | 5 | 0 | 17s | ❌ célula 5: OSError: Couldn't deserialize thrift: TProtocolException: Invalid data |
| `SINAN/serie-historica-tuberculose.ipynb` | 8 | 1 | 26s | ✅ funcionando |
| `SINASC/nascimentos-prematuridade-e-pre-natal.ipynb` | 22 | 4 | 33s | ✅ funcionando |
| `SINASC/perfil-dos-nascimentos.ipynb` | 9 | 1 | 9s | ✅ funcionando |
| `_comece-aqui/01-primeiros-passos.ipynb` | 10 | 0 | 6s | ✅ funcionando |
| `_comece-aqui/02-descobrir-dados-disponiveis.ipynb` | 6 | 0 | 14s | ✅ funcionando |
| `_comece-aqui/03-mapa-completo-das-bases.ipynb` | 8 | 0 | 59s | ✅ funcionando |
| `avancado/arquivos-grandes-e-sql.ipynb` | 3 | 0 | 17s | ❌ célula 3: OSError: Couldn't deserialize thrift: TProtocolException: Invalid data |
| `avancado/arquivos-grandes-pelas-ferramentas-da-pysus.ipynb` | 9 | 0 | 5s | ✅ funcionando |
| `avancado/compartilhar-dados-sem-expor-identificadores.ipynb` | 13 | 0 | 7s | ✅ funcionando |
| `cruzamentos/frio-e-coracao-replicando-um-estudo.ipynb` | 10 | 3 | 931s | ✅ funcionando |
| `cruzamentos/mortalidade-infantil-e-numeros-pequenos.ipynb` | 16 | 4 | 72s | ✅ funcionando |
| `cruzamentos/painel-do-municipio.ipynb` | 12 | 1 | 61s | ✅ funcionando |
| `indicadores/mortalidade-infantil.ipynb` | 11 | 1 | 17s | ✅ funcionando |
| `indicadores/populacao-e-taxas.ipynb` | 6 | 0 | 20s | ❌ célula 6: OSError: Couldn't deserialize thrift: invalid TType |

## Sentinelas: o que mudou desde a validação anterior

**`AtencaoPrimaria/ubs-no-mapa-e-o-que-o-cadastro-esconde.ipynb`**
- DERIVA: valor mudou sem o período mudar — olhe:
-   − 4. As suspeitas são poucas diante do total nacional — 3 de 47,920 unidades no país: confere
-   + 4. As suspeitas são poucas diante do total nacional — 3 de 47,930 unidades no país: confere

**`_comece-aqui/03-mapa-completo-das-bases.ipynb`**
- DERIVA: valor mudou sem o período mudar — olhe:
-   − 4. Funções da origem 'Saúde' que devolvem vazio: 9 de 11 — confere (é o estado conhecido da 2.10.6)
-   + 4. Funções da origem 'Saúde' com resposta: 2 de 11 — confere (o número varia com a saúde do portal)

> Deriva não reprova: o DATASUS retifica arquivos publicados, e
> isso é rotina. Mas valor que muda sem o período mudar merece
> um olhar antes do próximo commit.

> Um notebook só é listado como funcionando depois de executar
> todas as suas células sem erro, com dados reais.

# Validação dos notebooks

Gerado automaticamente por `_ferramentas/validar_todos.py`. Cada notebook
é executado do início ao fim, baixando dados reais do DATASUS.

**Última validação:** 01/09/2026  
**Resultado:** 36 de 36 notebooks funcionando  
**Versão da PySUS usada no teste:** 2.10.6

| Notebook | Células | Gráficos | Tempo | Situação |
|---|---:|---:|---:|---|
| `AtencaoPrimaria/producao-da-ubs-no-sisab-equipe-por-equipe.ipynb` | 11 | 1 | 34s | ✅ funcionando |
| `AtencaoPrimaria/painel-da-aps-programas-do-municipio.ipynb` | 14 | 1 | 8s | ✅ funcionando |
| `AtencaoPrimaria/previne-brasil-indicadores-da-aps.ipynb` | 14 | 2 | 30s | ✅ funcionando |
| `AtencaoPrimaria/ubs-no-mapa-e-o-que-o-cadastro-esconde.ipynb` | 11 | 1 | 5s | ✅ funcionando |
| `CIHA/atendimentos-ciha.ipynb` | 9 | 1 | 7s | ✅ funcionando |
| `CIHA/o-que-o-ciha-acrescenta-ao-sih.ipynb` | 13 | 2 | 89s | ✅ funcionando |
| `CNES/leitos-por-municipio.ipynb` | 10 | 1 | 7s | ✅ funcionando |
| `CNES/profissionais-de-saude.ipynb` | 9 | 1 | 8s | ✅ funcionando |
| `CNES/rede-assistencial-e-leitos-por-habitante.ipynb` | 17 | 3 | 12s | ✅ funcionando |
| `IBGE/populacao-denominadores-e-piramides.ipynb` | 18 | 4 | 113s | ✅ funcionando |
| `PNI/cobertura-vacinal-e-anos-incompletos.ipynb` | 12 | 3 | 61s | ✅ funcionando |
| `PNI/cobertura-vacinal.ipynb` | 8 | 1 | 7s | ✅ funcionando |
| `SIA/alta-complexidade-oncologia-e-dialise.ipynb` | 15 | 3 | 15s | ✅ funcionando |
| `SIA/dialise-o-caminho-do-paciente-renal.ipynb` | 15 | 1 | 86s | ✅ funcionando |
| `SIA/producao-ambulatorial.ipynb` | 10 | 1 | 13s | ✅ funcionando |
| `SIH/internacoes-por-causa.ipynb` | 10 | 1 | 7s | ✅ funcionando |
| `SIH/internacoes-sensiveis-a-atencao-primaria.ipynb` | 18 | 3 | 38s | ✅ funcionando |
| `SIM/causas-de-obito.ipynb` | 9 | 1 | 9s | ✅ funcionando |
| `SIM/mortalidade-prematura-por-dcnt.ipynb` | 19 | 4 | 109s | ✅ funcionando |
| `SINAN/arboviroses-dengue-chikungunya-zika.ipynb` | 16 | 4 | 13s | ✅ funcionando |
| `SINAN/decodificar-os-codigos-do-sinan.ipynb` | 14 | 1 | 8s | ✅ funcionando |
| `SINAN/dengue-por-estado-e-mes.ipynb` | 10 | 2 | 10s | ✅ funcionando |
| `SINAN/serie-historica-tuberculose.ipynb` | 8 | 1 | 26s | ✅ funcionando |
| `SINASC/nascimentos-prematuridade-e-pre-natal.ipynb` | 22 | 4 | 33s | ✅ funcionando |
| `SINASC/perfil-dos-nascimentos.ipynb` | 9 | 1 | 9s | ✅ funcionando |
| `_comece-aqui/01-primeiros-passos.ipynb` | 10 | 0 | 6s | ✅ funcionando |
| `_comece-aqui/02-descobrir-dados-disponiveis.ipynb` | 6 | 0 | 14s | ✅ funcionando |
| `_comece-aqui/03-mapa-completo-das-bases.ipynb` | 8 | 0 | 60s | ✅ funcionando |
| `avancado/arquivos-grandes-e-sql.ipynb` | 7 | 0 | 14s | ✅ funcionando |
| `avancado/arquivos-grandes-pelas-ferramentas-da-pysus.ipynb` | 9 | 0 | 5s | ✅ funcionando |
| `avancado/compartilhar-dados-sem-expor-identificadores.ipynb` | 13 | 0 | 7s | ✅ funcionando |
| `cruzamentos/frio-e-coracao-replicando-um-estudo.ipynb` | 10 | 3 | 930s | ✅ funcionando |
| `cruzamentos/mortalidade-infantil-e-numeros-pequenos.ipynb` | 16 | 4 | 71s | ✅ funcionando |
| `cruzamentos/painel-do-municipio.ipynb` | 12 | 1 | 62s | ✅ funcionando |
| `indicadores/mortalidade-infantil.ipynb` | 11 | 1 | 17s | ✅ funcionando |
| `indicadores/populacao-e-taxas.ipynb` | 9 | 1 | 11s | ✅ funcionando |

## Sentinelas: o que mudou desde a validação anterior

**`AtencaoPrimaria/producao-da-ubs-no-sisab-equipe-por-equipe.ipynb`**
- DERIVA: valor mudou sem o período mudar — olhe:
-   − 1. O SISAB devolveu o relatório — 307,820 linhas: confere
-   + 1. O SISAB devolveu o relatório — 307,840 linhas: confere

**`avancado/arquivos-grandes-e-sql.ipynb`**
- DERIVA: valor mudou sem o período mudar — olhe:
-   − 4. O SQL foi mais rápido que carregar tudo — leitura completa levou 0.3s: confere
-   + 4. O SQL foi mais rápido que carregar tudo — leitura completa levou 0.4s: confere

> Deriva não reprova: o DATASUS retifica arquivos publicados, e
> isso é rotina. Mas valor que muda sem o período mudar merece
> um olhar antes do próximo commit.

> Um notebook só é listado como funcionando depois de executar
> todas as suas células sem erro, com dados reais.

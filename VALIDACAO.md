# Validação dos notebooks

Gerado automaticamente por `_ferramentas/validar_todos.py`. Cada notebook
é executado do início ao fim, baixando dados reais do DATASUS.

**Última validação:** 27/08/2026  
**Resultado:** 3 de 3 notebooks funcionando  
**Versão da PySUS usada no teste:** 2.10.3

| Notebook | Células | Gráficos | Tempo | Situação |
|---|---:|---:|---:|---|
| `SIA/alta-complexidade-oncologia-e-dialise.ipynb` | 14 | 3 | 10s | ✅ funcionando |
| `SIA/dialise-o-caminho-do-paciente-renal.ipynb` | 13 | 1 | 77s | ✅ funcionando |
| `SIA/producao-ambulatorial.ipynb` | 9 | 1 | 12s | ✅ funcionando |

> Um notebook só é listado como funcionando depois de executar
> todas as suas células sem erro, com dados reais.

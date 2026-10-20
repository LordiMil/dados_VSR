# Fonte das páginas da calculadora

As páginas `site/o-custo-do-fixo.html` (calculadora) e `site/monte-carlo.html` (as 4.000 simulações) são geradas: um modelo HTML desta pasta é juntado aos dados de `processed/`. Para mudar texto, layout ou dados, edite o modelo ou rode de novo os scripts de dados, e monte as páginas outra vez.

| Arquivo | O que é |
|---|---|
| `calculadora.template.html` | Modelo da calculadora (layout, textos e código). `__DADOS__` recebe `processed/site_calculadora.json`; `__MC__` recebe o link da página de Monte Carlo. |
| `monte-carlo.template.html` | Modelo da página de Monte Carlo. `__DADOS__` recebe `processed/site_monte_carlo.json`; `__CALC__` recebe o link da calculadora. |
| `montar_paginas.py` | Junta modelo e dados e grava as duas páginas em `site/`. |

## Atualizar

1. Se o modelo financeiro mudou: `python scripts/11_dados_site.py <pasta PoliVSR-dados>` e `python scripts/12_dados_monte_carlo.py <pasta PoliVSR-dados>`.
2. `python site/fonte/montar_paginas.py`
3. No repositório do site (Next.js), copie as duas páginas para `public/calculadora/`. A aba "O Preço do Fixo" as abre com `?embed=1`, que esconde o cabeçalho e o rodapé próprios delas (o site já tem os seus).

Abertas sozinhas, sem `?embed=1`, as páginas mostram o próprio cabeçalho, que imita o do site.

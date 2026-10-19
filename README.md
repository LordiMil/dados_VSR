# PoliVSR – Pasta do projeto

Tudo o que o projeto PoliVSR (Hackathon Hitachi Energy 2026) usa fica nesta pasta. Organizada em 15/10/2026: os arquivos que estavam em Downloads e na Área de Trabalho foram trazidos para cá, e as cópias repetidas foram apagadas depois de conferidas byte a byte.

## Versão vigente
**v4c, de 14/10/2026.** Os números válidos são os da planilha-mestre atual, da pasta `processed/`, da calculadora em `site/` e do guia completo (`documentos/PoliVSR_Guia_Completo_do_Projeto.pdf`). Caso-base: arranjo 2:1 (um VSR no lugar de dois reatores fixos e de um dos dois vãos), preço do VSR pelos contratos públicos de 2025–26 (R$ 42,5 mi a 500 kV e 300 Mvar; R$ 8,6 mi a 230 kV e 40 Mvar), fase reserva do fixo de 500 kV por banco, comutador a vácuo, regime de leilão, 4.000 simulações.

**Não use números** de `_backup/`, de `documentos/antigos/` nem da seção "Histórico das versões", no fim deste arquivo: eles são de versões anteriores do modelo.

## Estrutura da pasta
- `PoliVSR_Base_de_Dados.xlsx` – planilha-mestre do modelo (comece pelas abas LEIA-ME e Parametros_Modelo).
- `FONTES_manifesto.csv` – catálogo dos dados brutos com URL, data de acesso, licença e SHA-256.
- `raw/` – dados brutos baixados sem alteração (ONS, ANEEL, BCB).
- `processed/` – séries e resultados gerados pelos scripts, incluindo `site_calculadora.json` (dados da calculadora do site).
- `scripts/` – pipeline em Python, do 00 ao 11 (ordem e uso nas seções abaixo).
- `site/o-custo-do-fixo.html` – a calculadora "O Custo do Fixo" no layout do site, pronta para abrir no navegador.
- `documentos/` – **guia completo do projeto para a equipe (`PoliVSR_Guia_Completo_do_Projeto.pdf`, comece por ele)**, guia do site e da pesquisa (`polivsr-escopo-site-e-pesquisa.md`), contexto do projeto e material de matemática financeira. Em `documentos/antigos/` ficam a Nota Metodológica e O Caminho dos Dados de 09/10 (valem para a base de dados, mas descrevem um motor da calculadora que foi substituído) e o placeholder de metodologia do site.
- `hackathon/` – material do case: enunciado (`Case Hitachi Energy.pdf`), divisão de tarefas, nivelamento técnico sobre VSR, análise de concorrência, vias de venda, a frente comercial (`frente-comercial/CLAUDE.md`), definições de agentes (`agentes/`) e o trabalho de concorrência feito com agentes (`analise-concorrencia/`).
- `_backup/` – versões anteriores da planilha-mestre (v1, v4a, v4b), só para registro.

## Base de dados do modelo

Acervo de dados com fonte primária para o modelo estocástico da calculadora "O Custo do Fixo".
Montado em 09/10/2026.

- `PoliVSR_Base_de_Dados.xlsx` – planilha-mestre (comece pelas abas LEIA-ME e Parametros_Modelo).
- `FONTES_manifesto.csv` – catálogo dos arquivos brutos: URL de origem, data de acesso, licença e SHA-256.
- `raw/ons`, `raw/aneel`, `raw/bcb` – arquivos baixados sem alteração (DESSEM: 499 arquivos diários concatenados, com a coluna `arquivo_fonte`).
- `processed/` – séries e estatísticas geradas pelos scripts (CSV separado por `;`, UTF-8).
- `scripts/` – rodar em ordem: 00 (manifesto), 01 (reatores, linhas, disponibilidade), 02 (carga e curva de pato), 03 (MMGD ANEEL), 04 (custos BPR e macro BCB), 05 (planilha-mestre: `python 05_planilha_mestre.py <esta pasta> <saida.xlsx>`).

Depois do 05: 06 (calibração antiga das manobras, mantida só por histórico), 07 (fontes reforçadas), 08 (literatura e volatilidade), 09 (modelo físico), 10 (modelo financeiro), 11 (dados do site).

Requisitos: Python 3 com pandas, numpy e openpyxl.
Fontes: ONS (cc-by), ANEEL (ODbL), Banco Central do Brasil (SGS).

## Histórico das versões (registro; não usar os números desta seção)

O que mudou em cada versão, na ordem em que aconteceu. Valores citados aqui podem ter sido substituídos por versões posteriores; os vigentes estão na seção "Versão vigente", no início.

### v2 — fontes reforçadas (09/10/2026)
- `scripts/07_fontes_reforcadas.py`: RAP por FT de reator (ANEEL SIGET), PVI por evento (Regras de Transmissão, Módulo 4 rev.2 — REN 1.137/2025), tabela de fatos com página/seção (`processed/fontes_reforcadas.csv`) e manifesto reconstruído (89 arquivos).
- WACC 8,00% agora citado no ato primário (Despacho ANEEL 675/2026, Anexo 1), não mais na imprensa.
- PAR/PEL 2025 (ONS) corrobora ~1 ciclo de manobra/dia por reator (p. 63–65).
- Modelo da calculadora: 33 posições de tap (Siemens/Amprion) e PVI mínima de 1,04 × PB somada a cada falha grave.
- Pendentes: custo de manutenção do disjuntor (% do preço) segue premissa; CAPEX do VSR depende da Hitachi Energy.

### v3 — pesquisa de literatura e volatilidade (13/10/2026)
- `scripts/08_pesquisa_volatilidade.py` (rodar depois do 05: `python 08_pesquisa_volatilidade.py <esta pasta> PoliVSR_Base_de_Dados.xlsx`): acrescenta à planilha-mestre as abas `Pesquisa_Literatura` (72 parâmetros com faixa, fonte, URL e confiança), `Pesquisa_Lacunas` (17 itens sem fonte aberta), `Volatilidade_Cenarios`, `Volatilidade_Mensal`, `Volatilidade_Anual` e `Interrupcoes_ENS`, e as linhas P57–P75 de `Parametros_Modelo`.
- Volatilidade (decisão P4): desvio-padrão dos desvios da carga líquida em torno do perfil típico (mês × dia útil/fim de semana × meia-hora), em % da demanda média; autocorrelação dos desvios em 30 min. Base: DESSEM (valores programados).
- Conferido: o BPR aberto não tem módulo de VSR (P5).
- A planilha v1 anterior foi guardada em `_backup/`.
- Cenários (13/10/2026): "Indústria" passou a se chamar "Polo eólico" (série = carga líquida do NE, dominada pela eólica). O Campo usa o fluxo horário verificado na interligação N–NE (ONS, Intercâmbios Entre Subsistemas, `raw/ons/ONS__intercambio_nacional_ho__*`, acrescentados ao manifesto); abas `Fluxo_NNE_Perfil` e `Fluxo_NNE_Mensal`, linhas P76–P78.
- `scripts/09_modelo_fisico.py` (rodar depois do 08): modelo físico-operacional, camada 1 do motor (decisão P1). Converte fluxo/carga em necessidade de compensação manobrável pela sobra de reativo da linha Qc·(1 − (P/SIL)²) e simula o reator fixo (degraus com histerese) e o VSR (taps e manobras residuais), nos arranjos 1:1 e 2:1. Saídas: `processed/modelo_fisico_*.csv`, `processed/modelo_fisico_camada1.json`, `processed/corredor_NNE_linhas.csv`; abas `Corredor_NNE` e `ModeloFisico_*`; linhas P79–P95.

### v4 — modelo financeiro, camada 2 (14/10/2026; caso-base atual é o da revisão v4c, no fim)
- `scripts/10_modelo_financeiro.py` (rodar depois do 09): motor financeiro-estocástico (Monte Carlo, 4.000 simulações por cenário; tornado com 1.500 por extremo e semente comum). Caso-base confirmado pelo grupo: arranjo 2:1, m = 50%, prêmio do VSR = 50% do preço dos dois reatores fixos (premissa, aguarda Hitachi), OLTC a vácuo, regime de leilão. Visões concessionária (12,11% a.a. real antes de impostos) e SIN (8,5% a.a.).
- Saídas: `processed/financeiro_{premissas,cartoes,cascata,nevoa,histograma,vpl_premio,operacionais,tornado}.csv` e `processed/modelo_financeiro_camada2.json`; abas `Fin_*` e linhas P96–P107 de `Parametros_Modelo`.
- Premissas sem fonte aberta estão marcadas na coluna de status de `Fin_Premissas`.
- Revisão de 14/10/2026 (v4b), após pesquisar por conta própria as perguntas da seção 6.8 do escopo (aba `Pesquisa_Hitachi`, `processed/pesquisa_perguntas_hitachi.csv`): o banco fixo de 500 kV passa a pagar a fase reserva (3+1R, EPE), que antes dava a franquia de 3 h sem entrar no custo; base = 1 fase compartilhada pelos 2 bancos. Prêmio do VSR com faixa pública de 15% a 65% (P108–P109); 50% segue como valor central. Novas variantes: fase reserva por banco ou nenhuma, reserva do VSR em pool de 1 para 10. A planilha anterior foi guardada em `_backup/PoliVSR_Base_de_Dados_v4a_2026-10-14.xlsx`.
- Revisão de 14/10/2026 (v4c), preço do VSR: o modelo deixa de usar o prêmio em % como entrada e passa a usar o preço do VSR em R$, ancorado em contratos públicos de 2025–26 (Energinet/GE Vernova, Litgrid) escalados por Mvar^0,6 × kV^0,5 e convertidos pelo euro do BCB de set/2026 (abas `Pesquisa_Precos_VSR` e `Fin_Precos_VSR`, `processed/pesquisa_precos_vsr.csv`, linhas P108–P111). O prêmio vira resultado. Estresse: nível de preço de 2023 (Energinet/Siemens e índice da Energy Community). A fase reserva do fixo de 500 kV passa a ser uma por banco, como no banco de referência 3+1R da EPE (compartilhada e nenhuma ficam como variantes). Planilha anterior em `_backup/PoliVSR_Base_de_Dados_v4b_2026-10-14.xlsx`.
- `scripts/11_dados_site.py` (rodar depois do 10): gera `processed/site_calculadora.json`, o contrato de dados da calculadora do site (seção 7 do escopo). Para cada cenário, visão e conjunto de premissas, traz VPL P10/P50/P90, chance de compensar e payback numa grade de preços do VSR (exatos, porque o VPL de cada simulação é afim no preço), além da névoa por ano, da cascata, dos operacionais e do dia típico do modelo físico.

# Glossário e ficha de números

## Glossário

**Sistema elétrico**
- **SIN (Sistema Interligado Nacional):** a rede elétrica que conecta quase todo o Brasil.
- **ONS (Operador Nacional do Sistema Elétrico):** opera o SIN e publica os planos de operação e ampliação (PAR/PEL).
- **EPE (Empresa de Pesquisa Energética):** planeja a expansão da transmissão.
- **ANEEL (Agência Nacional de Energia Elétrica):** regula o setor, faz os leilões e define a receita das transmissoras.
- **Transmissora:** empresa que constrói e opera linhas e subestações, recebendo uma receita anual regulada.
- **PAR/PEL:** plano do ONS com as ampliações e reforços da rede e a operação prevista para os próximos anos.
- **DESSEM:** modelo de programação diária do ONS; os dados de carga e geração dele são valores **programados**.
- **MMGD (micro e minigeração distribuída):** geração pequena, quase toda solar nos telhados, ligada à rede de distribuição.
- **Carga líquida:** o consumo menos a geração solar e eólica; é o que as usinas despacháveis e a rede de transmissão precisam atender.
- **Curva de pato:** o formato diário da carga líquida, que afunda ao meio-dia e sobe no fim da tarde.

**Física**
- **Potência ativa (MW, GW):** a energia que faz trabalho.
- **Potência reativa (Mvar):** energia que vai e volta entre os campos elétricos e magnéticos, sem fazer trabalho, mas que controla a tensão.
- **SIL (potência natural):** o carregamento em que uma linha gera e consome o mesmo reativo. Abaixo dele, sobra reativo e a tensão sobe.
- **Efeito Ferranti:** a tensão no fim de uma linha longa e pouco carregada fica maior que no início.
- **Carregamento capacitivo (Qc):** o reativo que a linha gera só por estar ligada.

**Equipamentos**
- **Reator de derivação (reator shunt):** equipamento que absorve reativo para baixar a tensão. **De barra:** ligado ao barramento da subestação. **De linha:** ligado diretamente a uma linha.
- **Reator fixo:** só tem dois estados, ligado ou desligado.
- **VSR (Variable Shunt Reactor, reator de derivação variável):** reator que ajusta a potência em pequenos passos, sem desligar.
- **Comutador sob carga (OLTC):** a peça que muda a posição (o tap) do VSR. Pode ser **a vácuo** (padrão em VSR, revisão a cada 300 mil operações) ou **a óleo** (revisão muito mais frequente).
- **Tap:** cada posição do comutador; o modelo usa 33.
- **Disjuntor:** a chave que liga e desliga um equipamento sob carga.
- **Manobra:** cada vez que o disjuntor liga ou desliga um reator.
- **Vão:** a "vaga" de um equipamento na subestação: disjuntor, chaves, transformadores de corrente, para-raios, proteção, estruturas e obra civil.
- **Fase reserva (banco 3+1R):** em 500 kV, o banco fixo tem três reatores monofásicos e um de reserva no pátio, que permite trocar uma fase em poucas horas.
- **STATCOM, SVC e compensador síncrono:** equipamentos de controle rápido de reativo (segundos), para contingências.

**Arranjo**
- **Compensação permanente:** a parte dos reatores que fica ligada quase sempre.
- **Compensação manobrável:** a parte que entra e sai ao longo do dia.
- **Arranjo 2:1:** um VSR com o dobro da potência substitui dois reatores fixos (um permanente e um manobrável). É o arranjo da calculadora.
- **Arranjo 1:1:** um VSR do tamanho de um reator fixo; não compensa no modelo.

**Regulação**
- **Leilão de transmissão:** a ANEEL licita obras novas; vence quem pede a menor receita anual.
- **RAP (Receita Anual Permitida):** a receita anual da transmissora por uma instalação.
- **Reforço:** obra autorizada numa instalação existente; a receita é calculada pela ANEEL item por item.
- **BPR (Banco de Preços de Referência):** a tabela de custos da ANEEL usada para calcular a receita dos reforços. Não tem VSR.
- **Parcela Variável:** o desconto na receita da transmissora quando um equipamento fica indisponível. Funciona como multa.
- **P&D ANEEL:** programa que obriga as transmissoras a aplicar 1% da receita operacional líquida em pesquisa e desenvolvimento.

**Finanças e estatística**
- **VPL (valor presente líquido):** a soma de todos os custos e economias ao longo dos anos, trazida para o dinheiro de hoje. Na calculadora, VPL positivo quer dizer que o VSR sai mais barato.
- **Taxa de desconto:** quanto o dinheiro futuro vale menos que o de hoje. A transmissora usa 12,11% ao ano (custo de capital regulatório da ANEEL, antes de impostos); o sistema usa a taxa social de 8,5% ao ano.
- **Payback:** quanto tempo até a economia pagar o investimento a mais. No caso-base, é imediato.
- **Preço de equilíbrio:** o maior preço do VSR em que ele ainda compensa.
- **Monte Carlo:** método que sorteia milhares de futuros possíveis e calcula o resultado em cada um.
- **P10, P50, P90:** os percentis. O P50 é a mediana; o P10, um caso pessimista; o P90, um otimista.
- **Névoa do risco:** o gráfico do custo acumulado de cada alternativa ao longo dos 30 anos, com a faixa entre P10 e P90.
- **Cascata:** o gráfico que mostra de onde vem o ganho do VSR, item por item.
- **Tornado:** o gráfico que mostra quais premissas mais mudam o resultado. A maior barra é o preço do VSR.
- **Caso-base:** o conjunto de premissas principal. **Variante:** uma premissa trocada para testar o resultado.

## Ficha de números

**O sistema**

| Número | O que é | Fonte |
|---|---|---|
| 1.084 reatores | Reatores de 230 kV ou mais em operação no SIN em 2026 (126 mil Mvar) | ONS, Dados Abertos, cadastro de equipamentos de controle de reativo |
| 550 reatores | O mesmo parque no fim de 2015 | ONS, idem |
| 0 | VSRs instalados no Brasil | ONS, idem, e análise de concorrentes do grupo |
| ~13.200 Mvar | Novos reatores de barra previstos até 2030 | ONS, PAR/PEL 2025, p. 64 |
| ~12.000 Mvar | Reatores de barra manobráveis de 500 kV previstos até 2030 | ONS, PAR/PEL 2025, p. 64 |
| até 40 VSRs | 12.000 Mvar ÷ 300 Mvar; um teto | Estimativa da equipe |
| ~140 → ~170 | Reatores ligados e desligados num dia útil de verão, 2026 → 2030 | ONS, PAR/PEL 2025, p. 64 |
| 36,8 → 77,3 GW | Carga líquida média do SIN em set/2026, às 12h e às 18h30 | ONS, DESSEM (programado) |
| 92,7% | Dias de 2025–26 em que o mínimo do SIN caiu entre 10h e 15h | ONS, DESSEM; tratamento do grupo |
| 53,9 GW | Geração distribuída (MMGD) em out/2026 | ANEEL, Dados Abertos |
| 2,46 × 0,25 | Falhas graves por 100 disjuntores por ano: de reator × de linha | CIGRÉ, Brochura Técnica 510 |
| 30/10/2026 · 8 lotes · R$ 8,9 bi | Leilão de Transmissão nº 4/2026 | ANEEL; imprensa (Cenário Energia, 22/09/2026) |

**O corredor Norte–Nordeste (cenário Campo)**

| Número | O que é | Fonte |
|---|---|---|
| 11 circuitos · 2.686 km | Linhas do corredor | ONS; tratamento do grupo |
| 3.937 Mvar | Reativo gerado pelas linhas | Cálculo do grupo |
| 10,4 GW | Potência natural (SIL) do corredor | Cálculo do grupo |
| 0,3 a 5,1 GW | Fluxo típico (percentis 5 e 95) | ONS, intercâmbio verificado |
| ~944 Mvar | Variação diária da sobra de reativo (6 degraus de 150 Mvar) | Modelo do grupo |
| ~2.990 Mvar | Sobra de reativo permanente | Modelo do grupo |
| 12 fixos → 6 VSRs | O corredor no arranjo 2:1 | Modelo do grupo |
| 11 × 0 | Manobras num dia típico (06/08/2025): fixo × VSR; o VSR fez 86 mudanças de tap | Modelo do grupo |

**A comparação a 500 kV (caso-base, R$ de set/2026)**

| Número | O que é | Fonte |
|---|---|---|
| R$ 42,5 mi (faixa R$ 37,1 a 50,1 mi) | Preço do VSR de 300 Mvar, só equipamento | Contratos Litgrid 2026 e Energinet/GE Vernova 2025, escalados pelo grupo |
| R$ 13,5 mi | Preço de um reator fixo de 150 Mvar, só equipamento | EPE NT-077/2021, corrigida pelo IPCA |
| R$ 13,0 mi | Um vão de reator | EPE NT-077/2021, corrigida pelo IPCA |
| R$ 4,5 mi | Uma fase reserva | EPE NT-077/2021 (banco 3+1R) |
| R$ 61,97 mi × R$ 55,55 mi | Dia da instalação: dois fixos × um VSR | Modelo do grupo |
| +58% | Quanto o VSR custa a mais que os dois reatores fixos | Modelo do grupo |
| R$ 51,1 mi | Preço de equilíbrio do VSR no Campo (+20% sobre o caso-base) | Modelo do grupo |

**Resultados do modelo (30 anos, 4.000 simulações)**

| Número | O que é |
|---|---|
| R$ 8,6 mi · 96% | Campo: ganho mediano e chance de compensar (transmissora) |
| R$ 6,6 a 11,0 mi | Campo: faixa P10–P90 |
| R$ 8,4 mi · 96% | Polo eólico (500 kV) |
| R$ 3,6 mi · 99% | Centro Urbano (230 kV) |
| R$ 9,1 · 9,0 · 3,8 mi | Campo, Polo eólico e Centro Urbano na visão do sistema |
| 592 por ano | Manobras evitadas por disjuntor no Campo (583 a 730 nos três cenários) |
| ~11 anos × 30+ anos | Até a troca do disjuntor: fixo × VSR, no Campo |
| 0,53 × 0,48 | Validação: manobras por dia por reator, modelo × medição |
| ±0,3 ponto percentual | Erro estatístico na chance de compensar |
| R$ 0,55 mi | Perdas do VSR em valor presente, no Campo, na visão do sistema |

Todos os resultados vêm do modelo PoliVSR v4c (14/10/2026), arquivos `processed/financeiro_*.csv` do repositório de dados.

## Fontes principais

- ONS. *PAR/PEL 2025*, ciclo 2026–2030. https://www.ons.org.br/AcervoDigitalDocumentosEPublicacoes/Revista%20PARPEL%202025-VF.pdf
- ONS, Dados Abertos: equipamentos de controle de reativo; balanço DESSEM; intercâmbio nacional. https://dados.ons.org.br/
- ANEEL, Dados Abertos: geração distribuída; Banco de Preços de Referência. https://dadosabertos.aneel.gov.br/
- ANEEL. Despacho nº 675/2026 (custo de capital regulatório).
- EPE. Nota Técnica EPE-DEE-NT-077/2021 (custos de reator e vão de 500 kV).
- Banco Central do Brasil, SGS (IPCA e câmbio).
- Ministério da Economia. Nota Técnica SEI nº 19911/2020 (taxa social de desconto).
- CIGRÉ. Bengtsson et al., *Variable shunt reactors*, A2-211, 2014; Brochura Técnica 510 (disjuntores).
- Hitachi Energy. VSR de 500 kV para energia eólica (08/10/2024); VSRs na Noruega (case Statnett e BKK).
- Repositório de dados do grupo: https://github.com/LordiMil/dados_VSR

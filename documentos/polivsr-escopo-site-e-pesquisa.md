# PoliVSR — Escopo do site e plano de pesquisa

> Documento-guia para a próxima etapa. Define **o que o site terá, onde, como o modelo funciona e quais dados/estatísticas precisamos buscar**. Contém as decisões de modelagem (seção 2) e o status da pesquisa (6.7); os dados em si ficam na planilha-mestre `PoliVSR_Base_de_Dados.xlsx`.
>
> Revisão 13/10/2026: corrigida a visão SIN (sem dupla contagem), regras de entrada e de exibição, casos-limite, modelo físico-operacional, custos e riscos do próprio VSR, decisões pendentes.
>
> Revisão 14/10/2026 (3), preço do VSR: o modelo passa a usar o preço do VSR em R$ ancorado em contratos públicos de 2025–26 (o prêmio vira resultado), a fase reserva do fixo de 500 kV segue a referência da EPE (uma por banco) e 4.4 ganhou o enquadramento para o hackathon (4.5).
>
> Revisão 14/10/2026 (2), após pesquisar por conta própria as perguntas à Hitachi Energy (6.8): o fixo de 500 kV passa a pagar a fase reserva (2.9), o prêmio ganha faixa pública de 15–65% e os resultados de 4.4 foram refeitos.
>
> Revisão 14/10/2026, modelo financeiro implementado (camada 2, seção 4.4): caso-base 2:1 confirmado pelo grupo (2.4); resultado da hipótese de 2.2; perguntas à Hitachi Energy atualizadas (6.8).
>
> Revisão 13/10/2026 (3), modelo físico implementado (3.5): arranjo 1:1 quase não reduz manobras; **proposta de caso-base 2:1** (2.4); narrativa do Campo corrigida (6.7).
>
> Revisão 13/10/2026 (2), após a pesquisa da seção 6: P2, P3 e P5 fechadas; perdas do reator passam a custo do VSR; novo contrafactual "fixo + manobra controlada" (2.8); risco de reserva do VSR trifásico; mínimo de regulação padrão de 50%; status da pesquisa e perguntas à Hitachi Energy (6.7 e 6.8). Os dados levantados estão na planilha-mestre, abas `Pesquisa_Literatura`, `Pesquisa_Lacunas` e `Volatilidade_*`.

---

## 1. Objetivo e público

- **Objetivo:** demonstrar, de forma auditável, que o VSR (Variable Shunt Reactor) é financeiramente superior ao reator shunt fixo no SIN, apesar do maior CAPEX — **ou mostrar, com a mesma transparência, em que condições não é**.
- **Público principal:** concessionárias de transmissão (engenharia + financeiro) e avaliadores do hackathon.
- **Posicionamento:** o VSR compete no controle quase estático do ciclo diário de carga leve, substituindo manobras repetidas de reatores fixos. Não compete com compensador síncrono ou SVC na necessidade dinâmica (ONS e EPE preferem compensador síncrono para isso; RT-ONS DPL 0091/2024).
- **Princípio de credibilidade:** todo número exibido deve ter fonte rastreável ou ser explicitamente rotulado como premissa/estimativa. Nada de variância zero ou "custo zero" que um engenheiro possa contestar. Os custos e riscos do próprio VSR entram no modelo com o mesmo rigor que os do reator fixo.

---

## 2. Decisões de modelagem ✅ fechadas em 13/10/2026 (pendências em 2.7)

### 2.1 Duas perspectivas de valor
Seletor com duas visões, porque os efeitos caem em bolsos diferentes. **Padrão: Concessionária.**

| Componente | Concessionária | SIN |
|---|---|---|
| Prêmio de CAPEX do VSR (equipamento) | Custo (neutralizado se a chave "prêmio reconhecido na RAP" estiver ligada) | **Sempre custo** (a chave RAP não se aplica) |
| CAPEX de vão evitado (caso 2:1) | Ganho | Ganho |
| Manutenção de disjuntor evitada (corretiva + preventiva) | Ganho | Ganho |
| Sobrevida / troca adiada do disjuntor | Ganho | Ganho |
| Parcela Variável evitada (falhas forçadas + desligamentos programados) | Ganho | **Não entra** — é transferência entre concessionária e usuários, não custo real |
| OPEX do OLTC (função do nº de operações de tap) | Custo | Custo |
| Manobras residuais do VSR (disjuntor abre abaixo do mínimo de regulação) | Custo | Custo |
| Falhas do próprio VSR/OLTC | Custo (via Parcela Variável) | Custo (via consequência real da indisponibilidade) |
| Energia não suprida evitada | Não entra | Ganho (custo do déficit, ver 2.3) |
| Perdas do próprio reator | Não entra (perdas não são custo da transmissora) | **Custo do VSR.** Na posição mínima o VSR ainda dissipa ~60% das perdas plenas (VSR 420 kV da HOPS: 145 kW a 80 Mvar contra 232 kW a 150 Mvar), enquanto o fixo desligado dissipa zero. Valorar por capitalização de perdas |
| Perdas na linha / perfil de tensão | Não entra | Argumento qualitativo, salvo se o modelo físico (seção 3) calcular o efeito |
| Reserva e indisponibilidade longa do VSR (ver 2.9) | Custo (CAPEX de reserva ou Parcela Variável de reparo longo) | Custo (consequência real da indisponibilidade) |
| Flexibilidade para renováveis | Argumento qualitativo | Argumento qualitativo (sem valor monetário) |

Regra geral: na visão SIN, tudo o que é transferência regulatória (Parcela Variável, receita da RAP) sai, e entra no lugar o **custo real** da indisponibilidade.

### 2.2 Remuneração do prêmio de CAPEX
- **Padrão: prêmio NÃO remunerado pela RAP.**
- Justificativa: é o caso real nos dois caminhos de contratação.
  - **Leilão:** a RAP é ofertada; o prêmio é custo de quem escolhe o VSR.
  - **Reforço autorizado (REN 905/2020):** a RAP é calculada prioritariamente pelo Banco de Preços de Referência ANEEL, que **não tem módulo de reator variável** (P5, conferido em 13/10/2026 nos três arquivos do BPR-Subestação do acervo; só existem reator monofásico, trifásico e de aterramento). O BPR aberto também não traz o preço do reator em si, só os acessórios; o custo de referência do reator fixo vem da EPE (EPE-DEE-NT-077/2021).
- **Chave opcional "prêmio reconhecido na RAP"** = cenário otimista, **válida só na visão Concessionária**. Se o prêmio for remunerado a uma taxa igual à taxa de desconto, seu VPL ≈ 0 e toda a economia vira ganho líquido.
- **Hipótese a testar (não afirmar antes do modelo):** o VSR é vantajoso mesmo sem o prêmio ser remunerado. O site só comunica isso se o modelo confirmar; caso contrário, mostra as condições em que vale.
- **Resultado (camada 2, 4.4):** confirmada **com condição**. No regime de leilão, sem o prêmio na RAP, o VSR vence nos três cenários desde que custe menos que o preço de equilíbrio: ~R$ 12,2 mi a 230 kV (Urbano, VSR de 40 Mvar) e ~R$ 51 mi a 500 kV (Campo e Polo eólico, VSR de 300 Mvar). Contratos públicos de 2025–26, escalados, dão R$ 37–50 mi a 500 kV (4.4). No **reforço com RAP pelo BPR**, a hipótese **não** se confirma para a concessionária: a RAP do vão que deixa de ser construído também deixa de ser recebida, então a economia do vão vai para a tarifa e o prêmio fica sem contrapartida. O SIN continua ganhando. O site deve dizer isso com essas palavras.

### 2.3 Convenções financeiras
| Item | Decisão |
|---|---|
| Tipo de análise | **Incremental** (VSR menos reator fixo) |
| Moeda | **Reais constantes**, base set/2026, corrigidos pelo IPCA |
| Taxa de desconto | **Concessionária:** WACC regulatório real antes de impostos (12,11%) aplicado a **fluxos antes de impostos**. Evita modelar IR/CSLL e incentivos SUDENE/SUDAM, que variam justamente nas regiões dos três cenários. **SIN (P3):** taxa social de desconto oficial de **8,5% a.a. real** (NT SEI 19911/2020/ME; Guia Geral de ACB), com 8% (EPE) como sensibilidade. Taxa mensal equivalente = (1 + taxa anual)^(1/12) − 1. Ajustável em slider avançado |
| Horizonte | **30 anos** (vida nominal do reator a óleo; também vida econômica dos estudos da EPE e prazo máximo de concessão). **Concessão existente (P2):** horizonte = prazo remanescente da concessão, com indenização do saldo não depreciado pelo VNR no fim (Lei 8.987/1995, art. 36; Lei 12.783/2013). Cenário alternativo sem indenização (proposta da CP ANEEL 43/2025 indeniza só reforços; contratos de leilão a partir de 2020 depreciam tudo no prazo). Marco visual aos 10 anos no fan chart |
| Valor residual | **Concessão nova:** zero para os reatores (mesma vida). **Concessão existente:** saldo não depreciado indenizado, pela depreciação regulatória do MCPSE (reator 2,78% a.a. ≈ 36 anos; disjuntor 3,03% a.a. ≈ 33 anos). Disjuntor trocado no meio da vida: valor residual pela vida restante, nas mesmas taxas |
| Granularidade | **Fluxos mensais** (payback em meses sem interpolação) |
| Transparência | Separar sempre **dado com fonte** de **premissa ajustável** (slider) |

### 2.4 Unidade de comparação (quantos fixos um VSR substitui)
- Base técnica: a literatura (CIGRÉ A2-211/2014; operador norueguês em 420 kV) indica **1 VSR no lugar de 2 reatores fixos**. Faixa de regulação típica **50–100%** da potência nominal, chegando a 80% de regulação (ex.: Amprion, 50–250 Mvar, 33 taps).
- **Caso 1:1:** 1 VSR vs. 1 reator manobrável de mesma potência máxima, cada um com seu vão. Ganho = redução de manobras; sem CAPEX de vão evitado.
- **Caso 2:1** (referência da literatura): 1 VSR substitui 2 fixos (o manobrável e uma fatia igual da compensação permanente, com m = 50%) → um vão completo (com disjuntor) evitado. No modelo físico, o VSR do 2:1 tem tamanho W/(1−m), em que W é a variação da necessidade que o banco manobrável cobre.
- **Resultado do modelo físico (3.5):** no **1:1** o VSR ainda manobra 1,0–1,7 vez/dia, contra 1,6–2,0 do fixo, porque a necessidade cai abaixo do mínimo de regulação todo dia; o ganho quase some. No **2:1**, o VSR manobra 0–0,12 vez/dia. **Decidido (confirmado pelo grupo em 14/10/2026): o caso-base é o 2:1**, e o 1:1 fica como sensibilidade que mostra o risco de subdimensionar o VSR. No Campo, o 2:1 é viável para mínimos de regulação de até 76%.
- **Definição do prêmio (evita contar o vão duas vezes):** prêmio = preço do VSR − preço do(s) reator(es) fixo(s) equivalente(s), **só equipamento**. Vãos, disjuntores e obra civil ficam em linha separada ("CAPEX de vão evitado").
- **Entrada do site (decidido em 14/10/2026):** o usuário informa o **preço do VSR em R$**, não o prêmio em %. O padrão vem de contratos públicos de 2025–26 (4.4) e o prêmio é calculado. Assim o resultado não herda a defasagem do preço de referência do fixo.
- **Manobras residuais do VSR:** o VSR não vai a 0 Mvar. Quando a rede pede compensação abaixo do mínimo de regulação, o disjuntor ainda abre. Essas manobras **entram no modelo** (por isso a linha do VSR tem névoa estreita, não nula).
- **Risco crítico do caso 1:1:** se, todo dia, a necessidade cair abaixo do mínimo de regulação (ex.: no pico noturno), o VSR também é desligado diariamente e a economia de manobras pode zerar. O **mínimo de regulação** é, portanto, parâmetro crítico: entra como slider avançado, no tornado e é reportado explicitamente pelo modelo.
- **Valor padrão do mínimo de regulação: 50%** da potência nominal. Fontes técnicas a 400–500 kV dão 45–60% (CIGRÉ A2-211/2014; especificação Energinet "≥ 50%"; HOPS 53%); mínimos de 20% aparecem só em material comercial. Faixa do slider: 20–60%.
- **N nacional vem dos dados:** a proporção de subestações com ≥ 2 reatores de barra manobráveis na mesma tensão (cadastro ONS) define o peso de cada caso nos números do dashboard.

### 2.5 Regras de entrada e de exibição
- **Sliders vs. Monte Carlo:**
  - **Prêmio de CAPEX:** determinístico (o valor do slider). Sua incerteza é tratada pelo prêmio de equilíbrio e pelo gráfico VPL × prêmio, não pela simulação.
  - **Demais sliders de custo/operação:** definem o **valor central** da distribuição correspondente; o Monte Carlo varia em torno dele.
- **Percentis rotulados como otimista/pessimista, nunca crus:**
  - VPL, prêmio de equilíbrio, P(VPL > 0): otimista = P90, pessimista = P10.
  - Payback: otimista = P10, pessimista = P90.
- **Tornado:** variáveis estocásticas variam entre P10 e P90; sliders variam numa faixa definida e documentada no PDF.

### 2.6 Casos-limite das métricas
| Situação | Tratamento |
|---|---|
| Prêmio líquido ≤ 0 (possível no caso 2:1) | Payback "imediato"; TIR "não aplicável"; cartão informa que o VSR é mais barato desde o início |
| Payback além do horizonte | Exibir "não se paga em 30 anos"; percentis calculados com valores censurados e exibir a **% de simulações sem payback** |
| TIR com múltiplas raízes (fluxos que mudam de sinal mais de uma vez, ex.: troca de disjuntor) | Exibir VPL como métrica principal; TIR só quando única |

### 2.7 Decisões pendentes
| # | Pendência | Opções | Impacto |
|---|---|---|---|
| P1 | **Arquitetura do motor estocástico** — ⏸️ adiada para a integração com o site (polivsr.vercel.app). A calculadora é desenvolvida primeiro aqui, em Python. **Restrição de projeto já valendo:** o modelo Python é construído em duas camadas separadas — (1) física/estocástica → taxas operacionais e caminhos de eventos; (2) financeira → custos, desconto e métricas — com saídas exportáveis em JSON | Na integração: (a) tabelas pré-calculadas; (b) motor em JavaScript; (c) API Python; (d) híbrida recomendada: Python gera taxas e caminhos de eventos (números aleatórios comuns), JavaScript aplica a camada financeira | Define o formato do contrato de dados (seção 7), a latência dos sliders e a hospedagem |
| P2 | **Horizonte em concessão existente** — ✅ decidida em 13/10/2026 | Opção avançada "prazo remanescente da concessão" com indenização do saldo não depreciado pelo VNR (depreciação MCPSE: reator 2,78% a.a., disjuntor 3,03% a.a.); cenário alternativo sem indenização (ver 2.3) | Muda VPL e payback para reforços em concessões antigas |
| P3 | **Taxa de desconto na visão SIN** — ✅ decidida em 13/10/2026 | **Taxa social de 8,5% a.a. real** (NT SEI 19911/2020/ME); 8% (EPE) e 12,11% como sensibilidade | Muda o VPL da visão SIN; como 8,5% e 8% são próximas, o resultado deve ser pouco sensível |
| P4 | **Definição física de "volatilidade da carga renovável"** — ✅ decidida em 13/10/2026 | **Volatilidade = desvio-padrão dos desvios da carga líquida em relação ao perfil típico do cenário, em % da carga média.** Resolução de 30 min onde houver (DESSEM), horária no restante. O formato do dia (vale do meio-dia, pico noturno) é determinístico e vem do cenário e da MMGD; o slider controla só as flutuações em torno dele. Desvios modelados como processo **autocorrelacionado** (autocorrelação estimada dos dados), não como ruído independente. Escala de 30 min–1 h justificada pelo ritmo das decisões de manobra. Valor padrão por cenário calibrado com dados ONS da região. Dica no site: "variação típica em torno do perfil diário" | Define como o slider entra no modelo físico (3.2) |
| P5 | **Confirmação no BPR** da ausência de módulo de VSR — ✅ confirmada em 13/10/2026 | Nenhum módulo de reator variável nos três arquivos do BPR-Subestação; só reator monofásico, trifásico e de aterramento | Sustenta a decisão 2.2 |

### 2.8 Contrafactual: fixo convencional ou fixo com manobra controlada
- A objeção mais provável da banca: "por que não manter o reator fixo e só instalar manobra controlada (point-on-wave)?". A PSEG (EUA) adotou exatamente isso, junto com a troca por VSR, após aumento de falhas de reatores (PJM TEAC, 07/07/2026). A própria Hitachi Energy vende manobra controlada (Switchsync).
- **Decisão:** a calculadora compara o VSR com dois contrafactuais, num seletor avançado:
  - **Fixo convencional** (padrão).
  - **Fixo + manobra controlada:** elimina as reignições, que respondem pela taxa de falha ~10× maior do disjuntor de reator, mas **não reduz os ciclos mecânicos** nem o desgaste por número de operações. Soma o custo do controlador ao CAPEX do fixo.
- Dados necessários: efeito da manobra controlada na taxa de falha e no desgaste; custo do controlador (ver 6.2 e 6.4).
- **Pesquisa (14/10/2026, 6.8 H7):** a manobra controlada já é prática corrente em disjuntor de reator (a BPA exige em disjuntores novos de reator; a Transgrid especifica nos vãos de reator). A 500 kV o disjuntor já tem polos independentes, então o custo é só o controlador e a fiação; a 230 kV pode exigir disjuntor novo. Como ela não reduz o número de manobras, o efeito no modelo fica restrito à taxa de falha do disjuntor, que pesa menos de R$ 0,5 mi no tornado: o contrafactual 2.8 quase não muda o veredito.

### 2.9 Reserva e indisponibilidade longa do VSR
- Em 500 kV, o padrão brasileiro de reator de barra é banco monofásico com fase reserva, como (3+1R) × 66,6 Mvar. O VSR costuma ser trifásico (Hitachi Energy até 550 kV / 300 Mvar): uma falha tira a unidade inteira de serviço, e a reserva custa uma unidade completa.
- Falha no OLTC tende a ser reparada no local (dias a semanas); falha interna do reator leva meses, e o prazo de unidade nova está em 80–210 semanas.
- **Decisão:** parâmetro avançado "estratégia de reserva do VSR" com três opções: (a) sem reserva (padrão), com cauda de indisponibilidade longa entrando na Parcela Variável (concessionária) ou na energia não suprida (SIN); (b) pool de reserva de 1 para 10, como a BPA faz com reatores de 500 kV; (c) reserva de 1 para 3.
- **Correção de 14/10/2026: o fixo de 500 kV paga a sua fase reserva.** A franquia de 3 h na falha do fixo vem da fase reserva, então o custo dela entra no lado do fixo. Padrão (revisto no mesmo dia): uma fase de W/3 por banco, como no banco de referência 3+1R da EPE (R$ 9,0 mi para os dois bancos de 500 kV). Variantes: uma compartilhada pelos dois bancos (R$ 4,5 mi) ou nenhuma (sem custo e sem franquia, com reparo longo). A 230 kV o fixo é trifásico, sem reserva, e nada muda.

---

## 3. Modelo físico-operacional (o coração da calculadora)

### 3.1 Cadeia causal
1. **Perfil de carga** horário do cenário (curva de carga líquida + volatilidade renovável).
2. **Necessidade de absorção de reativo** em cada intervalo: a sobra de reativo de uma linha é Qc·(1 − (P/SIL)²) (carregamento capacitivo menos o que a linha consome ao transportar P). A compensação permanente cobre a necessidade com a linha carregada; a manobrável cobre a variação W entre o p95 e o p5 do carregamento (ver 3.5).
3. **Resposta do reator fixo:** liga quando a necessidade/tensão passa do limiar superior e desliga abaixo do limiar inferior (histerese), conforme os critérios de operação do ONS → **nº de manobras do disjuntor**. No contrafactual com manobra controlada (2.8), as manobras são as mesmas, mas sem reignições.
4. **Resposta do VSR:** acompanha a necessidade por taps dentro da faixa [mínimo de regulação, 100%]; abaixo do mínimo, sai pelo disjuntor → **nº de operações de tap** + **manobras residuais**.
5. **Desgaste:** manobras → consumo de vida de contatos e mecanismo do disjuntor; operações de tap → manutenção do OLTC.
6. **Falhas e indisponibilidade:** taxas de falha (disjuntor, OLTC, reator) → horas indisponíveis (forçadas e programadas), incluindo a cauda longa do VSR sem reserva (2.9) → Parcela Variável (concessionária) ou consequência real (SIN). Taxas centrais: disjuntor de manobra de reator 2,46 falhas maiores/100 disjuntores-ano; disjuntor de linha (regime do VSR) 0,25 (CIGRÉ TB 510).
7. **Custos → fluxos mensais → métricas financeiras.**

### 3.2 Mapeamento dos sliders para o modelo
| Slider | Variável que altera | Efeito esperado |
|---|---|---|
| Extensão do trecho crítico (km) | Geração capacitiva → potência do reator necessária | Escala o porte do equipamento e a amplitude da necessidade de Mvar |
| Volatilidade da carga renovável (%) | Amplitude e frequência de variação da necessidade de Mvar (definição em P4) | Nº de cruzamentos de limiar (manobras do fixo) e de operações de tap |
| Custo médio por manutenção de disjuntor (R$) | Valor central da distribuição de custo de intervenção | OPEX do fixo |
| Prêmio de CAPEX do VSR — equipamento (R$) | Investimento incremental (determinístico) | VPL, payback, TIR |
| Mínimo de regulação do VSR (avançado; padrão 50%) | Limite inferior da faixa do VSR | Manobras residuais; viabilidade do caso 1:1 |
| Contrafactual (avançado) | Fixo convencional ou fixo + manobra controlada (2.8) | Taxa de falha e CAPEX do fixo |
| Estratégia de reserva do VSR (avançado) | Sem reserva ou reserva compartilhada (2.9) | Cauda de indisponibilidade do VSR ou CAPEX de reserva |
| N de fixos substituídos (avançado) | Vãos evitados; porte do VSR | CAPEX de vão evitado |

### 3.3 Parâmetros por cenário (a preencher na pesquisa)
| Parâmetro | Centro Urbano | Campo (interligação N–NE) | Polo eólico (antigo "Indústria") |
|---|---|---|---|
| Nível de tensão | | 500 kV (8 circuitos) e 230 kV (3) | |
| Tipo de reator (barra / linha) | Barra, manobrável | Barra, manobrável | Barra, manobrável |
| Potência típica do reator | | 150 Mvar (mediana 500 kV, cadastro ONS) | |
| Extensão padrão do trecho | | Corredor N–NE: 2.686 km em 11 circuitos; Qc = 3.937 Mvar; SIL = 10,4 GW | |
| Série-motriz do modelo físico (3.5) | \|carga líquida do NE sem eólica\| (DESSEM) | \|fluxo verificado N–NE\| (ONS) | \|carga líquida do NE\| (DESSEM) |
| Carregamento p5 / p95 | 2,0 / 15,7 GW | 0,29 / 5,09 GW (2,8% / 49% do SIL) | 0,37 / 9,56 GW |
| Degraus manobráveis no caso-base (N) | 1 (sem SIL de referência) | 6 (W = 944 Mvar ÷ 150 Mvar) | 1 (sem SIL de referência) |
| Volatilidade padrão (P4) | 5,2% (NE: demanda − MMGD − FV; DESSEM jun/2025–set/2026); φ30 = 0,92 | 11,7% da carga média do N (fluxo horário **verificado** N–NE em módulo, jan/2025–out/2026); φ1h = 0,89, τ ≈ 8 h | 17,2% (NE: carga líquida, dominada pela eólica; DESSEM); φ30 = 0,98, τ ≈ 23 h |
| Região (para N nacional e energia não suprida) | NE | N | NE |
| Faixa padrão de mínimo de regulação | 50% (20–60%) | 50% (20–60%) | 50% (20–60%) |

### 3.4 Validação ✅ (13/10/2026; aba `ModeloFisico_Validacao`)
- Nenhum parâmetro foi ajustado para reproduzir as referências. A histerese (eta = 0,3 do degrau) é premissa declarada, com sensibilidade de 0,1 a 0,75.
- **Reator em manobra diária:** o PAR/PEL 2025 fala em ~140 reatores de barra chaveados por dia útil de verão, ~1 ciclo (2 operações) cada. O modelo dá, por disjuntor manobrável, 2,0/dia no Centro Urbano, 1,6/dia no Campo e 1,6/dia no Polo eólico (média do período), dentro da faixa observada. No Centro Urbano o resultado vale para qualquer eta ≤ 0,5, porque é a forma do dia que manda.
- **Média da frota:** 140 × 2 ÷ 530 manobráveis ≈ 0,53 op/dia, igual ao único dado de campo encontrado (0,48 op/dia, reator de barra 400 kV). Os cenários da calculadora representam um reator em manobra diária; a média da frota é a base para os números nacionais do dashboard (D3/D4).

### 3.5 Implementação e resultados (13/10/2026; `scripts/09_modelo_fisico.py`)
- **Variável de necessidade:** r(t) = (u_hi² − u²)/(u_hi² − u_lo²), com u = |série-motriz| e u_lo/u_hi = p5/p95. r = 0 com a linha no p95 do carregamento (só a compensação permanente) e r = 1 no p5 (todo o banco manobrável ligado). Sem corte: r < 0 é carregamento extremo.
- **Fixo:** N degraus de W/N; cada um entra no meio do degrau + histerese/2 e sai no meio − histerese/2.
- **VSR 1:1:** tamanho W, faixa [m, 1]; sai pelo disjuntor quando r < m/2. **VSR 2:1:** tamanho W/(1−m), segue r em [0, 1] por taps (33 posições) e só sai quando r < −m/(2(1−m)).
- **Volatilidade (slider):** x_k = perfil + k·(x − perfil), com o dimensionamento fixo em k = 1.
- **Caso-base (2:1, m = 50%, k = 1, eta = 0,3):**

| Cenário | Manobras/dia por disjuntor do fixo (= evitadas por VSR) | Manobras residuais/dia do VSR | Taps/dia do VSR (piso) | Desajuste fixo → VSR (fração de W) |
|---|---|---|---|---|
| Centro Urbano (N = 1) | 2,00 | 0,00 | 60 | 0,17 → 0,01 |
| Campo (N = 6) | 1,62 | 0,01 | 59 | 0,05 → 0,02 |
| Polo eólico (N = 1) | 1,60 | 0,12 | 70 | 0,19 → 0,02 |

- **Sensibilidades** (grade completa em `ModeloFisico_Taxas`): a volatilidade de 0,5× a 2× leva o Campo de 0,9 a 1,8 e o Polo eólico de 1,3 a 2,0 manobras/dia (N = 1); o Centro Urbano fica em 2,0, dominado pela forma do dia. No 2:1, mínimo de regulação baixo aumenta as manobras residuais do VSR (m = 20%: 0,35/dia no Campo e 0,64/dia no Polo eólico).
- **Consequência para o OPEX do VSR:** ~60–70 operações de tap/dia (piso, pela resolução de 30 min a 1 h). Com OLTC a vácuo (300 mil operações) isso dá manutenção a cada ~12–14 anos; com OLTC a óleo na linha (20–50 mil operações), a cada 1–2 anos. O tipo de comutador muda o OPEX do VSR e vira pergunta prioritária à Hitachi Energy (6.8).
- **Limitações:** um barramento representativo por cenário, sem fluxo de potência da rede; taps/dia subestimados pela resolução; N do Centro Urbano e do Polo eólico sem SIL de referência; a compensação permanente precisa comportar a fatia que o VSR do 2:1 substitui (verificado só no Campo).
- **Saídas para o site (camada 1 da P1):** `processed/modelo_fisico_camada1.json` com taxas, mensal, validação e o dia típico de cada cenário (necessidade, degraus do fixo e nível do VSR), pronto para o gráfico "dimmer" (C1).

---

## 4. Métricas que o modelo vai calcular

### 4.1 Financeiras
| Métrica | Pergunta que responde | Onde aparece |
|---|---|---|
| **VPL incremental** | Quanto valor o VSR cria a mais que o fixo? | Cartão principal, cascata, histograma |
| **Payback descontado (meses)** | Em quanto tempo o prêmio se paga? | Cartão, intersecção no fan chart |
| **TIR do prêmio de CAPEX** | Quanto rende o dinheiro extra investido no VSR, comparado à taxa de desconto? | Detalhe / PDF (regras em 2.6) |
| **Custo anual equivalente** | Quanto cada alternativa custa por ano (mesma unidade da RAP)? | Detalhe / PDF |
| **Prêmio de CAPEX de equilíbrio** | Até quanto a mais o VSR pode custar e ainda compensar? | Cartão, gráfico VPL × prêmio |
| **P(VPL > 0)** | Qual a probabilidade de o VSR vencer? | Cartão, histograma |
| **% de simulações sem payback** | Com que frequência o prêmio não se paga no horizonte? | Cartão de payback |
| **Percentis P10 / P50 / P90** | Otimista, mediano e pessimista (rótulos conforme 2.5) | Cartões e fan chart |

### 4.2 Operacionais
- Manobras de disjuntor do fixo por ano.
- Operações de tap do VSR por ano.
- Manobras residuais do VSR por ano.
- Manobras evitadas por ano (fixo − residuais do VSR).
- Sobrevida adicionada ao disjuntor (anos até troca de contatos / fim de vida mecânica).
- Horas de indisponibilidade (forçadas e programadas) de cada alternativa.

### 4.3 Motor estocástico
- Simulação de Monte Carlo sobre as variáveis incertas: taxas de falha (disjuntor, OLTC, reator), custo de manutenção, duração de reparo (disjuntor e VSR), nº de manobras e de operações de tap (via volatilidade).
- O prêmio de CAPEX **não** é variável estocástica (regra 2.5).
- Saídas: distribuição de VPL e de payback, bandas de percentis por ano (fan chart), sensibilidade por variável (tornado).

### 4.4 Resultados da camada 2 (14/10/2026, terceira rodada; `scripts/10_modelo_financeiro.py`)
**Caso-base:**
- Arranjo 2:1: 1 VSR de W/(1−m) no lugar do reator manobrável W e de uma fatia W da compensação permanente, cada fixo com seu vão. W é 20 Mvar a 230 kV (Urbano) e 150 Mvar a 500 kV (Campo e Polo eólico), então o VSR tem 40 Mvar e 300 Mvar.
- **Preço do VSR em R$, ancorado em contratos públicos de 2025–26** (Energinet/GE Vernova e Litgrid), escalado por Mvar^0,6 × kV^0,5 e convertido pelo euro do BCB de set/2026 (R$ 5,92). O prêmio sobre os fixos é resultado, não entrada.
- A 500 kV, cada banco fixo paga sua fase reserva (3+1R, referência da EPE), que é o que lhe dá a franquia de 3 h (2.9).
- Mínimo de regulação m = 50%; OLTC a vácuo; VSR sem reserva; regime de leilão, com o prêmio fora da RAP.
- 30 anos e 4.000 simulações por cenário.
- Saídas na planilha-mestre: abas `Fin_*`, `Pesquisa_Hitachi`, `Pesquisa_Precos_VSR` e linhas P96–P111 de `Parametros_Modelo`; contrato de dados em `processed/financeiro_*.csv` e `processed/modelo_financeiro_camada2.json`.

**Preço do VSR usado (aba `Fin_Precos_VSR`):**

| Nível | 500 kV, 300 Mvar | 230 kV, 40 Mvar | De onde vem |
|---|---|---|---|
| Base | R$ 42,5 mi (+58% sobre os dois fixos) | R$ 8,6 mi (+48%) | Média dos contratos de 2025–26 |
| Faixa | R$ 37,1–50,1 mi | R$ 6,8–10,1 mi | Mesmos contratos, com o fator de tensão de 0,3 a 1,0 |
| Estresse | R$ 80,3–86,1 mi | R$ 16,2–17,4 mi | Contrato da Energinet de 2023 e índice da Energy Community |

**Cartões:**

| Cenário | VPL P50, concessionária (P10 a P90) | P(VPL > 0) | Payback P50 | Preço de equilíbrio do VSR P50 (P10–P90) | VPL P50, SIN |
|---|---|---|---|---|---|
| Urbano (230 kV) | R$ 3,63 mi (3,09 a 4,27) | 99% | imediato | R$ 12,2 mi (11,6–12,8), prêmio de 110% | R$ 3,80 mi |
| Campo (500 kV) | R$ 8,60 mi (6,58 a 10,99) | 96% | imediato (4% sem payback) | R$ 51,1 mi (48,9–53,4), prêmio de 89% | R$ 9,06 mi |
| Polo eólico (500 kV) | R$ 8,40 mi (6,52 a 10,72) | 96% | imediato (4% sem payback) | R$ 50,8 mi (48,9–53,1), prêmio de 89% | R$ 8,95 mi |

O payback é imediato porque, já no dia da compra, o VSR custa menos que os dois fixos com seus vãos e fases reserva (caso-limite de 2.6).

**Cascata (Campo, concessionária, VP médio em R$ mi):**

| Componente | Valor |
|---|---|
| Vão evitado | +13,00 |
| Fases reserva do fixo evitadas | +8,99 |
| Prêmio do VSR | −15,57 |
| **Saldo de CAPEX** | **+6,42** |
| Troca do disjuntor adiada | +1,32 |
| O&M do vão evitado | +0,99 |
| Falhas do disjuntor | +0,17 |
| Revisão geral | +0,06 |
| Manutenção preventiva | +0,06 |
| Manutenção do OLTC | −0,42 |
| Falhas do reator/VSR | −0,31 |
| Parcela Variável | −0,06 |
| **Saldo operacional** | **+1,81** |
| **VPL médio** | **+8,23** |

Na visão SIN, as perdas do VSR na posição mínima custam −0,10 (Urbano), −0,55 (Campo) e −0,44 (Polo eólico). A energia não suprida evitada é desprezível (< R$ 0,01 mi).

**Variações (Campo, concessionária):**

| Variação | VSR | VPL P50 | P(VPL > 0) |
|---|---|---|---|
| **Base** | R$ 42,5 mi | **R$ 8,6 mi** | **96%** |
| Preço do VSR na faixa baixa | R$ 37,1 mi | R$ 14,2 mi | 98% |
| Preço do VSR na faixa alta | R$ 50,1 mi | R$ 1,0 mi | 74% |
| Estresse: preço no nível de 2023 | R$ 80–86 mi | −R$ 29,5 a −35,4 mi | 0% |
| VSR e fixo na mesma base de preço (prêmio de −20%) | R$ 21,6 mi | R$ 29,8 mi | 100% |
| Prêmio de 50% (premissa anterior) | R$ 40,5 mi | R$ 10,7 mi | 97% |
| Fase reserva compartilhada pelos dois bancos | R$ 42,5 mi | R$ 4,1 mi | 93% |
| Fixo sem fase reserva (sem custo e sem franquia) | R$ 42,5 mi | −R$ 0,4 mi | 40% |
| Reforço com RAP pelo BPR (REN 905/2020) | R$ 42,5 mi | −R$ 4,4 mi | 5% |
| Prêmio reconhecido na RAP | R$ 42,5 mi | R$ 24,2 mi | 99% |
| OLTC a óleo (teste de estresse) | R$ 42,5 mi | R$ 1,1 mi | 61% |
| Reserva do VSR em pool de 1 para 10 | R$ 42,5 mi | R$ 4,4 mi | 94% |
| Reserva do VSR de 1 para 3 | R$ 42,5 mi | −R$ 5,6 mi | 3% |

No Urbano, a faixa de preço dá de R$ 2,1 a 5,5 mi; o estresse de 2023, de −R$ 4,1 a −5,3 mi; o reforço, −R$ 2,0 mi.

**Tornado do Campo (concessionária), por amplitude do VPL médio:**

| Variável | Amplitude (R$ mi) |
|---|---|
| Preço do VSR, faixa dos contratos de 2025–26 | 13,5 |
| Fase reserva do fixo, de nenhuma a uma por banco | 9,1 |
| Tipo de OLTC, vácuo ou óleo | 8,0 |
| Mínimo de regulação, de 60% a 20% | 5,9 |
| Vida mecânica real | 2,9 |
| Taxa de desconto | 1,3 |
| O&M do vão | 1,3 |
| Volatilidade | 1,1 |

As taxas de falha do disjuntor ficam abaixo de R$ 0,5 mi.

**O que o modelo mostrou:**
1. **No 2:1, a conta principal é de CAPEX:** o VSR evita um vão e as fases reserva dos dois bancos fixos, o que cobre o prêmio com folga a preços de 2025–26. O desgaste evitado no fixo, menos os custos próprios do VSR, soma ~R$ 1,8 mi de margem. "Menos manobras" é real, mas não é o que carrega o caso.
2. **O VSR compensa enquanto custar até ~R$ 51 mi (500 kV) ou ~R$ 12 mi (230 kV).** Os contratos de 2025–26 caem abaixo disso em toda a faixa; o nível de 2023 fica bem acima.
3. **O regime de contratação e a reserva mudam o sinal:** reforço com RAP pelo BPR, fixo sem fase reserva e reserva do VSR de 1 para 3 deixam o VPL negativo para a concessionária.
4. **O OLTC tem de ser a vácuo,** que é o padrão de mercado (6.8, H3). O VSR do 2:1 faz 32–38 mil operações de tap por ano; com vácuo, a manutenção sai a cada ~8–9 anos.
5. **Operacionais:** o fixo manobra 583–730 vezes por ano e o VSR, 0–42; o disjuntor do fixo chega à revisão geral em ~9–11 anos e à troca em ~9–12; o do VSR só faz a revisão por tempo, aos 20 anos.

**Premissas sem fonte firme (status "premissa" em `Fin_Premissas`):**
- Escala do preço do VSR para 500 kV e 300 Mvar (Mvar^0,6 × kV^β, β de 0,3 a 1,0): os contratos são de 330–400 kV e 140 Mvar.
- Preço do VSR de 230 kV e 40 Mvar: extrapolação grande; confiança baixa.
- Preço do reator fixo: EPE de 2021 corrigido pelo IPCA; reatores e transformadores encareceram mais que a inflação desde então, o que, se corrigido, favoreceria o VSR.
- Preço do reator de 230 kV (regra de escala a partir do 500 kV da EPE).
- O&M do vão de 0,5–2%/ano; custos de reparo; valor da energia das perdas (R$ 150/250/400 por MWh); fração de corte de carga por falha; fator de vida mecânica.

### 4.5 Enquadramento para o hackathon: favorecer o VSR sem mentir
**Regra:** onde a evidência deixa escolha, usamos a premissa defensável mais favorável ao VSR, dizemos que é uma escolha, e o site mostra o cenário contrário ao lado. Nada de número sem fonte, nada de esconder o estresse.

**Escolhas pró-VSR adotadas e por que se sustentam:**

| Escolha | Por que é defensável | O contrário, que o site também mostra |
|---|---|---|
| Preço do VSR pelos contratos de 2025–26 | São os mais recentes e disputados (2 propostas por lote na Energinet; concorrência pública na Litgrid) | Nível de 2023 (um contrato negociado, no pico da crise de suprimento): o VSR não compensa |
| Fase reserva por banco no fixo de 500 kV | É o banco de referência da EPE (3+1R) | Reserva compartilhada (VPL de R$ 4,1 mi) e sem reserva (−R$ 0,4 mi) |
| Arranjo 2:1 | É a aplicação de referência da literatura e dos fabricantes | 1:1, em que o ganho quase some (3.5) |
| OLTC a vácuo | É o padrão de mercado para VSR | OLTC a óleo como teste de estresse |
| Regime de leilão | O vão evitado fica com quem escolhe o VSR | Reforço com RAP pelo BPR: negativo para a transmissora |
| VSR sem reserva própria | Reserva trifásica dedicada é rara; o VSR serve como reserva flexível | Reserva de 1 para 3: negativo |

**Frase-guia para o site (verdadeira com as fontes atuais):** "Com os preços pagos por operadores europeus em 2025–26, um VSR que substitui dois reatores fixos e um vão de 500 kV economiza ~R$ 8,6 mi em valor presente, com 96% de chance de compensar. Ele compensa enquanto custar até ~R$ 51 mi."

**O que não dizer:**
- "O VSR é mais barato que um reator fixo": ele é mais barato que **dois** fixos com seus vãos.
- "O VSR sempre vale a pena": não vale no reforço com RAP pelo BPR, nem a preços de 2023.
- "O preço do VSR é X": é estimativa a partir de contratos europeus, até a Hitachi Energy cotar.

**Argumentos qualitativos a favor do VSR, sem valor monetário no modelo:** elimina os degraus de tensão das manobras; regula continuamente, o que ajuda a integrar renováveis; serve de reserva flexível em várias posições da rede; ocupa menos área que dois bancos com dois vãos.

---

## 5. Estrutura do site

### 5.1 Página inicial — Dashboard Nacional ("a dor")

| # | Componente | O que mostra | Observações |
|---|---|---|---|
| D1 | **Curva de pato do SIN** | Carga líquida horária típica, com faixa de variação (p5–p95) | Dados reais ONS; destacar a amplitude diária e o vale do meio-dia |
| D2 | **Crescimento da MMGD** | Evolução da potência instalada de geração distribuída | Explica por que a curva afunda cada ano mais |
| D3 | **Projeção de manobras** | Reatores chaveados/manobras por dia, hoje → horizonte do PAR/PEL | Substitui ou acompanha o contador "em tempo real" |
| D4 | **Contadores estimados "hoje"** | Manobras de reatores fixos no dia e reatores ligados agora | Rotular como **estimativa**; calculado a partir do padrão horário de manobras (fonte em 6.1); método documentado no PDF |
| D5 | **Parque instalado** | Quantidade de reatores (total e manobráveis), por região/tensão | Mapa ou barras por região |
| D6 | **Chamada para a calculadora** | Botão "Calcule o custo do fixo" | — |

### 5.2 Página da Calculadora "O Custo do Fixo"

#### Entradas (topo / lateral)
- **Seletor de cenário:** Centro Urbano · Campo (interligação N–NE) · Polo eólico (cada um carrega a tabela de parâmetros de 3.3).
  - **Polo eólico** substitui o antigo "Indústria" (decisão de 13/10/2026). Não existe dado público de carga por subestação para montar uma curva industrial sem inventá-la. Além disso, flutuações rápidas de carga industrial (segundos a minutos) são território de SVC/STATCOM, não de VSR, cujo comutador leva minutos de ponta a ponta. A série do NE, dominada pela eólica, varia em horas a dias, que é a faixa em que o VSR atua.
  - **Campo** passa a ser guiado pelo **fluxo na interligação**, não pela carga do Norte: o efeito Ferranti numa linha longa depende de quanto ela está carregada (com transferência baixa, sobra reativo capacitivo e o reator precisa entrar).
- **Seletor de perspectiva:** Concessionária · SIN.
- **Sliders:**
  - Extensão do trecho crítico (km)
  - Volatilidade da carga renovável (%)
  - Custo médio por manutenção de disjuntor (R$)
  - Preço do VSR — equipamento (R$); padrão = contratos públicos de 2025–26 escalados; o site mostra ao lado o prêmio resultante em %
- **Avançado (recolhível):**
  - Taxa de desconto (padrão 12,11% real antes de impostos na visão Concessionária; 8,5% real na visão SIN)
  - Chave "prêmio reconhecido na RAP" (padrão: desligada; visível só na visão Concessionária)
  - N de reatores fixos substituídos (padrão 2, caso-base 2:1; opção 1)
  - Mínimo de regulação do VSR (%; padrão 50%, faixa 20–60%)
  - Contrafactual: fixo convencional · fixo + manobra controlada (2.8)
  - Estratégia de reserva do VSR: sem reserva · reserva compartilhada (2.9)
  - Duração média de reparo
  - Prazo remanescente da concessão, com ou sem indenização (P2)

#### Primeira dobra — o veredito
Quatro cartões, cada um com **mediana + faixa otimista–pessimista** (rótulos conforme 2.5):
1. VPL incremental
2. Payback descontado (meses), com % de simulações sem payback
3. Probabilidade de o VSR compensar
4. Preço de equilíbrio do VSR (R$), com o prêmio correspondente em %

Os cartões seguem os casos-limite de 2.6. Abaixo deles: link **"Baixar Metodologia Estatística (PDF)"**.

#### Gráfico principal — a "Névoa de Risco" (fan chart)
- Eixo X: anos (0 → horizonte). Eixo Y: custo acumulado descontado (R$).
- **Reator fixo:** linha mediana envolta em bandas P10–P90 (e P25–P75) que se alargam com o tempo.
- **VSR:** começa acima (prêmio de CAPEX), cresce pouco (OPEX do OLTC, manobras residuais, falhas do próprio VSR), com banda **estreita mas existente**.
- **Intersecção** das linhas marcada como payback, com a incerteza do cruzamento visível.

#### Abaixo da dobra — a prova
| # | Gráfico | O que mostra | Por que importa |
|---|---|---|---|
| C1 | **"Dimmer" em 24 h** | Perfil diário do cenário: degraus liga/desliga do fixo (cada degrau = 1 manobra) vs. curva dos taps do VSR, com contagem de manobras do fixo, operações de tap e manobras residuais no dia | Explica o mecanismo em segundos, sem esconder o custo do VSR |
| C2 | **Cascata do VPL** | Componentes da tabela 2.1 conforme a perspectiva selecionada, chegando ao VPL | Mostra de onde vem o valor; linguagem do financeiro |
| C3 | **Desgaste do disjuntor** | Operações acumuladas vs. limite de vida mecânica (fixo e manobras residuais do VSR), ano de cruzamento de cada alternativa | Materializa a "sobrevida" |
| C4 | **VPL × preço do VSR** | Reta do VPL em função do preço do VSR, cruzando o zero; faixa dos contratos públicos de 2025–26 sombreada e posição do slider marcada | Responde "até quanto compensa pagar" |
| C5 | **Tornado de sensibilidade** | Variação do VPL por premissa (inclui mínimo de regulação) | Transparência; expõe premissas frágeis |
| C6 | **Histograma do VPL** | Distribuição simulada com área positiva destacada | Visualiza P(VPL > 0) |
| C7 | **Indicadores operacionais** | Métricas de 4.2 | Números concretos para engenharia |

**Prioridade se for preciso cortar:** cartões + fan chart + C1 (dimmer) + C2 (cascata).

### 5.3 Nota Técnica (PDF)
Seções previstas:
1. A dor do setor (efeito Ferranti, curva de pato, manobras)
2. Funcionamento do reator fixo vs. VSR
3. Perspectivas de valor e convenções financeiras (inclui tratamento das transferências na visão SIN)
4. Modelo físico-operacional (cadeia causal, critérios de manobra, mapeamento dos sliders)
5. Equações de desgaste e de falha (disjuntor, OLTC, reator)
6. Custos e riscos do próprio VSR (OLTC, perdas na posição mínima, reserva trifásica, reparo longo)
6a. Comparação com o reator fixo com manobra controlada; posicionamento frente a compensador síncrono e SVC
7. Modelo financeiro (VPL, payback, TIR, custo anual equivalente, equilíbrio, casos-limite)
8. Motor estocástico (distribuições, nº de iterações, percentis, rótulos)
9. Definição dos três cenários
10. Validação contra dados observados
11. Método dos contadores estimados do dashboard
12. Premissas, lacunas e limitações
13. Referências

---

## 6. O que vamos buscar (plano de pesquisa)

Para cada item: **o que precisamos** → **para qual componente** → **onde procurar**.

### 6.1 Perfil de carga e operação
| Dado | Alimenta | Onde procurar |
|---|---|---|
| Curva de carga líquida horária do SIN e por região | D1, cenários, C1 | ONS dados abertos |
| Evolução da MMGD | D2 | ANEEL |
| Número de reatores chaveados/manobras por dia e projeção | D3, D4, validação (3.4) | ONS PAR/PEL |
| **Padrão horário das manobras** (em que horas os reatores entram e saem) | D4 | ONS PAR/PEL; DESSEM; instruções de operação |
| Cadastro de reatores (tensão, potência, região, manobrável ou não) | D5, D4 | ONS cadastro de reativos; CIGRÉ |
| Nº de reatores de barra manobráveis por subestação e tensão (proporção com ≥ 2) | Peso dos casos 1:1 e 2:1 (2.4) | ONS cadastro de reativos (acervo existente) |
| **Critérios de manobra de reatores** (limiares, histerese, prioridade entre recursos) | Modelo físico (3.1, passos 3–4) | ONS Instruções de Operação / Manual de Procedimentos da Operação |
| **Faixas de tensão admissíveis** por nível de tensão | Modelo físico | ONS Procedimentos de Rede |
| Frequência de horas em que a necessidade fica abaixo do mínimo de regulação do VSR | Manobras residuais; risco do caso 1:1 | Curva de carga ONS + perfil dos cenários |
| Perfis típicos dos cenários urbano, campo e polo eólico (variação horária, volatilidade) | Cenários (3.3), C1 | ONS por subsistema; EPE estudos de controle de tensão N/NE |
| **Fluxo horário medido na interligação N–NE** (intercâmbio entre subsistemas, 2025–2026) — ✅ obtido em 13/10/2026 | Série do cenário Campo | ONS dados abertos, "Intercâmbios Entre Subsistemas" (`intercambio_nacional_ho`), em raw/ons |
| **Capacidade natural (SIL) e número de circuitos do corredor N–NE** | Converter fluxo em necessidade de reator no Campo | ONS cadastro de linhas (acervo); EPE |
| Geração reativa das linhas por km e por nível de tensão | Slider de extensão | ONS cadastro de linhas; literatura |

### 6.2 Disjuntor (lado do reator fixo)
| Dado | Alimenta | Onde procurar |
|---|---|---|
| Custo de manutenção preventiva e corretiva (substituir a premissa atual) | Cascata, fan chart | ANEEL; artigos de concessionárias; CIGRÉ A3 |
| Duração dos desligamentos programados para manutenção | Parcela Variável programada | ONS; ANEEL; artigos de manutenção |
| Número de operações até troca de contatos / fim de vida mecânica em manobra de reator | C3, sobrevida | IEC 62271-100/110; CIGRÉ A3 (chaveamento de reatores) |
| Taxa de falha de disjuntor em manobra indutiva frequente | Motor estocástico, névoa | CIGRÉ A3 (pesquisas internacionais de confiabilidade); IEEE |
| Duração típica de reparo/indisponibilidade após falha | Parcela Variável | ONS; artigos de manutenção |
| Custo de substituição completa do disjuntor | Sobrevida, valor residual | ANEEL BPR |
| Risco e custo de falha catastrófica (explosão, dano ao vão) | Cauda da distribuição | CIGRÉ; IEEE |
| **Efeito da manobra controlada** na taxa de falha e no desgaste do disjuntor de reator | Contrafactual 2.8 | CIGRÉ WG A3.07/13.07; Hitachi Energy (Switchsync); IEEE |

### 6.3 VSR, OLTC e reator
| Dado | Alimenta | Onde procurar |
|---|---|---|
| Prêmio de CAPEX do VSR sobre o reator fixo equivalente (só equipamento) | Slider, equilíbrio | Hitachi Energy; literatura; editais/leilões |
| **Nº de operações do OLTC até manutenção** e custo por intervenção | OPEX do VSR (função das operações de tap) | CIGRÉ A2; fabricantes de OLTC |
| Taxa de falha do OLTC (confiabilidade) | Banda do VSR | CIGRÉ A2 (pesquisas de falhas de transformadores/OLTC) |
| **Taxa de falha do reator** (fixo vs. VSR, falhas internas) | Risco dos dois lados | CIGRÉ A2 (pesquisas de confiabilidade de reatores/transformadores) |
| **Duração de reparo de falha do VSR/OLTC** (incl. falha interna do reator) | Parcela Variável do VSR; cauda de risco | CIGRÉ A2; fabricantes; relatos de concessionárias |
| Faixa de regulação disponível por nível de tensão (230/500 kV) e mínimo de regulação | Caso 2:1, manobras residuais, slider avançado | Hitachi Energy; CIGRÉ A2-211/2014 e A2-207/2016 |
| Casos reais de operação com redução de manobras | Argumento qualitativo, PDF | ABB/Hitachi Energy; Siemens; operadores europeus |
| **Estratégia de reserva para VSR trifásico** (custo, prazo de reparo e de reposição) | Risco 2.9 | Hitachi Energy; concessionárias com VSR (Statnett, Energinet) |

### 6.4 Infraestrutura evitada
| Dado | Alimenta | Onde procurar |
|---|---|---|
| Custo de um vão de reator completo (disjuntor, seccionadoras, TCs, proteção, obra civil) | Cascata (vãos evitados) | ANEEL BPR |
| Custo de reator shunt fixo por Mvar e nível de tensão | Base do prêmio | ANEEL BPR; leilões de transmissão |
| **Custo do controlador de manobra controlada** | CAPEX do contrafactual 2.8 | Hitachi Energy; orçamentos de concessionárias |

### 6.5 Regulatório e financeiro
| Dado | Alimenta | Onde procurar |
|---|---|---|
| Regras da Parcela Variável para reator e disjuntor do vão (falhas forçadas e desligamentos programados) | Cascata, risco | ANEEL — Regras dos Serviços de Transmissão |
| RAP típica de função de transmissão de reator | Parcela Variável | ANEEL SIGET |
| Valoração de reforço no BPR e confirmação da ausência de módulo de VSR | Decisão 2.2, pendência P5 | ANEEL (REN 905/2020, BPR) |
| **Prazo remanescente das concessões e regras de reversão/indenização** | Pendência P2 | ANEEL (contratos de concessão; regras de indenização) |
| WACC regulatório vigente | Taxa de desconto | ANEEL |
| Índices de correção (IPCA, câmbio) | Reais constantes | BCB |
| Vida útil regulatória de reator e disjuntor | Horizonte, valor residual | ANEEL (manual de controle patrimonial); literatura |

### 6.6 Visão SIN (somente para a perspectiva sistêmica)
| Dado | Alimenta | Onde procurar |
|---|---|---|
| Custo da energia não suprida | Visão SIN | ANEEL; EPE; ONS |
| Interrupções de carga associadas a falhas de equipamentos de manobra | Visão SIN | ONS dados abertos |
| Perdas do reator em carga parcial vs. plena | Visão SIN | Fabricantes; IEEE |
| Taxa de desconto social (se adotada em P3) | Visão SIN | EPE; literatura de avaliação de projetos |
| Valor de flexibilidade para integração de renováveis | Argumento qualitativo | EPE; literatura |

### 6.7 Status da pesquisa (13/10/2026)
Registro completo na planilha-mestre (v3): abas `Pesquisa_Literatura` (72 parâmetros com faixa, fonte, URL e confiança), `Pesquisa_Lacunas` (17 itens), `Volatilidade_*` e `Interrupcoes_ENS`; os valores centrais entram em `Parametros_Modelo` (P57–P75). Script: `scripts/08_pesquisa_volatilidade.py`.

| Bloco | Encontrado | Ainda falta |
|---|---|---|
| Disjuntor (6.2) | Taxa de falha maior de disjuntor de reator 2,46/100 disj.-ano (1,98–3,02; tanque vivo 6,79; linha 0,25), ~10× as demais aplicações; classes M1/M2; revisão geral por contagem (GL314: 3.000 ciclos ou 20 anos); reparo de 20–48 h com cauda até ~100 h | Custo de manutenção no Brasil; taxa de falha por nº de operações; fração de explosões; desligamento programado |
| VSR, OLTC e reator (6.3) | Manutenção do OLTC a óleo (20–100 mil op.) e a vácuo (300 mil op.); mínimo de regulação 45–60%; preços de VSR em contratos públicos (Energinet 2023 e 2025, Litgrid 2026, HOPS 2019; aba `Pesquisa_Precos_VSR`); projeto PSEG US$ 21,9 mi; perdas na posição mínima ~62% das plenas | Cotação de VSR de 500 kV no Brasil; taxa de falha de VSR; custo de intervenção no OLTC; taps/dia em campo; faixa a 230/500 kV |
| Infraestrutura (6.4) | Reator 500 kV 66,6 Mvar R$ 4,415 mi (EPE, mar/2021); CRB 500 kV R$ 9,589 mi (EPE); CRB 230 kV R$ 2,2–2,4 mi (BPR) | Preço do reator 230 kV; custo do controlador de manobra controlada |
| Regulatório (6.5) | BPR sem VSR (P5); depreciação MCPSE; prazo e indenização (P2); CAOM 2% do VNR | Texto primário do MCPSE; regra escrita da RAP do reforço |
| Visão SIN (6.6) | Custo do déficit R$ 8.291,25/MWh (2026); taxa social 8,5% (P3); 2.187 perturbações com Rede Básica em 2016–2025, mediana 11,5 MWh e p90 140 MWh por evento | Interrupções atribuídas a disjuntor |
| Volatilidade (P4) | Urbano 5,2%, Campo 11,7%, Polo eólico 17,2%; desvios persistentes (φ30 = 0,92–0,98 no DESSEM; φ1h = 0,89 no fluxo N–NE) | — |
| Interligação N–NE (Campo) | Fluxo horário verificado jan/2025–out/2026 (abas `Fluxo_NNE_*`): NE→N em 78% das horas; transferência mais leve às **18 h** (1,9 GW em média), mais pesada às 8 h (3,6 GW). Corredor: 11 circuitos, SIL 10,4 GW, Qc 3.937 Mvar (aba `Corredor_NNE`) | — |

Observações da calibração:
- O DESSEM é **programado**, não verificado. No fluxo N–NE de 2026, o desvio-padrão medido ficou só 0,6% acima do programado (P78 = 1,01): na escala horária, o programado não subestima a flutuação de forma relevante. Flutuações abaixo de 1 h (nuvens) continuam fora da base.
- A volatilidade do antigo cenário **Indústria** (NE, carga líquida) é dominada pela eólica regional. Decidido em 13/10/2026: o cenário passa a se chamar **Polo eólico** e mantém a série.
- O saldo do Nordeste (geração − demanda, DESSEM) mostra o NE exportando em 96% do tempo, com exportação **mais alta de madrugada** (~7,3 GW, vento noturno) e **mais baixa por volta das 17 h** (cerca de 5 GW). **Confirmado pelo fluxo verificado N–NE:** a interligação fica mais leve às 17–18 h (quando a solar do NE cai), não de madrugada (~2,8 GW). O "Ferranti violento nas madrugadas" do briefing não se sustenta e deve sair do texto do site.
- **Correção (modelo físico, 3.5):** as manobras do Campo não vêm das inversões de sentido. Com |P| ≈ 0 a sobra de reativo é máxima e os reatores simplesmente ficam ligados. Elas vêm das oscilações diárias do fluxo em torno de ~3,6 GW (35% do SIL): o reator entra quando a transferência alivia, no fim da tarde, e sai quando ela sobe, de manhã. As manobras acontecem o ano todo e são mais frequentes de julho a outubro (1,7–2,2/dia por disjuntor), quando o fluxo oscila todo dia nessa faixa; de fevereiro a maio a média é ~1,4/dia.
- A carga horária do ONS de 2015 a 2026 **não** mostra aumento das flutuações em torno do perfil; o efeito da MMGD aparece na **forma** do dia (curva de pato, amplitude), que entra de forma determinística pelo cenário.

### 6.8 Perguntas à Hitachi Energy (mentores do hackathon)
Em 14/10/2026 as sete perguntas foram pesquisadas em fontes abertas. As respostas, com faixa, confiança e fontes, estão na aba `Pesquisa_Hitachi` da planilha-mestre (H1 a H7).

| # | Pergunta | O que a pesquisa aberta respondeu | Confiança | O que ainda perguntar à Hitachi |
|---|---|---|---|---|
| 1 | Preço do VSR e prêmio sobre os reatores fixos que ele substitui | Contratos públicos: Litgrid 2026 (330 kV, 140 Mvar) € 3,5 mi; Energinet 2025 (GE Vernova, 400 kV, 70–140 Mvar) € 4,3 mi; Energinet 2023 (Siemens Energy) € 7,7 mi. Escalados para 500 kV e 150–300 Mvar: **R$ 37–50 mi** (2025–26) ou R$ 80–86 mi no nível de 2023 | média (preços reais; escala é premissa) | **Preço de um VSR de 500 kV e 150–300 Mvar entregue no Brasil, e de um banco fixo de 3 × 50 Mvar + R no mesmo pedido.** O equilíbrio do modelo é ~R$ 51 mi a 500 kV e ~R$ 12,2 mi a 230 kV |
| 2 | Mínimo de regulação a 230 e 500 kV | 40–55% com OLTC convencional; 20% com projeto avançado e mais caro. Primeiro VSR de 500 kV da Hitachi em 2024; portfólio declarado até 550 kV e 300 Mvar trifásico | média | O mínimo viável num VSR de 300 Mvar a 500 kV, e se seria trifásico ou banco monofásico |
| 3 | Tipo de OLTC e manutenção | Vácuo é o padrão de mercado (MR VACUTAP com versão para VSR, manutenção a cada 300 mil operações); a Hitachi tem OLTC a vácuo próprio | média | Confirmar o modelo de OLTC e a posição (neutro) a 500 kV |
| 4 | Operações de tap por dia em campo | Sem dado público; a Statnett descreve controle lento e manutenção "limitada" | sem dado | Dados de campo da Noruega (operações por dia ou por ano) |
| 5 | Taxa de falha da frota e tempo de reparo | Sem dado público; proxy de ~0,3%/ano (CIGRÉ TB 939) e 12–31% das falhas no comutador (TB 642) | baixa | Taxa de falha da frota de VSR e tempos de reparo |
| 6 | Reserva de VSR trifásico | Reserva trifásica é rara, por custo; a BPA mantém um pool de reatores de 500 kV para 30 instalados; a Statnett usa o VSR como reserva flexível. No Brasil, banco 3+1R | média | Se oferecem VSR monofásico a 500 kV (banco com fase reserva) |
| 7 | Custo e efeito da manobra controlada (Switchsync) | Sem preço público. A 500 kV o custo é só controlador e fiação; evita reacendimentos, mas não reduz manobras. Prática corrente (BPA, Transgrid, PSEG) | média (efeito) | Preço do Switchsync por disjuntor |

**O que a pesquisa mudou no modelo:** o fixo de 500 kV passou a pagar a fase reserva (2.9), o preço do VSR passou a ser entrada em R$ ancorada nos contratos públicos (P108–P111, abas `Pesquisa_Precos_VSR` e `Fin_Precos_VSR`), o OLTC a óleo virou teste de estresse e a reserva do VSR ganhou a opção de pool de 1 para 10.

---

## 7. Contrato de dados modelo → site (o que o motor precisa entregar)

Formato e granularidade dependem da pendência **P1** (arquitetura). Conteúdo mínimo:

- **Cartões:** VPL, payback, P(VPL > 0) e preço de equilíbrio do VSR (com o prêmio em %), com P10/P50/P90, rótulos otimista/pessimista (2.5) e % de simulações sem payback.
- **Sinalizadores de casos-limite (2.6):** payback imediato, TIR não aplicável, sem payback no horizonte.
- **Fan chart:** por mês ou ano, percentis do custo acumulado descontado de cada alternativa.
- **Dimmer:** série de 24 h por cenário com estado do fixo (degraus), posição de tap do VSR e contagens (manobras do fixo, operações de tap, manobras residuais).
- **Cascata:** valor presente de cada componente da tabela 2.1, por perspectiva.
- **Desgaste:** operações acumuladas por ano para cada alternativa e limite de vida.
- **VPL × preço do VSR:** curva para uma faixa de preços, com a faixa dos contratos públicos.
- **Tornado:** impacto no VPL de cada variável (baixo/alto).
- **Histograma:** amostras ou bins do VPL simulado.
- **Operacionais:** métricas de 4.2.

---

## 8. Próximos passos

1. ~~Fechar as decisões do item 2~~ ✅ — P2, P3, P4 e P5 decididas; P1 adiada para a integração (com restrição de duas camadas).
2. ~~Executar a pesquisa da seção 6~~ ✅ (13/10/2026; ver 6.7) — falta enviar as perguntas de 6.8 à Hitachi Energy e cobrir as lacunas de `Pesquisa_Lacunas`.
3. Preencher a tabela de parâmetros por cenário (3.3) — volatilidade dos três cenários, região e mínimo de regulação feitos; faltam só tensão, tipo e potência do reator e extensão padrão (e o SIL do corredor N–NE para o Campo).
4. ~~Construir o modelo físico-operacional e validá-lo~~ ✅ (3.4 e 3.5). Caso-base 2:1 confirmado em 14/10/2026 (2.4).
5. ~~Definir as distribuições de probabilidade das variáveis incertas~~ ✅ (aba `Fin_Premissas`, com fonte ou status de premissa).
6. ~~Implementar o motor (Python) e gerar o contrato de dados da seção 7~~ ✅ (4.4; `scripts/10_modelo_financeiro.py`, `processed/financeiro_*.csv`). Falta só a série de 24 h do dimmer, que sai da camada 1.
7. ~~Pesquisar por conta própria as perguntas de 6.8~~ ✅ (14/10/2026; abas `Pesquisa_Hitachi` e `Pesquisa_Precos_VSR`). A cotação da Hitachi Energy para 500 kV no Brasil (pergunta 1) substituiria a faixa dos contratos europeus; as demais perguntas viram confirmação.
8. Decidir P1 (arquitetura) e integrar ao site, substituindo os placeholders.
9. Redigir a Nota Técnica.

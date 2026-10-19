Calculadora "O Custo do Fixo"
Projeto: PoliVSR — Hackathon Hitachi Energy
Destinatários: Agentes de IA (Frente de Modelagem Estatística, Pesquisa e Documentação)

Este documento estabelece a arquitetura, as regras de negócio e os parâmetros de engenharia para a criação do modelo estocástico da nossa Calculadora de Payback. O objetivo do grupo é provar financeiramente que o uso de Variable Shunt Reactors (VSR), produzidos pela Hitachi Energy em Guarulhos, é superior ao uso de reatores shunt fixos no Sistema Interligado Nacional (SIN).

### 1. O Problema Sistêmico e a Solução (O "OPEX Invisível")

O sistema elétrico brasileiro possui linhas de transmissão muito longas que, em períodos de carga leve, geram excesso de reativo capacitivo (Efeito Ferranti) e elevam perigosamente a tensão. O equipamento tradicional para absorver esse excesso é o reator shunt fixo.

* O gargalo do modelo fixo: Funciona como um "tudo ou nada". O Operador Nacional do Sistema (ONS) precisa manobrar (ligar/desligar) o disjuntor constantemente para acompanhar a variação da carga ao longo do dia. O chaveamento indutivo é severo, destrói os contatos mecânicos do disjuntor e gera um alto OPEX (Custo Operacional) de manutenção que as concessionárias absorvem silenciosamente.


* O VSR (Variable Shunt Reactor): Utiliza um comutador de derivação em carga (OLTC) que ajusta a absorção de reativo em degraus suaves, sem manobrar o disjuntor. Ele atua como um "dimmer", acompanhando a necessidade da rede, mitigando o desgaste físico e conferindo flexibilidade para lidar com fontes intermitentes (solar e eólica).


* Nossa Estratégia Comercial: O VSR tem um custo de aquisição (CAPEX) maior. A calculadora provará que a economia em OPEX e a confiabilidade pagam o investimento a médio prazo.



### 2. Estrutura Atual do Front-End (Site PoliVSR)

O site já possui a interface montada para receber a inteligência matemática desenvolvida por vocês. Ele é dividido em duas grandes necessidades de dados:

A. Dashboard Nacional (Página Inicial)
Precisamos de dados macroeconômicos e elétricos de alto nível para ancorar o problema na realidade nacional.

* Curva de Pato Nacional: Gráfico ilustrando o afundamento da carga líquida diurna devido à forte penetração de geração solar distribuída e o pico agressivo no fim do dia.


* Métricas em Tempo Real (Estimativas Estocásticas): Quantidade de manobras de disjuntor de reatores fixos ocorrendo no país "hoje" e o número de reatores fixos ligados no momento.

B. A Calculadora "O Custo do Fixo" (Página de Simulação)
O usuário seleciona um cenário operacional e ajusta parâmetros (sliders). A calculadora devolve o risco financeiro.

* Os 3 Cenários (Inputs Fixos de Perfil):
1. *Centro Urbano (Ex: Salvador, Recife):* Foco em geração distribuída e variação brusca de tensão diurna.


2. *Campo (Ex: Interligação Norte-Nordeste):* Foco em Efeito Ferranti violento nas madrugadas devido à extensão das linhas.


3. *Indústria (Ex: Camaçari, Manaus):* Foco em volatilidade contínua e regulação fina.




* Sliders (Inputs do Usuário): Extensão do trecho crítico (km), Volatilidade da carga renovável (%), Custo médio por manutenção de disjuntor (R$), Prêmio de CAPEX do VSR (R$).

### 3. Entregáveis Esperados dos Agentes

Vocês devem estruturar um modelo matemático (em Python/R) e um relatório formal baseados nos dados acima.

3.1 Funções Matemáticas e Outputs do Modelo
O motor estocástico deve cruzar os inputs do usuário com a frequência de falhas esperada e cuspir as seguintes saídas para a nossa interface:

* Tempo de Payback: Estimativa em meses, acompanhada de um intervalo de confiança (Otimista vs. Pessimista).


* Impacto Operacional: Quantidade de manobras de disjuntor evitadas por ano e a sobrevida adicionada aos equipamentos de manobra (em anos) pelo uso do VSR.
* OPEX Acumulado (10 anos): Custo de manutenção projetado do Reator Fixo versus o Custo zero (ou irrisório) de manobra do VSR.
* A "Névoa de Risco" (Fan Chart): Matriz de dados para a plotagem do gráfico principal. A linha do Reator Fixo deve crescer envolta em uma "névoa" (intervalo de variância/risco estocástico de quebra precoce) que se alarga com o tempo. A linha do VSR deve ser plana e livre de névoa.

3.2 Bibliografia Oficial e Pesquisa Expandida (Obrigatório)

* Não alucinem dados. Ancorem todas as taxas de desgaste, custos de intervenção mecânica e perfis de carga em relatórios do ONS (PAR/PEL 2025) e da EPE (Estudos de controle de tensão nas regiões Norte e Nordeste).


* Usem os cadernos e brochuras do CIGRÉ (Grupo de Trabalho A2) para fundamentar a confiabilidade do OLTC frente ao chaveamento indutivo de disjuntores.


* *Liberdade de Pesquisa:* Vocês estão autorizados e encorajados a buscar literatura complementar (artigos IEEE, estatísticas globais de confiabilidade de equipamentos de alta tensão) para encontrar outras variáveis ocultas de OPEX (custo de energia não fornecida, risco de quebra catastrófica, etc.) que ajudem a vender o valor do VSR.



3.3 A Nota Técnica (Documento PDF)
Todo esse esforço de pesquisa, cálculo e código deve ser consolidado em um relatório textual executivo. Este documento será disponibilizado para download no site ("Baixar Metodologia Estatística (PDF)") para conferir credibilidade e auditoria à nossa calculadora. O relatório deve explicar com clareza a dor do setor, detalhar as equações de desgaste utilizadas e listar as referências bibliográficas oficiais. Ele deve ser entregue pronto para diagramação.
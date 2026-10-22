# A calculadora "O Custo do Fixo"

## Que pergunta ela responde

Numa subestação que precisaria de dois reatores fixos, **compensa instalar um VSR no lugar deles?** A calculadora compara as duas alternativas ao longo de 30 anos, mês a mês, e traz tudo para dinheiro de hoje.

## O que o usuário escolhe

- **Cenário operacional:** Centro Urbano, Campo ou Polo eólico (ver abaixo).
- **Quem avalia:** a **transmissora** (taxa de 12,11% ao ano, com a multa por indisponibilidade) ou o **sistema (SIN)** (taxa social de 8,5% ao ano, com as perdas do VSR e a energia não suprida).
- **Preço do VSR, só equipamento:** R$ 42,5 mi no caso-base a 500 kV, com atalhos para a faixa dos contratos de 2025–26 e para o nível de 2023.
- **Preço de 1 reator fixo, só equipamento:** R$ 13,5 mi no caso-base a 500 kV (referência EPE de 2021 corrigida pelo IPCA).
- **Premissas:** o caso-base ou uma das variantes (ver "Onde o VSR não compensa").

## O que ela mostra

- **Valor do VSR em 30 anos (VPL):** quanto o VSR economiza em relação aos fixos, em valor presente. Positivo quer dizer que o VSR sai mais barato. O número grande é a **mediana** de 4.000 simulações; P10 e P90 são os casos pessimista e otimista.
- **Chance de compensar:** em quantas das 4.000 simulações o VSR saiu mais barato.
- **Preço de equilíbrio ("Compensa até"):** o preço máximo do VSR para ele ainda valer a pena.
- **Impacto operacional:** payback, manobras evitadas por ano, troca do disjuntor, vão evitado.
- **Abas:**
  - **Risco:** a névoa do risco, com o custo acumulado de cada alternativa ano a ano (linha = mediana; faixa = P10 a P90).
  - **Preço:** o VPL em função do preço do VSR.
  - **Operação:** um dia típico, com a necessidade da rede, os degraus do fixo e a curva do VSR.
  - **Valor:** a cascata, que mostra de onde vem o valor (o que soma a favor e o que pesa contra o VSR).
- **Investimento no dia da instalação:** a tabela de quanto custa cada alternativa na compra.

## Como ela calcula: duas camadas

**Camada 1, o modelo físico.** Pega a curva real de 2025–26 do ONS e calcula, hora a hora, quanto reator a rede precisa. Depois simula:
- o **fixo**, que entra e sai em degraus, com uma folga (histerese) para não ligar e desligar a cada pequena oscilação;
- o **VSR**, que muda de posição no comutador (33 posições) e só sai pelo disjuntor em carregamento extremo.

Resultado: quantas manobras o disjuntor do fixo faz, quantas operações o comutador do VSR faz e quantas vezes o VSR ainda precisa do disjuntor. **Nenhum parâmetro foi ajustado** para bater com a realidade, e mesmo assim bate: o modelo dá 0,53 manobra por dia por reator na média da frota, contra 0,48 medida em campo, e fica dentro do que o ONS relata.

**Camada 2, o modelo financeiro.** Soma 360 meses de custos de cada lado:
- **fixo:** compra (dois reatores, duas fases reserva e dois vãos), manutenção, revisão e troca do disjuntor, falhas e multas por indisponibilidade;
- **VSR:** compra (o VSR e um vão), manutenção do comutador, falhas graves (sem reserva, ficando meses fora), multas e, na visão do sistema, as perdas.

Tudo é trazido a valor presente pela taxa de quem avalia.

## O Monte Carlo: 4.000 futuros

Quase tudo no modelo é incerto: quantas vezes um disjuntor falha, quanto ele dura na prática, quanto custa e quanto demora um reparo. Um número só esconderia o risco, e a pergunta da transmissora é: **qual a chance de eu me arrepender?**

Por isso o modelo roda **4.000 simulações** por cenário. Em cada uma, sorteia:
- a taxa de falha do disjuntor de reator (1,98 a 3,02 falhas graves por 100 disjuntores por ano, CIGRÉ);
- a vida mecânica real do disjuntor (10.000 ciclos de catálogo divididos por um fator de 1 a 5);
- a taxa de falha grave do reator ou do VSR (0,30% a 0,53% ao ano);
- custos e tempos de reparo;
- o número de operações do comutador.

Depois percorre os 360 meses, sorteando quando acontecem as falhas, e calcula o VPL de cada futuro.

**Comparação justa:** o fixo e o VSR enfrentam sempre o mesmo futuro sorteado, como dois pneus testados na mesma estrada, no mesmo dia. Assim, a diferença entre eles vem da tecnologia, e não da sorte do sorteio. Por isso também o site responde na hora quando se mexe no preço: o resultado de cada simulação é uma reta em função do preço.

**Precisão:** com 4.000 simulações, o erro estatístico é de cerca de ±0,3 ponto percentual na chance de compensar e ±R$ 0,07 mi no VPL médio do Campo.

## Os três cenários

| | Centro Urbano | Campo | Polo eólico |
|---|---|---|---|
| Tensão e reator | 230 kV, 20 Mvar | 500 kV, 150 Mvar por degrau | 500 kV, 150 Mvar |
| VSR do arranjo 2:1 | 40 Mvar | 300 Mvar | 300 Mvar |
| O que move a curva | carga do Nordeste menos geração nos telhados e solar | fluxo medido na interligação Norte–Nordeste | carga do Nordeste menos telhados, solar e eólica |
| Manobras/ano do fixo (evitadas) | 730 | 592 | 583 |
| Manobras/ano que o VSR ainda faz | 0 | 3 | 42 |

- **Centro Urbano:** subestação de 230 kV que alimenta uma região metropolitana. A necessidade de reator é maior perto do meio-dia, no fundo da curva de pato.
- **Campo:** subestação no meio do corredor de linhas longas Norte–Nordeste. Ali o que importa é quanto a linha está carregada: ela fica mais leve às 18h (1,9 GW em média), quando a solar do Nordeste cai, e mais pesada às 8h (3,6 GW). É o único cenário em que a física das linhas dá o tamanho total da necessidade (~944 Mvar, ou 6 degraus de 150 Mvar).
- **Polo eólico:** região dominada pelo vento, onde há períodos de vento e de calmaria que duram horas a dias. É o cenário mais volátil: a curva oscila com desvio-padrão de 17,2% da carga média do Nordeste, contra 5,2% no Centro Urbano.

## Resultados do caso-base (visão da transmissora)

| Cenário | Ganho em 30 anos (mediana) | Faixa P10–P90 | Chance de compensar | Compensa até |
|---|---|---|---|---|
| Campo, 500 kV | R$ 8,6 mi | R$ 6,6 a 11,0 mi | 96% | R$ 51,1 mi |
| Polo eólico, 500 kV | R$ 8,4 mi | R$ 6,5 a 10,7 mi | 96% | R$ 50,8 mi |
| Centro Urbano, 230 kV | R$ 3,6 mi | R$ 3,1 a 4,3 mi | 99% | R$ 12,2 mi |

Na visão do sistema (taxa social de 8,5%): Campo R$ 9,1 mi, Polo eólico R$ 9,0 mi, Centro Urbano R$ 3,8 mi.

**De onde vem o ganho no Campo:**
- **No dia da compra:** dois fixos custam R$ 61,97 mi (2 reatores R$ 26,97 mi + 2 fases reserva R$ 8,99 mi + 2 vãos R$ 26,01 mi). Um VSR custa R$ 55,55 mi (VSR R$ 42,54 mi + 1 vão R$ 13,00 mi). O VSR já começa **R$ 6,4 mi mais barato**, e por isso o **payback é imediato**.
- **O prêmio do VSR:** ele custa R$ 15,6 mi a mais que os dois reatores fixos (+58%), mas o vão evitado (R$ 13,0 mi) e as fases reserva evitadas (R$ 9,0 mi) mais do que pagam essa diferença.
- **Na operação:** cerca de 590 manobras a menos por ano em cada disjuntor; o disjuntor do fixo é trocado em 9 a 12 anos, e o do VSR passa os 30 anos sem troca.
- **Na névoa do risco:** no ano 30, o custo acumulado do fixo chega a R$ 66,1 mi e o do VSR a R$ 57,3 mi (medianas); as curvas nunca se cruzam.
- **Folga de preço:** o VSR compensa até R$ 51,1 mi, 20% acima do preço-base de R$ 42,5 mi.

**Por que a taxa de desconto pesa pouco:** o maior ganho acontece no dia da compra, que não é descontado. Variando a taxa de 8% a 14%, o VPL do Campo vai de R$ 9,2 mi a R$ 8,0 mi.

## Onde o VSR não compensa (responda com transparência se perguntarem)

| Situação (Campo, transmissora) | Ganho mediano | Chance de compensar |
|---|---|---|
| VSR no preço de 2023 (R$ 80 a 86 mi, pico da crise de suprimento) | −R$ 30 a −35 mi | 0% |
| Reforço autorizado, com receita calculada pelo Banco de Preços da ANEEL | −R$ 4,4 mi | 5% |
| Reserva de um VSR para cada três instalados | −R$ 5,6 mi | 4% |
| Banco fixo sem fase reserva | −R$ 0,4 mi | 40% |
| Comutador a óleo em vez de a vácuo | +R$ 1,1 mi | 61% |
| Preço no topo da faixa dos contratos (R$ 50,1 mi) | +R$ 1,0 mi | 74% |

E também:
- **Troca de reator antigo:** o vão já existe, então não há vão evitado.
- **Subestação com um só reator:** o VSR teria de ser desligado quase todo dia.

O foco do projeto é a **obra nova** com dois bancos de reator.

Variantes favoráveis, para comparação: reserva compartilhada de 1 para 10 (R$ 4,4 mi, 94%); preço na faixa baixa dos contratos (R$ 14,2 mi, 98%); prêmio do VSR remunerado na receita (R$ 24,2 mi, 99%).

## Limitações declaradas

- O **preço do VSR** é estimado a partir de contratos públicos europeus (Litgrid 2026; Energinet com GE Vernova 2025), escalados para 500 kV e 300 Mvar. É a maior incerteza do modelo, até a Hitachi cotar o caso brasileiro.
- O modelo físico usa uma **barra típica, sem fluxo de potência**; dizer quantos VSRs vão em cada subestação exigiria um estudo da rede.
- O 2:1 foi **verificado no Campo**; nos outros dois cenários é premissa.
- Os dados do Centro Urbano e do Polo eólico vêm do DESSEM do ONS, que é **programado**; o Campo usa fluxo **verificado**.
- Não há dado público de falha da frota de VSR; o modelo usa a taxa de reatores e transformadores (CIGRÉ).
- O modelo é **antes de impostos**.

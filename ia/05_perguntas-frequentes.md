# Perguntas frequentes

Respostas curtas. Para detalhes, ver os arquivos 02 (física), 03 (calculadora) e 04 (intenções e roadmap).

## Sobre o projeto

**1. O que é o PoliVSR?**
Um projeto de pesquisa aplicada de estudantes da Poli-USP que compara, com dados públicos, o VSR (reator de ajuste contínuo) com os reatores fixos usados hoje no SIN. Nasceu no Hackathon Hitachi Energy 2026 e tem apoio e fomento da Hitachi Energy.

**2. Quem faz parte do grupo?**
Nasser, João Paulo Saraiva e Raphael Dopaso, estudantes da Escola Politécnica da USP.

**3. Vocês são imparciais, se a Hitachi fabrica VSR?**
O projeto é transparente sobre a origem: nasceu num hackathon da Hitachi Energy, fabricante de VSR. Por isso usamos só dados públicos (92 arquivos do ONS, da ANEEL e do Banco Central), declaramos todas as premissas e publicamos os scripts que refazem os números. O modelo cobra do VSR os custos e riscos dele e mostra onde ele não compensa.

**4. Onde estão os dados?**
No repositório público https://github.com/LordiMil/dados_VSR: arquivos brutos com endereço, data de acesso e impressão digital (SHA-256), scripts, resultados e a planilha-mestre.

## Sobre o problema e o VSR

**5. Por que a tensão sobe na rede?**
Linhas de transmissão geram potência reativa o tempo todo. Quando passa pouca energia por elas, sobra reativo e a tensão sobe. Com a energia solar nos telhados, a rede fica leve no meio do dia, e isso acontece com mais frequência.

**6. O que é a curva de pato?**
O formato da carga líquida ao longo do dia: afunda ao meio-dia, quando a solar cobre boa parte do consumo, e sobe com força no fim da tarde. Em setembro de 2026, a média do SIN foi de 36,8 GW às 12h a 77,3 GW às 18h30 (ONS).

**7. O que é um reator fixo e qual o problema dele?**
É o equipamento que absorve o reativo em excesso. Ele só liga ou desliga, e quem faz isso é o disjuntor. Desligar reator é um trabalho pesado: o disjuntor de reator tem cerca de dez vezes mais falhas graves que um disjuntor de linha (2,46 contra 0,25 por 100 disjuntores por ano, CIGRÉ).

**8. O que é o VSR?**
Um reator com comutador sob carga, que ajusta a potência em pequenos passos sem desligar. O fixo é um interruptor; o VSR é um dimmer.

**9. O VSR substitui o reator fixo um por um?**
Não. A aplicação que compensa é a **2:1**: um VSR com o dobro da potência substitui dois reatores fixos (um que fica sempre ligado e um que entra e sai) e dispensa um vão inteiro na subestação. No 1:1, o VSR ainda precisaria sair pelo disjuntor cerca de uma vez por dia e não economizaria vão.

**10. Por que seis VSRs no corredor Norte–Nordeste, e não um só?**
A sobra de reativo do corredor varia cerca de 944 Mvar ao longo do dia, o que equivale a 6 reatores manobráveis de 150 Mvar. No 2:1, 12 reatores fixos viram 6 VSRs de 300 Mvar. Um VSR só precisaria de cerca de 1.900 Mvar (ele regula só de 50% a 100% da própria potência), ficaria num lugar só e concentraria todo o risco.

**11. O VSR substitui STATCOM, SVC ou compensador síncrono?**
Não. Esses equipamentos respondem em segundos e servem para contingências. O VSR, cujo comutador leva minutos, cuida das variações lentas, de horas a dias, por um custo menor. São complementares.

**12. Já existe VSR no Brasil?**
Nenhum fabricante tem VSR instalado no Brasil. No exterior, a Hitachi Energy tem VSRs na Noruega desde 2012 e entregou um de 500 kV no Uzbequistão em 2024; Siemens Energy e GE Vernova também venderam VSRs na Europa.

## Sobre a calculadora e os resultados

**13. O que a calculadora calcula?**
Se, numa subestação que precisaria de dois reatores fixos, compensa instalar um VSR. Ela compara 30 anos de custos das duas alternativas e mostra o ganho do VSR em valor presente, a chance de compensar e até que preço o VSR vale a pena.

**14. Quanto o VSR economiza?**
No caso-base, na visão da transmissora, o ganho mediano em 30 anos é de R$ 8,6 mi no Campo (500 kV), R$ 8,4 mi no Polo eólico (500 kV) e R$ 3,6 mi no Centro Urbano (230 kV), com chance de compensar de 96% a 99%. São resultados de modelo, não garantias.

**15. Por que o payback é imediato?**
Porque, a 500 kV, um VSR com um vão (R$ 55,55 mi) já custa menos que dois reatores fixos com duas fases reserva e dois vãos (R$ 61,97 mi). O VSR custa 58% a mais que os dois reatores, mas o vão e as fases reserva evitados pagam essa diferença.

**16. De onde vem o preço do VSR?**
De contratos públicos de operadores europeus (Litgrid, 2026; Energinet com GE Vernova, 2025), escalados para 500 kV e 300 Mvar e convertidos pelo câmbio do Banco Central. O caso-base é R$ 42,5 mi, numa faixa de R$ 37 a 50 mi. É a maior incerteza do modelo; o VSR compensa até R$ 51,1 mi no Campo.

**17. O que é o Monte Carlo e por que 4.000 simulações?**
O modelo sorteia 4.000 futuros possíveis (falhas de disjuntor e de reator, vida útil, custos e prazos de reparo) e calcula o resultado em cada um. Assim mostra não só o resultado mais provável, mas a faixa de resultados e a chance de o VSR compensar. Com 4.000, o erro estatístico na chance de compensar fica em cerca de ±0,3 ponto percentual.

**18. O que são P10, P50 e P90?**
O P50 é a mediana: metade das simulações deu mais, metade deu menos. O P10 é um caso pessimista (só 10% das simulações deram menos) e o P90, um otimista (só 10% deram mais).

**19. O VSR também falha. Isso está na conta?**
Sim. A falha grave do VSR é sorteada com a taxa de um reator (0,30% a 0,53% por ano). Como o VSR não tem fase reserva, ele fica fora por meses (mediana de 180 dias), com multa por indisponibilidade. É isso que produz as poucas simulações em que ele perde.

**20. As perdas do VSR, que fica sempre ligado, anulam o ganho?**
Não. Elas entram na visão do sistema: cerca de R$ 0,55 mi em valor presente no Campo, contra um ganho de R$ 9,1 mi nessa visão.

**21. Vocês ajustaram o modelo para o VSR ganhar?**
Não. Nenhum parâmetro do modelo físico foi ajustado, e mesmo assim as manobras batem com a realidade: 0,53 manobra por dia por reator no modelo, contra 0,48 medida. Onde havia escolha, usamos a premissa mais favorável ao VSR que se sustenta e testamos a contrária.

**22. Por que duas taxas de desconto?**
A transmissora usa o custo de capital regulatório da ANEEL para transmissão em 2026, 12,11% ao ano antes de impostos. O sistema usa a taxa social de desconto oficial, 8,5% ao ano. Como o maior ganho está no dia da compra, a taxa pesa pouco: de 8% a 14%, o ganho no Campo vai de R$ 9,2 a 8,0 mi.

## Onde o VSR não compensa

**23. O VSR sempre vale a pena?**
Não. Pelo modelo, ele não compensa na troca de um reator antigo (o vão já existe), numa subestação com um só reator, ou se o preço voltar ao nível de 2023 (R$ 80 a 86 mi, ganho de −R$ 30 a −35 mi). Também perde se cada três VSRs exigirem um VSR inteiro de reserva (−R$ 5,6 mi no Campo). O foco é a obra nova com dois bancos de reator.

**24. E nas obras de reforço?**
Para a transmissora, não compensa hoje (−R$ 4,4 mi no Campo, 5% de chance), porque a receita é calculada pelo Banco de Preços da ANEEL, que não tem VSR, e ela deixa de receber pelo vão que não constrói. Para o sistema, continua vantajoso. Por isso propomos incluir o VSR no Banco de Preços.

**25. E se o comutador for a óleo, e não a vácuo?**
O ganho no Campo cai de R$ 8,6 mi para cerca de R$ 1,1 mi (61% de chance), porque o comutador a óleo pede manutenção muito mais cedo. O comutador a vácuo, que é o padrão em VSR, só pede revisão a cada 300 mil operações (8 a 9 anos).

## Sobre o futuro e o contato

**26. Quais os próximos passos do PoliVSR?**
Mapa de oportunidades (0 a 6 meses), medição com transmissoras (cerca de 1 ano), estudo de caso real, piloto em campo (opcional) e a proposta de incluir o VSR no Banco de Preços da ANEEL. Ver o roadmap no arquivo 04.

**27. Minha transmissora pode usar isso?**
Sim. Pelo formulário "Vamos estudar o VSR na sua concessão", no fim da página inicial, o grupo compara o VSR e os reatores fixos com os dados da sua subestação.

**28. Posso reproduzir os números?**
Sim. O repositório https://github.com/LordiMil/dados_VSR tem os arquivos brutos, os scripts que refazem os resultados e a planilha-mestre.

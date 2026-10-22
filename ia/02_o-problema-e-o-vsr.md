# O problema e o VSR

## 1. Potência ativa e reativa

A energia que faz trabalho (acender lâmpada, girar motor, esquentar chuveiro) é a **potência ativa**, medida em watts (MW, GW). Numa rede de corrente alternada também existe a **potência reativa**, medida em var (Mvar): uma energia que vai e volta entre os campos elétricos e magnéticos dos equipamentos, sem fazer trabalho.

**Analogia:** no copo de chope, a cerveja é a potência ativa e a espuma é a reativa. A espuma ocupa espaço sem matar a sede.

A regra prática: **o reativo controla a tensão.** Sobra de reativo faz a tensão subir; falta faz cair. O operador precisa manter a tensão numa faixa estreita.

## 2. Por que a tensão sobe nas linhas longas

Uma linha de transmissão tem dois efeitos que disputam o reativo:
- a **capacitância** entre os cabos e a terra **gera** reativo o tempo todo, só por a linha estar ligada;
- a **indutância** dos cabos **consome** reativo, e consome mais quanto mais energia passa.

Existe um carregamento em que os dois se anulam: a **potência natural (SIL)**. Abaixo dela, sobra reativo e a tensão sobe. Com a linha quase vazia, a tensão na ponta fica maior que na origem: é o **efeito Ferranti**, que cresce com o comprimento da linha.

**Analogia:** uma gangorra. De um lado, a linha empurra a tensão para cima, sempre com a mesma força. Do outro, a energia que passa puxa para baixo. Quando passa pouca energia, o lado que empurra para cima ganha, e é preciso colocar peso do outro lado: os **reatores**.

Fórmula usada no modelo: sobra de reativo = Qc × [1 − (P ÷ SIL)²], em que Qc é o reativo gerado pela linha e P a potência transportada.

**Exemplo real:** o corredor Norte–Nordeste tem 11 circuitos e 2.686 km de linhas. Elas geram 3.937 Mvar e só se equilibram com 10,4 GW passando, mas transportam na prática de 0,3 a 5,1 GW. Sobra reativo o tempo todo, e a sobra varia cerca de **944 Mvar** entre os momentos mais leve e mais pesado.

## 3. A curva de pato

Com a energia solar, principalmente nos telhados (a micro e minigeração distribuída, ou MMGD, já soma **53,9 GW** segundo a ANEEL), a carga que a rede transmite afunda ao meio-dia e volta com força no fim da tarde. O desenho lembra um pato: a barriga ao meio-dia e o pescoço à noite.

Em setembro de 2026, a carga líquida média do SIN caiu a **36,8 GW às 12h** e subiu a **77,3 GW às 18h30** (ONS). Em 92,7% dos dias de 2025–26, o mínimo do SIN caiu entre 10h e 15h.

Quando a rede fica leve, sobra reativo e a tensão sobe. Por isso os reatores entram e saem de serviço todo dia.

## 4. O reator fixo e as manobras

O **reator de derivação** (ou reator shunt) é o equipamento que absorve o excesso de reativo e segura a tensão. O **reator fixo** só tem dois estados: ligado ou desligado. Quem liga e desliga é o **disjuntor**.

- O SIN tem **1.084 reatores** de 230 kV ou mais (126 mil Mvar); cerca de **530** são manobráveis. Eram 550 reatores em 2015.
- Num dia útil de verão de 2026, cerca de **140 reatores** de barra são ligados e desligados; o ONS projeta **170 em 2030** (PAR/PEL 2025).
- Desligar um reator é um dos trabalhos mais duros para um disjuntor: o arco elétrico pode reacender e gerar sobretensões. O disjuntor de reator tem **2,46 falhas graves por 100 disjuntores por ano**, contra **0,25** de um disjuntor de linha (CIGRÉ), cerca de dez vezes mais.

## 5. O VSR

O **VSR (Variable Shunt Reactor, ou reator de derivação variável)** é o mesmo tipo de reator com um **comutador sob carga (OLTC)**, a mesma peça dos transformadores. O comutador muda quantas espiras da bobina estão em uso e, com isso, quanto reativo o VSR absorve, em pequenos passos (33 posições no modelo), **sem desligar**.

**Analogia:** o reator fixo é um interruptor; o VSR é um dimmer.

Limites e custos que o VSR tem:
- **Não vai a zero.** Regula entre um mínimo e a potência máxima; o modelo usa mínimo de 50%.
- **Comutador:** cada mudança de posição é uma operação. O VSR faz de 32 a 38 mil por ano. O comutador a vácuo, padrão em VSR, pede manutenção a cada 300 mil operações, ou seja, a cada 8 a 9 anos.
- **Sem fase reserva:** o VSR costuma ser trifásico, com as três fases num tanque só. Se falha gravemente, fica meses fora (mediana de 180 dias no modelo), e a reserva teria de ser um VSR inteiro.
- **Perdas:** fica sempre ligado e, mesmo na posição mínima, dissipa cerca de 62% das perdas que teria na potência máxima.

## 6. Por que um VSR substitui dois reatores fixos (o arranjo 2:1)

Numa subestação, a compensação tem duas partes: uma **permanente**, que fica ligada quase sempre, e uma **manobrável**, que entra e sai ao longo do dia.

- **No 1:1**, um VSR do tamanho do reator manobrável regula de 50% a 100% dele. Quando a necessidade cai abaixo da metade, ele precisa sair pelo disjuntor do mesmo jeito. No Campo, ainda manobraria cerca de 1 vez por dia, e não economizaria vão nenhum. Não compensa.
- **No 2:1**, o VSR tem o dobro do tamanho e substitui **um reator manobrável e um permanente**. O mínimo dele fica em cima da necessidade permanente, e a faixa de regulação cobre a variação do dia. Assim ele quase não precisa do disjuntor (cerca de 3 vezes por ano no Campo) e a subestação dispensa **um vão inteiro**.

É a aplicação de referência do CIGRÉ (artigo A2-211/2014). O 2:1 exige compensação permanente suficiente: no corredor Norte–Nordeste há ~2.990 Mvar permanentes, e o arranjo é viável até um mínimo de regulação de 76%.

**Exemplo do corredor Norte–Nordeste:** os ~944 Mvar que variam no dia equivalem a 6 reatores manobráveis de 150 Mvar. No 2:1, **12 reatores fixos** (6 manobráveis e 6 permanentes) viram **6 VSRs de 300 Mvar**, cada um regulando de 150 a 300 Mvar. Um VSR só não daria: precisaria de ~1.900 Mvar, ficaria num lugar só e concentraria todo o risco.

## 7. O que é um vão e uma fase reserva

- **Vão:** a "vaga" de cada reator na subestação. Inclui disjuntor, chaves seccionadoras, transformadores de corrente, para-raios, proteção e controle, estruturas e obra civil. A 500 kV custa cerca de **R$ 13,0 mi**.
- **Fase reserva:** em 500 kV, o banco fixo padrão tem três unidades monofásicas mais uma de reserva no pátio (banco 3+1R). Se uma unidade falha, a troca leva poucas horas. Cada fase reserva custa cerca de **R$ 4,5 mi**.

## 8. Ganhos que o modelo não coloca em reais

- A tensão fica sem os degraus de cada manobra: a distância entre a compensação e a necessidade cai de 5% para 2% da faixa no Campo.
- Menos área ocupada na subestação.
- Ajuda a integrar renováveis, que variam ao longo do dia.
- A operação deixa de ter uma ordem de manobra diária para cada reator.

## 9. O que o VSR não substitui

Compensador síncrono, SVC e STATCOM servem para resposta rápida e contingências (segundos). O VSR, cujo comutador leva minutos, cuida das variações lentas, de horas a dias, por um custo menor. São complementares.

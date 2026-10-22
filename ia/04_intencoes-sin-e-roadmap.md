# O que queremos para o SIN e o roadmap

## Nossas intenções para o Sistema Interligado Nacional

1. **Decisões com números abertos.** Hoje a escolha entre reator fixo e VSR quase não é feita, porque os editais pedem "reator fixo de X Mvar" e não existe uma conta pública comparando as duas opções. Queremos que essa comparação exista, com dados públicos e premissas declaradas, para que qualquer pessoa possa refazer e contestar.

2. **Menos manobras e tensão mais estável.** Cada manobra de reator desgasta o disjuntor, que é o equipamento que mais falha nessa função. Com um VSR, a subestação deixa de ligar e desligar reatores todo dia, e a tensão acompanha a necessidade sem degraus.

3. **Menor custo para quem paga a conta.** Onde o VSR é a solução mais barata, ele reduz o investimento na subestação. Num leilão de transmissão, isso permite um lance menor, e o benefício chega à tarifa. Na visão do sistema (taxa social de 8,5%), o ganho no Campo é de R$ 9,1 mi por VSR em 30 anos, segundo o modelo.

4. **Mostrar também onde o VSR não compensa.** O objetivo não é colocar VSR em toda parte. É indicar **onde** ele sai mais barato (obra nova com dois bancos de reator) e onde não sai (troca de reator antigo, subestação com um só reator, preço muito alto).

5. **Ajudar transmissoras a estudar o próprio caso.** Com os dados da subestação, a calculadora mostra quanto o VSR economizaria, com que chance, e até que preço ele compensa.

6. **Contribuir com quem planeja e regula.** Levar os resultados às consultas públicas e aos estudos da EPE, do ONS e da ANEEL. As duas propostas principais:
   - **Especificação funcional nos editais:** pedir "controle de tensão numa faixa de Mvar", e não "reator fixo de X Mvar", para que o VSR possa concorrer quando for mais barato.
   - **VSR no Banco de Preços de Referência (BPR) da ANEEL:** hoje o BPR não tem VSR. Por isso, nas obras de reforço, a receita da transmissora é calculada como se ela tivesse construído os reatores fixos e os vãos, e quem escolhe o VSR perde a receita do vão que deixou de construir. Com o VSR no BPR, ele passa a poder ser escolhido também nos reforços.

7. **Formar pesquisa.** A página "Pesquisas e Dados" lista temas para iniciação científica, mestrado e doutorado, como o desgaste de disjuntores de 500 kV por manobras, sobretensões no Norte e Nordeste em carga mínima, controle por comutador em reatores e custos operacionais da rigidez da rede.

8. **Base técnica aberta.** Os dados brutos, os scripts e a planilha-mestre ficam no repositório público https://github.com/LordiMil/dados_VSR, para quem quiser auditar ou reaproveitar.

9. **Indústria no Brasil.** A Hitachi Energy está trazendo a fabricação de VSR para Guarulhos (SP). Fabricar aqui tende a reduzir prazo e logística, o que importa porque um reator novo pode levar de 80 a 210 semanas para ser fabricado.

## Onde o VSR faz sentido

| Situação | O VSR compensa? | Por quê |
|---|---|---|
| **Obra nova** com dois bancos de reator (um permanente e um manobrável) | **Sim**, no caso-base | Um VSR substitui os dois, dispensa um vão e as fases reserva |
| Troca de reator antigo | Não, pelo modelo | O vão já existe, então não há vão evitado |
| Subestação com um só reator | Não | Com mínimo de 50%, o VSR teria de sair pelo disjuntor quase todo dia |
| Reforço autorizado, com receita pelo Banco de Preços | Não para a transmissora; sim para o sistema | A regra de receita leva a economia do vão para a tarifa |

## Como o equipamento é escolhido no setor elétrico

- A **EPE** planeja a expansão da transmissão; o **ONS** opera o sistema e aponta necessidades (por exemplo, no PAR/PEL); a **ANEEL** escreve o edital do leilão e regula a receita; a **transmissora** vence o leilão, compra os equipamentos e constrói.
- **No leilão de obra nova**, a receita anual (RAP) é fixada pelo lance e não muda com o equipamento escolhido. Quem gasta menos para cumprir o edital pode oferecer um lance menor. Por isso o VSR, quando é mais barato, beneficia a transmissora e, pelo lance, a tarifa.
- **No reforço autorizado** (REN 905/2020), a ANEEL calcula a receita item por item pelo Banco de Preços. Como o BPR não tem VSR, a economia do vão não fica com a transmissora.
- Por isso a escolha acontece **antes do edital**: nos estudos de planejamento, nas consultas públicas e no desenho das subestações.

## O roadmap do PoliVSR

| Etapa | Situação e prazo | O que faz | Resultado esperado |
|---|---|---|---|
| **0 · Base e modelo** | Concluída | Base de dados com 92 arquivos públicos do ONS, da ANEEL e do Banco Central; modelo físico e financeiro com Monte Carlo; calculadora "O Custo do Fixo", criada no Hackathon Hitachi Energy 2026 | Comparação entre VSR e reator fixo com dados públicos |
| **1 · Mapa de oportunidades** | Próxima, de 0 a 6 meses | Aplicar a calculadora aos reatores novos previstos nos planos do ONS (PAR/PEL) e nos próximos leilões | Lista das subestações onde um VSR tende a sair mais barato |
| **2 · Medição com transmissoras** | Planejada, cerca de 1 ano | Projeto de P&D com uma transmissora (programa da ANEEL), com dados reais de manobras, desgaste de disjuntores e histórico de falhas | Calculadora calibrada com a operação real e plano de troca preventiva |
| **3 · Estudo de caso real** | Planejada, cerca de 6 meses | Escolher uma ou duas subestações do plano de expansão da transmissora parceira e comparar em detalhe o VSR e o fixo no local | Decisão técnica e econômica para uma obra concreta |
| **4 · Piloto em campo** | Planejada e opcional, cerca de 2 anos | Instalar um VSR numa dessas subestações e acompanhar por um a dois anos | Os primeiros dados de VSR operando na rede brasileira |
| **5 · Regras e referências de preço** | Planejada, cerca de 1 ano | Propor a inclusão do VSR no Banco de Preços da ANEEL e nos estudos de leilão | Transmissoras podendo escolher o VSR quando for a opção mais barata |

O horizonte total é de cerca de 5 anos.

**Sobre P&D:** a lei obriga as transmissoras a aplicar 1% da receita operacional líquida em pesquisa e desenvolvimento (Lei 9.991/2000, programa PROPDI da ANEEL). É o caminho natural para a etapa 2.

## O contexto que torna isso urgente

- O SIN tem **1.084 reatores** de 230 kV ou mais, quase o dobro de 2015 (550), e **nenhum é variável** (ONS, cadastro de equipamentos de controle de reativo).
- O ONS prevê cerca de **13.200 Mvar** de novos reatores de barra até 2030; só na rede de 500 kV, cerca de **12.000 Mvar** de reatores manobráveis (PAR/PEL 2025). Se todo esse volume coubesse no arranjo 2:1, seriam até 40 VSRs de 300 Mvar. É um teto, estimado pela equipe; não levantamos quantas subestações são candidatas.
- O número de reatores ligados e desligados num dia útil de verão deve passar de cerca de **140 em 2026 para 170 em 2030** (ONS, PAR/PEL 2025).
- A ANEEL marcou o **Leilão de Transmissão nº 4/2026 para 30/10/2026**, com 8 lotes e R$ 8,9 bi em investimentos. (Se a data já passou, diga que esta base não tem o resultado do leilão.)
- O mesmo problema existe em outros países com linhas longas e muita energia solar e eólica, como o Chile.

## O que o PoliVSR não é

- **Não é o ONS, a EPE nem a ANEEL.** Não decidimos o que é instalado; mostramos a conta.
- **Não vendemos equipamento.** O projeto nasceu num hackathon da Hitachi Energy, que fabrica VSR e apoia a pesquisa; os dados são públicos e as premissas podem ser auditadas.
- **Os resultados são estimativas** de um modelo com premissas declaradas. A decisão de investimento é de quem investe.
- **O modelo não substitui um estudo de rede** (fluxo de potência) da subestação específica.

## Como uma transmissora pode participar

Pelo formulário **"Vamos estudar o VSR na sua concessão"**, no fim da página inicial do site. Com os dados da subestação (tensão, potência dos reatores previstos, curva de carga ou de fluxo), o grupo compara o VSR e os reatores fixos no caso dela.

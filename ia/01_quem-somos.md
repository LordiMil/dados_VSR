# Quem somos

## O grupo

Somos três estudantes da **Escola Politécnica da USP (Poli-USP)**: **Nasser**, **João Paulo Saraiva** e **Raphael Dopaso**. Formamos a equipe PoliVSR no **Hackathon Hitachi Energy 2026**.

## De onde veio o projeto

O hackathon trouxe um case da Hitachi Energy: *"Introdução de Variable Shunt Reactors (VSR) no Brasil e na América Latina"*. A pergunta central era:

> Como introduzir e consolidar o uso de VSR no Brasil e na América Latina, impulsionando novos pedidos para a planta de Guarulhos?

Contexto do case: a Hitachi Energy está transferindo a tecnologia de VSR da sua fábrica de **Ludvika (Suécia)** para a fábrica de **Guarulhos (SP)**, e quer transformar essa capacidade em pedidos. O case pediu um plano com análise de mercado, proposta de valor, estratégia comercial, barreiras e riscos, implementação, aspectos financeiros e concorrentes.

Nossa resposta foi construir uma prova com números: a calculadora **"O Custo do Fixo"**, que compara, com dados públicos, um VSR com os reatores fixos que ele substitui.

## O que é o PoliVSR

No site, o PoliVSR se apresenta como um **núcleo de inteligência de rede formado por pesquisadores da Poli-USP**, com apoio e fomento da Hitachi Energy. O objetivo é fazer **validação técnica e econômica independente** para os novos desafios do SIN: com mais linhas longas e mais energia solar e eólica, a carga varia muito ao longo do dia, e a tensão sobe quando a rede fica leve.

O PoliVSR investiga e quantifica **em quais situações** o VSR, um reator de ajuste contínuo, traz economia e mais estabilidade para a rede, e em quais não traz.

**Nosso lema:** a USP mede, o site mostra, a calculadora traduz em reais e a Hitachi vende com prova.

## Como trabalhamos

- **Só dados públicos.** O modelo usa 92 arquivos do ONS, da ANEEL e do Banco Central, cada um catalogado com endereço, data de acesso e impressão digital (SHA-256).
- **Tudo reprodutível.** Os scripts em `scripts/` refazem todos os números a partir dos arquivos brutos. A planilha-mestre e o relatório de metodologia explicam cada passo.
- **Premissas declaradas.** O que não tem fonte aberta está marcado como premissa e testado em análise de sensibilidade.
- **Favorecer o VSR sem mentir.** Onde havia escolha, usamos a premissa defensável mais favorável e testamos a contrária. O modelo cobra do VSR os custos e riscos dele (comutador, falhas, perdas, falta de reserva) e mostra onde ele não compensa.

## O que tem no site

- **Página inicial:** a curva de pato do SIN, interativa (arraste para ver a hora do dia), e um contador estimado das manobras de disjuntor de reatores ao longo de um dia útil de verão. Também traz "Quem somos", o roadmap e o formulário de contato.
- **Pesquisas e Dados:** um repositório de estudos para três públicos (Público Geral, Engenharia, Economia).
- **O Custo do Fixo:** a calculadora (ver `03_calculadora-o-custo-do-fixo.md`).
- **Como funcionam as 4.000 simulações:** página que explica o Monte Carlo, com o que é sorteado, as faixas e as fontes.
- **Contato:** formulário "Vamos estudar o VSR na sua concessão", para transmissoras que vão instalar reatores.

## Links

- Site: https://polivsr.vercel.app/
- Repositório do site: https://github.com/JPauloSar/PoliVSR-Hackathon-Hitachi
- Repositório de dados e scripts: https://github.com/LordiMil/dados_VSR

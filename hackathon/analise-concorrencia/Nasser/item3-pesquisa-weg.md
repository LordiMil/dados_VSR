# Pesquisa Item 3 — WEG S.A.

## Resumo executivo

A WEG é fabricante brasileiro confirmado de **reatores de derivação (shunt reactors) FIXOS**,
com produção 100% nacional, até classe 550 kV. **Não foi encontrada nenhuma fonte primária
confiável que confirme um produto de reator variável/controlável (VSR/CSR)** — tecnologia de
regulação contínua de reativos, que é a lacuna funcional definida no contexto do caso. A
afirmação específica de que a "WEG lançou a primeira linha de produção de CSR de 550 kV da
América Latina em 2023, reduzindo dependência de importação em 65%" é **refutada como não
confirmada / provável alucinação**, conforme detalhado na seção "Questão em aberto".

Por outro lado, encontrei evidência sólida e recente (2025) de que a WEG está ativa no espaço
de **compensação dinâmica de reativos via compensadores síncronos rotativos** — uma tecnologia
diferente do VSR/CSR (mais próxima, em custo e porte, do STATCOM/SVC que o contexto pede para
excluir da categoria de concorrente direto, mas mencionar como alternativa cara).

---

## 1. Produto confirmado: Reator de Derivação (Shunt Reactor) FIXO

**Evidência de fabricação no Brasil:**
- A WEG opera 4 fábricas no Brasil (Blumenau, Gravataí, Itajaí e Hortolândia) dedicadas a
  transformadores, autotransformadores e reatores. A unidade de Blumenau/SC atua com
  transformadores, autotransformadores, reatores, subestações e linhas de transmissão até
  classe 550 kV, capacidade até 400 MVA; a unidade de Gravataí/RS produz transformadores,
  autotransformadores e reatores até classe 550 kV, capacidade até 600 MVA.
  Fonte: certificado ISO 9001:2015 — WEG Equipamentos Elétricos S.A., Unidade Transmissão &
  Distribuição — https://static.weg.net/medias/h73/h77/ISO-9001-2015-T-D-PORT.pdf (consultado em 08/09/2026, sem data de emissão explícita no documento).
- Catálogo oficial WEG de "Reatores Tipo Shunt" (linha Transformadores e Reatores a Óleo,
  Geração, Transmissão e Distribuição):
  https://www.weg.net/catalog/weg/PT/pt_PT/Geração,-Transmissão-e-Distribuição/Transformadores-e-Reatores-a-Óleo/Reatores-Tipo-Shunt/c/GTD_TO_ROP
  (consultado em 08/09/2026 — a página bloqueou fetch direto via HTTP 403, mas é referenciada
  e indexada pela própria WEG como catálogo de produto ativo; **não foi possível extrair da
  própria página o texto completo devido a bloqueio de acesso automatizado — recomendo
  verificação manual**).
- Caso de fornecimento internacional (LatAm, fora do Brasil) confirmado: WEG forneceu
  transformadores e reatores de derivação (shunt reactors) de 500 kV para um parque eólico no
  norte da Colômbia (6 reatores de derivação). Fonte: WEG Institutional News —
  "WEG Transformers and Shunt Reactors are supplied for a wind farm in northern Colombia" —
  https://www.weg.net/institutional/JM/en/news/products-and-solutions/weg-transformers-and-shunt-reactors-are-supplied-for-a-wind-farm-in-northern-colombia
  (data de publicação não capturada na busca; recomendo checagem manual da data no link).

**IMPORTANTE — correção de um dado herdado do mapeamento anterior:** a página da AECweb
"Reatores de Derivação Monofásicos até 550 kV - 70 MVAr" (https://www.aecweb.com.br/produto/reatores-de-derivacao-monofasicos-ate-550-kv-70-mvar/18368,
consultada em 08/09/2026) **é do fabricante Toshiba, não da WEG**. O dado "550 kV / 70 MVAr"
usado no contexto repassado a mim parece ter se originado dessa página, mas a atribuição à WEG
está **incorreta**. A capacidade real da WEG (conforme fonte oficial ISO 9001 acima) é
"classe 550 kV, até 400 MVA (Blumenau)" e "classe 550 kV, até 600 MVA (Gravataí)" — não há
menção a "70 MVAr" como teto de potência da WEG em nenhuma fonte primária encontrada. **Reporto
isso como correção/questão em aberto**: a especificação exata de MVAr máximo por unidade de
reator shunt fixo da WEG não foi confirmada com uma fonte técnica própria da WEG (datasheet).

Todos os produtos de reator de derivação identificados como sendo da WEG são **fixos** (sem
menção a comutador de tapes sob carga — OLTC — ou a regulação contínua/magnética de reativos).

---

## 2. VSR/CSR (regulação contínua de reativos): NÃO CONFIRMADO — questão em aberto

Busquei especificamente por:
- "reator controlável" / "reator variável" WEG
- "controllable shunt reactor" / "variable shunt reactor" WEG
- "reator saturado" / "reator magneticamente controlado" / MCSR + WEG
- Patentes WEG no INPI sobre reatores saturáveis/controlados
- Press releases da WEG sobre lançamento de linha de produção de CSR
- A frase específica "primeira linha de produção de CSR de 550 kV da América Latina" e o dado
  "redução de 65% na dependência de importação"

**Resultado: nenhuma fonte primária (site oficial da WEG, press release, nota de imprensa
especializada, patente no INPI, catálogo técnico) confirma que a WEG fabrica ou já lançou um
produto VSR/CSR.** Nenhum resultado de busca, incluindo buscas diretas pela frase suspeita,
retornou qualquer registro dela em veículo de imprensa, nota da WEG ou documento técnico.

**Fonte parcialmente relacionada, mas de baixa confiabilidade:** o relatório de mercado da
Global Market Insights sobre "Variable Shunt Reactor Market" lista a WEG entre os "key players"
do setor, junto com Hitachi Energy, Siemens Energy, Toshiba, GE, CG Power, Fuji Electric, Nissin
Electric, SGB Smit, Hyosung, entre outros.
Fonte: https://www.gminsights.com/industry-analysis/variable-shunt-reactor-market (consultado em 08/09/2026).
Essa listagem **não traz nenhum produto nomeado, contrato, patente ou detalhe técnico
específico da WEG** — é uma lista genérica de fabricantes de transformadores/reatores de grande
porte, do tipo comum em relatórios de mercado pagos, que frequentemente incluem players apenas
por atuarem no mercado adjacente de transformadores/reatores (mesmo que fixos), sem verificar se
o fabricante específico realmente vende a variante controlável. **Esta é provavelmente a origem
da confusão/alucinação** que gerou a afirmação sobre "primeira linha de produção de CSR da
WEG" repassada no contexto anterior — recomendo tratar esse relatório como fonte fraca e não
citá-lo como prova de produto real sem confirmação adicional.

**Conclusão sobre a afirmação específica investigada:**
> "WEG lançou a primeira linha de produção de CSR de 550 kV da América Latina em 2023,
> reduzindo dependência de importação em 65%"

Esta afirmação é **REFUTADA / NÃO CONFIRMADA**. Não há qualquer fonte primária rastreável
(site da WEG, press release, imprensa especializada em energia — CanalEnergia, Transformers
Magazine, epbr, MegaWhat, etc. — ou documento oficial) que a sustente. Deve ser tratada como
dado inexistente/fabricado até prova em contrário, e **não deve ser usada na análise de
concorrência do Nasser** como se fosse fato confirmado.

---

## 3. O que a WEG de fato está fazendo em compensação de reativos (2024-2026): Compensadores Síncronos

Tecnologia diferente do VSR/CSR (máquina rotativa, não reator estático de núcleo saturável ou
com OLTC), mas relevante para contextualizar a estratégia da WEG no espaço de estabilização de
tensão/reativos em transmissão:

- **Leilão de Transmissão ANEEL nº 04/2025**: incluiu, pela primeira vez, sete unidades de
  compensadores síncronos entre os lotes licitados. Análise do Bradesco BBI aponta a WEG como
  possível beneficiária, caso seja escolhida como fornecedora pelos vencedores dos lotes.
  Fonte: InfoMoney, "Aneel leiloará R$ 5,53 bi em linhas de transmissão; WEG pode sair entre
  beneficiadas" — https://www.infomoney.com.br/mercados/aneel-leiloara-r-553-bi-em-linhas-de-transmissao-weg-pode-sair-entre-beneficiadas/ — publicado em 28/10/2025.

- **Contrato confirmado (pós-leilão)**: a WEG firmou contrato para fornecer uma solução
  compensadora completa — Compensador Síncrono de 165 MVAr, Transformador Trifásico de 165 MVA,
  transformadores auxiliares, sistema de partida, quadros elétricos e sistemas de controle,
  comando, proteção e excitação — para o Lote 4 do Leilão de Transmissão ANEEL nº 04/2025
  (contratante: Guaporé Sul Transmissora de Energia S.A., do portfólio BTG Pactual), conectando
  Jauru (MT) a Vilhena (RO), linhas de 500 kV/230 kV totalizando ~354 km, na Subestação Vilhena 2
  (500/230 kV). Objetivo: estabilizar a Rede Básica do SIN no subsistema Acre-Rondônia.
  Fonte: Folha de Vilhena, "WEG firma contrato para fornecimento de solução compensadora ao SIN"
  — https://folhadevilhena.com.br/13/07/2026/weg-firma-contrato-para-fornecimento-de-solucao-compensadora-ao-sin/ — publicado em 13/07/2026.

**Nota de enquadramento (conforme critério do contexto):** compensadores síncronos rotativos são
tecnologicamente distintos de VSR/CSR — não são reatores estáticos de núcleo saturável nem
reatores com OLTC. Em termos de porte e custo, aproximam-se mais da categoria que o contexto do
caso pede para **excluir como concorrente direto** (tipo STATCOM/SVC de grande porte) e mencionar
apenas como "alternativa cara" para contraste. Portanto, **este contrato NÃO deve ser
apresentado como evidência de que a WEG compete diretamente na lacuna funcional do VSR/CSR** —
deve ser mencionado apenas como contexto de que a WEG está comercialmente ativa e crescendo no
espaço mais amplo de estabilização de tensão/reativos em transmissão no Brasil, com um produto de
categoria de custo mais alta.

---

## 4. Posicionamento (preço, porte, diferencial)

- **Porte:** a WEG é o maior fabricante de motores elétricos da América Latina e um dos maiores
  conglomerados de equipamentos elétricos do mundo, com operações em ~140 países e múltiplas
  fábricas no Brasil dedicadas a T&D. Fonte: Wikipedia "WEG Industries" (agregador secundário,
  usado aqui só para porte geral, não para dados técnicos) — consultado 08/09/2026.
- **Diferencial declarado (fixo, não VSR/CSR):** produção nacional integral de reatores de
  derivação fixos até classe 550 kV, o que reduz lead time/logística de importação para
  projetos de transmissão no Brasil comparado a fornecedores importados — mas isso se aplica
  apenas à linha de reatores FIXOS, não à tecnologia de regulação contínua. Não encontrei dado
  de preço público (lista de preços ou benchmark $/MVAr) em nenhuma fonte.
- **Sem produto VSR/CSR = sem posicionamento de preço nessa categoria específica.** Não há como
  comparar a WEG a Hitachi Energy (ou outros fabricantes de VSR/CSR confirmados) nesta lacuna
  funcional específica, porque a WEG aparentemente não participa desse nicho de produto.

---

## 5. Questões em aberto / dados não confirmados (reportar explicitamente ao time)

1. **Não confirmado:** existência de qualquer produto VSR/CSR da WEG. Nenhuma fonte primária
   encontrada apesar de busca extensiva (site oficial, imprensa especializada, INPI, press
   releases). A afirmação de "primeira linha de produção de CSR de 550 kV da América Latina em
   2023 / -65% importação" deve ser tratada como **não confirmada / provável alucinação** e não
   reutilizada sem essa ressalva.
2. **Dado corrigido, não apenas em aberto:** a especificação "550 kV / 70 MVAr" atribuída à WEG
   no contexto repassado pertence, na verdade, a um produto da **Toshiba** listado na AECweb, não
   da WEG. Recomendo remover essa atribuição incorreta de qualquer material do case.
3. **Fonte fraca identificada:** o relatório da Global Market Insights lista a WEG como "player"
   do mercado de VSR sem qualquer evidência de produto — tratar como fonte não confiável para
   fins de afirmação factual; possível origem da confusão anterior.
4. **Não confirmado por falta de acesso:** o catálogo oficial WEG de "Reatores Tipo Shunt"
   (link acima) bloqueou acesso automatizado (HTTP 403). Recomendo que alguém acesse
   manualmente para extrair specs técnicas completas (MVAr máximo, se há alguma variante com
   OLTC) direto da fonte primária antes de fechar a análise de concorrentes.
5. **Data de publicação não capturada:** para a notícia da WEG sobre o fornecimento para o
   parque eólico na Colômbia (shunt reactors 500 kV), não consegui extrair a data exata de
   publicação a partir dos resultados de busca — recomendo checagem manual no link para avaliar
   se está dentro da janela dos últimos 2 anos exigida pelo escopo.

---

## Fontes consultadas (organizadas por afirmação, ver corpo do texto para citação em contexto)

- WEG — Certificado ISO 9001:2015, Unidade Transmissão & Distribuição:
  https://static.weg.net/medias/h73/h77/ISO-9001-2015-T-D-PORT.pdf
- WEG — Catálogo "Reatores Tipo Shunt":
  https://www.weg.net/catalog/weg/PT/pt_PT/Geração,-Transmissão-e-Distribuição/Transformadores-e-Reatores-a-Óleo/Reatores-Tipo-Shunt/c/GTD_TO_ROP
- WEG — Notícia institucional, fornecimento Colômbia:
  https://www.weg.net/institutional/JM/en/news/products-and-solutions/weg-transformers-and-shunt-reactors-are-supplied-for-a-wind-farm-in-northern-colombia
- AECweb — Reator de derivação 550 kV / 70 MVAr (fabricante real: Toshiba):
  https://www.aecweb.com.br/produto/reatores-de-derivacao-monofasicos-ate-550-kv-70-mvar/18368
- InfoMoney — Leilão ANEEL e WEG (28/10/2025):
  https://www.infomoney.com.br/mercados/aneel-leiloara-r-553-bi-em-linhas-de-transmissao-weg-pode-sair-entre-beneficiadas/
- Folha de Vilhena — Contrato WEG compensador síncrono (13/07/2026):
  https://folhadevilhena.com.br/13/07/2026/weg-firma-contrato-para-fornecimento-de-solucao-compensadora-ao-sin/
- Global Market Insights — Variable Shunt Reactor Market (fonte fraca, sem evidência específica de produto WEG):
  https://www.gminsights.com/industry-analysis/variable-shunt-reactor-market
- Wikipedia — WEG Industries (uso apenas para porte/contexto geral, não dado técnico):
  https://en.wikipedia.org/wiki/WEG_Industries

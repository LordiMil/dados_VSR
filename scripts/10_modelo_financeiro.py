"""10 - Modelo financeiro e estocastico (camada 2 da calculadora; secoes 2 e 4 do escopo).

Unidade economica (arranjo 2:1, decidido em 14/10/2026): 1 VSR de W/(1-m) Mvar substitui 2 reatores fixos, cada um com seu vao:
  A = reator manobravel de W Mvar (opera como no modelo fisico) e B = fatia permanente de m*W/(1-m) Mvar (quase nunca manobra).
  W = reator de barra mediano do cadastro ONS: 20 Mvar (230 kV, Centro Urbano) e 150 Mvar (500 kV, Campo e Polo eolico).
  A 500 kV o fixo e banco monofasico com fase reserva (3+1R, EPE): o custo da fase reserva entra no lado do fixo (base: 1 fase de W/3
  por banco, como no banco de referencia da EPE; variantes: compartilhada e nenhuma), e e ela que da a franquia de 3 h na falha do fixo.
  Preco do VSR (revisao de 14/10/2026): entrada em R$, ancorada em contratos publicos de 2025-26 (Energinet, Litgrid) escalados por
  Mvar^0,6 x kV^0,5 e convertidos pelo euro do BCB; o premio sobre os fixos vira resultado. Estresse: nivel de preco de 2023.
Fluxos mensais em reais constantes de set/2026, 30 anos, descontados a 12,11% a.a. real (Concessionaria) ou 8,5% (SIN).
Operacoes do disjuntor e do comutador vem do modelo fisico (processed/modelo_fisico_taxas.csv, caso-base 2:1).
Eventos por simulacao: manutencao preventiva (72 meses), revisao geral por contagem, troca do disjuntor no fim da vida mecanica,
falhas maiores e menores do disjuntor (taxa cresce com o numero de ciclos), falhas do reator, do nucleo do VSR e do OLTC,
manutencao do OLTC por numero de comutacoes, Parcela Variavel (Modulo 4 rev.2), energia nao suprida e perdas (so SIN).
VPL incremental = custo do fixo - custo do VSR (positivo = VSR vale mais). Todas as premissas, com fonte ou marcadas como premissa,
vao para processed/financeiro_premissas.csv e para a aba Fin_Premissas.
Uso: python 10_modelo_financeiro.py <pasta_base_PoliVSR-dados> <planilha.xlsx>   (rodar depois do 09)"""
import sys, os, glob, json, time, numpy as np, pandas as pd, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
BASE, XL = sys.argv[1], sys.argv[2]; R = BASE + '/raw/ons/'; P = BASE + '/processed/'
t0 = time.time(); H = 360; S0, ST = int(os.environ.get('S0', 4000)), int(os.environ.get('ST', 1500))

# ======================= 1. Insumos =======================
mac = pd.read_csv(P + 'macro_bcb_mensal.csv', sep=';', encoding='utf-8-sig').set_index('mes')
idx = mac.ipca_indice_base_dez2009.dropna(); FIM = idx.index[-1]
ipca = lambda de: float(idx[FIM] / idx[de])
lit = pd.read_csv(P + 'pesquisa_literatura_2026-10-13.csv', sep=';', encoding='utf-8-sig')
LV = lambda txt: float(lit.loc[lit.parametro.str.startswith(txt), 'provavel'].iloc[0])
disj = pd.read_csv(P + 'bpr_disjuntor_preco_unitario.csv', sep=';', encoding='utf-8-sig')
PDISJ = {kv: float(disj.loc[disj.kv == kv, 'preco_corrigido_IPCA'].iloc[0]) for kv in (230.0, 500.0)}
rap = pd.read_csv(P + 'siget_rap_reatores_estatisticas.csv', sep=';', encoding='utf-8-sig')
RAPFT = {kv: float(rap.loc[(rap.tipo == 'RTB') & (rap.kV == kv), 'mediana'].iloc[0]) for kv in (230.0, 500.0)}
REAT500_MVAR = LV('Reator monofásico 500 kV 66,6 Mvar') * 1e6 / 66.6 * ipca('2021-03')          # EPE mar/2021 -> set/2026
ESCALA230 = (66.6 / 20) ** 0.4                                                                   # premissa: regra de escala (expoente 0,6)
PREAT = {500.0: REAT500_MVAR, 230.0: REAT500_MVAR * ESCALA230}
CRB500 = LV('Conexão de reator de barra (CRB) 500 kV') * 1e6 * ipca('2021-03')
CRB230 = LV('Conexão de reator de barra (CRB) 230 kV') * (LV('Conexão de reator de barra (CRB) 500 kV') / 5.28) * 1e6 * ipca('2021-03')
PVAO = {500.0: CRB500, 230.0: CRB230}
DEFICIT = LV('Custo do déficit'); TSD = LV('Taxa social de desconto') / 100; WACC = 0.1211
tx = pd.read_csv(P + 'modelo_fisico_taxas.csv', sep=';', encoding='utf-8-sig')
J9 = json.load(open(P + 'modelo_fisico_camada1.json', encoding='utf-8'))
NB = J9['meta']['caso_base']['N']
CEN = {'urbano': dict(nome='Centro Urbano', kv=230.0, W=20.0), 'campo': dict(nome='Campo (interligação N–NE)', kv=500.0, W=150.0),
       'polo_eolico': dict(nome='Polo eólico', kv=500.0, W=150.0)}
def fis(cen, m=0.5, k=1.0):
    r = tx[(tx.cenario == cen) & (tx.arranjo == '2:1') & (tx.N == NB[cen]) & np.isclose(tx.m, m) & np.isclose(tx.k, k) & np.isclose(tx.eta, 0.3)].iloc[0]
    return dict(opsA=r.fixo_ops_dia_por_disjuntor_manobravel, opsB=r.fatia_fixa_substituida_ops_dia, opsV=r.vsr_manobras_residuais_dia, taps=r.vsr_taps_dia)
# perdas: posicao media do VSR = media de clip(r, 0, 1) na serie do modelo fisico
d = pd.read_csv(glob.glob(R + '*balanco_dessem_detalhe__CONSOLIDADO*.csv')[0], sep=';')
d['date'] = pd.to_datetime(d.din_programacaodia)
def dser(f):
    g = d[d.cod_subsistema == 'NE'].drop_duplicates(['date', 'num_patamar'])
    c = g.groupby('date').num_patamar.nunique(); g = g[g.date.isin(c[c == 48].index)]
    return f(g).values
fl = pd.read_csv(P + 'fluxo_NNE_horario.csv', sep=';', encoding='utf-8-sig')
UU = {'urbano': np.abs(dser(lambda g: g.val_demanda - g.val_ger_mmgd - g.val_ger_fotovoltaica)), 'campo': np.abs(fl.fluxo_N_para_NE_MW.values),
      'polo_eolico': np.abs(dser(lambda g: g.val_demanda - g.val_ger_mmgd - g.val_ger_fotovoltaica - g.val_ger_eolica))}
RBAR = {}
for c_, u in UU.items():
    lo, hi = J9['series'][c_]['lo'], J9['series'][c_]['hi']
    RBAR[c_] = float(np.clip((hi ** 2 - u ** 2) / (hi ** 2 - lo ** 2), 0, 1).mean())

# ---- preco do VSR: contratos publicos (pesquisa de 14/10/2026) escalados para o VSR de cada cenario ----
EURBRL = float(mac.loc[FIM, 'eur_brl_media'])                        # BCB, media do mes-base (set/2026)
ESC_Q, ESC_KV = 0.6, {'baixo': 0.3, 'central': 0.5, 'alto': 1.0}      # preco ~ Mvar^0,6 x (kV)^beta (premissa)
QREF = {500.0: 300.0, 230.0: 40.0}                                    # VSR do caso-base 2:1: W/(1-m) com m = 50%
U_VSR = {'Energinet': 'https://www.evergabe.com/da/bud/400-kv-reaktor-nup-procurement-of-seven-7-400-kv-70-140-mvar-variable-shunt-reactor-1479773/',
         'Litgrid': 'https://ukininkopatarejas.lt/naujienos/litgrid-pasirase-sutarti-del-triju-valdomu-suntiniu-reaktoriu-pirkimo/',
         'Energinet23': 'https://ted.europa.eu/en/notice/704840-2023/pdf',
         'UIC': 'https://www.energy-community.org/dam/jcr:04918378-b344-4aec-b224-7795c8587321/ECRB%20TEN_E%20UIC%20-%20final.pdf',
         'Melina': 'https://balkangreenenergynews.com/hops-siemens-sign-eur-5-million-contract-under-sincro-grid-project/',
         'Mraclin': 'https://www.hops.hr/vijesti/implementacija-europskog-projekta-naprednih-mreza-sincrogrid-napreduje-prema-planu',
         'PSEG': 'https://www.pjm.com/-/media/planning/rtep-dev/expan-plan-process/ferc-order-1000/rtep-proposal-windows/2023-window-1-redacted-proposals/proposal-2023-w1-107.ashx',
         'BiH': 'https://ebrd.com/work-with-us/projects/psd/53896.html'}
VPC = pd.DataFrame([
 ('C1', 'Litgrid (Lituânia)', 2026, 'AB Kauno tiltai (contratada)', 330, 140, 3, 10.496 / 3, '€ 10,496 mi por 3 unidades', 'fornecimento', 'concorrência pública', 'base', U_VSR['Litgrid']),
 ('C2', 'Energinet (Dinamarca)', 2025, 'GE Vernova (Grid Solutions)', 400, 140, 7, 30.01 / 7, '€ 30,01 mi por 7 unidades (2 lotes)', 'fornecimento',
  '2 propostas por lote (€ 23,9–31,2 mi)', 'base', U_VSR['Energinet']),
 ('C3', 'Energinet (Dinamarca)', 2023, 'Siemens Energy', 400, 140, 5, 38.388505 / 5, '€ 38,39 mi por 5 unidades', 'fornecimento', 'negociado', 'estresse', U_VSR['Energinet23']),
 ('C4', 'Energy Community – índice de custo unitário (3 contratos)', 2025, '—', 400, 200, None, 0.051 * 200, '€ 0,051 mi/Mvar (150–250 Mvar)', 'índice', '—', 'estresse', U_VSR['UIC']),
 ('C5', 'HOPS (Croácia) – Melina', 2019, 'Siemens / Končar', 400, 200, 1, 4.93, 'HRK 36,5 mi', 'com implantação', '—', 'referência (preço anterior a 2021)', U_VSR['Melina']),
 ('C6', 'HOPS (Croácia) – Mraclin', 2019, 'Siemens', 220, 100, 1, 24.9 / 7.45, 'HRK 24,9 mi', 'chave na mão', '—', 'referência (preço anterior a 2021)', U_VSR['Mraclin']),
 ('C7', 'PSEG / PJM (EUA)', 2023, '—', 230, 150, 1, None, 'US$ 29,6 mi por 2 projetos de VSR de 150 Mvar (230 e 345 kV)', 'projeto completo com disjuntores', '—',
  'contexto (escopo de projeto)', U_VSR['PSEG']),
 ('C8', 'Elektroprenos BiH (Bósnia)', 2025, '—', 400, 150, 4, None, '€ 54,3 mi por 4 VSR com vãos e SCADA', 'projeto completo', '—', 'contexto (escopo de projeto)', U_VSR['BiH']),
], columns=['id', 'comprador', 'ano', 'fornecedor', 'tensao_kV', 'mvar_max', 'unidades', 'preco_unit_EUR_mi', 'preco_original', 'escopo', 'concorrencia', 'uso', 'fonte'])
def escala(p_eur, q, kv, kv_alvo, beta):
    return p_eur * (QREF[kv_alvo] / q) ** ESC_Q * (kv_alvo / kv) ** beta * 1e6 * EURBRL
for kv_ in (500.0, 230.0):
    VPC[f'vsr_{int(kv_)}kV_R_central'] = [escala(p, q, k, kv_, ESC_KV['central']) if p == p and p is not None else None
                                          for p, q, k in zip(VPC.preco_unit_EUR_mi, VPC.mvar_max, VPC.tensao_kV)]
PVL, PV_LEVEL = [], {}
for kv_ in (500.0, 230.0):
    b = VPC[VPC.uso == 'base']; s = VPC[VPC.uso == 'estresse']
    cen_ = [escala(p, q, k, kv_, ESC_KV['central']) for p, q, k in zip(b.preco_unit_EUR_mi, b.mvar_max, b.tensao_kV)]
    lo_ = [escala(p, q, k, kv_, ESC_KV['baixo']) for p, q, k in zip(b.preco_unit_EUR_mi, b.mvar_max, b.tensao_kV)]
    hi_ = [escala(p, q, k, kv_, ESC_KV['alto']) for p, q, k in zip(b.preco_unit_EUR_mi, b.mvar_max, b.tensao_kV)]
    st_ = [escala(p, q, k, kv_, ESC_KV['central']) for p, q, k in zip(s.preco_unit_EUR_mi, s.mvar_max, s.tensao_kV)]
    PV_LEVEL[kv_] = {'base': float(np.mean(cen_)), 'baixo': float(min(lo_ + hi_)), 'alto': float(max(lo_ + hi_)),
                     'estresse_baixo': float(min(st_)), 'estresse_alto': float(max(st_))}
    for niv, txt in [('base', 'média dos contratos de 2025–26 (C1, C2), β = 0,5'), ('baixo', 'menor valor dos contratos de 2025–26 com β de 0,3 a 1,0'),
                     ('alto', 'maior valor dos contratos de 2025–26 com β de 0,3 a 1,0'), ('estresse_baixo', 'contrato de 2023 ou índice UIC 2025 (C3, C4), o menor'),
                     ('estresse_alto', 'contrato de 2023 ou índice UIC 2025 (C3, C4), o maior')]:
        PVL.append(dict(kv=int(kv_), nivel=niv, mvar_vsr=QREF[kv_], preco_vsr_R=PV_LEVEL[kv_][niv], metodo=txt))
PVL = pd.DataFrame(PVL)
VPC.to_csv(P + 'pesquisa_precos_vsr.csv', index=False, sep=';', encoding='utf-8-sig')
PREMIO_RAZAO = -0.20     # VSR e fixo na mesma base de preco: razao VSR/fixo ~1,0 por Mvar (Europa) x regra de escala 2^0,6/2 = 0,76

# ---- premissas (valor central, faixa, distribuicao, fonte, status) ----
PREM = [
 ('Unidade', 'Mínimo de regulação do VSR (m)', 0.5, '', 'fixo (slider)', 'Decisão 2.4; CIGRÉ A2-211', 'decisão'),
 ('Unidade', 'Reator manobrável W – 230 kV (Centro Urbano)', 20, 'Mvar', 'fixo', 'Mediana do cadastro ONS (script 06)', 'dado'),
 ('Unidade', 'Reator manobrável W – 500 kV (Campo, Polo eólico)', 150, 'Mvar', 'fixo', 'Mediana do cadastro ONS (script 06)', 'dado'),
 ('Preços', 'Reator fixo 500 kV, por Mvar (set/2026)', REAT500_MVAR, 'R$/Mvar', 'fixo', 'EPE-DEE-NT-077/2021 (R$ 4,415 mi / 66,6 Mvar, mar/2021) × IPCA', 'dado'),
 ('Preços', 'Reator fixo 230 kV, por Mvar (set/2026)', PREAT[230.0], 'R$/Mvar', 'fixo', 'Premissa: 500 kV × (66,6/20)^0,4 (regra de escala)', 'premissa'),
 ('Preços', 'Vão de reator (CRB) 500 kV (set/2026)', CRB500, 'R$', 'fixo', 'EPE-DEE-NT-077/2021 (R$ 9,589 mi, mar/2021) × IPCA', 'dado'),
 ('Preços', 'Vão de reator (CRB) 230 kV (set/2026)', CRB230, 'R$', 'fixo', 'BPR soma direta (R$ 2,28 mi) × razão EPE/BPR do 500 kV (9,589/5,28) × IPCA', 'derivado'),
 ('Preços', 'Disjuntor 230 kV (set/2026)', PDISJ[230.0], 'R$', 'fixo', 'ANEEL BPR × IPCA (P29)', 'dado'),
 ('Preços', 'Disjuntor 500 kV (set/2026)', PDISJ[500.0], 'R$', 'fixo', 'ANEEL BPR × IPCA (P28)', 'dado'),
 ('Preços', 'Preço do VSR 500 kV, 150–300 Mvar (set/2026)', PV_LEVEL[500.0]['base'], 'R$', 'fixo (slider); faixa e estresse em Fin_Precos_VSR',
  'Média dos contratos públicos de 2025–26 (Energinet/GE; Litgrid), escalada por Mvar^0,6 × (kV)^0,5 e convertida a € 1 = R$ %.2f (BCB, set/2026). '
  'Aba Pesquisa_Precos_VSR. Cotação da Hitachi Energy ainda pendente' % EURBRL, 'dado + premissa'),
 ('Preços', 'Preço do VSR 230 kV, 20–40 Mvar (set/2026)', PV_LEVEL[230.0]['base'], 'R$', 'fixo (slider)',
  'Mesmos contratos, escalados para 40 Mvar e 230 kV (extrapolação grande; confiança baixa)', 'dado + premissa'),
 ('Preços', 'Regra de escala do preço do VSR', 'preço ∝ Mvar^0,6 × kV^β; β = 0,5 (faixa 0,3–1,0)', '', 'fixo', 'Premissa (regra dos seis décimos, a mesma do reator de 230 kV)', 'premissa'),
 ('Preços', 'Prêmio do VSR (resultado, não entrada)', 'preço do VSR ÷ preço dos 2 fixos − 1', 'fração', 'derivado',
  'Base: +%.0f%% a 500 kV e +%.0f%% a 230 kV. Variante "mesma base de preço": %.0f%% (razão VSR/fixo ≈ 1 por Mvar na Europa)' % (
      100 * (PV_LEVEL[500.0]['base'] / (300 * REAT500_MVAR) - 1), 100 * (PV_LEVEL[230.0]['base'] / (40 * PREAT[230.0]) - 1), 100 * PREMIO_RAZAO), 'derivado'),
 ('Preços', 'Fase reserva do banco fixo de 500 kV', '1 unidade monofásica de W/3 Mvar por banco (3+1R)', '', 'fixo (variantes: compartilhada; nenhuma)',
  'EPE-DEE-NT-077/2021, Tab. 7-1: banco de barra de referência 3+1R, uma reserva por banco. A fase reserva é o que dá a franquia de 3 h na falha do fixo (Módulo 4 rev.2)', 'dado'),
 ('Receita', 'RAP de FT de reator de barra – 230 kV', RAPFT[230.0], 'R$/ano', 'fixo', 'ANEEL SIGET, mediana (P50)', 'dado'),
 ('Receita', 'RAP de FT de reator de barra – 500 kV', RAPFT[500.0], 'R$/ano', 'fixo', 'ANEEL SIGET, mediana (P51)', 'dado'),
 ('Receita', 'RAP da FT do VSR', 2, '× RAP de uma FT de reator', 'fixo', 'Premissa: mesma receita dos dois fixos (exposição à PV)', 'premissa'),
 ('Parcela Variável', 'Ko / Kp do reator; teto por evento', '150 / 10; 3 PB', '', 'fixo', 'Módulo 4 rev.2 (REN 1.137/2025); teto de 12 meses = 25% de 12 PB', 'dado'),
 ('Parcela Variável', 'Franquia de falha do reator fixo 500 kV com fase reserva', '3 h', '', 'fixo', 'Módulo 4 rev.2, Seção 4.3, item 5.9', 'dado'),
 ('Disjuntor', 'Falha maior – disjuntor de linha (λ0)', '0,23 / 0,25 / 0,28', '%/ano', 'triangular', 'CIGRÉ TB 510 (P58)', 'dado'),
 ('Disjuntor', 'Falha maior – disjuntor de manobra de reator (λref, a 1 ciclo/dia)', '1,98 / 2,46 / 3,02', '%/ano', 'triangular', 'CIGRÉ TB 510 (P57); 1 ciclo/dia é premissa', 'dado + premissa'),
 ('Disjuntor', 'Taxa de falha em função dos ciclos', 'λ = λ0 + (λref − λ0) × ciclos/365', '', 'fórmula', 'Premissa (G02 em Pesquisa_Lacunas)', 'premissa'),
 ('Disjuntor', 'Falhas menores por falha maior', '7,1 – 7,9', '×', 'uniforme', 'CIGRÉ TB 83/510 (derivado)', 'dado'),
 ('Disjuntor', 'Custo de falha menor', '0,5 / 1 / 2', '% do disjuntor', 'triangular', 'Premissa', 'premissa'),
 ('Disjuntor', 'Reparo de falha maior: duração', 'lognormal, mediana 24 h, p90 100 h; 5–15% vão à fábrica (14–42 dias)', '', 'mistura', 'Vikesjö 2008; Karimabadi 2020; GE GL314 (câmara só na fábrica)', 'dado + premissa'),
 ('Disjuntor', 'Reparo de falha maior: custo', '5 / 15 / 30', '% do disjuntor', 'triangular', 'Premissa', 'premissa'),
 ('Disjuntor', 'Falha catastrófica (explosão) entre as falhas maiores', '2 – 8', '%', 'uniforme', 'Premissa (G04); custo 1,5 × disjuntor, 30 dias fora', 'premissa'),
 ('Disjuntor', 'Preventiva regulatória', 'a cada 72 meses; 1 / 2 / 3% do disjuntor; 8 h programadas', '', 'triangular', 'Módulo 4 rev.2 (P56); custo: Jeromin 2009 (≈0,3%/ano)', 'dado + premissa'),
 ('Disjuntor', 'Revisão geral (custo por manutenção – slider)', 0.10, 'fração do disjuntor', 'central × triangular(0,7; 1; 1,3)', 'Jeromin 2009 (≈10% por revisão); slider do site', 'premissa-chave'),
 ('Disjuntor', 'Revisão geral: gatilho', '2.000 / 3.000 / 5.000 ciclos CO ou 20 anos; 24 h programadas', '', 'triangular', 'GE GL314; Hermosillo 2002', 'dado'),
 ('Disjuntor', 'Vida mecânica até a troca', '10.000 ciclos ÷ fator 1–5', 'ciclos CO', 'uniforme no fator', 'IEC 62271-100 M2 (P43); IEEE PES TF 2017, real ≈ 5× menor (P42)', 'dado + premissa'),
 ('Disjuntor', 'Troca do disjuntor', '1,2 × preço; 72 h programadas', '', 'fixo', 'Premissa (instalação)', 'premissa'),
 ('Disjuntor', 'Incerteza das operações do modelo físico', '0,8 / 1 / 1,2', '×', 'triangular', 'Premissa (calibração por plausibilidade, 3.4)', 'premissa'),
 ('Reator', 'Falha grave de reator (por unidade)', '0,30 / 0,41 / 0,53', '%/ano', 'triangular', 'CIGRÉ TB 939; Martin & Tenbohlen 2026; TB 642', 'dado'),
 ('Reator', 'Falha do OLTC (adicional do VSR)', '0,04 / 0,10 / 0,16', '%/ano', 'triangular', 'Derivado de TB 642 × TB 939', 'derivado'),
 ('Reator', 'Reparo de falha grave do reator/VSR sem reserva', 'lognormal, mediana 180 d, p90 540 d; custo 30–100% do equipamento', '', 'lognormal / uniforme', 'Belknap (AEP) 2015; prazos de fábrica 80–210 semanas', 'premissa'),
 ('Reator', 'Falha do OLTC: duração e custo', '3–21 dias; 5–15% do VSR', '', 'uniforme', 'Premissa (G06)', 'premissa'),
 ('VSR', 'Operações de tap: fator sobre o piso do modelo físico', '1 – 2', '×', 'uniforme', 'Premissa (resolução de 30 min a 1 h)', 'premissa'),
 ('VSR', 'Manutenção do OLTC a vácuo', 'a cada 300.000 comutações; 1 / 2 / 3% do VSR; 48 h programadas', '', 'triangular',
  'MR VACUTAP VR/VRX (versão para VSR; relatório de ensaio VR 2E 001e); padrão de mercado (H3); custo: premissa (G06)', 'dado + premissa'),
 ('VSR', 'Manutenção do OLTC a óleo (teste de estresse)', '20–50 mil comutações ou 4–7 anos', '', 'uniforme', 'MR OILTAP R, Um ≥ 245 kV; improvável em VSR novo (H3)', 'dado'),
 ('VSR', 'Reserva do VSR (variantes)', 'sem reserva (base); 1 reserva para 3 VSR; pool de 1 para 10', '', 'variante',
  'Base: reparo longo com Parcela Variável. Pool: BPA mantém reatores de reserva de 500 kV para 30 instalados (H6)', 'dado + premissa'),
 ('Vão', 'O&M de rotina do vão (exceto disjuntor)', '0,5 / 1 / 2', '% do vão por ano', 'triangular', 'Premissa; teto = CAOM 2% do VNR (NT 103/2024-STR)', 'premissa'),
 ('SIN', 'Probabilidade de corte de carga dada falha maior do disjuntor do reator', '2 – 10', '%', 'uniforme', 'Premissa (G14)', 'premissa'),
 ('SIN', 'Energia não suprida por corte', 'lognormal, mediana 11,5 MWh, p90 140 MWh', 'MWh', 'lognormal', 'ONS interrupção de carga 2016–2025 (P75)', 'dado'),
 ('SIN', 'Custo do déficit', DEFICIT, 'R$/MWh', 'fixo', 'NT 11/2025/GPRE/GEPME/AGM (P65)', 'dado'),
 ('SIN', 'Perdas do reator', '1,55 kW/Mvar pleno; VSR na posição mínima = 62% do pleno', '', 'fixo', 'IPST 2015 (HOPS 420 kV)', 'dado'),
 ('SIN', 'Valor da energia das perdas', '150 / 250 / 400', 'R$/MWh', 'triangular', 'Premissa sem fonte (CME da EPE não localizado)', 'premissa'),
 ('Financeiro', 'Taxa de desconto – Concessionária', WACC, 'a.a. real', 'fixo (slider)', 'Despacho ANEEL 675/2026 (pré-impostos)', 'dado'),
 ('Financeiro', 'Taxa de desconto – SIN', TSD, 'a.a. real', 'fixo', 'NT SEI 19911/2020/ME', 'dado'),
 ('Financeiro', 'Horizonte', 30, 'anos', 'fixo', 'Decisão 2.3', 'decisão'),
]
PRM = pd.DataFrame(PREM, columns=['grupo', 'parametro', 'valor_central', 'unidade', 'distribuicao', 'fonte', 'status'])
PRM.to_csv(P + 'financeiro_premissas.csv', index=False, sep=';', encoding='utf-8-sig')

# ---- pesquisa propria das perguntas a Hitachi Energy (escopo 6.8), 14/10/2026 ----
PH = pd.DataFrame([
 ('H1', 'Preço do VSR e prêmio sobre os reatores fixos que ele substitui (só equipamento)',
  'Sem cotação pública para 500 kV no Brasil, mas há contratos públicos reais (aba Pesquisa_Precos_VSR): Litgrid 2026, 330 kV 140 Mvar, € 3,5 mi por unidade; '
  'Energinet 2025 (GE Vernova, 2 propostas por lote), 400 kV 70–140 Mvar, € 4,3 mi; Energinet 2023 (Siemens Energy), € 7,7 mi; HOPS 2019, € 3,3–4,9 mi; '
  'índice da Energy Community 2025, € 51 mil/Mvar. Escalados para o VSR de 500 kV e 150–300 Mvar: R$ 40–53 mi com os contratos de 2025–26 e R$ 80–95 mi '
  'no nível de 2023. Na Europa, o VSR recente custa por Mvar quase o mesmo que um reator fixo (€ 25–31 mil contra € 26–38 mil, National Grid 2024 e NEP 2023).',
  'R$ 40–53 mi (500 kV, contratos 2025–26); estresse R$ 80–95 mi', 'média (preços reais; escala para 500 kV é premissa)',
  'https://www.evergabe.com/da/bud/400-kv-reaktor-nup-procurement-of-seven-7-400-kv-70-140-mvar-variable-shunt-reactor-1479773/ | '
  'https://ukininkopatarejas.lt/naujienos/litgrid-pasirase-sutarti-del-triju-valdomu-suntiniu-reaktoriu-pirkimo/ | https://ted.europa.eu/en/notice/704840-2023/pdf | '
  'https://www.energy-community.org/dam/jcr:04918378-b344-4aec-b224-7795c8587321/ECRB%20TEN_E%20UIC%20-%20final.pdf | '
  'https://www.nationalgrid.com/document/353111/download',
  'O preço do VSR passa a ser entrada em R$ (média dos contratos de 2025–26); o prêmio vira resultado. Variantes: faixa baixa e alta, estresse no nível de 2023 e mesma base de preço (prêmio de −20%).'),
 ('H2', 'Mínimo de regulação viável a 230 kV e a 500 kV',
  '400–420 kV: 40–55% com OLTC convencional (MR: faixa máxima de 60%; ABB: 45–60%; Energinet ≥ 50%); 20% com projeto avançado e mais caro (Siemens/Amprion 50–250 Mvar). '
  '230 kV: faixa maior (242 kV 50–100 Mvar; fator 2,5 a 150 kV). 500 kV: primeiro VSR da Hitachi Energy em 2024 (Uzbequistão); portfólio declarado até 550 kV e 300 Mvar trifásico; '
  'MR: até 60% de faixa a 800 kV com projeto avançado.',
  'm = 40–55% (convencional); 20% possível', 'média',
  'https://www.reinhausen.com/fileadmin/media/mediathek/variable_active_and_reactive_power_control.pdf | '
  'https://www.hitachienergy.com/products-and-solutions/transformers/reactors-and-inductors/variable-shunt-reactors | '
  'https://www.hitachienergy.com/us/en/news-and-events/features/2024/10/hitachi-energy-scales-up-variable-shunt-reactor-to-500-kv-for-wind-power-applications | '
  'https://publications.lib.chalmers.se/records/fulltext/174457/174457.pdf',
  'm = 50% mantido. O VSR de 300 Mvar a 500 kV do arranjo 2:1 está no limite do portfólio declarado.'),
 ('H3', 'Tipo de OLTC e intervalo de manutenção',
  'Vácuo é o padrão: o MR VACUTAP VR/VRX tem versão para VSR, com manutenção a cada 300 mil operações e sem limite de tempo; Siemens/Amprion usam MR. '
  'A Hitachi Energy tem OLTC a vácuo próprio (VUCL, Um até 362 kV), o que sugere comutador no lado do neutro a 500 kV (inferência).',
  'vácuo; 300 mil operações', 'média',
  'https://storage.mtender.gov.md/get/2a2d98ca-c41b-473d-9516-24c74de21023-1701691313734 | '
  'https://www.hitachienergy.com/us/en/products-and-solutions/insulation-and-components/transformer-insulation-components/tap-changers/vacuum-on-load-tap-changers/on-load-tap-changers-type-vucl',
  'OLTC a óleo passa a teste de estresse.'),
 ('H4', 'Operações de tap por dia em serviço',
  'Sem dado público de campo. Statnett: controle lento, com necessidade de manutenção "limitada" (CIGRÉ A2-211/2014).',
  'sem dado (modelo: ~90–105/dia, conservador)', 'sem dado',
  'https://www.hitachienergy.com/content/dam/pg/references/files/variable-shunt-reactors-cigre2014-a2-211-2014.pdf',
  'Sem mudança; com OLTC a vácuo, manutenção a cada 8–9 anos.'),
 ('H5', 'Taxa de falha da frota de VSR e tempo de reparo',
  'Sem estatística pública; a Hitachi Energy alega o "menor MTBF do setor" sem número. Proxies: CIGRÉ TB 939 (1.204 falhas graves em 425 mil unidades-ano, ≈ 0,28%/ano); '
  'parcela do comutador 12–31% das falhas graves (TB 642, transformadores).',
  '≈ 0,3%/ano (proxy)', 'baixa (proxy)',
  'https://electra.cigre.org/336-october-2024/technical-brochures/analysis-of-ac-transformer-reliability | '
  'https://www.nsenergybusiness.com/features/featurea-new-assessment-of-power-transformer-reliability-6045374/',
  'Premissas mantidas.'),
 ('H6', 'Reserva de VSR trifásico',
  'Concessionárias raramente guardam reserva trifásica, por custo (Chalmers). A BPA mantém reatores de reserva de 500 kV para 30 instalados. '
  'A Statnett usa o VSR como reserva flexível, porque ele serve em várias posições (CIGRÉ A2-211/2014; ABB Review). No Brasil, o banco de 500 kV de referência é monofásico 3+1R (EPE).',
  'pool ~1 para 10', 'média',
  'https://www.bpa.gov/-/media/Aep/finance/asset-management/public-materials-project-synopsis/ross-heatline-replace-500-kv-system-spare-shunt-reactors.pdf | '
  'https://publications.lib.chalmers.se/records/fulltext/174457/174457.pdf',
  'A fase reserva passa a ser cobrada no fixo de 500 kV (antes ele tinha a franquia de 3 h sem pagar a fase). Nova variante: reserva do VSR em pool de 1 para 10.'),
 ('H7', 'Custo e efeito da manobra controlada (Switchsync) no disjuntor de reator',
  'Sem preço público. A 500 kV o disjuntor já tem polos independentes: custo = controlador e fiação; a 230 kV pode exigir disjuntor novo (SEL 2008). '
  'Evita o reacendimento do arco na abertura, principal causa de falha de disjuntor de reator: a BPA exige em disjuntores novos de reator, a PSEG adotou após falhas (PJM 2026), '
  'a Transgrid especifica nos vãos de reator. Não reduz o número de manobras.',
  'sem preço público', 'média (efeito); sem dado (custo)',
  'https://static.selinc.com/assets/Literature/Publications/Technical%20Papers/6288_ControlledSwitching_DT-JP-DG_20080206_Web.pdf | '
  'https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2026/20260707/20260707-item-15---reliability-analysis-update.pdf | '
  'https://www.transgrid.com.au/media/2n0mdu1u/transgrid-pscr_improving-voltage-control-in-southern-nsw.pdf',
  'O contrafactual 2.8 (fixo com manobra controlada) é a prática atual; ele reduz só a taxa de falha do disjuntor, que pesa menos de R$ 0,5 mi no tornado.'),
], columns=['id', 'pergunta', 'resposta', 'valor_ou_faixa', 'confianca', 'fontes', 'implicacao_no_modelo'])
PH.to_csv(P + 'pesquisa_perguntas_hitachi.csv', index=False, sep=';', encoding='utf-8-sig')
print('Preços set/2026: reator 500 kV %.0f R$/Mvar; 230 kV %.0f; vão 500 %.2f mi; vão 230 %.2f mi; disj 500 %.2f mi; 230 %.2f mi | r̄' % (
      REAT500_MVAR, PREAT[230.0], CRB500 / 1e6, CRB230 / 1e6, PDISJ[500.0] / 1e6, PDISJ[230.0] / 1e6), {k: round(v, 3) for k, v in RBAR.items()})

# ======================= 2. Simulacao =======================
tri = lambda rng, a, m, b, n: rng.triangular(a, m, b, n)
def pv_forcado(PB, Dmin):
    return np.minimum(PB * (150 * np.minimum(Dmin, 300) + 10 * np.maximum(Dmin - 300, 0)) / 43200, 3 * PB * np.ceil(Dmin / 525600))
pv_prog = lambda PB, Dh: PB * 10 * Dh * 60 / 43200

def simular(cen, visao, S, seed, fix=None, premio=None, preco='base', regime='leilao', premio_rap=False, oltc='vacuo', reserva='sem', m=0.5, k=1.0,
            crev=0.10, taxa=None, fase_reserva='por_banco'):
    """preco (do VSR, R$ dos contratos escalados): 'base' | 'baixo' | 'alto' | 'estresse_baixo' | 'estresse_alto'; premio (fracao) substitui o preco.
    reserva (do VSR): 'sem' | '1:3' | '1:10'.  fase_reserva (do fixo de 500 kV): 'por_banco' | 'compartilhada' | 'nenhuma'."""
    fix = fix or {}; rng = np.random.default_rng(seed); c = CEN[cen]; kv = c['kv']; W = c['W']
    SB, SV = m * W / (1 - m), W / (1 - m)
    pD, pR, pV = PDISJ[kv], PREAT[kv], PVAO[kv]
    i = taxa if taxa is not None else (WACC if visao == 'concessionaria' else TSD)
    im = (1 + i) ** (1 / 12) - 1; disc = (1 + im) ** -np.arange(H + 1)
    fz = lambda name, draw: np.full(S, fix[name], float) if name in fix else draw
    # ---- sorteios ----
    lam0 = fz('lam0', tri(rng, .0023, .0025, .0028, S)); lref = fz('lam_ref', tri(rng, .0198, .0246, .0302, S))
    fops = fz('f_ops', tri(rng, .8, 1, 1.2, S)); ftap = fz('f_taps', rng.uniform(1, 2, S))
    nrev = fz('n_rev', tri(rng, 2000, 3000, 5000, S)); flife = fz('f_vida', rng.uniform(1, 5, S)); life = 10000 / flife
    cprev = tri(rng, .01, .02, .03, S); crv = crev * fz('f_crev', tri(rng, .7, 1, 1.3, S)); cmi = tri(rng, .005, .01, .02, S); rmi = rng.uniform(7.1, 7.9, S)
    ccor = tri(rng, .05, .15, .30, S); pcat = fz('p_cat', rng.uniform(.02, .08, S)); plong = rng.uniform(.05, .15, S)
    lamR = fz('lam_R', tri(rng, .003, .0041, .0053, S)); lamO = fz('lam_O', tri(rng, .0004, .001, .0016, S))
    coltc = tri(rng, .01, .02, .03, S); om = fz('om_vao', tri(rng, .005, .01, .02, S))
    pint = fz('p_int', rng.uniform(.02, .10, S)); vE = fz('v_E', tri(rng, 150, 250, 400, S))
    f = fis(cen, m, k)
    # ---- unidade e precos ----
    prA, prB = W * pR, SB * pR; prFix = prA + prB
    prVSR = prFix * (1 + premio) if premio is not None else PV_LEVEL[kv][preco] * (SV / QREF[kv]) ** ESC_Q
    RAPft = RAPFT[kv]; PB = {'A': RAPft / 12, 'B': RAPft / 12, 'V': 2 * RAPft / 12}
    conc = visao == 'concessionaria'
    CF = {'fixo': np.zeros((S, H + 1)), 'vsr': np.zeros((S, H + 1))}; PVC = {}
    def add(alt, comp, sims, months, amt):
        sims = np.asarray(sims); months = np.asarray(months); amt = np.broadcast_to(np.asarray(amt, float), sims.shape)
        if sims.size == 0: return
        np.add.at(CF[alt], (sims, months), amt)
        PVC[(alt, comp)] = PVC.get((alt, comp), np.zeros(S)) + np.bincount(sims, weights=amt * disc[months], minlength=S)
    allS = np.arange(S)
    # ---- CAPEX ----
    add('fixo', 'CAPEX reatores', allS, np.zeros(S, int), prFix); add('vsr', 'CAPEX reatores', allS, np.zeros(S, int), prFix)
    add('vsr', 'Prêmio do VSR', allS, np.zeros(S, int), prVSR - prFix)
    add('fixo', 'CAPEX vão', allS, np.zeros(S, int), 2 * pV); add('vsr', 'CAPEX vão', allS, np.zeros(S, int), pV)
    # fase reserva do banco monofasico de 500 kV (3+1R, EPE): e ela que da a franquia de 3 h na falha do fixo
    tem_fase = kv == 500.0 and fase_reserva != 'nenhuma'
    if tem_fase:
        prRes = (max(W, SB) / 3 if fase_reserva == 'compartilhada' else (W + SB) / 3) * pR
        add('fixo', 'Fase reserva do fixo', allS, np.zeros(S, int), prRes)
    frac_res = {'sem': 0.0, '1:3': 1 / 3, '1:10': 1 / 10}[reserva]
    if frac_res: add('vsr', 'Reserva do VSR', allS, np.zeros(S, int), prVSR * frac_res)
    meses = np.arange(1, H + 1)
    # ---- O&M de rotina do vao ----
    add('fixo', 'O&M do vão', np.repeat(allS, H), np.tile(meses, S), np.repeat(2 * om * (pV - pD) / 12, H))
    add('vsr', 'O&M do vão', np.repeat(allS, H), np.tile(meses, S), np.repeat(om * (pV - pD) / 12, H))
    # ---- disjuntores ----
    def disjuntor(alt, key, ops_dia):
        cyc_m = np.maximum(ops_dia * fops / 2 * 30.4375, 1e-9)          # ciclos CO por mes
        lam = lam0 + (lref - lam0) * cyc_m * 12 / 365                    # falhas maiores por ano
        # preventiva a cada 72 meses
        mp = np.arange(72, H + 1, 72); ss = np.repeat(allS, len(mp)); mm = np.tile(mp, S)
        add(alt, 'Manutenção preventiva', ss, mm, np.repeat(cprev * pD, len(mp)))
        if conc: add(alt, 'Parcela Variável', ss, mm, pv_prog(PB[key], 8))
        # revisao geral e troca (laco por simulacao)
        rs, rm, ra, ts, tm = [], [], [], [], []
        for s in range(S):
            Trep = life[s] / cyc_m[s]; Trev = min(nrev[s] / cyc_m[s], 240.0); ini = 0.0
            while ini < H:
                fim = ini + Trep; t = ini + Trev
                while t < min(fim, H + 1e-9):
                    rs.append(s); rm.append(int(np.ceil(t))); ra.append(crv[s] * pD); t += Trev
                if fim <= H: ts.append(s); tm.append(int(np.ceil(fim)))
                ini = fim
        add(alt, 'Revisão geral', rs, np.minimum(rm, H), ra)
        add(alt, 'Troca do disjuntor', ts, np.minimum(tm, H), 1.2 * pD)
        if conc:
            add(alt, 'Parcela Variável', rs, np.minimum(rm, H), pv_prog(PB[key], 24)); add(alt, 'Parcela Variável', ts, np.minimum(tm, H), pv_prog(PB[key], 72))
        # falhas maiores
        cnt = rng.poisson(np.repeat((lam / 12)[:, None], H, 1)); ss, mi = np.nonzero(cnt); n = cnt[ss, mi]
        ss = np.repeat(ss, n); mi = np.repeat(mi, n) + 1; ne = ss.size
        if ne:
            cat = rng.random(ne) < pcat[ss]; lng = rng.random(ne) < plong[ss]
            Dh = np.where(cat, 720.0, np.where(lng, rng.uniform(14, 42, ne) * 24, np.exp(np.log(24) + 1.113 * rng.standard_normal(ne))))
            cost = np.where(cat, 1.5 * pD, ccor[ss] * pD)
            add(alt, 'Falhas do disjuntor', ss, mi, cost)
            if conc: add(alt, 'Parcela Variável', ss, mi, pv_forcado(PB[key], Dh * 60))
            else:
                ens = (rng.random(ne) < pint[ss]) * np.exp(np.log(11.47) + 1.95 * rng.standard_normal(ne))
                add(alt, 'Energia não suprida', ss, mi, ens * DEFICIT)
        # falhas menores
        cnt = rng.poisson(np.repeat((lam * rmi / 12)[:, None], H, 1)); ss, mi = np.nonzero(cnt); n = cnt[ss, mi]
        add(alt, 'Falhas do disjuntor', np.repeat(ss, n), np.repeat(mi, n) + 1, np.repeat(cmi[ss] * pD, n))
        return cyc_m
    cA = disjuntor('fixo', 'A', f['opsA']); cB = disjuntor('fixo', 'B', f['opsB']); cV = disjuntor('vsr', 'V', f['opsV'])
    # ---- falhas de reator ----
    def falha_reator(alt, key, lamv, preco, longa, cmin=.3, cmax=1.0, dur=None):
        cnt = rng.poisson(np.repeat((lamv / 12)[:, None], H, 1)); ss, mi = np.nonzero(cnt); n = cnt[ss, mi]
        ss = np.repeat(ss, n); mi = np.repeat(mi, n) + 1; ne = ss.size
        if ne == 0: return
        add(alt, 'Falhas do reator/VSR', ss, mi, rng.uniform(cmin, cmax, ne) * preco)
        if conc and longa:
            Dd = dur(ne) if dur else np.exp(np.log(180) + 0.857 * rng.standard_normal(ne))
            add(alt, 'Parcela Variável', ss, mi, pv_forcado(PB[key], Dd * 1440))
    longa_fixo = not tem_fase                                            # com fase reserva: franquia de 3 h, sem Parcela Variavel longa
    falha_reator('fixo', 'A', lamR, prA, longa_fixo); falha_reator('fixo', 'B', lamR, prB, longa_fixo)
    falha_reator('vsr', 'V', lamR, prVSR, True, dur=(lambda n: np.full(n, 30.0)) if frac_res else None)
    falha_reator('vsr', 'V', lamO, prVSR, True, .05, .15, dur=lambda n: rng.uniform(3, 21, n))
    # ---- manutencao do OLTC ----
    tap_m = f['taps'] * ftap * 30.4375
    if oltc == 'vacuo': Tol = 300000 / tap_m
    else: Tol = np.minimum(rng.uniform(20000, 50000, S) / tap_m, rng.uniform(48, 84, S))
    ss, mm = [], []
    for s in range(S):
        t = Tol[s]
        while t <= H: ss.append(s); mm.append(int(np.ceil(t))); t += Tol[s]
    ss = np.array(ss, int); mm = np.minimum(np.array(mm, int), H)
    add('vsr', 'Manutenção do OLTC', ss, mm, coltc[ss] * prVSR)
    if conc: add('vsr', 'Parcela Variável', ss, mm, pv_prog(PB['V'], 48))
    # ---- perdas (SIN) ----
    if not conc:
        rb = RBAR[cen]; lk = 1.55                                          # kW/Mvar
        dkw = lk * (SV * (0.62 + 0.38 * rb) - (SB + W * rb))              # VSR - fixo, kW medios
        add('vsr', 'Perdas', np.repeat(allS, H), np.tile(meses, S), np.repeat(dkw * 8760 / 12 / 1000 * vE, H))
    # ---- ajustes regulatorios (so Concessionaria) ----
    crf = im / (1 - (1 + im) ** -H)
    if conc and regime == 'reforco':
        add('vsr', 'RAP (ajuste regulatório)', np.repeat(allS, H), np.tile(meses, S), np.full(S * H, pV * crf))
    if conc and premio_rap:
        add('vsr', 'RAP (ajuste regulatório)', np.repeat(allS, H), np.tile(meses, S), np.full(S * H, -(prVSR - prFix) * crf))
    # ---- metricas ----
    inc = (CF['fixo'] - CF['vsr']) * disc; cum = np.cumsum(inc, 1)
    vpl = cum[:, -1]
    neg = cum < 0; has = neg.any(1); last = H - np.argmax(neg[:, ::-1], 1)          # ultimo mes com acumulado negativo
    pay = np.where(has, last + 1, 0).astype(float); pay[vpl < 0] = np.nan             # payback definitivo; VPL < 0 = sem payback
    pay[has & (last >= H)] = np.nan
    # vpl linear no premio: dV/dpremio (custo do premio + itens proporcionais ao preco do VSR)
    out = dict(vpl=vpl, payback=pay, CFd={a: np.cumsum(CF[a] * disc, 1) for a in CF}, PVC=PVC, prFix=prFix, prVSR=prVSR, pV=pV,
               cyc=dict(A=cA, B=cB, V=cV), taps_ano=tap_m * 12, Tol=Tol, f=f, life=life, nrev=nrev)
    return out

def resumo(o):
    v, p = o['vpl'], o['payback']
    pc = np.where(np.isnan(p), np.inf, p)                                # sem payback no horizonte = censurado (> 360 meses)
    qp = lambda x: (lambda z: float(z) if np.isfinite(z) else np.nan)(np.percentile(pc, x, method='lower'))
    return dict(vpl_p10=float(np.percentile(v, 10)), vpl_p50=float(np.percentile(v, 50)), vpl_p90=float(np.percentile(v, 90)), vpl_media=float(v.mean()),
                p_vpl_pos=float((v > 0).mean()),
                payback_meses_p10=qp(10), payback_meses_p50=qp(50), payback_meses_p90=qp(90),
                pct_payback_imediato=float((p == 0).mean()), pct_sem_payback=float(np.isnan(p).mean()))

# ======================= 3. Execucao =======================
rows, casc, fan, hist, curva, oper, torn = [], [], [], [], [], [], []
JS = {}
for cen in CEN:
    for vis in ('concessionaria', 'sin'):
        o = simular(cen, vis, S0, 11)
        o0 = simular(cen, vis, S0, 11, premio=0.0)                       # mesmos numeros aleatorios: VPL linear no premio
        o1 = simular(cen, vis, S0, 11, premio=1.0)
        dvdp = o0['vpl'] - o1['vpl']                                     # perda de VPL por unidade de premio (fracao)
        be = o0['vpl'] / dvdp                                            # premio de equilibrio (fracao dos reatores substituidos)
        pb = o['prVSR'] / o['prFix'] - 1                                 # premio implicito no preco-base do VSR
        r = dict(cenario=cen, visao=vis, variante='base', **resumo(o), preco_vsr_R=o['prVSR'], premio_implicito=pb,
                 premio_equilibrio_p10=float(np.percentile(be, 10)), premio_equilibrio_p50=float(np.percentile(be, 50)), premio_equilibrio_p90=float(np.percentile(be, 90)),
                 preco_vsr_equilibrio_p10_R=float(np.percentile(be, 10) * o['prFix'] + o['prFix']), preco_vsr_equilibrio_p50_R=float(np.percentile(be, 50) * o['prFix'] + o['prFix']),
                 preco_vsr_equilibrio_p90_R=float(np.percentile(be, 90) * o['prFix'] + o['prFix']), reatores_substituidos_R=o['prFix'], vao_evitado_R=o['pV'])
        rows.append(r)
        if vis == 'concessionaria':
            VAR = [('regime: reforço com RAP pelo BPR', dict(regime='reforco')), ('prêmio reconhecido na RAP', dict(premio_rap=True)),
                   ('OLTC a óleo (teste de estresse)', dict(oltc='oleo')), ('reserva do VSR: 1 para 3', dict(reserva='1:3')),
                   ('reserva do VSR: pool 1 para 10', dict(reserva='1:10')),
                   ('preço do VSR: faixa baixa (contratos 2025–26)', dict(preco='baixo')), ('preço do VSR: faixa alta (contratos 2025–26)', dict(preco='alto')),
                   ('preço do VSR: estresse, nível de 2023 (menor)', dict(preco='estresse_baixo')),
                   ('preço do VSR: estresse, nível de 2023 (maior)', dict(preco='estresse_alto')),
                   ('VSR e fixo na mesma base de preço (prêmio de −20%)', dict(premio=PREMIO_RAZAO)),
                   ('prêmio de 50% (premissa anterior)', dict(premio=0.5))]
            if CEN[cen]['kv'] == 500.0:
                VAR[5:5] = [('fase reserva do fixo: uma compartilhada pelos 2 bancos', dict(fase_reserva='compartilhada')),
                            ('fase reserva do fixo: nenhuma (sem custo e sem franquia)', dict(fase_reserva='nenhuma'))]
            for nome, kw in VAR:
                ov = simular(cen, vis, S0, 11, **kw)
                rows.append(dict(cenario=cen, visao=vis, variante=nome, **resumo(ov), preco_vsr_R=ov['prVSR'], premio_implicito=ov['prVSR'] / ov['prFix'] - 1))
        # cascata (media do valor presente por componente, fixo - VSR)
        comps = sorted({c_ for (_, c_) in o['PVC']})
        for c_ in comps:
            a = o['PVC'].get(('fixo', c_), np.zeros(S0)).mean(); b = o['PVC'].get(('vsr', c_), np.zeros(S0)).mean()
            casc.append(dict(cenario=cen, visao=vis, componente=c_, vp_fixo=a, vp_vsr=b, ganho_vsr=a - b))
        # nevoa (custo acumulado descontado, por ano)
        for y in range(31):
            mth = 12 * y
            for alt in ('fixo', 'vsr'):
                vv = o['CFd'][alt][:, mth]
                fan.append(dict(cenario=cen, visao=vis, ano=y, alternativa=alt, p10=np.percentile(vv, 10), p25=np.percentile(vv, 25), p50=np.percentile(vv, 50),
                                p75=np.percentile(vv, 75), p90=np.percentile(vv, 90)))
        # histograma do VPL
        hcnt, edges = np.histogram(o['vpl'], bins=30)
        for j_ in range(30): hist.append(dict(cenario=cen, visao=vis, de=edges[j_], ate=edges[j_ + 1], simulacoes=int(hcnt[j_])))
        # VPL x premio
        for pr in np.round(np.arange(0, 2.01, 0.1), 2):
            vv = o0['vpl'] - dvdp * pr
            curva.append(dict(cenario=cen, visao=vis, premio=pr, premio_R=pr * o['prFix'], preco_vsr_R=(1 + pr) * o['prFix'], vpl_p10=np.percentile(vv, 10), vpl_p50=np.percentile(vv, 50),
                              vpl_p90=np.percentile(vv, 90), p_vpl_pos=(vv > 0).mean()))
        # operacionais
        if vis == 'concessionaria':
            cA, cV = o['cyc']['A'], o['cyc']['V']
            oper.append(dict(cenario=cen, ops_fixo_ano=float(np.median(cA) * 2 * 12), ops_vsr_ano=float(np.median(cV) * 2 * 12),
                             manobras_evitadas_ano=float(np.median(cA - cV) * 2 * 12 + o['f']['opsB'] * 365),
                             anos_ate_revisao_fixo=float(np.median(np.minimum(o['nrev'] / cA, 240)) / 12), anos_ate_revisao_vsr=float(np.median(np.minimum(o['nrev'] / cV, 240)) / 12),
                             anos_ate_troca_fixo=float(min(np.median(o['life'] / cA) / 12, 100)), anos_ate_troca_vsr=float(min(np.median(o['life'] / cV) / 12, 100)),
                             taps_vsr_ano=float(np.median(o['taps_ano'])), anos_entre_manut_oltc=float(np.median(o['Tol']) / 12),
                             falhas_maiores_disj_fixo_30a=float(np.median((0.0025 + (0.0246 - 0.0025) * cA * 12 / 365) * 30)),
                             falhas_maiores_disj_vsr_30a=float(np.median((0.0025 + (0.0246 - 0.0025) * cV * 12 / 365) * 30))))
        # tornado
        base_mean = float(o['vpl'].mean())
        TV = [('Preço do VSR (contratos de 2025–26: faixa baixa – alta)', dict(preco='baixo'), dict(preco='alto')),
              ('Falha do disjuntor de reator (1,98 – 3,02%/ano)', dict(fix={'lam_ref': .0198}), dict(fix={'lam_ref': .0302})),
              ('Falha do disjuntor de reator: tanque morto 1,17 – tanque vivo 6,79%/ano', dict(fix={'lam_ref': .0117}), dict(fix={'lam_ref': .0679})),
              ('Vida mecânica: real = nominal ÷ 1 – ÷ 5', dict(fix={'f_vida': 1.0}), dict(fix={'f_vida': 5.0})),
              ('Revisão geral a cada 5.000 – 2.000 ciclos', dict(fix={'n_rev': 5000}), dict(fix={'n_rev': 2000})),
              ('Custo da revisão geral (5% – 20% do disjuntor)', dict(crev=0.05), dict(crev=0.20)),
              ('Volatilidade 0,5× – 2× (slider)', dict(k=0.5), dict(k=2.0)),
              ('Mínimo de regulação 60% – 20% (slider)', dict(m=0.6), dict(m=0.2)),
              ('O&M de rotina do vão (0,5% – 2%/ano)', dict(fix={'om_vao': .005}), dict(fix={'om_vao': .02})),
              ('Falha grave do reator/VSR (0,30 – 0,53%/ano)', dict(fix={'lam_R': .003}), dict(fix={'lam_R': .0053})),
              ('OLTC: vácuo – óleo', dict(oltc='vacuo'), dict(oltc='oleo')),
              ('Taxa de desconto (8% – 14%)', dict(taxa=0.08), dict(taxa=0.14))]
        if CEN[cen]['kv'] == 500.0:
            TV += [('Fase reserva do fixo: nenhuma – uma por banco', dict(fase_reserva='nenhuma'), dict(fase_reserva='por_banco'))]
        if vis == 'sin':
            TV += [('Valor da energia das perdas (R$ 150 – 400/MWh)', dict(fix={'v_E': 150}), dict(fix={'v_E': 400})),
                   ('Corte de carga por falha do disjuntor (2% – 10%)', dict(fix={'p_int': .02}), dict(fix={'p_int': .10}))]
        for nome, lo, hi in TV:
            vl = float(simular(cen, vis, ST, 7, **lo)['vpl'].mean()); vh = float(simular(cen, vis, ST, 7, **hi)['vpl'].mean())
            torn.append(dict(cenario=cen, visao=vis, variavel=nome, vpl_baixo=vl, vpl_alto=vh, amplitude=abs(vh - vl), vpl_base_media=base_mean))
        print(f'{cen}/{vis}: VPL P50 {r["vpl_p50"] / 1e6:.2f} mi (P10 {r["vpl_p10"] / 1e6:.2f}, P90 {r["vpl_p90"] / 1e6:.2f}); P(VPL>0) {r["p_vpl_pos"]:.2f}; '
              f'payback P50 {r["payback_meses_p50"]} m; VSR R$ {r["preco_vsr_R"] / 1e6:.1f} mi (prêmio {r["premio_implicito"]:+.0%}); '
              f'equilíbrio P50 R$ {r["preco_vsr_equilibrio_p50_R"] / 1e6:.1f} mi ({r["premio_equilibrio_p50"]:+.0%}) ({time.time() - t0:.0f}s)')
CA = pd.DataFrame(rows); CS = pd.DataFrame(casc); FN = pd.DataFrame(fan); HI = pd.DataFrame(hist); CU = pd.DataFrame(curva); OP = pd.DataFrame(oper)
TO = pd.DataFrame(torn).sort_values(['cenario', 'visao', 'amplitude'], ascending=[True, True, False])
for nm, df_ in [('cartoes', CA), ('cascata', CS), ('nevoa', FN), ('histograma', HI), ('vpl_premio', CU), ('operacionais', OP), ('tornado', TO)]:
    for c_ in df_.columns:
        if df_[c_].dtype.kind == 'f': df_[c_] = df_[c_].round(4)
    df_.to_csv(P + f'financeiro_{nm}.csv', index=False, sep=';', encoding='utf-8-sig')
json.dump(dict(meta=dict(gerado_em='2026-10-14', script='scripts/10_modelo_financeiro.py', simulacoes=S0, simulacoes_tornado=ST, moeda='R$ de set/2026',
                         unidade='1 VSR de W/(1−m) Mvar no lugar de 2 reatores fixos com vão (arranjo 2:1)', cenarios=CEN, eur_brl=EURBRL),
               precos_vsr=PVL.to_dict(orient='records'), contratos_vsr=VPC.astype(object).where(VPC.notna(), None).to_dict(orient='records'),
               premissas=PRM.astype(str).to_dict(orient='records'), cartoes=CA.to_dict(orient='records'), cascata=CS.to_dict(orient='records'),
               nevoa=FN.to_dict(orient='records'), histograma=HI.to_dict(orient='records'), vpl_premio=CU.to_dict(orient='records'),
               operacionais=OP.to_dict(orient='records'), tornado=TO.to_dict(orient='records')),
          open(P + 'modelo_financeiro_camada2.json', 'w', encoding='utf-8'), ensure_ascii=False, default=float)
pd.set_option('display.width', 250)
print(CA[['cenario', 'visao', 'variante', 'preco_vsr_R', 'premio_implicito', 'vpl_p10', 'vpl_p50', 'vpl_p90', 'p_vpl_pos', 'payback_meses_p50', 'pct_payback_imediato', 'pct_sem_payback', 'premio_equilibrio_p50', 'preco_vsr_equilibrio_p50_R']].round(2).to_string())
print(CS[CS.visao == 'concessionaria'].round(0).to_string())
print(OP.round(2).to_string())
print(TO[TO.visao == 'concessionaria'][['cenario', 'variavel', 'vpl_baixo', 'vpl_alto', 'amplitude']].round(0).to_string())

# ======================= 4. Planilha =======================
F = 'Arial'
fT = Font(name=F, size=14, bold=True); fS = Font(name=F, size=9, italic=True, color='555555')
fH = Font(name=F, size=10, bold=True, color='FFFFFF'); fN = Font(name=F, size=10); fBold = Font(name=F, size=10, bold=True)
fGreen = Font(name=F, size=10, color='008000'); fBlue = Font(name=F, size=10, color='0000FF')
hdrFill = PatternFill('solid', fgColor='1F3864'); keyFill = PatternFill('solid', fgColor='FFFF00'); thin = Side(style='thin', color='BFBFBF')
wb = openpyxl.load_workbook(XL)
NEW = ['Fin_Premissas', 'Fin_Precos_VSR', 'Fin_Cartoes', 'Fin_Cascata', 'Fin_Nevoa', 'Fin_Tornado', 'Fin_VPL_Premio', 'Fin_Operacionais', 'Pesquisa_Hitachi', 'Pesquisa_Precos_VSR']
for n_ in NEW:
    if n_ in wb.sheetnames: del wb[n_]
REF = {}
def sheet_df(name, title, source, df, key=None, numfmt=None, widths=None, notes=None):
    fim = 'Fontes_Reforcadas' if 'Fontes_Reforcadas' in wb.sheetnames else 'Fontes_Primarias'
    ws = wb.create_sheet(name, wb.sheetnames.index(fim))
    ws['A1'] = title; ws['A1'].font = fT; ws['A2'] = 'Fonte: ' + source; ws['A2'].font = fS
    if notes: ws['A3'] = notes; ws['A3'].font = fS
    for jj, c_ in enumerate(df.columns, 1):
        cell = ws.cell(4, jj, str(c_)); cell.font = fH; cell.fill = hdrFill; cell.alignment = Alignment(wrap_text=True, vertical='center')
    for i_, row in enumerate(df.itertuples(index=False), 5):
        for jj, v in enumerate(row, 1):
            if v is None or (isinstance(v, float) and np.isnan(v)): v = None
            elif isinstance(v, np.integer): v = int(v)
            elif isinstance(v, np.floating): v = float(v)
            cell = ws.cell(i_, jj, v); cell.font = fN; cell.alignment = Alignment(wrap_text=True, vertical='top')
            if numfmt and df.columns[jj - 1] in numfmt: cell.number_format = numfmt[df.columns[jj - 1]]
        if key is not None:
            k_ = tuple(row[list(df.columns).index(x)] for x in key)
            for jj, c_ in enumerate(df.columns, 1): REF[(name, k_, c_)] = f"'{name}'!${get_column_letter(jj)}${i_}"
    ws.freeze_panes = 'A5'
    for jj, c_ in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(jj)].width = (widths or {}).get(c_) or min(max(len(str(c_)) + 2, 11), 40)
    ws.row_dimensions[4].height = 30
SRC = 'Script: scripts/10_modelo_financeiro.py (camada 2). Operações: modelo físico (script 09, caso-base 2:1). '
NOTE = (f'Unidade: 1 VSR de W/(1−m) Mvar no lugar de 2 reatores fixos com vão; W = 20 Mvar (230 kV) ou 150 Mvar (500 kV); m = 50%. R$ de set/2026; '
        f'{S0} simulações; VPL incremental = custo do fixo − custo do VSR (positivo = VSR vale mais). Concessionária a 12,11% real com Parcela Variável; SIN a 8,5% sem Parcela Variável, com energia não suprida e perdas.')
MR = '#,##0'
sheet_df('Fin_Premissas', 'Modelo financeiro: premissas, faixas e fontes', SRC, PRM.assign(valor_central=PRM.valor_central.astype(str)),
         widths={'grupo': 14, 'parametro': 52, 'valor_central': 30, 'distribuicao': 22, 'fonte': 60, 'status': 14},
         notes='status: dado (fonte primária ou técnica), derivado (conta sobre dados), premissa (sem fonte; entra no tornado ou na lista de lacunas), premissa-chave (slider do site).')
sheet_df('Fin_Precos_VSR', 'Modelo financeiro: preço do VSR usado em cada nível (R$ de set/2026)', SRC + 'Contratos na aba Pesquisa_Precos_VSR.', PVL, key=('kv', 'nivel'),
         notes=f'Preço ∝ Mvar^0,6 × kV^β, convertido a € 1 = R$ {EURBRL:.4f} (BCB, set/2026). O VSR de cada cenário é escalado do tamanho de referência para W/(1−m).',
         numfmt={'preco_vsr_R': MR, 'mvar_vsr': '0'}, widths={'metodo': 60})
sheet_df('Fin_Cartoes', 'Modelo financeiro: cartões do veredito por cenário, visão e variante', SRC, CA, key=('cenario', 'visao', 'variante'), notes=NOTE,
         numfmt={**{c_: MR for c_ in CA.columns if c_.startswith('vpl') or c_.endswith('_R')}, 'p_vpl_pos': '0%', 'pct_payback_imediato': '0%', 'pct_sem_payback': '0%', 'premio_implicito': '0%',
                 'premio_equilibrio_p10': '0%', 'premio_equilibrio_p50': '0%', 'premio_equilibrio_p90': '0%', 'payback_meses_p10': '0', 'payback_meses_p50': '0', 'payback_meses_p90': '0'},
         widths={'variante': 34})
sheet_df('Fin_Cascata', 'Modelo financeiro: valor presente médio por componente (cascata do VPL)', SRC, CS, notes=NOTE + ' ganho_vsr = vp_fixo − vp_vsr.',
         numfmt={'vp_fixo': MR, 'vp_vsr': MR, 'ganho_vsr': MR}, widths={'componente': 28})
sheet_df('Fin_Nevoa', 'Modelo financeiro: custo acumulado descontado por ano (névoa de risco)', SRC, FN, notes=NOTE, numfmt={c_: MR for c_ in ('p10', 'p25', 'p50', 'p75', 'p90')})
sheet_df('Fin_Tornado', 'Modelo financeiro: tornado de sensibilidade (VPL médio com cada premissa no extremo)', SRC + f'{ST} simulações por extremo, mesma semente.', TO,
         notes='Cada linha fixa uma premissa no limite indicado e mantém as demais sorteadas.', numfmt={'vpl_baixo': MR, 'vpl_alto': MR, 'amplitude': MR, 'vpl_base_media': MR},
         widths={'variavel': 58})
sheet_df('Fin_VPL_Premio', 'Modelo financeiro: VPL em função do prêmio do VSR', SRC, CU, key=('cenario', 'visao', 'premio'), notes='prêmio = fração do preço dos reatores fixos substituídos.',
         numfmt={'premio': '0%', 'premio_R': MR, 'vpl_p10': MR, 'vpl_p50': MR, 'vpl_p90': MR, 'p_vpl_pos': '0%'})
sheet_df('Fin_Operacionais', 'Modelo financeiro: indicadores operacionais (medianas)', SRC, OP, key=('cenario',), numfmt={c_: '#,##0.0' for c_ in OP.columns if c_ != 'cenario'})
sheet_df('Pesquisa_Precos_VSR', 'Preços públicos de VSR (contratos e índices) e conversão para os VSR do modelo', 'Pesquisa própria em fontes abertas, 14/10/2026; registrada pelo script 10.',
         VPC, notes='uso: base = entra na média do preço-base; estresse = cenário de preço alto; referência e contexto = só para comparação (preço anterior a 2021 ou escopo de projeto).',
         numfmt={'preco_unit_EUR_mi': '0.00', 'vsr_500kV_R_central': MR, 'vsr_230kV_R_central': MR}, widths={'comprador': 30, 'preco_original': 34, 'fonte': 50, 'uso': 22})
sheet_df('Pesquisa_Hitachi', 'Perguntas à Hitachi Energy (escopo 6.8): o que a pesquisa aberta respondeu', 'Pesquisa própria em fontes abertas, 14/10/2026; registrada pelo script 10.',
         PH, key=('id',), notes='Respostas a confirmar com a Hitachi Energy. Confiança: alta, média, baixa ou sem dado.',
         widths={'id': 5, 'pergunta': 34, 'resposta': 80, 'valor_ou_faixa': 22, 'confianca': 16, 'fontes': 60, 'implicacao_no_modelo': 50})
ws = wb['Parametros_Modelo']
first = next((r_ for r_ in range(5, ws.max_row + 1) if isinstance(ws.cell(r_, 1).value, str) and ws.cell(r_, 1).value[1:].isdigit() and int(ws.cell(r_, 1).value[1:]) >= 96), None)
if first: ws.delete_rows(first, ws.max_row - first + 1)
CR = lambda cen, vis, col: '=' + REF[('Fin_Cartoes', (cen, vis, 'base'), col)]
PR = []
for cen, c in CEN.items():
    PR += [('Financeiro (camada 2)', f'VPL incremental P50 – {c["nome"]} – Concessionária', CR(cen, 'concessionaria', 'vpl_p50'), 'R$', 'Cartão 1', 'Script 10', 'Fin_Cartoes',
            'Prêmio de 50% (centro da faixa pública 15–65%); P10/P90 e variantes na aba de origem.'),
           ('Financeiro (camada 2)', f'Probabilidade de o VSR compensar – {c["nome"]} – Concessionária', CR(cen, 'concessionaria', 'p_vpl_pos'), 'fração', 'Cartão 3', 'Script 10', 'Fin_Cartoes', ''),
           ('Financeiro (camada 2)', f'Preço de equilíbrio do VSR P50 – {c["nome"]} – Concessionária', CR(cen, 'concessionaria', 'preco_vsr_equilibrio_p50_R'), 'R$', 'Cartão 4',
            'Script 10', 'Fin_Cartoes', 'Até esse preço o VSR compensa; prêmio de equilíbrio em fração na aba de origem.'),
           ('Financeiro (camada 2)', f'VPL incremental P50 – {c["nome"]} – SIN', CR(cen, 'sin', 'vpl_p50'), 'R$', 'Cartão 1 (visão SIN)', 'Script 10', 'Fin_Cartoes', '')]
PL = lambda kv, niv: '=' + REF[('Fin_Precos_VSR', (kv, niv), 'preco_vsr_R')]
PR += [('Financeiro (camada 2)', 'Preço-base do VSR 230 kV (40 Mvar)', PL(230, 'base'), 'R$', 'Preço do VSR (slider)', 'Contratos públicos de 2025–26 escalados', 'Fin_Precos_VSR', 'Extrapolação grande; confiança baixa.'),
       ('Financeiro (camada 2)', 'Preço-base do VSR 500 kV (300 Mvar)', PL(500, 'base'), 'R$', 'Preço do VSR (slider)', 'Contratos públicos de 2025–26 escalados', 'Fin_Precos_VSR', 'Cotação da Hitachi Energy pendente.'),
       ('Financeiro (camada 2)', 'Preço do VSR 500 kV – faixa baixa', PL(500, 'baixo'), 'R$', 'Limite do slider', 'Contratos públicos de 2025–26 escalados', 'Fin_Precos_VSR', ''),
       ('Financeiro (camada 2)', 'Preço do VSR 500 kV – faixa alta', PL(500, 'alto'), 'R$', 'Limite do slider', 'Contratos públicos de 2025–26 escalados', 'Fin_Precos_VSR', 'Estresse no nível de 2023 na aba de origem.')]
start = ws.max_row + 1
for i_, (g, p_, v, u, uso, fonte, aba, obs) in enumerate(PR, start):
    vals = [f'P{96 + i_ - start}', g, p_, v, u, uso, fonte, aba, obs]
    for jj, x in enumerate(vals, 1):
        cc = ws.cell(i_, jj, x); cc.font = fN; cc.alignment = Alignment(wrap_text=True, vertical='top'); cc.border = Border(bottom=thin)
    ws.cell(i_, 4).font = fGreen if isinstance(v, str) and v.startswith('=') else fBlue; ws.cell(i_, 4).number_format = MR if u == 'R$' else '0%'
ws = wb['LEIA-ME']; lines = []
for r_ in range(1, ws.max_row + 1):
    v = ws.cell(r_, 1).value
    if v == 'Abas da planilha': break
    lines.append([v or '', 'T' if r_ == 1 else ('B' if ws.cell(r_, 1).font.b else 'N')])
lines = [x for x in lines if not x[0].startswith(('6. Fin_',))]
out = []
for t, f_ in lines:
    if t.startswith('3. Reprodutibilidade'):
        t = '3. Reprodutibilidade: os arquivos brutos estão em raw/ e os scripts Python em scripts/ (00 a 10). Rodar na ordem regenera tudo; o 08, o 09 e o 10 rodam depois do 05, nessa ordem, e acrescentam as abas da v3. O manifesto traz o SHA-256 de cada arquivo bruto.'
    out.append((t, f_))
    if t.startswith('5. '):
        out.append(('6. Fin_*: camada 2 (script 10) – Monte Carlo dos fluxos mensais de 30 anos, arranjo 2:1, visões Concessionária e SIN: cartões, cascata, névoa, tornado, VPL × prêmio e premissas com fonte (P96 em diante). '
                    'A aba Pesquisa_Hitachi registra o que a pesquisa aberta respondeu às perguntas da seção 6.8 do escopo; Pesquisa_Precos_VSR traz os contratos públicos de VSR e Fin_Precos_VSR, o preço usado no modelo.', 'N'))
ws.delete_rows(1, ws.max_row)
FMT = {'T': fT, 'B': fBold, 'N': fN}
for i_, (t, f_) in enumerate(out, 1):
    cc = ws.cell(i_, 1, t if t else None); cc.font = FMT[f_]; cc.alignment = Alignment(wrap_text=True, vertical='top')
r_ = len(out) + 2; ws.cell(r_, 1, 'Abas da planilha').font = fBold
for k_, name in enumerate(wb.sheetnames, r_ + 1): ws.cell(k_, 1, name).font = fN
wb.save(XL)
pm = wb['Parametros_Modelo']; print('ok', XL, len(wb.sheetnames), 'abas; Parametros_Modelo até', pm.cell(pm.max_row, 1).value, f'({time.time() - t0:.0f}s)')

"""08 - Pesquisa de literatura (13/10/2026) e calibracao da volatilidade (decisao P4).
1) Volatilidade (P4): desvio-padrao dos desvios da carga liquida em torno do perfil tipico
   (mes x dia util/fim de semana x meia-hora), em % da demanda media do subsistema; autocorrelacao dos desvios.
   Base semi-horaria: ONS BALANCO_DESSEM_DETALHE, mesmas series de cenario do script 06.
   Tendencia anual: ONS curva de carga horaria 2015-2026 (carga, nao carga liquida), mesmo metodo em base horaria.
2) Energia nao suprida por perturbacao com envolvimento da Rede Basica (ONS INTERRUPCAO_CARGA), 2016-2025.
3) Pesquisa de literatura feita por agentes em 13/10/2026: parametros com faixa, fonte e confianca; lacunas.
4) Acrescenta a planilha-mestre as abas Pesquisa_Literatura, Pesquisa_Lacunas, Volatilidade_Cenarios,
   Volatilidade_Mensal, Volatilidade_Anual e Interrupcoes_ENS, as linhas P57+ de Parametros_Modelo e atualiza o LEIA-ME.
   Idempotente: rodar de novo substitui o que este script criou.
Uso: python 08_pesquisa_volatilidade.py <pasta_base_PoliVSR-dados> <planilha.xlsx>   (rodar depois do 05)"""
import sys, os, glob, hashlib, numpy as np, pandas as pd, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
BASE, XL = sys.argv[1], sys.argv[2]; R = BASE + '/raw/ons/'; P = BASE + '/processed/'

# ======================= 1. Volatilidade =======================
def vol(df, step_h, min_days_month=20):
    df = df.copy()
    df['t'] = df.date + pd.to_timedelta((df.slot - 1) * step_h * 60, unit='min')
    df = df.sort_values('t')
    df['mes'] = df.date.dt.to_period('M').astype(str)
    nd = df.groupby('mes').date.nunique(); df = df[df.mes.isin(nd[nd >= min_days_month].index)].copy()
    df['tipo_dia'] = np.where(df.date.dt.dayofweek < 5, 'util', 'fds')
    grp = df.groupby(['mes', 'tipo_dia', 'slot']).x
    n = grp.transform('size').astype(float)
    df['dev'] = (df.x - grp.transform('mean')) * np.sqrt(n / (n - 1)).where(n > 1)   # corrige o vies do perfil estimado
    df = df.dropna(subset=['dev']).copy()
    df['dev_intra'] = df.dev - df.groupby('date').dev.transform('mean')
    gap = df.t.diff().dt.total_seconds().div(3600).round(6); c1 = gap.eq(step_h)
    prev = df.dev.shift(1)
    phi = np.corrcoef(prev[c1], df.dev[c1])[0, 1]
    gap2 = (df.t - df.t.shift(2)).dt.total_seconds().div(3600).round(6); c2 = gap2.eq(2 * step_h)
    phi2 = np.corrcoef(df.dev.shift(2)[c2], df.dev[c2])[0, 1]
    inc = (df.dev - prev)[c1]; dm = df.dem.mean()
    s = dict(dias=int(df.date.nunique()), meses=int(df.mes.nunique()), inicio=str(df.date.min().date()), fim=str(df.date.max().date()),
             demanda_media_MW=dm, serie_media_MW=df.x.mean(), sigma_MW=df.dev.std(),
             sigma_pct=100 * df.dev.std() / dm, sigma_intradiario_pct=100 * df.dev_intra.std() / dm,
             sigma_diario_pct=100 * df.groupby('date').dev.mean().std() / dm, sigma_incremento_pct=100 * inc.std() / dm,
             phi_1passo=phi, phi_2passos=phi2, tau_h=(-step_h / np.log(phi)) if 0 < phi < 1 else np.nan)
    m = df.groupby('mes')[['date', 'dem', 'dev', 'dev_intra']].apply(lambda g: pd.Series({'dias': g.date.nunique(), 'demanda_media_MW': g.dem.mean(),
            'sigma_pct': 100 * g.dev.std() / g.dem.mean(), 'sigma_intradiario_pct': 100 * g.dev_intra.std() / g.dem.mean()})).reset_index()
    s.update(sigma_mensal_p10_pct=m.sigma_pct.quantile(.1), sigma_mensal_p50_pct=m.sigma_pct.median(), sigma_mensal_p90_pct=m.sigma_pct.quantile(.9))
    return s, m

d = pd.read_csv(glob.glob(R + '*balanco_dessem_detalhe__CONSOLIDADO*.csv')[0], sep=';')
d['date'] = pd.to_datetime(d.din_programacaodia); d['slot'] = d.num_patamar.astype(int)
liq = lambda g: g.val_demanda - g.val_ger_mmgd - g.val_ger_fotovoltaica - g.val_ger_eolica
gdl = lambda g: g.val_demanda - g.val_ger_mmgd - g.val_ger_fotovoltaica
def series_df(sub, f):
    g = d[d.cod_subsistema == sub].drop_duplicates(['date', 'slot']).sort_values(['date', 'slot'])
    c = g.groupby('date').slot.nunique(); g = g[g.date.isin(c[c == 48].index)]
    return pd.DataFrame({'date': g.date.values, 'slot': g.slot.values, 'x': f(g).values, 'dem': g.val_demanda.values})
SER = [('urbano', 'Centro Urbano', 'NE', gdl, 'NE: demanda − MMGD − FV (eólica remota não entra; igual ao script 06)'),
       ('polo_eolico', 'Polo eólico (corredor renovável do NE)', 'NE', liq, 'NE: carga líquida (demanda − MMGD − FV − eólica), dominada pela eólica regional')]
SER += [(f'ref_{s}', 'referência', s, liq, f'{s}: carga líquida') for s in ['N', 'NE', 'SE', 'S']]
rows, mens = [], []
def addrow(key, cen, sub, desc, df, step):
    s_, m = vol(df, step)
    p1, p2 = s_.pop('phi_1passo'), s_.pop('phi_2passos')
    phis = {'phi_30min': p1, 'phi_60min': p2} if step == 0.5 else {'phi_30min': np.nan, 'phi_60min': p1}
    s_['sigma_incremento_passo_pct'] = s_.pop('sigma_incremento_pct')
    rows.append(dict(serie=key, cenario=cen, subsistema=sub, definicao=desc, resolucao='30 min' if step == 0.5 else '1 h', **s_, **phis))
    m.insert(0, 'serie', key); mens.append(m)
for key, cen, sub, f, desc in SER:
    addrow(key, cen, sub, desc, series_df(sub, f), 0.5)
fr = [series_df(s, liq).set_index(['date', 'slot']) for s in ['N', 'NE', 'SE', 'S']]
j = pd.concat(fr, axis=1, keys=range(4), join='inner')
sin = pd.DataFrame({'x': sum(j[(k, 'x')] for k in range(4)), 'dem': sum(j[(k, 'dem')] for k in range(4))}).reset_index()
addrow('ref_SIN', 'referência', 'SIN', 'SIN: carga líquida (soma dos 4 subsistemas)', sin, 0.5)
h = pd.read_csv(P + 'carga_horaria_2015_2026_longo.csv', sep=';', encoding='utf-8-sig')
h['t'] = pd.to_datetime(h.t); h['date'] = h.t.dt.normalize(); h['slot'] = h.t.dt.hour + 1
an = []
for sub in sorted(h.id_subsistema.unique()):
    g = h[h.id_subsistema == sub].drop_duplicates(['date', 'slot'])
    c = g.groupby('date').slot.nunique(); g = g[g.date.isin(c[c == 24].index)]
    for ano, gy in g.groupby(g.date.dt.year):
        s, _ = vol(pd.DataFrame({'date': gy.date, 'slot': gy.slot, 'x': gy.carga, 'dem': gy.carga}), 1.0)
        an.append(dict(subsistema=sub, ano=int(ano), dias=s['dias'], carga_media_MW=s['demanda_media_MW'], sigma_pct=s['sigma_pct'],
                       sigma_intradiario_pct=s['sigma_intradiario_pct'], sigma_diario_pct=s['sigma_diario_pct'], phi_1h=s['phi_1passo']))
# ---- Campo: fluxo horario medido na interligacao N-NE (ONS, intercambio entre subsistemas) ----
fl = pd.concat([pd.read_csv(f, sep=';') for f in sorted(glob.glob(R + '*intercambio_nacional_ho__INTERCAMBIO_NACIONAL_*.csv'))], ignore_index=True)
fl['o'] = fl.id_subsistema_origem.astype(str).str.strip(); fl['d'] = fl.id_subsistema_destino.astype(str).str.strip()
fl = fl[fl.o.isin(['N', 'NE']) & fl.d.isin(['N', 'NE'])].copy()
sg = np.where(fl.o == 'N', 1.0, -1.0)   # 2025: par fixo N->NE com sinal; 2026: par no sentido do fluxo, valor positivo
fl['fluxo_N_para_NE_MW'] = sg * fl.val_intercambiomwmed
fl['prog_N_para_NE_MW'] = sg * fl.val_intercambioprogmwmed if 'val_intercambioprogmwmed' in fl else np.nan
fl['t'] = pd.to_datetime(fl.din_instante); fl = fl.drop_duplicates('t').sort_values('t').reset_index(drop=True)
fl['date'] = fl.t.dt.normalize(); fl['slot'] = fl.t.dt.hour + 1; fl['hora'] = fl.t.dt.hour; fl['mes'] = fl.t.dt.to_period('M').astype(str)
fl = fl.merge(h[h.id_subsistema == 'N'][['t', 'carga']], on='t', how='left')
fl[['t', 'fluxo_N_para_NE_MW', 'prog_N_para_NE_MW', 'carga']].rename(columns={'carga': 'carga_N_MW'}).to_csv(P + 'fluxo_NNE_horario.csv', index=False, sep=';', encoding='utf-8-sig')
def hser(col, base=None):
    g = (fl if base is None else base).dropna(subset=[col])
    c = g.groupby('date').slot.nunique(); g = g[g.date.isin(c[c == 24].index)]
    return pd.DataFrame({'date': g.date.values, 'slot': g.slot.values, 'x': g[col].abs().values, 'dem': g.carga.fillna(g.carga.mean()).values})
addrow('campo', 'Campo (interligação N–NE)', 'N–NE', 'Fluxo medido N–NE em módulo (|P|), horário (ONS, intercâmbio entre subsistemas); em % da carga média do N', hser('fluxo_N_para_NE_MW'), 1.0)
both = fl.dropna(subset=['fluxo_N_para_NE_MW', 'prog_N_para_NE_MW'])
addrow('ref_NNE_medido_2026', 'referência', 'N–NE', 'Fluxo N–NE medido em módulo, só nas horas com valor programado (2026)', hser('fluxo_N_para_NE_MW', both), 1.0)
addrow('ref_NNE_programado_2026', 'referência', 'N–NE', 'Fluxo N–NE programado em módulo, mesmas horas (2026)', hser('prog_N_para_NE_MW', both), 1.0)
cons = fl.t.diff().eq(pd.Timedelta(hours=1))
fl['inv'] = (np.sign(fl.fluxo_N_para_NE_MW) != np.sign(fl.fluxo_N_para_NE_MW.shift(1))) & cons
xq = lambda q: (lambda v: v.quantile(q))
FP = fl.groupby('hora').agg(fluxo_medio_MW=('fluxo_N_para_NE_MW', 'mean'), abs_medio_MW=('fluxo_N_para_NE_MW', lambda v: v.abs().mean()),
                            fluxo_p10_MW=('fluxo_N_para_NE_MW', xq(.1)), fluxo_p50_MW=('fluxo_N_para_NE_MW', 'median'),
                            fluxo_p90_MW=('fluxo_N_para_NE_MW', xq(.9)), pct_horas_NE_para_N=('fluxo_N_para_NE_MW', lambda v: 100 * (v < 0).mean())).reset_index()
def mstat(g):
    v = g.fluxo_N_para_NE_MW
    return pd.Series({'horas': len(g), 'fluxo_medio_MW': v.mean(), 'abs_medio_MW': v.abs().mean(), 'pct_horas_NE_para_N': 100 * (v < 0).mean(),
                      'inversoes_por_dia': g.inv.sum() / g.date.nunique(), 'pct_horas_abs_abaixo_500MW': 100 * (v.abs() < 500).mean()})
FM = fl.groupby('mes')[['fluxo_N_para_NE_MW', 'inv', 'date']].apply(mstat).reset_index()
tt = mstat(fl); tt['mes'] = 'total'; FM = pd.concat([FM, tt.to_frame().T], ignore_index=True)
FM['horas'] = FM.horas.astype(int)
for c in FM.columns[2:]: FM[c] = FM[c].astype(float).round(2)
FP = FP.round(2)
print('Fluxo N-NE:', fl.t.min(), '->', fl.t.max(), '| NE->N em %.1f%% das horas | inversões/dia %.2f | hora de menor |P| médio: %d h (%.0f MW); maior: %d h (%.0f MW)' % (
      100 * (fl.fluxo_N_para_NE_MW < 0).mean(), fl.inv.sum() / fl.date.nunique(), FP.loc[FP.abs_medio_MW.idxmin(), 'hora'], FP.abs_medio_MW.min(),
      FP.loc[FP.abs_medio_MW.idxmax(), 'hora'], FP.abs_medio_MW.max()))
VC = pd.DataFrame(rows)
VM = pd.concat(mens, ignore_index=True)
VA = pd.DataFrame(an)
for df_ in (VC, VM, VA, FP):
    for c in df_.columns:
        if df_[c].dtype.kind == 'f': df_[c] = df_[c].round(4)
VC.to_csv(P + 'volatilidade_cenarios.csv', index=False, sep=';', encoding='utf-8-sig')
VM.to_csv(P + 'volatilidade_mensal.csv', index=False, sep=';', encoding='utf-8-sig')
VA.to_csv(P + 'volatilidade_anual_carga_horaria.csv', index=False, sep=';', encoding='utf-8-sig')
pd.set_option('display.width', 250)
print(VC[['serie', 'resolucao', 'dias', 'meses', 'demanda_media_MW', 'sigma_MW', 'sigma_pct', 'sigma_intradiario_pct', 'sigma_diario_pct', 'sigma_incremento_passo_pct',
          'phi_30min', 'phi_60min', 'tau_h', 'sigma_mensal_p10_pct', 'sigma_mensal_p90_pct']].to_string())
FP.to_csv(P + 'fluxo_NNE_perfil_horario.csv', index=False, sep=';', encoding='utf-8-sig')
FM.to_csv(P + 'fluxo_NNE_mensal.csv', index=False, sep=';', encoding='utf-8-sig')
# ---- manifesto: arquivos brutos do intercambio ----
MAN = BASE + '/FONTES_manifesto.csv'; man = pd.read_csv(MAN, sep=';', encoding='utf-8-sig', dtype=str); have = set(man.arquivo_local)
UI = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/intercambio_nacional_ho/'
addm = []
for f in sorted(glob.glob(R + 'ONS__intercambio_nacional_ho__*')):
    rel = 'raw/ons/' + os.path.basename(f)
    if rel in have: continue
    addm.append(dict(arquivo_local=rel, instituicao='ONS - Operador Nacional do Sistema Elétrico', conjunto='intercambio_nacional_ho',
                     pagina_portal='https://dados.ons.org.br/dataset/intercambio-nacional', url_origem=UI + os.path.basename(f).split('__', 2)[2],
                     data_acesso='2026-10-13', bytes=str(os.path.getsize(f)), sha256=hashlib.sha256(open(f, 'rb').read()).hexdigest(),
                     licenca='Creative Commons Atribuição (cc-by), conforme metadados do portal'))
if addm:
    man = pd.concat([man, pd.DataFrame(addm)], ignore_index=True); man.to_csv(MAN, index=False, sep=';', encoding='utf-8-sig')
print(len(addm), 'arquivos acrescentados ao manifesto;', len(man), 'entradas')

# ======================= 2. Energia nao suprida =======================
ic = pd.read_csv(R + 'ONS__interrupcao_carga__INTERRUPCAO_CARGA.csv', sep=';')
ic['ano'] = pd.to_datetime(ic.din_interrupcaocarga).dt.year
rb = ic[ic.flg_envolveuredebasica.eq('S')]
ev = rb.groupby('cod_perturbacao').agg(ano=('ano', 'min'), MW=('val_cargainterrompida_mw', 'sum'), MWh=('val_energianaosuprida_mwh', 'sum'),
                                       min_recomp=('val_tempomedio_minutos', 'max')).reset_index()
ev = ev[ev.ano.between(2016, 2025)]
def est(g):
    q = lambda c, p: g[c].quantile(p)
    return pd.Series({'perturbacoes': len(g), 'MW_p10': q('MW', .1), 'MW_p50': q('MW', .5), 'MW_p90': q('MW', .9),
                      'MWh_p10': q('MWh', .1), 'MWh_p50': q('MWh', .5), 'MWh_p90': q('MWh', .9), 'MWh_media': g.MWh.mean(),
                      'MWh_total': g.MWh.sum(), 'min_recomp_p50': q('min_recomp', .5), 'min_recomp_p90': q('min_recomp', .9)})
EN = ev.groupby('ano')[['MW', 'MWh', 'min_recomp']].apply(est).reset_index(); EN['ano'] = EN.ano.astype(int).astype(str)
tot = est(ev); tot['ano'] = '2016–2025'; EN = pd.concat([EN, tot.to_frame().T], ignore_index=True)
EN['perturbacoes'] = EN.perturbacoes.astype(int)
for c in EN.columns:
    if c not in ('ano', 'perturbacoes'): EN[c] = EN[c].astype(float).round(2)
EN = EN[['ano'] + [c for c in EN.columns if c != 'ano']]
EN.to_csv(P + 'interrupcoes_ens_rede_basica.csv', index=False, sep=';', encoding='utf-8-sig')
print(EN.to_string())

# ======================= 3. Pesquisa de literatura =======================
N = None
U_CIG = 'https://otik.uk.zcu.cz/bitstream/11025/32358/1/BP_NovakVaclav.pdf'
U_GL = 'https://www.gevernova.com/grid-solutions/products/manuals/iti/cbr/gl314/D1174PT_GL314.pdf'
U_VIK = 'https://odr.chalmers.se/bitstreams/2c4284c2-d28c-48bd-8d30-0a214a8b684b/download'
U_JER = 'https://ewh.ieee.org/conf/powertech/2009/papers/635.pdf'
U_MR = 'https://im-tek.com/docs/messko-oiltapr-rm-228bc79cdd8a.pdf'
U_IPST = 'https://www.ipstconf.org/papers/Proc_IPST2015/15IPST012.pdf'
U_TED = 'https://ted.europa.eu/en/notice/704840-2023/pdf'
U_EPE77 = 'https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-276/topico-577/EPE-DEE-NT-077-2021-rev0.pdf'
U_EPE57 = 'https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-276/topico-708/EPE-DEE-RE-057-2024-rev0%20-%20Refor%C3%A7os%20Resili%C3%AAncia%20Acre%20e%20Rond%C3%B4nia.pdf'
U_ONS91 = 'https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-276/topico-708/RT-ONS%20DPL%200091-2024%20e%20EPE-DEE-RE-073-2024-r0%20-%20Indica%C3%A7%C3%A3o%20de%20CS%20na%20%C3%A1rea%20MG.pdf'
U_BPR = 'https://dadosabertos.aneel.gov.br/dataset/bpr-banco-de-precos-de-referencia-subestacao'
U_ETEM = 'https://etemsa.com.br/wp-content/uploads/sites/4/2024/10/ETEM_DF_Regulatorias_2011.pdf'
TB510 = 'CIGRÉ TB 510 (WG A3.06, 2012), reproduzida em Novák, TCC ZČU 2018'
# chave, bloco, secao_6, parametro, min, provavel, max, unidade, data_base, condicao, fonte, url, acesso, confianca, tipo_fonte, uso
L = [
 ('', 'Disjuntor', '6.2', 'Endurance mecânica – classe M1', N, 2000, N, 'sequências de operação', '—', 'Ensaio de tipo, qualquer tensão. M2 = 10.000 (P43)', 'IEC 62271-100, cl. 4.110, via ata IEEE PES Switchgear Committee HVCB 2001', 'https://bibliotheek.ehb.be:3193/soc/pes/switchgear/minutes/2001-2/F01HVCBa6.pdf', 'norma paga; ata aberta', 'alta', 'norma (via ata)', 'Teto mecânico; a 1 ciclo CO/dia, M1 se esgota em ~5,5 anos'),
 ('rev_ciclos', 'Disjuntor', '6.2', 'Revisão geral do disjuntor GE GL314 – por contagem', N, 3000, N, 'ciclos CO', '—', '245/300 kV, tanque vivo; o que vier primeiro entre 3.000 ciclos, 20 anos ou N·I² = 16.000 kA²; câmaras recondicionadas só na fábrica', 'GE Vernova – manual GL314 (PT), L51-003PT p. 2–3 e L51-051PT', U_GL, 'aberto', 'média', 'fabricante', 'Gatilho determinístico de revisão geral (a 1 ciclo/dia ≈ 8 anos)'),
 ('', 'Disjuntor', '6.2', 'Revisão geral do disjuntor GE GL314 – por calendário', N, 20, N, 'anos', '—', 'Idem; inspeção a cada 5 anos', 'GE Vernova – manual GL314 (PT), L51-003PT p. 2–3', U_GL, 'aberto', 'média', 'fabricante', 'Gatilho por tempo (disjuntor do VSR, que quase não manobra)'),
 ('', 'Disjuntor', '6.2', 'Intervalo de manutenção por contagem (exemplo genérico)', 2000, N, 2500, 'operações', '2002', 'Exemplo; manobra de reator citada como caso típico de redução de desgaste com manobra controlada', 'Hermosillo, "Overall Benefits of Controlled Switching", seminário CIGRE WG 13.07, 2002, p. 2', 'https://ewh.ieee.org/soc/pes/switchgear/presentations/tp_files/2003-1_Thu_4_Hermosillo.pdf', 'aberto', 'média', 'artigo técnico', 'Faixa do gatilho por contagem'),
 ('', 'Disjuntor', '6.2', 'Operações observadas – disjuntor de reator de barra 400 kV', N, 175, N, 'operações/ano', '2011', '1.400 operações em 8 anos, SF6', 'Jeyaraj & Habtay (2011), citados em Oliveira, dissertação UFCG 2015, cap. 3', 'https://bdtd.ufcg.edu.br/bitstream/riufcg/19967/1/ADRIANO%20COSTA%20DE%20OLIVEIRA%20-%20DISSERTA%c3%87%c3%83O%20PPGEE%202015.pdf', 'aberto', 'baixa', 'secundária', 'Validação da regra de manobra (3.4)'),
 ('maf_reator', 'Disjuntor', '6.2', 'Falha maior (MaF) – disjuntor de manobra de reator shunt (todas as tecnologias)', 1.98, 2.46, 3.02, 'MaF/100 disjuntores-ano', '2004–2007', 'Faixa = limites de confiança publicados (não quartis); população pequena', TB510 + ', Tab. 4.9; Vajnar 2018, Tab. II', U_CIG, 'aberto (TB paga)', 'média', 'reprodução de fonte primária', 'Taxa central de falha do disjuntor do reator fixo (P57)'),
 ('', 'Disjuntor', '6.2', 'MaF – manobra de reator, disjuntor de tanque vivo', N, 6.79, N, 'MaF/100 disjuntores-ano', '2004–2007', 'Tecnologia mais comum em subestação convencional', TB510 + ', Tab. 4.9', U_CIG, 'aberto (TB paga)', 'média', 'reprodução de fonte primária', 'Cenário pessimista; depende da frota brasileira'),
 ('', 'Disjuntor', '6.2', 'MaF – manobra de reator, disjuntor de tanque morto', N, 1.17, N, 'MaF/100 disjuntores-ano', '2004–2007', 'GIS: 0,96', TB510 + ', Tab. 4.9', U_CIG, 'aberto (TB paga)', 'média', 'reprodução de fonte primária', 'Cenário otimista'),
 ('maf_linha', 'Disjuntor', '6.2', 'MaF – disjuntor de linha (regime do VSR)', 0.23, 0.25, 0.28, 'MaF/100 disjuntores-ano', '2004–2007', 'Referência para disjuntor que quase não manobra', TB510 + ', Tab. 4.9; Vajnar 2018, Tab. II', U_CIG, 'aberto (TB paga)', 'média', 'reprodução de fonte primária', 'Taxa do disjuntor do VSR (P58)'),
 ('', 'Disjuntor', '6.2', 'MaF – todos os disjuntores SF6 (3ª pesquisa)', 0.28, 0.30, 0.32, 'MaF/100 disjuntores-ano', '2004–2007', '≥ 60 kV; 281.090 disjuntores-ano', 'CIGRÉ TB 509 (resumo); Vajnar, Elektrotechnika a informatika 2018, p. 143–144', 'https://dspace5old.zcu.cz/bitstream/11025/30733/3/Vajnar.pdf', 'resumo aberto (TB paga)', 'alta', 'fonte primária (resumo)', 'Confere P37'),
 ('', 'Disjuntor', '6.2', 'Fator manobra de reator ÷ demais aplicações', N, 10, N, 'x', '2004–2007', '"ten time larger"; causa: sobretensões de reignição nas aberturas frequentes', 'Ito et al., "CIGRE Reliability Survey on Equipment", CIGRE Science & Engineering nº 23, 2021, §5', 'https://cse.cigre.org/cse-n023/cigre-reliability-survey-on-equipment', 'aberto', 'alta', 'fonte primária (conferida em 13/10/2026)', 'Coerência entre MaF de reator e de linha'),
 ('', 'Disjuntor', '6.2', 'MaF por tensão – 200–300 kV (equipamento 245 kV)', 0.30, 0.35, 0.41, 'MaF/100 disjuntores-ano', '2004–2007', 'Todas as aplicações', TB510 + ', Tab. 4.8', U_CIG, 'aberto (TB paga)', 'média', 'reprodução de fonte primária', 'Ajuste por tensão (cenário 230 kV)'),
 ('', 'Disjuntor', '6.2', 'MaF por tensão – 500–700 kV (equipamento 550 kV)', 0.30, 0.46, 0.67, 'MaF/100 disjuntores-ano', '2004–2007', 'Todas as aplicações', TB510 + ', Tab. 4.8', U_CIG, 'aberto (TB paga)', 'média', 'reprodução de fonte primária', 'Ajuste por tensão (cenários 500 kV)'),
 ('', 'Disjuntor', '6.2', 'Razão falhas menores ÷ falhas maiores', 7.1, N, 7.9, 'x', '1988–2007', 'Global; falhas menores são subnotificadas', 'Derivado de CIGRÉ TB 83 e TB 510 (via Vajnar 2018; OSTI 63032)', 'https://www.osti.gov/biblio/63032', 'aberto', 'média', 'derivado', 'Falhas menores ≈ 7–8 × MaF'),
 ('', 'Disjuntor', '6.2', 'Falhas – disjuntor de linha vs. de reator, 400 kV (Suécia)', 1.3, N, 4.5, 'falhas/100 disjuntores-ano', '≈1997', 'Mín. = disjuntor de linha; máx. = disjuntor de reator', 'Karlsson et al., IEEE TPWRD 12(4):1486–92, 1997, citado em Vikesjö, dissertação Chalmers 2008, Tab. 1 p. 21', U_VIK, 'aberto', 'baixa', 'secundária', 'Confirmação independente da razão reator/linha'),
 ('', 'Disjuntor', '6.2', 'Falha em abrir ("stuck") por ciclo de operação', N, 0.000177, N, 'por ciclo', '≈1997', '400 kV, Suécia', 'Karlsson et al. 1997, via Vikesjö 2008, Tab. 3 p. 23', U_VIK, 'aberto', 'baixa', 'secundária', 'Risco de falha na abertura'),
 ('', 'Disjuntor', '6.2', 'Falhas de disjuntor 400 kV – estatística nórdica', 0.59, N, 1.7, 'falhas/100 disjuntores-ano', '1997–2011', 'Mín. = 2011; máx. ≈ média 1997–2006 (inclui operações indevidas); a maioria das falhas de 400 kV ocorreu em disjuntores de reator', 'ENTSO-E, Nordic Grid Disturbance & Fault Statistics 2011, Tab. 5.16 p. 47', 'https://eepublicdownloads.entsoe.eu/clean-documents/pre2015/publications/nordic/operations/130627_Nordic_Grid_Disturbance_and_Fault_Statistics_2011.pdf', 'aberto', 'alta', 'fonte primária (TSO)', 'Evidência qualitativa e ordem de grandeza'),
 ('', 'Disjuntor', '6.2', 'Tempo de reparo após falha – estudos de confiabilidade', 3, N, 100, 'h', '1991–2008', 'Faixa central 16–48 h (Svenska Kraftnät 6–24 h; Karlsson 48 h; 500 kV 100 h)', 'Vikesjö 2008, Tab. 2 p. 22 (compilação)', U_VIK, 'aberto', 'baixa', 'secundária', 'Distribuição do reparo (PVI e ENS)'),
 ('', 'Disjuntor', '6.2', 'Tempo de reparo – frota real 400 kV (Irã)', N, 20, N, 'h', '2014–2017', '99 disjuntores SF6; taxa total 3,69 falhas/100 disjuntores-ano', 'Karimabadi et al., Archives of Electrical Engineering 69(2), 2020, Tab. 4', 'https://journals.pan.pl//Content/116234/PDF/art_12.pdf', 'aberto', 'média', 'artigo técnico', 'Mediana do reparo'),
 ('', 'Disjuntor', '6.2', 'Custo de revisão geral (EnBW 110 kV)', N, 10, N, '% do investimento por revisão', '≈2009', '€ 3.400 a cada 5 anos (≈ 2%/ano, derivado); valores "exemplares"', 'Jeromin et al., IEEE PowerTech 2009, Tab. 2 e 5', U_JER, 'aberto', 'média', 'artigo técnico', 'Âncora da premissa de custo de manutenção (10%)'),
 ('', 'Disjuntor', '6.2', 'Custo de inspeção (EnBW 110 kV)', N, 0.3, N, '% do investimento por ano', '≈2009', '€ 200 a cada 2 anos (derivado)', 'Jeromin et al., IEEE PowerTech 2009, Tab. 6', U_JER, 'aberto', 'média', 'derivado', 'OPEX de rotina'),
 ('', 'Disjuntor', '6.2', 'Substituição de disjuntor 220 kV (Austrália)', N, 1.09, N, 'AUD mi por unidade', '2016/17', 'AUD 6,52 mi por 6 unidades, inclui custos de projeto (derivado)', 'TasNetworks, Investment Evaluation Summary, 2018, p. 1 e 12', 'https://www.aer.gov.au/system/files/TasNetworks%20-Replace%20220%20kV%20Sprechur%20and%20Schuh%20HPF%20live%20tank%20circuit%20breakers%20-%2029%20November%202018.pdf', 'aberto', 'média', 'derivado', 'Ordem de grandeza da consequência de falha catastrófica'),
 ('', 'Disjuntor', '6.2', 'Explosões de disjuntor em manobra de reator (caso)', N, 2, N, 'eventos em ~15 anos numa SE', '2003', '400 kV SF6, Irã; um disjuntor falhou 5 vezes desde 1987 abrindo reator', 'Khodabakhchian et al., IPST 2003', 'https://www.ipstconf.org/papers/Proc_IPST2003/03IPST04a-03.pdf', 'aberto', 'média', 'artigo técnico', 'Evidência qualitativa da cauda'),
 ('', 'VSR/OLTC', '6.3', 'OLTC a óleo OILTAP R – manutenção (no neutro ou Um < 245 kV)', 40000, 80000, 100000, 'operações (ou 7 anos)', '—', '≤ 600 A sem filtro = 80.000; com filtro de óleo = 100.000; cai com corrente maior. Em VSR o comutador costuma ficar no lado do neutro (confirmar com o fabricante)', 'Maschinenfabrik Reinhausen, Operating Instructions OILTAP R, §7.2, Tab. 6 (p. 49) e Tab. 8 (p. 50)', U_MR, 'aberto', 'média', 'fabricante', 'OPEX do OLTC a óleo'),
 ('', 'VSR/OLTC', '6.3', 'OLTC a óleo OILTAP R – manutenção (na linha, Um ≥ 245 kV)', 20000, 35000, 50000, 'operações', '—', '1ª manutenção em 2 anos ou 20.000 op.; depois a cada 4 anos (6 com filtro); 50.000 com filtro', 'Maschinenfabrik Reinhausen, Operating Instructions OILTAP R, §7.2, Tab. 7 (p. 50)', U_MR, 'aberto', 'média', 'fabricante', 'OPEX do OLTC a óleo (caso conservador)'),
 ('', 'VSR/OLTC', '6.3', 'OLTC a óleo – vida do inserto do diverter', N, 800000, N, 'operações', '—', 'Seletor: verificar com 1 milhão', 'Maschinenfabrik Reinhausen, Operating Instructions OILTAP R, §7.2 (p. 49)', U_MR, 'aberto', 'média', 'fabricante', 'Vida do comutador'),
 ('', 'VSR/OLTC', '6.3', 'OLTC a vácuo VACUTAP VR/VM – manutenção', N, 300000, N, 'operações (sem limite de tempo)', '2017', 'Vida do inserto 1,2 milhão (VR); 1,5 milhão de operações mecânicas (VM)', 'MR, relatório de ensaio de tipo VR 2E 001e (2017), §5 p. 6; folheto IN5062036', 'https://www.reinhausen.com/fileadmin/downloadcenter/products/oltc/vr/flyer/in5062036_en.pdf', 'aberto', 'média', 'fabricante', 'OPEX do OLTC a vácuo (confere P44)'),
 ('', 'VSR/OLTC', '6.3', 'OLTC a vácuo ABB (VUCG/VUCL, VUBB, VRLTC) – inspeção', 300000, N, 500000, 'operações (sem limite de tempo)', '2013', 'Convencional a óleo ≈ 100.000', 'ABB, "New vacuum on-load tap changer portfolio", 2013', 'https://new.abb.com/news/detail/49370/new-vacuum-on-load-tap-changer-portfolio', 'aberto', 'média', 'fabricante', 'OPEX do OLTC a vácuo (linha Hitachi Energy)'),
 ('', 'VSR/OLTC', '6.3', 'Prática de concessionária – manutenção de OLTC a óleo', N, 4, N, 'anos (vácuo: até 600.000 op.)', 'nov/2025', 'Frota AusNet 66–500 kV', 'AusNet, AMS 10-67 Power Transformers and Oil Filled Reactors, p. 18', 'https://www.aer.gov.au/system/files/2025-11/AusNet%20Services%20-%20TRR%202027-32%20Technical%20AMS%2010-67%20Power%20Transformers%20and%20Oil%20Filled%20Reactors%20-%2010%20Nov%202025%20-%20PUBLIC.pdf', 'aberto', 'média', 'concessionária', 'Periodicidade real'),
 ('', 'VSR/OLTC', '6.3', 'Falha grave – transformador de subestação (TB 642)', N, 0.53, N, '%/ano', '1996–2010', '≥ 100 kV; 964 falhas em 167.459 transformador-anos; elevadores 0,95', 'CIGRÉ TB 642 (WG A2.37, 2015), via Transformer Technology nº 4', 'https://transformer-technology.com/mitigating-failure-risk-in-power-transformers-eletronorte-case-study-transformer-technology-issue-4/', 'aberto (TB paga)', 'baixa', 'secundária', 'Taxa-base do reator/VSR'),
 ('', 'VSR/OLTC', '6.3', 'Fração das falhas graves atribuída ao comutador (TB 642)', 12, N, 31, '%', '1996–2010', 'Mín. = elevadores; máx. = subestação; a fração cai com a tensão', 'CIGRÉ TB 642, via NS Energy / Modern Power Systems 2018', 'https://www.nsenergybusiness.com/features/featurea-new-assessment-of-power-transformer-reliability-6045374/', 'aberto', 'baixa', 'secundária', 'Taxa do OLTC = fração × taxa total'),
 ('', 'VSR/OLTC', '6.3', 'Falha grave – transformadores e reatores ≥ 100 kV (TB 939)', N, 0.3, N, '%/ano', '2010–2020', '> 425 mil unidade-anos', 'CIGRÉ TB 939 (WG A2.62, 2024), via Electra 336 e IEH Stuttgart', 'https://electra.cigre.org/336-october-2024/technical-brochures/analysis-of-ac-transformer-reliability', 'aberto (TB paga)', 'média', 'resumo de fonte primária', 'Taxa-base do reator'),
 ('', 'VSR/OLTC', '6.3', 'Falha grave – dados CIGRÉ reanalisados', N, 0.41, N, '%/ano', '2026', '1.358 falhas em 331.379 anos de operação, 50 concessionárias', 'Martin & Tenbohlen, Energies 19(13):3197, 2026, §2.1', 'https://www.mdpi.com/1996-1073/19/13/3197', 'aberto', 'média', 'artigo revisado', 'Taxa-base do reator'),
 ('', 'VSR/OLTC', '6.3', 'Defeitos em reatores – países nórdicos (todas as faltas)', 2.13, 6.69, 13.12, 'defeitos/100 unidades-ano', '2000–2009', '198 reatores; não separa VSR; inclui faltas não graves', 'ENTSO-E/Nordel, Nordic Grid Disturbance and Fault Statistics 2009, Tab. 5.22 (p. 45)', 'https://eepublicdownloads.entsoe.eu/clean-documents/pre2015/publications/entsoe/RG_SOC_Nordic/FaultStatistics2009.pdf', 'aberto', 'alta', 'fonte primária (TSO)', 'Frequência de defeitos do reator (fixo e VSR)'),
 ('', 'VSR/OLTC', '6.3', 'Falha grave atribuível ao OLTC (estimativa)', 0.04, N, 0.16, '%/ano', '—', '(12–31%) × (0,3–0,53 %/ano)', 'Derivado das linhas TB 642 e TB 939 acima', '', '—', 'baixa', 'derivado', 'Acréscimo de risco do VSR'),
 ('', 'VSR/OLTC', '6.3', 'Restabelecimento após falha de fase de banco com reserva', 3, N, 2190, 'h', '2015', 'Mín. = reserva comutável (3 h); dias com reserva no local; máx. ≈ 3 meses trazendo reserva de outra SE (até US$ 1 mi por evento)', 'Belknap (AEP), CIGRÉ US NC 2015', 'https://cigre-usnc.org/wp-content/uploads/2015/10/Belknap.pdf', 'aberto', 'média', 'concessionária', 'Indisponibilidade longa do VSR sem fase reserva (2.9)'),
 ('', 'VSR/OLTC', '6.3', 'Prazo de entrega de transformador de potência novo', 80, 120, 210, 'semanas', '2024', 'Eram ~50 semanas em 2021; reatores não citados', 'Wood Mackenzie 2024; NIAC/CISA 2024, p. 3', 'https://woodmac.com/news/opinion/supply-shortages-and-an-inflexible-market-give-rise-to-high-power-transformer-lead-times/', 'aberto', 'média', 'analista de mercado', 'Reparo/substituição de VSR sem reserva'),
 ('', 'VSR/OLTC', '6.3', 'Prazo contratual de um VSR (HOPS Melina)', N, 15, N, 'meses', '2019', 'Antes da crise de prazos', 'Balkan Green Energy News', 'https://balkangreenenergynews.com/?p=26696', 'aberto', 'baixa', 'imprensa', 'Referência de prazo'),
 ('min_reg', 'VSR/OLTC', '6.3', 'Mínimo de regulação – VSR 420 kV (Hitachi/ABB)', 45, N, 60, '% da nominal', '2014', '90–200 Mvar (45%); projeto anterior 120–200 Mvar (60%); a faixa é limitada pela tensão de degrau do OLTC', 'Bengtsson, Ryen, Rui, Olsson – CIGRÉ A2-211, 2014', 'https://www.hitachienergy.com/content/dam/pg/references/files/variable-shunt-reactors-cigre2014-a2-211-2014.pdf', 'aberto', 'alta', 'fonte primária', 'Padrão do slider: 50% (P60)'),
 ('', 'VSR/OLTC', '6.3', 'Mínimo de regulação – especificação Energinet 400 kV', N, 50, N, '% da nominal', '2023', '70–140 Mvar ("≥ 50%"), ONAN', 'Energinet – TED 704840-2023', U_TED, 'aberto', 'alta', 'ato oficial', 'Padrão do slider'),
 ('', 'VSR/OLTC', '6.3', 'Mínimo de regulação – VSR 420 kV HOPS', N, 53, N, '% da nominal', '2015', '80–150 Mvar, 29 posições, núcleo de 5 colunas', '"Transients Caused by Switching of 420 kV Three-Phase VSR", IPST 2015', U_IPST, 'aberto', 'média', 'artigo técnico', 'Padrão do slider'),
 ('', 'VSR/OLTC', '6.3', 'Mínimo de regulação – 242 kV e 300 kV', 50, N, 53, '% da nominal', '~2009', '242 kV: 50–100 Mvar; 300 kV: 80–150 Mvar; faixa viável de 110 a 525 kV', 'Bengtsson, ABB Review Special Report, p. 41–44', 'https://library.e.abb.com/public/b9950e8daa93c268c1257ab8003b1097/41-44%20sr109_72dpi.pdf', 'aberto', 'média', 'fabricante', 'Cenário 230 kV'),
 ('', 'VSR/OLTC', '6.3', 'Mínimo de regulação alegado em material comercial', N, 20, N, '% da nominal', '2026', 'Siemens Energy ("até 80% de regulação", portfólio); CHINT 500 kV 24–120 Mvar', 'Siemens Energy, página de reatores; CHINT, folheto CIGRÉ Paris 2026', 'https://www.siemens-energy.com/global/en/home/products-services/product/reactors.html', 'aberto', 'baixa', 'fabricante (marketing)', 'Limite otimista do slider'),
 ('vsr_energinet', 'VSR/OLTC', '6.3', 'Preço de VSR – Energinet (5 × 400 kV, 70–140 Mvar)', N, 7.68, N, '€ mi por unidade', 'contrato de 20/07/2023', '€ 38.388.505 por 5 unidades, sem IVA; ≈ € 54,8 mil/Mvar da potência máxima (derivado); fornecedor Siemens Energy', 'Energinet – TED 704840-2023', U_TED, 'aberto', 'alta', 'ato oficial (conferido em 13/10/2026)', 'Ordem de grandeza do CAPEX do VSR'),
 ('', 'VSR/OLTC', '6.3', 'Preço de VSR – HOPS Melina (≈ 200 Mvar)', N, 4.93, N, '€ mi', '2019', 'HRK 36,5 mi; inclui implantação; potência pela T&D World', 'Balkan Green Energy News; T&D World', 'https://balkangreenenergynews.com/?p=26696', 'aberto', 'baixa', 'imprensa', 'Ordem de grandeza do CAPEX do VSR'),
 ('', 'VSR/OLTC', '6.3', 'Projeto de VSR 150 Mvar substituindo reator fixo – PSEG (EUA)', 13.6, 21.9, 23.5, 'US$ mi por projeto', 'jul/2026', '230 kV: 13,6 → 21,9; 345 kV: 16,0 → 23,5; inclui disjuntores novos com manobra controlada (point-on-wave), adotada após aumento de falhas de reatores', 'PJM TEAC 07/07/2026, item 15, slide 7 (b3794.1/.2)', 'https://www.pjm.com/-/media/DotCom/committees-groups/committees/teac/2026/20260707/20260707-item-15---reliability-analysis-update.pdf', 'aberto', 'alta', 'documento oficial (conferido em 13/10/2026)', 'Escopo de projeto (não só equipamento); evidência do contrafactual 2.8'),
 ('reator_500', 'VSR/OLTC', '6.4', 'Reator monofásico 500 kV 66,6 Mvar – custo de referência', N, 4.415, N, 'R$ mi por unidade', 'mar/2021', '≈ R$ 66 mil/Mvar; banco de barra (3+1R) × 66,6 Mvar = R$ 17,66 mi; preço da Base de Referência de Preços ANEEL mar/2021', 'EPE-DEE-NT-077/2021, Tab. 7-1, p. 24', U_EPE77, 'aberto', 'média', 'documento técnico oficial', 'Base do prêmio de CAPEX (reator fixo)'),
 ('', 'VSR/OLTC', '6.4', 'Reator monofásico 50 Mvar – BPR (via artigo)', N, 2.56, N, 'R$ mi por unidade', 'mar/2019', 'Tensão não informada (o texto indica reator de linha de 500 kV)', 'Barroso et al., Revista Gestão em Foco nº 13, 2021, Tab. 1–2, p. 171', 'https://portal.unisepe.com.br/unifia/wp-content/uploads/sites/10001/2021/07/Sensibilidade-do-Valor-do-Investimento-nos-Lances-em-Licita%C3%A7%C3%B5es-de-Empreendimento-de-Transmiss%C3%A3o-p%C3%A1g-167-%C3%A0-184.pdf', 'aberto', 'baixa', 'secundária', 'Confere o custo de referência do reator'),
 ('', 'VSR/OLTC', '6.4', 'Custo de reator – MISO', 14262, N, 23625, 'US$/Mvar', '2021–2023', '69–500 kV; o item não diz "shunt"', 'MISO Transmission Cost Estimation Guide (MTEP21 via PUCT 53601, p. 27; MTEP23 via arXiv 2604.01338)', 'https://interchange.puc.texas.gov/Documents/53601_1_1208306.PDF', 'aberto', 'média', 'documento técnico', 'Comparação internacional'),
 ('', 'VSR/OLTC', '6.4', 'Reator shunt "turnkey" – WECC', N, 20000, N, 'US$/Mvar', '2012', '230, 345 e 500 kV', 'Black & Veatch para o WECC, Tab. 3-4', 'https://efis.psc.mo.gov/Document/Display/280923', 'aberto', 'média', 'documento técnico', 'Comparação internacional'),
 ('perdas_min', 'VSR/OLTC', '6.6', 'Perdas do VSR na posição mínima', N, 62, N, '% das perdas plenas', '2015', 'VSR 420 kV: 145 kW a 80 Mvar contra 232 kW a 150 Mvar; fixo desligado = 0', 'IPST 2015 (HOPS), tabela de dados do VSR', U_IPST, 'aberto', 'média', 'artigo técnico', 'Perdas como custo do VSR (visão SIN)'),
 ('', 'VSR/OLTC', '6.6', 'Capitalização de perdas de reator (ADMIE, Grécia)', N, 5827, N, '€/kW', '2016', '116,7 €/kW·ano + 0,0438 €/kWh (7.500 h/ano), reator 400 kV', 'IPTO/ADMIE, TD-95/6 (2016) e TD-95/3 (2012)', 'https://www.admie.gr/sites/default/files/inline-files/groups/ADMIE_DAPM/408702/408702_TECHNICAL_DESCRIPTION_TD_-95a-6.pdf', 'aberto', 'alta', 'documento oficial (TSO)', 'Valorar perdas'),
 ('', 'BPR e regulatório', '6.5', 'Módulo de reator variável / VSR no BPR', N, 'ausente', N, '—', 'arquivos de 01/10/2026', 'Nenhuma ocorrência de "variável", "comutador", "VSR", "controlad" ou "regul" nos 3 CSVs do BPR-Subestação; só existem RM, RT e RA', 'ANEEL – BPR-Subestação (REH 758/2009 e REH 2.514/2019), cópia em raw/aneel', U_BPR, 'aberto', 'alta', 'fonte primária (conferida em 13/10/2026)', 'Fecha P5 (decisão 2.2)'),
 ('', 'BPR e regulatório', '6.4', 'Módulo RM no BPR aberto – só acessórios', N, 0.19, N, 'R$ mi por módulo', 'civil dez/2011; demais jun/2017', 'Base, parede corta-fogo, caixa separadora de óleo, combate a incêndio, estrutura; o reator em si (UC 330) não tem preço', 'ANEEL – BPR item-módulo-equipamento', U_BPR, 'aberto', 'alta', 'fonte primária', 'Explica a ausência do preço do reator'),
 ('crb_500', 'BPR e regulatório', '6.4', 'Conexão de reator de barra (CRB) 500 kV, arranjo DJM – custo modular EPE', N, 9.589, N, 'R$ mi', 'mar/2021', '≈ 1,8 × a soma direta do BPR aberto (5,28, base 2017): não misturar bases', 'EPE-DEE-NT-077/2021, Tab. 7-1', U_EPE77, 'aberto', 'média', 'documento técnico oficial', 'CAPEX de vão evitado (caso 2:1)'),
 ('', 'BPR e regulatório', '6.4', 'Conexão de reator de barra (CRB) 230 kV – soma direta do BPR', 2.18, 2.28, 2.38, 'R$ mi', 'equip. mai/2017; civil dez/2011', 'Arranjos BPT / BD4 / BD5; disjuntor ≈ 13% do módulo', 'ANEEL – BPR item-módulo-manobra (soma sobre a cópia local)', U_BPR, 'aberto', 'alta', 'fonte primária (soma)', 'CAPEX de vão evitado (230 kV)'),
 ('', 'BPR e regulatório', '6.4', 'Módulo de infraestrutura de manobra (MIM) 500 kV', 3.348, 4.105, N, 'R$ mi', 'mar/2021 e 2024', 'Mín. = mar/2021; provável = 2024 (data-base não declarada)', 'EPE-DEE-NT-077/2021, Tab. 7-1; RT-ONS DPL 0091/2024 e EPE-DEE-RE-073/2024, Tab. 6-1', U_ONS91, 'aberto', 'média', 'documento técnico oficial', 'CAPEX de vão evitado'),
 ('dep_reator', 'BPR e regulatório', '6.5', 'Depreciação regulatória – reator', N, 2.78, N, '% a.a.', 'vigente desde 2012', 'Vida ≈ 36 anos; MCPSE (REN 367/2009, Tabela XVI alterada pela REN 474/2012; REN 674/2015); revisão do MCPSE em consulta, vigência proposta 01/01/2027', 'DFR ETEM 2011, §9 (cita a REN 474/2012)', U_ETEM, 'aberto', 'média', 'secundária que cita ato', 'Valor residual e indenização (P2)'),
 ('dep_disj', 'BPR e regulatório', '6.5', 'Depreciação regulatória – disjuntor', N, 3.03, N, '% a.a.', 'vigente desde 2012', 'Vida ≈ 33 anos; seccionadora 3,33%; transformador de força 2,86%', 'DFR ETEM 2011, §9 (cita a REN 474/2012)', U_ETEM, 'aberto', 'média', 'secundária que cita ato', 'Valor residual do disjuntor trocado (2.3)'),
 ('', 'BPR e regulatório', '6.5', 'Vida econômica em estudos de expansão da EPE', N, 30, N, 'anos', '2024', 'Estudos de transmissão', 'EPE-DEE-RE-057/2024, §4.4.4', U_EPE57, 'aberto', 'média', 'documento técnico oficial', 'Confere o horizonte de 30 anos'),
 ('', 'BPR e regulatório', '6.5', 'Prazo da concessão de transmissão', N, 30, N, 'anos (máximo)', '—', 'Prazo necessário à amortização, limitado a 30 anos, prorrogável; licitação por até 30 anos (redação da Lei 15.269/2025)', 'Lei 9.074/1995, art. 4º §3º; Lei 12.783/2013, art. 8º', 'https://www.planalto.gov.br/ccivil_03/leis/l9074cons.htm', 'aberto', 'alta', 'lei', 'Horizonte (P2)'),
 ('', 'BPR e regulatório', '6.5', 'Reversão com indenização do investimento não amortizado', N, 'VNR', N, '—', '—', 'Indeniza investimentos reversíveis ainda não amortizados ou depreciados; pago pelo vencedor da nova licitação (Decreto 11.314/2022, art. 6º)', 'Lei 8.987/1995, art. 36; Lei 12.783/2013, art. 8º §2º e art. 15 §1º', 'https://www.planalto.gov.br/ccivil_03/leis/l8987cons.htm', 'aberto', 'alta', 'lei', 'Valor residual em concessão existente (P2)'),
 ('', 'BPR e regulatório', '6.5', 'Proposta ANEEL para concessões em fim de vigência', N, 'indenizar só reforços não amortizados', N, '—', 'CP de 11/12/2025 a 10/03/2026', 'Contratos dos leilões a partir de 2020 já depreciam tudo no prazo; regulamento previsto até o fim de 2026', 'CP ANEEL nº 43/2025 (número via imprensa)', 'https://agenciainfra.com/blog/transmissoras-temem-prejuizos-com-relicitacao-sem-indenizacao/', 'aberto', 'baixa', 'imprensa', 'Cenário sem indenização (P2)'),
 ('', 'BPR e regulatório', '6.5', 'CAOM de reforços e melhorias (concessões prorrogadas)', N, 2.0, N, '% do VNR por ano', '2023', 'VNR pelo BPR; custo contábil (VOC) para o que não cabe no BPR', 'ANEEL – NT 103/2024-STR, §79 e §83', 'https://ri.isaenergiabrasil.com.br/Arquivos/Download/NT-103-2024-STR-ANEEL.pdf', 'aberto', 'média', 'documento técnico oficial', 'Referência de O&M regulatório; base possível para a chave "prêmio reconhecido"'),
 ('deficit', 'Visão SIN', '6.6', 'Custo do déficit', 7643.82, 8291.25, 8327.76, 'R$/MWh', 'nov/2025 (IGP-DI)', 'Provável = 2026; mín. = 2022; máx. = 2025 (implícito, derivado); patamar único atualizado pelo IGP-DI (REN 795/2017; REN 1.032/2022)', 'Nota Técnica nº 11/2025/GPRE/GEPME/AGM – custo do déficit 2026', 'https://www.ccee.org.br/documents/80415/30980462/SEI_0145495_Nota_Tecnica_11_2025_GPRE_GEPME_AGM%20-%20Custo%20do%20d%C3%A9ficit%202026.pdf/7ac089d9-41ab-8995-3fa4-256182e94180', 'aberto', 'alta', 'ato oficial (conferido em 13/10/2026)', 'Valor da energia não suprida (visão SIN); é custo de suficiência, não de interrupção local'),
 ('tsd', 'Visão SIN', '6.6', 'Taxa social de desconto', 5.71, 8.5, 11.44, '% a.a. real', '22/05/2020', 'Infraestrutura; adotada no Guia Geral de ACB v2 (out/2021)', 'Nota Técnica SEI nº 19911/2020/ME', 'https://www.gov.br/gestao/pt-br/central-de-conteudo/publicacoes/notas-tecnicas/2020/nt_taxa-social_vf.pdf', 'aberto', 'alta', 'ato oficial', 'Taxa de desconto da visão SIN (P3)'),
 ('', 'Visão SIN', '6.6', 'Taxa de desconto em estudos de transmissão da EPE', N, 8, N, '% a.a.', '2023–2024', 'Comparação de alternativas a valor presente', 'EPE-DEE-RE-057/2024, §4.4.4; EPE-DEE-NT-003/2024, Tab. 8-6', U_EPE57, 'aberto', 'média', 'documento técnico oficial', 'Sensibilidade da visão SIN'),
 ('', 'Visão SIN', '6.6', 'Planejamento da expansão: energia não suprida só em MW/%', N, 'sem R$/MWh próprio', N, '—', '2020–2024', 'O PDE usa o mesmo custo do déficit da operação', 'GT Modernização – Critério de Suprimento (MME/EPE, 2020); EPE-DEE-RE-057/2024', 'https://www.epe.gov.br/sites-pt/areas-de-atuacao/energia-eletrica/Documents/2020_GT%20Moderniza%C3%A7%C3%A3o_Crit%C3%A9rio%20de%20Suprimento_Relat%C3%B3rio%20Final.pdf', 'aberto', 'média', 'documento técnico oficial', 'Justifica usar o custo do déficit'),
 ('', 'Visão SIN', '6.6', 'Evento de cauda – falha de disjuntor (SE Xingu, 21/03/2018)', N, 51692, N, 'MWh não supridos', '2018', '20.508 MW interrompidos; perturbação ONS 5799/2018', 'ONS dados abertos (interrupção de carga); Poder360', 'https://www.poder360.com.br/brasil/ons-falha-em-disjuntor-causou-apagao-no-norte-e-nordeste/', 'aberto', 'média', 'dado oficial + imprensa', 'Ilustração da cauda (não é frequência)'),
 ('', 'Visão SIN', '6.6', 'Evento de cauda – incêndio em reator (LT 525 kV Bateias–Ibiúna C2, 14/10/2025)', N, 3803, N, 'MWh não supridos', '2025', '8.187 MW interrompidos; perturbação ONS 0176/2026', 'ONS dados abertos; Cenário Energia', 'https://cenarioenergia.com.br/2025/10/29/ons-detalha-causas-e-respostas-a-perturbacao-de-14-de-outubro-99-da-carga-recomposta-em-1h15/', 'aberto', 'média', 'dado oficial + imprensa', 'Ilustração da cauda (risco do próprio reator)'),
 ('', 'Posicionamento', '6.6', 'Manobra de reatores para necessidade dinâmica (ONS/EPE)', N, 'inadequada; preferem compensador síncrono', N, '—', 'out/2024', 'Sobretensão de 1,113 pu em Pres. Juscelino; reator de −150 Mvar levaria a ≈ 1,098 pu', 'RT-ONS DPL 0091/2024, p. 20–24', U_ONS91, 'aberto', 'média', 'documento técnico oficial', 'Posicionar o VSR no ciclo diário quase estático'),
 ('', 'Posicionamento', '6.6', 'Custo de compensação variável (referência)', 103.9, N, 229.9, 'R$ mi', 'mar/2024; 2024', 'Mín. = SVC 230 kV (−50/+100 Mvar); máx. = compensador síncrono (−200/+300 Mvar); banco de reator 500 kV = 17,7', 'EPE-DEE-RE-077/2024; RT-ONS DPL 0091/2024', 'https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-276/topico-708/EPE-DEE-RE-077-2024-rev0%20-%20Centro-Sul%20e%20Sul%20da%20Bahia%20-%20Parte%20II.pdf', 'aberto', 'média', 'documento técnico oficial', 'Custo do VSR frente a SVC e compensador síncrono'),
]
LC = ['id', 'bloco', 'secao_6', 'parametro', 'min', 'provavel', 'max', 'unidade', 'data_base', 'condicao_validade', 'fonte', 'url', 'acesso', 'confianca', 'tipo_fonte', 'uso_no_modelo']
LIT = pd.DataFrame([(f'L{i:02d}',) + t[1:] for i, t in enumerate(L, 1)], columns=LC)
KEY = {t[0]: f'L{i:02d}' for i, t in enumerate(L, 1) if t[0]}
LIT.to_csv(P + 'pesquisa_literatura_2026-10-13.csv', index=False, sep=';', encoding='utf-8-sig')
G = [
 ('Custo de manutenção de disjuntor no Brasil (R$ por intervenção; troca de contatos e bocais)', 'CIGRÉ TB 165 "Life management of circuit breakers" (2000); Heising et al., IEEE IAS 1994 (DOI 10.1109/IAS.1994.377738); anais do SNPTEE', 'pago / CIGRÉ Brasil', 'OPEX do fixo (slider)', 'Manter a premissa de 10% com Jeromin 2009 como âncora; perguntar a concessionárias'),
 ('Taxa de falha maior em função do número de operações', 'CIGRÉ TB 510; TB 947 (WG A3.48, 2024); força-tarefa IEEE C37.015', 'pago', 'Forma λ = λ0 + β·N', 'Usar β derivado como premissa declarada, com sensibilidade'),
 ('Distribuição da indisponibilidade após falha maior', 'CIGRÉ TB 510; TB 83 (1994); Heising et al. 1994; Energiforsk 2023:974 §7', 'pago / parcial', 'PVI e energia não suprida', 'Lognormal como premissa (mediana ~24 h, cauda ~100 h, mais semanas se a câmara vai à fábrica)'),
 ('Fração de falhas maiores com fogo ou explosão', 'CIGRÉ TB 510 (tabela "MaF – fires/explosions")', 'pago', 'Cauda da distribuição', 'Sensibilidade explícita, rotulada como premissa'),
 ('Duração do desligamento programado de manutenção do disjuntor', 'Vikesjö 2008 §11.5; dados de intervenções do ONS', 'aberto / parcial', 'Parcela Variável programada', 'Buscar'),
 ('Custo e duração de uma intervenção no OLTC', 'CIGRÉ TB 445 "Guide for Transformer Maintenance" (2011); serviços MR; planos de ativos Transgrid/Powerlink', 'pago / aberto', 'OPEX do VSR', 'Perguntar à Hitachi Energy'),
 ('Taxa de falha específica de VSR', 'CIGRÉ TB 939 (2024); TB 655 (WG A2.48, 2016); CIGRÉ A2-204/2018', 'pago', 'Névoa do VSR', 'Perguntar à Hitachi Energy'),
 ('Faixa de regulação a 230 kV e 500 kV de fabricante tradicional', 'CIGRÉ A2-207/2016 (Kirchner et al., Maschinenfabrik Reinhausen); TB 655', 'pago', 'Mínimo de regulação', 'Perguntar à Hitachi Energy'),
 ('Prêmio de CAPEX explícito (VSR contra fixo equivalente, só equipamento)', 'AEMO Transmission Cost Database v3.1; Hitachi Energy', 'cadastro / privado', 'VPL e prêmio de equilíbrio', 'Prioridade: perguntar à Hitachi Energy'),
 ('Operações de tap por dia em VSR em serviço', 'CIGRÉ 12-308/1998; ISH2015-20; CIGRÉ A2-204/2018', 'pago', 'OPEX do OLTC', 'Derivar do modelo físico (3.1)'),
 ('Preço do reator 230 kV e do reator como equipamento (UC 330)', 'Planilha completa do BPR (bpr@aneel.gov.br); Resoluções Autorizativas de reforço com reator 230 kV', 'sob pedido', 'Base do prêmio', 'Usar o custo de referência EPE (500 kV) e pedir a planilha à ANEEL'),
 ('Texto primário das taxas de depreciação do MCPSE', 'REN 474/2012 (Tabela XVI); REN 674/2015', 'aberto (site bloqueado no ambiente da pesquisa)', 'Valor residual', 'Confirmar'),
 ('Regra escrita: RAP do reforço até o fim da concessão e valor residual', 'Regras dos Serviços de Transmissão, Módulo 3 (REN 905/2020); PRORET Submódulo 9.1; NT 428-SCT/ANEEL', 'aberto', 'P2', 'Confirmar'),
 ('Interrupções de carga atribuídas a disjuntor', 'Relatórios de análise de perturbação do ONS (SIPER)', 'restrito', 'Visão SIN', 'Usar a energia não suprida geral (Interrupcoes_ENS) com fração atribuída como premissa'),
 ('Efeito da manobra controlada na taxa de falha e no desgaste; custo do controlador', 'CIGRÉ WG A3.07 / 13.07 (controlled switching); Hitachi Energy Switchsync', 'aberto / parcial', 'Contrafactual 2.8', 'Pesquisar'),
 ('Estratégia de reserva para VSR trifásico (custo e prazo)', 'Hitachi Energy; concessionárias com VSR (Statnett, Energinet)', 'privado', 'Risco 2.9', 'Perguntar à Hitachi Energy'),
 ('Valor em R$/MWh de energia não suprida próprio do planejamento da transmissão', 'Referência [17] do EPE-DEE-RE-057/2024', 'aberto', 'Visão SIN', 'Buscar; por ora, custo do déficit'),
]
LAC = pd.DataFrame([(f'G{i:02d}',) + g for i, g in enumerate(G, 1)], columns=['id', 'o_que_falta', 'melhor_fonte_provavel', 'acesso', 'impacto_no_modelo', 'acao'])
LAC.to_csv(P + 'pesquisa_lacunas_2026-10-13.csv', index=False, sep=';', encoding='utf-8-sig')
print(len(LIT), 'parâmetros;', len(LAC), 'lacunas')

# ======================= 4. Planilha-mestre =======================
F = 'Arial'
fT = Font(name=F, size=14, bold=True); fS = Font(name=F, size=9, italic=True, color='555555')
fH = Font(name=F, size=10, bold=True, color='FFFFFF'); fN = Font(name=F, size=10)
fBlue = Font(name=F, size=10, color='0000FF'); fGreen = Font(name=F, size=10, color='008000'); fBold = Font(name=F, size=10, bold=True)
hdrFill = PatternFill('solid', fgColor='1F3864'); keyFill = PatternFill('solid', fgColor='FFFF00')
thin = Side(style='thin', color='BFBFBF')
wb = openpyxl.load_workbook(XL)
NEW = ['Pesquisa_Literatura', 'Pesquisa_Lacunas', 'Volatilidade_Cenarios', 'Volatilidade_Mensal', 'Volatilidade_Anual', 'Interrupcoes_ENS', 'Fluxo_NNE_Perfil', 'Fluxo_NNE_Mensal']
for n in NEW:
    if n in wb.sheetnames: del wb[n]
pos = wb.sheetnames.index('Fontes_Reforcadas') if 'Fontes_Reforcadas' in wb.sheetnames else wb.sheetnames.index('Fontes_Primarias')
REF = {}
def sheet_df(name, idx, title, source, df, key=None, numfmt=None, widths=None, notes=None, blue=()):
    ws = wb.create_sheet(name, idx)
    ws['A1'] = title; ws['A1'].font = fT
    ws['A2'] = 'Fonte: ' + source; ws['A2'].font = fS
    if notes: ws['A3'] = notes; ws['A3'].font = fS
    r0 = 4
    for jj, c in enumerate(df.columns, 1):
        cell = ws.cell(r0, jj, str(c)); cell.font = fH; cell.fill = hdrFill; cell.alignment = Alignment(wrap_text=True, vertical='center')
    for i, row in enumerate(df.itertuples(index=False), r0 + 1):
        for jj, v in enumerate(row, 1):
            if v is None or (isinstance(v, float) and np.isnan(v)): v = None
            elif isinstance(v, np.integer): v = int(v)
            elif isinstance(v, np.floating): v = float(v)
            col = df.columns[jj - 1]
            cell = ws.cell(i, jj, v); cell.font = fBlue if (col in blue and v is not None) else fN
            cell.alignment = Alignment(wrap_text=True, vertical='top')
            if numfmt and col in numfmt: cell.number_format = numfmt[col]
        if key is not None:
            k = row[list(df.columns).index(key)]
            for jj, c in enumerate(df.columns, 1): REF[(name, k, c)] = f"'{name}'!${get_column_letter(jj)}${i}"
    ws.freeze_panes = ws.cell(r0 + 1, 1)
    for jj, c in enumerate(df.columns, 1):
        ws.column_dimensions[get_column_letter(jj)].width = (widths or {}).get(c) or min(max(len(str(c)) + 2, 11), 40)
    ws.row_dimensions[r0].height = 30
    return ws
SRC_LIT = 'Pesquisa por três agentes em 13/10/2026 (disjuntor; VSR/OLTC/reator; regulatório e visão SIN), com conferência na fonte dos itens marcados. Script: scripts/08_pesquisa_volatilidade.py'
sheet_df('Pesquisa_Literatura', pos, 'Pesquisa de literatura: parâmetros com faixa, fonte e confiança (13/10/2026)', SRC_LIT, LIT, key='id',
         widths={'id': 6, 'bloco': 14, 'secao_6': 8, 'parametro': 44, 'min': 11, 'provavel': 13, 'max': 11, 'unidade': 18, 'data_base': 14,
                 'condicao_validade': 50, 'fonte': 46, 'url': 36, 'acesso': 14, 'confianca': 11, 'tipo_fonte': 20, 'uso_no_modelo': 36},
         notes='Azul = valor digitado da literatura. Faixa: min/max quando a fonte dá intervalo; "derivado" = conta sobre o número da fonte, não dado novo. Confiança: alta = norma, CIGRÉ, ato oficial ou TSO; média = artigo técnico ou fabricante; baixa = fonte secundária.',
         blue=('min', 'provavel', 'max'))
sheet_df('Pesquisa_Lacunas', pos + 1, 'Pesquisa de literatura: o que não foi encontrado em fonte aberta (13/10/2026)', SRC_LIT, LAC,
         widths={'id': 6, 'o_que_falta': 52, 'melhor_fonte_provavel': 60, 'acesso': 18, 'impacto_no_modelo': 26, 'acao': 50})
SRC_V = 'ONS – BALANCO_DESSEM_DETALHE (semi-horário, programado) e Intercâmbios Entre Subsistemas (horário, verificado; acesso em 13/10/2026, cc-by). Script: scripts/08_pesquisa_volatilidade.py'
NOTE_V = ('Volatilidade (decisão P4) = desvio-padrão dos desvios da série em torno do perfil típico (mês × dia útil/fim de semana × meia-hora), em % da demanda média do subsistema; '
          'desvios corrigidos pelo viés do perfil estimado (× √(n/(n−1))); só meses com ≥ 20 dias completos. Intradiário = desvio menos a média do dia; diário = desvio-padrão da média diária dos desvios. '
          'φ = autocorrelação dos desvios; τ = −Δt/ln φ.')
pct = '0.00'
sheet_df('Volatilidade_Cenarios', pos + 2, 'Volatilidade da carga líquida por cenário (decisão P4)', SRC_V, VC, key='serie', notes=NOTE_V,
         numfmt={**{c: pct for c in VC.columns if c.endswith('_pct')}, 'demanda_media_MW': '#,##0', 'serie_media_MW': '#,##0', 'sigma_MW': '#,##0',
                 'phi_30min': '0.000', 'phi_60min': '0.000', 'tau_h': '0.0'}, widths={'definicao': 44, 'cenario': 14, 'resolucao': 10})
SRC_F = 'ONS – Portal de Dados Abertos, Intercâmbios Entre Subsistemas (intercambio_nacional_ho), horário, verificado; acesso em 13/10/2026, cc-by. Script: scripts/08_pesquisa_volatilidade.py'
NOTE_F = '2025: par fixo N→NE com sinal (negativo = NE→N). 2026: o par vem no sentido do fluxo, com valor positivo; convertido para N→NE com sinal. Positivo = Norte exporta para o Nordeste. Inversão = troca de sentido entre horas consecutivas (|P| passa por zero, transferência mínima).'
sheet_df('Fluxo_NNE_Perfil', pos + 6, 'Fluxo medido na interligação Norte–Nordeste: perfil por hora do dia (jan/2025–out/2026)', SRC_F, FP, key='hora', notes=NOTE_F,
         numfmt={**{c: '#,##0' for c in FP.columns if c.endswith('_MW')}, 'pct_horas_NE_para_N': '0.0'})
sheet_df('Fluxo_NNE_Mensal', pos + 7, 'Fluxo medido na interligação Norte–Nordeste: resumo mensal', SRC_F, FM, key='mes', notes=NOTE_F,
         numfmt={'fluxo_medio_MW': '#,##0', 'abs_medio_MW': '#,##0', 'pct_horas_NE_para_N': '0.0', 'inversoes_por_dia': '0.00', 'pct_horas_abs_abaixo_500MW': '0.0'})
sheet_df('Volatilidade_Mensal', pos + 3, 'Volatilidade da carga líquida por mês e série', SRC_V, VM, notes=NOTE_V,
         numfmt={'demanda_media_MW': '#,##0', 'sigma_pct': pct, 'sigma_intradiario_pct': pct})
sheet_df('Volatilidade_Anual', pos + 4, 'Volatilidade da carga horária por subsistema e ano, 2015–2026 (tendência)',
         'ONS – curva de carga horária 2015–2026 (processed/carga_horaria_2015_2026_longo.csv). Script: scripts/08_pesquisa_volatilidade.py', VA,
         notes='Mesmo método da P4 em base horária, mas sobre a CARGA (não a carga líquida: eólica e FV centralizadas não são descontadas). Serve para ver a tendência; o valor do slider vem de Volatilidade_Cenarios. 2026 é parcial.',
         numfmt={'carga_media_MW': '#,##0', 'sigma_pct': pct, 'sigma_intradiario_pct': pct, 'sigma_diario_pct': pct, 'phi_1h': '0.000'})
sheet_df('Interrupcoes_ENS', pos + 5, 'Energia não suprida por perturbação com envolvimento da Rede Básica, 2016–2025',
         'ONS – Portal de Dados Abertos, INTERRUPCAO_CARGA.csv (acesso em 09/10/2026, cc-by). Script: scripts/08_pesquisa_volatilidade.py', EN, key='ano',
         notes='Uma linha por perturbação (cod_perturbacao): MW e MWh somados entre agentes; tempo de recomposição = maior tempo médio entre agentes. O dado aberto não traz a causa: inclui todas as origens, não só disjuntor.',
         numfmt={c: '#,##0.0' for c in EN.columns if c not in ('ano', 'perturbacoes')})
fim = 'Fontes_Reforcadas' if 'Fontes_Reforcadas' in wb.sheetnames else 'Fontes_Primarias'
for nm in ('Fluxo_NNE_Perfil', 'Fluxo_NNE_Mensal'):
    wb.move_sheet(nm, offset=wb.sheetnames.index(fim) - wb.sheetnames.index(nm))
# ---- Parametros_Modelo: P57+ ----
ws = wb['Parametros_Modelo']
first = next((r for r in range(5, ws.max_row + 1) if isinstance(ws.cell(r, 1).value, str) and ws.cell(r, 1).value[1:].isdigit() and int(ws.cell(r, 1).value[1:]) >= 57), None)
if first: ws.delete_rows(first, ws.max_row - first + 1)
rng = lambda a, b: a + ':' + b.split('!')[1]
HR = rng(REF[('Fluxo_NNE_Perfil', 0, 'hora')], REF[('Fluxo_NNE_Perfil', 23, 'hora')])
AB = rng(REF[('Fluxo_NNE_Perfil', 0, 'abs_medio_MW')], REF[('Fluxo_NNE_Perfil', 23, 'abs_medio_MW')])
HMIN = f'=INDEX({HR},MATCH(MIN({AB}),{AB},0))'
LR = lambda k, c='provavel': '=' + REF[('Pesquisa_Literatura', KEY[k], c)]
VR = lambda s, c: '=' + REF[('Volatilidade_Cenarios', s, c)]
PR = [
 ('Confiabilidade (pesquisa)', 'Taxa de falha grave – disjuntor de manobra de reator shunt', LR('maf_reator'), 'falhas/100 disjuntores-ano', 'Taxa central de falha do disjuntor do reator fixo', 'CIGRÉ TB 510 via Novák 2018', 'Pesquisa_Literatura', 'Substitui P37 para o disjuntor de reator. Faixa 1,98–3,02; tanque vivo 6,79; tanque morto 1,17.', False),
 ('Confiabilidade (pesquisa)', 'Taxa de falha grave – disjuntor de linha (regime do VSR)', LR('maf_linha'), 'falhas/100 disjuntores-ano', 'Taxa do disjuntor do VSR, que quase não manobra', 'CIGRÉ TB 510 via Novák 2018', 'Pesquisa_Literatura', 'Razão reator ÷ linha ≈ 10 (CIGRE CSE nº 23).', False),
 ('Manutenção (pesquisa)', 'Revisão geral do disjuntor por contagem (GE GL314)', LR('rev_ciclos'), 'operações', 'Gatilho de revisão do disjuntor do fixo (ciclos CO)', 'GE Vernova – manual GL314', 'Pesquisa_Literatura', 'Ou 20 anos, o que vier primeiro. Faixa genérica 2.000–2.500 operações (Hermosillo 2002).', False),
 ('VSR (pesquisa)', 'Mínimo de regulação do VSR 400–500 kV (padrão do slider)', 50, '% (escala 0–100)', 'Manobras residuais e viabilidade do caso 1:1', 'CIGRÉ A2-211/2014; Energinet TED 704840-2023', 'Pesquisa_Literatura', 'Faixa 45–60% nas fontes técnicas; 20% só em material comercial.', True),
 ('VSR (pesquisa)', 'Perdas do VSR na posição mínima', LR('perdas_min'), '% (escala 0–100)', 'Perdas como custo do VSR (visão SIN)', 'IPST 2015 (HOPS 420 kV)', 'Pesquisa_Literatura', 'Fixo desligado dissipa zero.', False),
 ('Custos (pesquisa)', 'Reator monofásico 500 kV 66,6 Mvar – custo de referência (mar/2021)', LR('reator_500'), 'R$ mi', 'Base do prêmio de CAPEX', 'EPE-DEE-NT-077/2021', 'Pesquisa_Literatura', 'O BPR aberto não traz o preço do reator em si.', False),
 ('Custos (pesquisa)', 'Conexão de reator de barra 500 kV (DJM) – custo modular EPE (mar/2021)', LR('crb_500'), 'R$ mi', 'CAPEX de vão evitado (caso 2:1)', 'EPE-DEE-NT-077/2021', 'Pesquisa_Literatura', 'Não misturar com a soma direta do BPR aberto (base 2017).', False),
 ('Custos (pesquisa)', 'Preço de VSR 400 kV 70–140 Mvar – Energinet (2023)', LR('vsr_energinet'), '€ mi', 'Ordem de grandeza do CAPEX do VSR', 'Energinet – TED 704840-2023', 'Pesquisa_Literatura', 'Escopo diferente do reator EPE: não é o prêmio. Prêmio segue pendente (Hitachi Energy).', True),
 ('Visão SIN (pesquisa)', 'Custo do déficit 2026', LR('deficit'), 'R$/MWh', 'Valor da energia não suprida', 'NT 11/2025/GPRE/GEPME/AGM', 'Pesquisa_Literatura', 'Custo de suficiência, não de interrupção local: declarar como premissa.', False),
 ('Visão SIN (pesquisa)', 'Taxa social de desconto', LR('tsd'), '% (escala 0–100)', 'Taxa de desconto da visão SIN (P3)', 'NT SEI 19911/2020/ME', 'Pesquisa_Literatura', 'EPE usa 8% (sensibilidade).', False),
 ('Regulatório (pesquisa)', 'Depreciação regulatória – reator', LR('dep_reator'), '% (escala 0–100)', 'Valor residual e indenização (P2)', 'MCPSE via DFR ETEM 2011', 'Pesquisa_Literatura', 'Vida ≈ 36 anos.', False),
 ('Regulatório (pesquisa)', 'Depreciação regulatória – disjuntor', LR('dep_disj'), '% (escala 0–100)', 'Valor residual do disjuntor trocado', 'MCPSE via DFR ETEM 2011', 'Pesquisa_Literatura', 'Vida ≈ 33 anos.', False),
 ('Volatilidade (P4)', 'Volatilidade padrão – Centro Urbano', VR('urbano', 'sigma_pct'), '% (escala 0–100)', 'Valor padrão do slider de volatilidade', 'ONS – DESSEM detalhado', 'Volatilidade_Cenarios', 'NE, demanda − MMGD − FV. Faixa mensal p10–p90 na aba de origem.', False),
 ('Volatilidade (P4)', 'Volatilidade padrão – Campo', VR('campo', 'sigma_pct'), '% (escala 0–100)', 'Valor padrão do slider de volatilidade', 'ONS – intercâmbio entre subsistemas', 'Volatilidade_Cenarios', 'Fluxo horário medido N–NE em módulo; em % da carga média do N.', False),
 ('Volatilidade (P4)', 'Volatilidade padrão – Polo eólico', VR('polo_eolico', 'sigma_pct'), '% (escala 0–100)', 'Valor padrão do slider de volatilidade', 'ONS – DESSEM detalhado', 'Volatilidade_Cenarios', 'NE, carga líquida, dominada pela eólica regional (variações lentas, de horas a dias).', False),
 ('Volatilidade (P4)', 'Autocorrelação de 30 min dos desvios – Centro Urbano', VR('urbano', 'phi_30min'), 'adim.', 'Persistência do processo de desvios', 'ONS – DESSEM detalhado', 'Volatilidade_Cenarios', '', False),
 ('Volatilidade (P4)', 'Autocorrelação de 1 h dos desvios – Campo', VR('campo', 'phi_60min'), 'adim.', 'Persistência do processo de desvios', 'ONS – intercâmbio entre subsistemas', 'Volatilidade_Cenarios', 'Série horária.', False),
 ('Volatilidade (P4)', 'Autocorrelação de 30 min dos desvios – Polo eólico', VR('polo_eolico', 'phi_30min'), 'adim.', 'Persistência do processo de desvios', 'ONS – DESSEM detalhado', 'Volatilidade_Cenarios', '', False),
 ('Visão SIN (dados ONS)', 'Energia não suprida por perturbação com Rede Básica – mediana 2016–2025', '=' + REF[('Interrupcoes_ENS', '2016–2025', 'MWh_p50')], 'MWh', 'Consequência típica de uma interrupção', 'ONS – INTERRUPCAO_CARGA', 'Interrupcoes_ENS', 'Inclui todas as causas; p90 e média na aba de origem.', False),
 ('Campo (dados ONS)', 'Inversões de sentido do fluxo N–NE por dia (média)', '=' + REF[('Fluxo_NNE_Mensal', 'total', 'inversoes_por_dia')], 'por dia', 'Passagens de |P| por zero (transferência mínima, máximo Ferranti)', 'ONS – intercâmbio entre subsistemas', 'Fluxo_NNE_Mensal', 'Valores por mês na aba de origem.', False),
 ('Campo (dados ONS)', 'Hora do dia de menor transferência média N–NE', HMIN, 'hora do dia', 'Quando a interligação fica mais leve (pede reator)', 'ONS – intercâmbio entre subsistemas', 'Fluxo_NNE_Perfil', 'Testa a narrativa "Ferranti nas madrugadas".', False),
 ('Campo (dados ONS)', 'Razão σ medido ÷ σ programado – fluxo N–NE (2026)', '=' + REF[('Volatilidade_Cenarios', 'ref_NNE_medido_2026', 'sigma_MW')] + '/' + REF[('Volatilidade_Cenarios', 'ref_NNE_programado_2026', 'sigma_MW')], 'x', 'Quanto o dado programado subestima a flutuação real', 'ONS – intercâmbio (verificado e programado)', 'Volatilidade_Cenarios', 'Acima de 1: os valores do DESSEM (programados) são piso.', False),
]
start = ws.max_row + 1
for i, (g, p, v, u, uso, fonte, aba, obs, key_) in enumerate(PR, start):
    vals = [f'P{57 + i - start}', g, p, v, u, uso, fonte, aba, obs]
    for jj, x in enumerate(vals, 1):
        c = ws.cell(i, jj, x); c.font = fN; c.alignment = Alignment(wrap_text=True, vertical='top'); c.border = Border(bottom=thin)
    vc = ws.cell(i, 4)
    if isinstance(v, str) and v.startswith('='):
        vc.font = fGreen if (v.count('!') == 1 and '(' not in v and '/' not in v) else fN
    else:
        vc.font = fBlue
    vc.number_format = {'adim.': '0.000', 'R$ mi': '#,##0.000', '€ mi': '#,##0.000', 'operações': '#,##0', 'hora do dia': '0', 'x': '0.00', 'por dia': '0.00'}.get(u, '#,##0.00')
    if key_: vc.fill = keyFill
# ---- LEIA-ME ----
ws = wb['LEIA-ME']
lines = []
for r in range(1, ws.max_row + 1):
    v = ws.cell(r, 1).value
    if v == 'Abas da planilha': break
    lines.append([v or '', 'T' if r == 1 else ('B' if ws.cell(r, 1).font.b else 'N')])
lines[0][0] = 'PoliVSR – Base de Dados do Modelo (v3, 13/10/2026 – pesquisa de literatura e volatilidade)'
INS = ('4. Pesquisa_Literatura', 'Volatilidade (decisão P4)', '• Os cenários usam', '• Pesquisa_Literatura:', '• Cenários (v3):')
lines = [x for x in lines if not x[0].startswith(INS)]
out = []
for t, f in lines:
    if t.startswith('3. Reprodutibilidade'):
        t = '3. Reprodutibilidade: os arquivos brutos estão em raw/ e os scripts Python em scripts/ (00 a 08). Rodar na ordem regenera tudo; o 08 roda depois do 05 e acrescenta as abas da v3. O manifesto traz o SHA-256 de cada arquivo bruto.'
    if t.startswith('• O preço do reator em si') and 'Conferido em 13/10/2026' not in t:
        t += ' Conferido em 13/10/2026: o BPR aberto não tem nenhum módulo de VSR; do reator, só os acessórios (aba Pesquisa_Literatura).'
    if t.startswith('• Sem fonte aberta para o custo de manutenção'):
        t = '• Sem fonte aberta brasileira para o custo de manutenção do disjuntor: segue como premissa (10%, ajustável); a literatura (Jeromin 2009) dá ≈ 10% do investimento por revisão geral.'
    out.append((t, f))
    if t.startswith('3. Reprodutibilidade'):
        out.append(('4. Pesquisa_Literatura e Pesquisa_Lacunas: parâmetros levantados em 13/10/2026 (faixa mín./provável/máx., fonte, URL, confiança) e o que não foi encontrado em fonte aberta. Volatilidade_*: calibração da decisão P4. Interrupcoes_ENS: energia não suprida por perturbação. As linhas P57 em diante de Parametros_Modelo puxam essas abas.', 'N'))
    if t.startswith('Disponibilidade FTRT'):
        out.append(('Volatilidade (decisão P4) = desvio-padrão dos desvios da carga líquida em torno do perfil típico (mês × dia útil/fim de semana × meia-hora), em % da demanda média do subsistema. φ30 = autocorrelação dos desvios em 30 min.', 'N'))
    if t.startswith('• Sem fonte aberta brasileira'):
        out.append(('• Os cenários usam o subsistema (NE, N) do DESSEM como aproximação da barra; a volatilidade de uma subestação específica pode ser maior.', 'N'))
        out.append(('• Cenários (v3): Centro Urbano (NE: demanda − MMGD − FV, DESSEM), Campo (interligação N–NE: fluxo horário verificado em módulo, ONS intercâmbio entre subsistemas, abas Fluxo_NNE_*) e Polo eólico (antigo "Indústria": carga líquida do NE, dominada pela eólica). A volatilidade do Campo está em % da carga média do N.', 'N'))
        out.append(('• Pesquisa_Literatura: confiança "baixa" = fonte secundária; "derivado" = conta sobre o número da fonte. Itens marcados "conferida em 13/10/2026" foram checados na fonte primária.', 'N'))
ws.delete_rows(1, ws.max_row)
FM = {'T': fT, 'B': fBold, 'N': fN}
for i, (t, f) in enumerate(out, 1):
    c = ws.cell(i, 1, t if t else None); c.font = FM[f]; c.alignment = Alignment(wrap_text=True, vertical='top')
r = len(out) + 2
ws.cell(r, 1, 'Abas da planilha').font = fBold
for k, name in enumerate(wb.sheetnames, r + 1): ws.cell(k, 1, name).font = fN
wb.save(XL)
pm = wb['Parametros_Modelo']
print('ok', XL, len(wb.sheetnames), 'abas; Parametros_Modelo até', pm.cell(pm.max_row, 1).value)

"""11 - Dados da calculadora do site (contrato de dados da secao 7 do escopo).

Reusa o motor do script 10 (secoes 1 e 2, sem rodar a execucao nem mexer na planilha) e gera processed/site_calculadora.json:
para cada cenario, visao (concessionaria / SIN) e conjunto de premissas, as estatisticas do VPL, da probabilidade de compensar e do
payback numa grade de DOIS precos: o do VSR (R$) e o do reator fixo (fator f sobre a referencia EPE/ANEEL corrigida pelo IPCA).
Os sorteios nao dependem dos precos, e cada fluxo do modelo e afim no preco do VSR e no preco por Mvar do fixo (custo do equipamento,
fase reserva e reparos proporcionais ao preco). Por isso tres rodadas com a mesma semente (f = 1 e VSR = fixos; f = 1 e VSR = 2 x fixos;
f = 2 e VSR = fixos de referencia) dao o resultado exato em qualquer ponto da grade. Entre pontos, a calculadora interpola linearmente.
Tambem exporta a nevoa (custo acumulado descontado por ano) das premissas-base, a cascata, os operacionais e um dia tipico de UMA
subestacao (banco fixo A manobravel + fatia permanente B, contra 1 VSR), para o grafico de reativo e de tensao estimada.
Uso: python 11_dados_site.py <pasta_base_PoliVSR-dados>   (rodar depois do 10)"""
import sys, os, json, time, numpy as np
BASE = sys.argv[1]; t0 = time.time()
SRC = open(os.path.join(BASE, 'scripts', '10_modelo_financeiro.py'), encoding='utf-8').read()
CUT = SRC.index('# ======================= 3. Execucao')
sys.argv = ['10_modelo_financeiro.py', BASE, os.path.join(BASE, 'PoliVSR_Base_de_Dados.xlsx')]
G = {'__name__': 'motor10'}
exec(compile(SRC[:CUT], '10_modelo_financeiro.py (secoes 1-2)', 'exec'), G)
simular, CEN, PV_LEVEL, VPC, EURBRL, S0, H, J9, fis, PREAT, PVAO = (G[k] for k in ('simular', 'CEN', 'PV_LEVEL', 'VPC', 'EURBRL', 'S0', 'H', 'J9', 'fis', 'PREAT', 'PVAO'))
P = os.path.join(BASE, 'processed') + '/'

GRADE = {500.0: np.round(np.arange(15.0, 90.0 + 1e-9, 1.0), 2), 230.0: np.round(np.arange(3.0, 18.0 + 1e-9, 0.2), 2)}   # preco do VSR, R$ mi
FGRID = np.round(np.arange(0.5, 1.6 + 1e-9, 0.1), 2)       # preco do fixo: fator sobre a referencia (EPE/ANEEL mar/2021 x IPCA)
F_NOMINAL = 1 / G['ipca']('2021-03')                        # referencia de 2021 sem correcao pelo IPCA
VAR = [('base', 'Premissas-base', {}, 'todas'),
       ('reforco', 'Reforço com RAP pelo BPR', {'regime': 'reforco'}, 'concessionaria'),
       ('rap', 'Prêmio reconhecido na RAP', {'premio_rap': True}, 'concessionaria'),
       ('pool', 'Reserva do VSR em pool de 1 para 10', {'reserva': '1:10'}, 'todas'),
       ('res13', 'Reserva do VSR de 1 para 3', {'reserva': '1:3'}, 'todas'),
       ('fase_comp', 'Fase reserva compartilhada pelos 2 bancos', {'fase_reserva': 'compartilhada'}, '500'),
       ('fase_nenhuma', 'Fixo sem fase reserva', {'fase_reserva': 'nenhuma'}, '500'),
       ('oleo', 'OLTC a óleo (teste de estresse)', {'oltc': 'oleo'}, 'todas')]
r1 = lambda x, n=3: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)

def pay50(cum):
    """Mediana do payback (meses) com a mesma regra do script 10: censurado (> 360) quando o VPL e negativo ou nao vira no horizonte."""
    vpl = cum[:, -1]
    neg = cum < 0; has = neg.any(1); last = H - np.argmax(neg[:, ::-1], 1)
    pay = np.where(has, last + 1, 0).astype(float); pay[vpl < 0] = np.inf; pay[has & (last >= H)] = np.inf
    z = np.percentile(pay, 50, method='lower')
    return float(z) if np.isfinite(z) else None

def rodar(cen, vis, kw, kv, prFix0):
    """Tres rodadas de mesma semente; devolve os incrementos acumulados e as rodadas."""
    o0 = simular(cen, vis, S0, 11, premio=0.0, **kw)                     # f = 1, VSR = fixos de referencia
    o1 = simular(cen, vis, S0, 11, premio=1.0, **kw)                     # f = 1, VSR = 2 x fixos de referencia
    p_ref = PREAT[kv]; PREAT[kv] = 2 * p_ref                             # f = 2 (preco por Mvar do fixo dobrado)
    try:
        o2 = simular(cen, vis, S0, 11, premio=prFix0 / (2 * prFix0) - 1, **kw)   # VSR mantido no valor absoluto de o0
    finally:
        PREAT[kv] = p_ref
    assert abs(o2['prVSR'] - prFix0) < 1e-3 and abs(o2['prFix'] - 2 * prFix0) < 1e-3
    inc = [o['CFd']['fixo'] - o['CFd']['vsr'] for o in (o0, o1, o2)]
    return o0, o1, o2, inc[0], inc[1] - inc[0], inc[2] - inc[0]          # base, d/d(VSR = +1 x fixos), d/d(f = +1)

OUT = dict(meta=dict(gerado_em=time.strftime('%Y-%m-%d'), fonte='scripts/11_dados_site.py sobre o motor do script 10', simulacoes=S0, eur_brl=EURBRL,
                     moeda='R$ de set/2026', horizonte_anos=30, taxa_concessionaria=G['WACC'], taxa_sin=G['TSD'], fgrid=FGRID.tolist(),
                     f_nominal_2021=round(F_NOMINAL, 4),
                     precos_fonte=dict(
                         fixo='EPE-DEE-NT-077/2021, Tab. 7-1: reator monofásico de 500 kV e 66,6 Mvar a R$ 4,415 mi (Base de Referência de Preços ANEEL, mar/2021), corrigido pelo IPCA até set/2026',
                         fixo230='Preço por Mvar do 500 kV ajustado pela regra de escala (66,6/20)^0,4 (premissa)',
                         vao='Conexão de reator de barra (CRB): EPE-DEE-NT-077/2021 (500 kV, R$ 9,589 mi em mar/2021); 230 kV pelo BPR da ANEEL × razão EPE/BPR; corrigidos pelo IPCA',
                         vsr='Contratos públicos de fornecimento de 2025–26 (Litgrid, Energinet) escalados por Mvar^0,6 × kV^0,5; câmbio BCB set/2026')),
           contratos=[{k: (None if (isinstance(v, float) and not np.isfinite(v)) else (v.item() if hasattr(v, 'item') else v)) for k, v in row.items()}
                      for row in VPC.to_dict(orient='records')],
           cenarios={})
NOMES = {'urbano': ('Centro Urbano', 'Base: Salvador, Recife, Fortaleza · 230 kV'), 'campo': ('Campo', 'Base: Interligação N–NE · 500 kV'),
         'polo_eolico': ('Polo eólico', 'Base: carga líquida do Nordeste · 500 kV')}
U_NOME = {'urbano': ('Carga líquida do Nordeste', 'demanda menos solar e micro e minigeração distribuída (ONS, DESSEM)'),
          'campo': ('Fluxo Norte–Nordeste', 'módulo do fluxo verificado na interligação (ONS)'),
          'polo_eolico': ('Carga líquida do Nordeste com eólica', 'módulo da demanda menos solar, micro e minigeração e eólica (ONS, DESSEM)')}
ETA = J9['meta']['caso_base']['eta']; M = J9['meta']['caso_base']['m']; NB = J9['meta']['caso_base']['N']

def dia_subestacao(cen, W):
    """Dia tipico de UMA subestacao: banco A (W, manobravel, regra de 1 banco com histerese), fatia permanente B (S_B) e 1 VSR (S_V)
    com as posicoes de tap do modelo fisico. Nos cenarios de 1 banco (Centro Urbano, Polo eolico) A e exatamente o nivel do modelo;
    no Campo o modelo usa 6 bancos no corredor, e aqui se mostra uma subestacao com 1 banco sob a mesma necessidade normalizada."""
    dt = J9['dia_tipico'][cen]; r = np.array(dt['r'], float); tap = np.array(dt['nivel_vsr'], float); n = r.size
    SB, SV = M * W / (1 - M), W / (1 - M); Bm = M / (1 - M)
    if NB[cen] == 1:
        A = np.array(dt['nivel_fixo'], float)
    else:
        on, off = 0.5 + ETA / 2, 0.5 - ETA / 2; A = np.zeros(n); s = 1.0 if r[0] > 0.5 else 0.0
        for i in range(n):
            if s == 0 and r[i] > on: s = 1.0
            elif s == 1 and r[i] < off: s = 0.0
            A[i] = s
    sai, volta = -Bm / 2 - ETA * Bm / 2, -Bm / 2 + ETA * Bm / 2              # mesma regra de saida da fatia B (modelo fisico)
    B = np.ones(n); s = 1.0
    for i in range(n):
        if s == 1 and r[i] < sai: s = 0.0
        elif s == 0 and r[i] > volta: s = 1.0
        B[i] = s
    taps = int(round(np.abs(np.diff(tap)).sum() * 32))
    # carregamento que move o cenario (MW), recuperado de r pela mesma formula do modelo fisico: r = (hi^2 - u^2) / (hi^2 - lo^2)
    lo, hi = J9['series'][cen]['lo'], J9['series'][cen]['hi']
    u = np.sqrt(np.maximum(hi ** 2 - r * (hi ** 2 - lo ** 2), 0.0))
    return dict(data=dt['data'], hora=dt['hora'], r=[r1(x, 4) for x in r], A=A.astype(int).tolist(), B=B.astype(int).tolist(), tap=[r1(x, 5) for x in tap],
                u=[r1(x, 0) for x in u], u_lo=r1(lo, 0), u_hi=r1(hi, 0), u_nome=U_NOME[cen],
                W=W, SB=SB, SV=SV, manobras_fixo=int(np.abs(np.diff(A)).sum() + np.abs(np.diff(B)).sum()), taps_vsr=taps,
                bancos_corredor=NB[cen], manobras_corredor=dt['manobras_fixo'], taps_modelo=dt['taps_vsr'])

for cen, c in CEN.items():
    kv = c['kv']; W = c['W']; grade = GRADE[kv]
    o_ref = simular(cen, 'concessionaria', 200, 1)
    prFix0, pV = o_ref['prFix'], o_ref['pV']; pR0 = PREAT[kv]
    f = fis(cen)
    C = dict(nome=NOMES[cen][0], base=NOMES[cen][1], kv=int(kv), W=W, mvar_vsr=W / (1 - M), preco_fixos=prFix0, preco_vao=pV,
             preco_mvar_fixo=pR0, preco_banco_fixo=W * pR0, fase_reserva_mvar=((W + M * W / (1 - M)) / 3 if kv == 500.0 else 0.0),
             precos={k: v * (1.0) for k, v in PV_LEVEL[kv].items()}, grade=grade.tolist(), dia=dia_subestacao(cen, W), visoes={})
    for vis in ('concessionaria', 'sin'):
        V = {'variantes': {}}
        for key, nome, kw, onde in VAR:
            if onde == 'concessionaria' and vis != 'concessionaria': continue
            if onde == '500' and kv != 500.0: continue
            o0, o1, o2, inc0, dV, dF = rodar(cen, vis, kw, kv, prFix0)
            xv = grade * 1e6 / prFix0 - 1                                  # VSR em unidades de "x fixos de referencia" acima de 1
            st = {k: [] for k in ('p10', 'p50', 'p90', 'ppos', 'pay50')}
            eq = {'p10': [], 'p50': [], 'p90': []}
            v0, dv, df = inc0[:, -1], dV[:, -1], dF[:, -1]
            for fv in FGRID:
                vf = v0 + (fv - 1) * df                                    # VPL em VSR = fixos de referencia, para este f
                VV = vf[:, None] + dv[:, None] * xv[None, :]               # S x grade
                for q in (10, 50, 90): st[f'p{q}'].append([r1(x / 1e6) for x in np.percentile(VV, q, axis=0)])
                st['ppos'].append([r1(x, 4) for x in (VV > 0).mean(0)])
                base_f = inc0 + (fv - 1) * dF
                st['pay50'].append([pay50(base_f + dV * x) for x in xv])
                be = prFix0 * (1 - vf / dv) / 1e6                          # preco do VSR que zera o VPL de cada simulacao (R$ mi)
                for q in (10, 50, 90): eq[f'p{q}'].append(r1(np.percentile(be, q), 3))
            comps = sorted({cc for o in (o0, o1, o2) for (_, cc) in o['PVC']})
            casc = []
            for cc in comps:
                g = [o['PVC'].get(('fixo', cc), np.zeros(S0)).mean() - o['PVC'].get(('vsr', cc), np.zeros(S0)).mean() for o in (o0, o1, o2)]
                if max(abs(x) for x in g) < 1: continue
                casc.append(dict(c=cc, a=r1(g[0] / 1e6, 4), bv=r1((g[1] - g[0]) / prFix0, 6), bf=r1((g[2] - g[0]) / 1e6, 4)))
                # ganho (R$ mi) = a + bv x (preco do VSR - fixos de referencia, R$ mi) + bf x (f - 1)
            V['variantes'][key] = dict(nome=nome, stats=st, equilibrio=eq, cascata=casc)
            if key == 'base':
                anos = list(range(31)); mi = [12 * y for y in anos]
                fx0 = o0['CFd']['fixo'][:, mi] / 1e6; dfx = o2['CFd']['fixo'][:, mi] / 1e6 - fx0
                vs0 = o0['CFd']['vsr'][:, mi] / 1e6; dvs = o1['CFd']['vsr'][:, mi] / 1e6 - vs0
                assert np.allclose(o2['CFd']['vsr'][:, mi] / 1e6, vs0)                   # o custo do VSR nao depende do preco do fixo
                nev = dict(anos=anos, fixo={'p10': [], 'p50': [], 'p90': []}, vsr={'p10': [], 'p50': [], 'p90': []})
                for fv in FGRID:
                    ff = fx0 + (fv - 1) * dfx
                    for q in ('p10', 'p50', 'p90'): nev['fixo'][q].append([r1(x, 3) for x in np.percentile(ff, int(q[1:]), axis=0)])
                for x in xv:
                    vv = vs0 + dvs * x
                    for q in ('p10', 'p50', 'p90'): nev['vsr'][q].append([r1(y, 3) for y in np.percentile(vv, int(q[1:]), axis=0)])
                V['nevoa'] = nev
                if vis == 'concessionaria':
                    cA, cV = o0['cyc']['A'], o0['cyc']['V']
                    C['oper'] = dict(ops_fixo_ano=r1(np.median(cA) * 24, 1), ops_vsr_ano=r1(np.median(cV) * 24, 1),
                                     manobras_evitadas_ano=r1(np.median(cA - cV) * 24 + f['opsB'] * 365, 1),
                                     anos_ate_troca_fixo=r1(np.median(o0['life'] / cA) / 12, 1), anos_ate_revisao_fixo=r1(np.median(np.minimum(o0['nrev'] / cA, 240)) / 12, 1),
                                     taps_vsr_ano=r1(np.median(o0['taps_ano']), 0), anos_entre_manut_oltc=r1(np.median(o0['Tol']) / 12, 1))
            i1 = int(np.argmin(np.abs(FGRID - 1.0)))
            print(f'{cen}/{vis}/{key}: VPL P50 no preço-base ~{np.interp(PV_LEVEL[kv]["base"] / 1e6, grade, st["p50"][i1]):.2f} mi; '
                  f'equilíbrio P50 R$ {eq["p50"][i1]} mi; com fixo a 0,8x: {np.interp(PV_LEVEL[kv]["base"] / 1e6, grade, st["p50"][i1 - 2]):.2f} mi ({time.time() - t0:.0f}s)', flush=True)
        C['visoes'][vis] = V
    OUT['cenarios'][cen] = C
json.dump(OUT, open(P + 'site_calculadora.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), default=float)
print('ok', P + 'site_calculadora.json', round(os.path.getsize(P + 'site_calculadora.json') / 1e3), 'kB', f'({time.time() - t0:.0f}s)')

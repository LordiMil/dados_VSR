"""11 - Dados da calculadora do site (contrato de dados da secao 7 do escopo).

Reusa o motor do script 10 (secoes 1 e 2, sem rodar a execucao nem mexer na planilha) e gera processed/site_calculadora.json:
para cada cenario, visao (concessionaria / SIN) e conjunto de premissas, as estatisticas do VPL, da probabilidade de compensar e do
payback numa grade de precos do VSR (R$). O VPL de cada simulacao e afim no preco do VSR (os sorteios nao dependem do preco), entao
duas rodadas com a mesma semente (premio 0 e premio 1) dao o resultado exato em qualquer preco da grade.
Tambem exporta a nevoa (custo acumulado descontado por ano) das premissas-base, a cascata, os operacionais e o dia tipico do modelo fisico.
Uso: python 11_dados_site.py <pasta_base_PoliVSR-dados>   (rodar depois do 10)"""
import sys, os, json, time, numpy as np
BASE = sys.argv[1]; t0 = time.time()
SRC = open(os.path.join(BASE, 'scripts', '10_modelo_financeiro.py'), encoding='utf-8').read()
CUT = SRC.index('# ======================= 3. Execucao')
sys.argv = ['10_modelo_financeiro.py', BASE, os.path.join(BASE, 'PoliVSR_Base_de_Dados.xlsx')]
G = {'__name__': 'motor10'}
exec(compile(SRC[:CUT], '10_modelo_financeiro.py (secoes 1-2)', 'exec'), G)
simular, CEN, PV_LEVEL, VPC, EURBRL, S0, H, J9, fis = (G[k] for k in ('simular', 'CEN', 'PV_LEVEL', 'VPC', 'EURBRL', 'S0', 'H', 'J9', 'fis'))
P = os.path.join(BASE, 'processed') + '/'

GRADE = {500.0: np.round(np.arange(15.0, 90.0 + 1e-9, 1.0), 2), 230.0: np.round(np.arange(3.0, 18.0 + 1e-9, 0.2), 2)}   # R$ mi
VAR = [('base', 'Premissas-base', {}, 'todas'),
       ('reforco', 'Reforço com RAP pelo BPR', {'regime': 'reforco'}, 'concessionaria'),
       ('rap', 'Prêmio reconhecido na RAP', {'premio_rap': True}, 'concessionaria'),
       ('pool', 'Reserva do VSR em pool de 1 para 10', {'reserva': '1:10'}, 'todas'),
       ('res13', 'Reserva do VSR de 1 para 3', {'reserva': '1:3'}, 'todas'),
       ('fase_comp', 'Fase reserva compartilhada pelos 2 bancos', {'fase_reserva': 'compartilhada'}, '500'),
       ('fase_nenhuma', 'Fixo sem fase reserva', {'fase_reserva': 'nenhuma'}, '500'),
       ('oleo', 'OLTC a óleo (teste de estresse)', {'oltc': 'oleo'}, 'todas')]
r1 = lambda x, n=3: None if x is None or (isinstance(x, float) and not np.isfinite(x)) else round(float(x), n)

def payback_stats(cum):
    """cum: S x (H+1) incremento acumulado descontado (fixo - VSR). Mesma regra do script 10."""
    vpl = cum[:, -1]
    neg = cum < 0; has = neg.any(1); last = H - np.argmax(neg[:, ::-1], 1)
    pay = np.where(has, last + 1, 0).astype(float); pay[vpl < 0] = np.nan; pay[has & (last >= H)] = np.nan
    pc = np.where(np.isnan(pay), np.inf, pay)
    q = lambda x: (lambda z: float(z) if np.isfinite(z) else None)(np.percentile(pc, x, method='lower'))
    return dict(p10=float(np.percentile(vpl, 10)), p50=float(np.percentile(vpl, 50)), p90=float(np.percentile(vpl, 90)), media=float(vpl.mean()),
                ppos=float((vpl > 0).mean()), pay10=q(10), pay50=q(50), pay90=q(90), imed=float((pay == 0).mean()), sem=float(np.isnan(pay).mean()))

OUT = dict(meta=dict(gerado_em=time.strftime('%Y-%m-%d'), fonte='scripts/11_dados_site.py sobre o motor do script 10', simulacoes=S0, eur_brl=EURBRL,
                     moeda='R$ de set/2026', horizonte_anos=30, taxa_concessionaria=G['WACC'], taxa_sin=G['TSD']),
           contratos=[{k: (None if (isinstance(v, float) and not np.isfinite(v)) else (v.item() if hasattr(v, 'item') else v)) for k, v in row.items()}
                      for row in VPC.to_dict(orient='records')],
           cenarios={})
NOMES = {'urbano': ('Centro Urbano', 'Base: Salvador, Recife, Fortaleza · 230 kV'), 'campo': ('Campo', 'Base: Interligação N–NE · 500 kV'),
         'polo_eolico': ('Polo eólico', 'Base: carga líquida do Nordeste · 500 kV')}
for cen, c in CEN.items():
    kv = c['kv']; W = c['W']; grade = GRADE[kv]
    o_ref = simular(cen, 'concessionaria', 200, 1)
    prFix, pV = o_ref['prFix'], o_ref['pV']
    dt = J9['dia_tipico'][cen]
    f = fis(cen)
    C = dict(nome=NOMES[cen][0], base=NOMES[cen][1], kv=int(kv), W=W, mvar_vsr=W / 0.5, preco_fixos=prFix, preco_vao=pV,
             precos={k: v * (1.0) for k, v in PV_LEVEL[kv].items()}, grade=grade.tolist(),
             dia=dict(data=dt['data'], hora=dt['hora'], r=[r1(x) for x in dt['r']], fixo=[r1(x) for x in dt['nivel_fixo']],
                      vsr=[r1(x) for x in dt['nivel_vsr']], manobras_fixo=dt['manobras_fixo'], manobras_vsr=dt['manobras_vsr'], taps_vsr=dt['taps_vsr'],
                      bancos_fixos=J9['meta']['caso_base']['N'][cen]),
             visoes={})
    for vis in ('concessionaria', 'sin'):
        V = {'variantes': {}}
        for key, nome, kw, onde in VAR:
            if onde == 'concessionaria' and vis != 'concessionaria': continue
            if onde == '500' and kv != 500.0: continue
            o0 = simular(cen, vis, S0, 11, premio=0.0, **kw); o1 = simular(cen, vis, S0, 11, premio=1.0, **kw)
            inc0 = o0['CFd']['fixo'] - o0['CFd']['vsr']; dinc = (o1['CFd']['fixo'] - o1['CFd']['vsr']) - inc0      # incremento por unidade de premio
            st = {k: [] for k in ('p10', 'p50', 'p90', 'media', 'ppos', 'pay10', 'pay50', 'pay90', 'imed', 'sem')}
            for preco in grade:
                s = payback_stats(inc0 + dinc * (preco * 1e6 / prFix - 1))
                for k in st: st[k].append(r1(s[k] / 1e6 if k in ('p10', 'p50', 'p90', 'media') else s[k], 4))
            be = -inc0[:, -1] / dinc[:, -1]                                                                      # premio de equilibrio por simulacao
            comps = sorted({cc for (_, cc) in o0['PVC']} | {cc for (_, cc) in o1['PVC']})
            casc = []
            for cc in comps:
                g0 = o0['PVC'].get(('fixo', cc), np.zeros(S0)).mean() - o0['PVC'].get(('vsr', cc), np.zeros(S0)).mean()
                g1 = o1['PVC'].get(('fixo', cc), np.zeros(S0)).mean() - o1['PVC'].get(('vsr', cc), np.zeros(S0)).mean()
                if abs(g0) < 1 and abs(g1) < 1: continue
                casc.append(dict(c=cc, a=r1(g0 / 1e6, 4), b=r1((g1 - g0) / 1e6, 4)))                           # ganho = a + b * premio (R$ mi)
            V['variantes'][key] = dict(nome=nome, stats=st, equilibrio_mi=[r1((1 + np.percentile(be, q)) * prFix / 1e6, 3) for q in (10, 50, 90)],
                                       cascata=casc)
            if key == 'base':
                anos = list(range(31)); mi = [12 * y for y in anos]
                fx = o0['CFd']['fixo'][:, mi] / 1e6
                v0 = o0['CFd']['vsr'][:, mi] / 1e6; dv = (o1['CFd']['vsr'][:, mi] / 1e6) - v0
                nev = dict(anos=anos, fixo={q: [r1(x, 3) for x in np.percentile(fx, int(q[1:]), axis=0)] for q in ('p10', 'p50', 'p90')}, vsr={'p10': [], 'p50': [], 'p90': []})
                for preco in grade:
                    vv = v0 + dv * (preco * 1e6 / prFix - 1)
                    for q in ('p10', 'p50', 'p90'): nev['vsr'][q].append([r1(x, 3) for x in np.percentile(vv, int(q[1:]), axis=0)])
                V['nevoa'] = nev
                if vis == 'concessionaria':
                    cA, cV = o0['cyc']['A'], o0['cyc']['V']
                    C['oper'] = dict(ops_fixo_ano=r1(np.median(cA) * 24, 1), ops_vsr_ano=r1(np.median(cV) * 24, 1),
                                     manobras_evitadas_ano=r1(np.median(cA - cV) * 24 + f['opsB'] * 365, 1),
                                     anos_ate_troca_fixo=r1(np.median(o0['life'] / cA) / 12, 1), anos_ate_revisao_fixo=r1(np.median(np.minimum(o0['nrev'] / cA, 240)) / 12, 1),
                                     taps_vsr_ano=r1(np.median(o0['taps_ano']), 0), anos_entre_manut_oltc=r1(np.median(o0['Tol']) / 12, 1))
            print(f'{cen}/{vis}/{key}: VPL P50 no preço-base ~{np.interp(PV_LEVEL[kv]["base"] / 1e6, grade, st["p50"]):.2f} mi; '
                  f'equilíbrio P50 R$ {V["variantes"][key]["equilibrio_mi"][1]} mi ({time.time() - t0:.0f}s)', flush=True)
        C['visoes'][vis] = V
    OUT['cenarios'][cen] = C
json.dump(OUT, open(P + 'site_calculadora.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'), default=float)
print('ok', P + 'site_calculadora.json', round(os.path.getsize(P + 'site_calculadora.json') / 1e3), 'kB', f'({time.time() - t0:.0f}s)')

"""12 - Dados da página "Simulações de Monte Carlo" do site.

Reusa o motor do script 10 (seções 1 e 2) e gera processed/site_monte_carlo.json com, para cada cenário, na visão da transmissora,
com as premissas-base e os preços de referência (VSR = média dos contratos de 2025–26; fixo = EPE/ANEEL mar/2021 x IPCA):
  - 60 trajetórias sorteadas ao acaso entre as 4.000 (vantagem acumulada do VSR em valor presente, ano a ano) e as faixas P10/P50/P90;
  - um futuro de exemplo com VPL negativo (falha grave do próprio VSR) e o ano em que ela acontece;
  - o histograma dos 4.000 VPL e as estatísticas;
  - a lista dos parâmetros sorteados em cada simulação e dos eventos sorteados mês a mês, com faixas e fontes, conferida contra o
    código de simular() no script 10 (linhas dos sorteios).
Uso: python 12_dados_monte_carlo.py <pasta_base_PoliVSR-dados>   (rodar depois do 10)"""
import sys, os, json, time, numpy as np
BASE = sys.argv[1]; t0 = time.time()
SRC = open(os.path.join(BASE, 'scripts', '10_modelo_financeiro.py'), encoding='utf-8').read()
CUT = SRC.index('# ======================= 3. Execucao')
sys.argv = ['10_modelo_financeiro.py', BASE, os.path.join(BASE, 'PoliVSR_Base_de_Dados.xlsx')]
G = {'__name__': 'motor10'}
exec(compile(SRC[:CUT], '10_modelo_financeiro.py (secoes 1-2)', 'exec'), G)
simular, CEN, S0 = G['simular'], G['CEN'], G['S0']
P = os.path.join(BASE, 'processed') + '/'
# conferência: os sorteios descritos abaixo precisam existir no código do motor, com estes números
for trecho in ['tri(rng, .0023, .0025, .0028, S)', 'tri(rng, .0198, .0246, .0302, S)', 'tri(rng, .8, 1, 1.2, S)', 'rng.uniform(1, 2, S)',
               'tri(rng, 2000, 3000, 5000, S)', 'rng.uniform(1, 5, S)', 'tri(rng, .01, .02, .03, S)', 'tri(rng, .7, 1, 1.3, S)',
               'tri(rng, .005, .01, .02, S)', 'rng.uniform(7.1, 7.9, S)', 'tri(rng, .05, .15, .30, S)', 'rng.uniform(.02, .08, S)',
               'rng.uniform(.05, .15, S)', 'tri(rng, .003, .0041, .0053, S)', 'tri(rng, .0004, .001, .0016, S)', 'coltc = tri(rng, .01, .02, .03, S)',
               "fz('om_vao', tri(rng, .005, .01, .02, S))", 'rng.uniform(.02, .10, S)', 'tri(rng, 150, 250, 400, S)',
               'np.exp(np.log(24) + 1.113', 'rng.uniform(14, 42, ne)', 'np.exp(np.log(180) + 0.857', 'rng.uniform(3, 21, n)',
               'np.exp(np.log(11.47) + 1.95', 'rng.uniform(cmin, cmax, ne)', 'cmin=.3, cmax=1.0', '.05, .15, dur=']:
    assert trecho in SRC, f'sorteio não encontrado no script 10: {trecho}'

T, U = 'triangular', 'uniforme'
# (grupo, nome, tipo, mínimo, mais provável, máximo, unidade, onde entra, fonte)
PARAMS = [
 ('Disjuntores', 'Falhas graves de disjuntor que quase não manobra', T, 0.23, 0.25, 0.28, '% ao ano', 'fixo e VSR', 'CIGRÉ TB 510'),
 ('Disjuntores', 'Falhas graves de disjuntor que manobra reator uma vez por dia', T, 1.98, 2.46, 3.02, '% ao ano', 'fixo e VSR', 'CIGRÉ TB 510'),
 ('Disjuntores', 'Falhas pequenas para cada falha grave', U, 7.1, None, 7.9, 'falhas', 'fixo e VSR', 'CIGRÉ TB 510 (derivado)'),
 ('Disjuntores', 'Chance de a falha grave ser uma explosão', U, 2, None, 8, '%', 'fixo e VSR', 'premissa'),
 ('Disjuntores', 'Chance de o reparo ir para a fábrica', U, 5, None, 15, '%', 'fixo e VSR', 'manual GE GL314; premissa'),
 ('Disjuntores', 'Custo do reparo de uma falha grave', T, 5, 15, 30, '% do disjuntor', 'fixo e VSR', 'premissa'),
 ('Disjuntores', 'Custo de uma falha pequena', T, 0.5, 1, 2, '% do disjuntor', 'fixo e VSR', 'premissa'),
 ('Disjuntores', 'Custo da manutenção preventiva (a cada 6 anos)', T, 1, 2, 3, '% do disjuntor', 'fixo e VSR', 'Jeromin et al. 2009; premissa'),
 ('Disjuntores', 'Manobras até a revisão geral (ou 20 anos)', T, 2000, 3000, 5000, 'manobras', 'fixo e VSR', 'manual GE GL314; Hermosillo 2002'),
 ('Disjuntores', 'Custo da revisão geral', T, 7, 10, 13, '% do disjuntor', 'fixo e VSR', 'Jeromin et al. 2009'),
 ('Disjuntores', 'Vida mecânica real até a troca do disjuntor', U, 2000, None, 10000, 'manobras', 'fixo e VSR', 'IEC 62271-100; IEEE PES 2017'),
 ('Disjuntores', 'Erro no número de manobras do modelo físico', T, 0.8, 1, 1.2, '× o calculado', 'fixo e VSR', 'premissa'),
 ('Reatores e VSR', 'Falha grave de reator ou do VSR', T, 0.30, 0.41, 0.53, '% ao ano', 'fixo e VSR', 'CIGRÉ TB 939; Martin e Tenbohlen 2026'),
 ('Reatores e VSR', 'Falha do comutador do VSR', T, 0.04, 0.10, 0.16, '% ao ano', 'VSR', 'CIGRÉ TB 642 e TB 939 (derivado)'),
 ('Reatores e VSR', 'Trocas de tap além das que os dados enxergam', U, 1, None, 2, '× o calculado', 'VSR', 'premissa (dados a cada 30 min ou 1 h)'),
 ('Reatores e VSR', 'Custo da manutenção do comutador', T, 1, 2, 3, '% do VSR', 'VSR', 'premissa'),
 ('Vão de manobra', 'Operação e manutenção de rotina do vão', T, 0.5, 1, 2, '% do vão por ano', 'fixo (2 vãos) e VSR (1 vão)', 'premissa; teto da ANEEL (NT 103/2024)'),
 ('Só na visão do sistema', 'Chance de a falha grave de disjuntor cortar carga', U, 2, None, 10, '%', 'fixo e VSR', 'premissa'),
 ('Só na visão do sistema', 'Valor da energia perdida no VSR', T, 150, 250, 400, 'R$ por MWh', 'VSR', 'premissa'),
]
EVENTOS = [
 ('Falhas de disjuntor em cada mês', 'Sorteio de Poisson com a taxa da simulação. A taxa de cada disjuntor fica entre a do que quase não manobra e a do que manobra todo dia, conforme as manobras dele.'),
 ('Tempo de reparo do disjuntor', 'Reparo no local: mediana de 24 horas, 9 em cada 10 até 100 horas. Na fábrica: de 14 a 42 dias. Explosão: 30 dias e 1,5 vez o preço do disjuntor.'),
 ('Falha grave de reator ou do VSR', 'Custo de 30% a 100% do equipamento. O VSR sem reserva fica parado com mediana de 180 dias (9 em cada 10 até 540 dias). No fixo de 500 kV, a fase reserva entra em até 3 horas.'),
 ('Falha do comutador do VSR', 'De 3 a 21 dias parado e custo de 5% a 15% do preço do VSR.'),
 ('Carga cortada (só visão do sistema)', 'Energia não suprida com mediana de 11,5 MWh por corte (9 em cada 10 até cerca de 140 MWh), dos dados do ONS de 2016 a 2025, ao custo do déficit.'),
]

OUT = dict(meta=dict(gerado_em=time.strftime('%Y-%m-%d'), simulacoes=S0, semente=11, meses=360, moeda='R$ de set/2026',
                     visao='transmissora (12,11% a.a.)', precos='VSR: média dos contratos de 2025–26; fixo: referência EPE/ANEEL de 2021 corrigida pelo IPCA'),
           parametros=[dict(grupo=g, nome=n, tipo=t, min=a, moda=b, max=c, unidade=u, onde=o, fonte=f) for g, n, t, a, b, c, u, o, f in PARAMS],
           eventos=[dict(nome=n, texto=t) for n, t in EVENTOS], cenarios={})
NOMES = {'urbano': 'Centro Urbano', 'campo': 'Campo', 'polo_eolico': 'Polo eólico'}
rs = np.random.default_rng(2026)
for cen in CEN:
    o = simular(cen, 'concessionaria', S0, 11, preco='base')
    inc = (o['CFd']['fixo'] - o['CFd']['vsr']) / 1e6                    # vantagem acumulada do VSR, valor presente (R$ mi), mês a mês
    anos = np.arange(0, 361, 12); traj = inc[:, anos]
    vpl = inc[:, -1]
    amostra = np.sort(rs.choice(S0, 60, replace=False))
    neg = np.where(vpl < 0)[0]
    ex = int(neg[np.argmin(np.abs(vpl[neg] - np.median(vpl[neg])))]) if neg.size else None      # futuro negativo típico
    ano_falha = int(np.argmin(np.diff(traj[ex]))) + 1 if ex is not None else None             # ano da maior queda
    lo, hi = np.floor(vpl.min()), np.ceil(vpl.max())
    larg = 1.0 if hi - lo <= 60 else 2.0
    ed = np.arange(lo, hi + larg, larg); cnt, _ = np.histogram(vpl, ed)
    OUT['cenarios'][cen] = dict(
        nome=NOMES[cen], kv=int(CEN[cen]['kv']), preco_vsr=round(o['prVSR'] / 1e6, 2), preco_fixos=round(o['prFix'] / 1e6, 2),
        anos=list(range(31)),
        linhas=[[round(float(x), 2) for x in traj[i]] for i in amostra],
        faixa={q: [round(float(x), 2) for x in np.percentile(traj, int(q[1:]), axis=0)] for q in ('p10', 'p50', 'p90')},
        exemplo=dict(linha=[round(float(x), 2) for x in traj[ex]], ano=ano_falha, vpl=round(float(vpl[ex]), 2)) if ex is not None else None,
        hist=dict(de=[round(float(x), 2) for x in ed[:-1]], largura=larg, n=cnt.tolist()),
        stats=dict(p10=round(float(np.percentile(vpl, 10)), 2), p50=round(float(np.percentile(vpl, 50)), 2), p90=round(float(np.percentile(vpl, 90)), 2),
                   media=round(float(vpl.mean()), 2), ppos=round(float((vpl > 0).mean()), 4), negativas=int((vpl < 0).sum()),
                   ep_media=round(float(vpl.std(ddof=1) / np.sqrt(S0)), 3)))
    s = OUT['cenarios'][cen]['stats']
    print(f'{cen}: VPL P10 {s["p10"]} P50 {s["p50"]} P90 {s["p90"]}; positivo {s["ppos"]:.1%}; negativas {s["negativas"]}; exemplo ano {ano_falha} ({time.time() - t0:.0f}s)', flush=True)
json.dump(OUT, open(P + 'site_monte_carlo.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print('ok', P + 'site_monte_carlo.json', round(os.path.getsize(P + 'site_monte_carlo.json') / 1e3), 'kB')

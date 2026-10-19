"""07 - Fontes reforcadas (2026-10-09).
1) RAP por Funcao Transmissao (FT) de reator - SIGET/ANEEL (lista previa de reajuste da RAP).
2) Parcela Variavel por Indisponibilidade (PVI) por evento - Regras dos Servicos de Transmissao, Modulo 4 rev.2 (REN 1.137/2025).
3) Tabela de fatos documentais com pagina/secao (Despacho ANEEL 675/2026, Modulo 4, PAR/PEL 2025, literatura VSR).
4) Reconstroi o FONTES_manifesto.csv (script 00) e acrescenta os arquivos brutos novos (SIGET, atos ANEEL, PAR/PEL)."""
import pandas as pd, os, hashlib, runpy
B = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')); P = B + '/processed/'

# ---------- 1. SIGET: RAP por FT de reator ----------
d = pd.read_csv(B + '/raw/aneel/ANEEL__siget__siget-lista-modulos-previa-reajuste-rap.csv', sep=';', encoding='latin-1', dtype=str)
d['tipo'] = d.NomFuncaoTransmissao.str.extract(r'^FT (\w+)')[0]
d = d[d.tipo.isin(['RTB', 'RTL']) & (d.DcsSitRAP == 'Ativa')].copy()   # RTB = reator de barra; RTL = reator de linha
d['rap'] = d.VlrRAPCiclo.str.replace(',', '.').astype(float)
ft = d.groupby(['NomFuncaoTransmissao', 'tipo'], as_index=False).agg(
    UF=('SigUF', 'first'), concessionaria=('SigConcessionariaModulo', 'first'),
    n_modulos=('rap', 'size'), rap_ciclo_RS=('rap', 'sum'), ciclo_ref=('DatRefCiclo', 'first'))
ft['kV'] = ft.NomFuncaoTransmissao.str.extract(r' (\d+) kV')[0].astype(float)
ft['Mvar'] = pd.to_numeric(ft.NomFuncaoTransmissao.str.extract(r'kV ([\d,]+) Mvar')[0].str.replace(',', '.'), errors='coerce')
ft['RAP_por_Mvar'] = ft.rap_ciclo_RS / ft.Mvar
ft.sort_values(['tipo', 'kV', 'rap_ciclo_RS']).to_csv(P + 'siget_rap_FT_reatores.csv', index=False, sep=';', encoding='utf-8-sig')
qq = lambda x: (lambda s: s.quantile(x))
st = (ft[ft.kV >= 230].groupby(['tipo', 'kV']).agg(
    n_FT=('rap_ciclo_RS', 'size'), p10=('rap_ciclo_RS', qq(.1)), p25=('rap_ciclo_RS', qq(.25)),
    mediana=('rap_ciclo_RS', 'median'), p75=('rap_ciclo_RS', qq(.75)), p90=('rap_ciclo_RS', qq(.9)),
    media=('rap_ciclo_RS', 'mean'), mediana_RAP_por_Mvar=('RAP_por_Mvar', 'median'), mediana_Mvar=('Mvar', 'median'))
    .round(2).reset_index())
st.to_csv(P + 'siget_rap_reatores_estatisticas.csv', index=False, sep=';', encoding='utf-8-sig')
print(st.to_string())

# ---------- 2. PVI por evento (Modulo 4 rev.2, Secao 4.3 item 4.2 Eq.3; Anexo I: REA Ko=150, Kp=10) ----------
KO, KP, D = 150, 10, 30; MIN = 24 * 60 * D
def pvi_frac(minutos, forcado=True):
    if forcado:
        return (KO * min(minutos, 300) + KP * max(minutos - 300, 0)) / MIN   # Ko reduzido a Kp apos o 300o minuto
    return KP * minutos / MIN
rows = []
for kv in [230, 500]:
    rap = float(st[(st.tipo == 'RTB') & (st.kV == kv)].mediana.iloc[0]); PB = rap / 12
    for tipo, durs in [('forcado (OUTROS DESLIGAMENTOS)', [60, 180, 300, 720, 1440, 4320, 10080]),
                       ('programado (DESLIGAMENTO PROGRAMADO)', [480, 1440])]:
        for m in durs:
            f = pvi_frac(m, tipo.startswith('forcado'))
            rows.append(dict(kV=kv, RAP_FT_RTB_mediana_RS=round(rap, 2), PB_mensal_RS=round(PB, 2), tipo=tipo,
                             duracao_min=m, duracao_h=m / 60, PVI_em_PB=round(f, 4), PVI_RS=round(f * PB, 2),
                             parcela_no_mes_RS=round(min(f, 0.5) * PB, 2), diferido_meses_seguintes_RS=round(max(f - 0.5, 0) * PB, 2),
                             teto_12m_RS=round(0.25 * 12 * PB, 2), PVI_RS_apos_teto_12m=round(min(f, 3.0) * PB, 2)))
pv = pd.DataFrame(rows); pv.to_csv(P + 'pvi_reator_por_evento.csv', index=False, sep=';', encoding='utf-8-sig')
print(pv[['kV', 'tipo', 'duracao_h', 'PVI_em_PB', 'PVI_RS']].to_string())

# ---------- 3. Fatos documentais (pagina/secao) ----------
pp = open(B + '/raw/ons/parpel2025/parpel_pdf.txt', encoding='utf-8', errors='replace').read().split('\f')
pag = lambda k: next((i + 1 for i, p in enumerate(pp) if k in p), None)
M4 = 'raw/aneel/atos/ANEEL__regtransm__mod04_prestacao_servicos_rev02.pdf'
U4 = 'https://git.aneel.gov.br/publico/centralconteudo/-/raw/main/procreg/regtransm/modulo04/mod04_prestacao_servicos_rev02.pdf'
DS = 'raw/aneel/atos/ANEEL__cedoc__dsp2026675ti.pdf'; UDS = 'https://www2.aneel.gov.br/cedoc/dsp2026675ti.pdf'
PL = 'raw/ons/parpel2025/ONS__PARPEL2025__Revista_PARPEL_2025-VF.pdf'
UPL = 'https://www.ons.org.br/AcervoDigitalDocumentosEPublicacoes/Revista%20PARPEL%202025-VF.pdf'
TG = 'https://aer.gov.au/system/files/Transgrid%20-%20Substations%20Renewal%20and%20Maintenance%20Strategy%20-%2030%20Nov%202021%20-%20PUBLIC.pdf'
REG, OPE, FAB, PRE = 'A - ato regulatório', 'A - operador do sistema', 'B - fabricante', 'C - premissa declarada'
F = [  # parametro, valor, uso no modelo, fonte, arquivo local, localizacao, url, nivel
 ('WACC transmissão real pós-impostos', '8,00% a.a.', 'taxa de desconto (wacc)', 'Despacho ANEEL nº 675/2026, Anexo 1', DS, 'Anexo 1 (vigência a partir de 01/03/2026)', UDS, REG),
 ('WACC transmissão real pré-impostos', '12,11% a.a.', 'sensibilidade', 'Despacho ANEEL nº 675/2026, Anexo 1', DS, 'Anexo 1', UDS, REG),
 ('Componentes do WACC', 'Ke 10,41%; Kd pós-impostos 4,35%; 60,23% capital próprio / 39,77% terceiros', 'documentação', 'Despacho ANEEL nº 675/2026, Anexo 1', DS, 'Anexo 1', UDS, REG),
 ('Despacho 1.174/2026', 'altera apenas parâmetros da distribuição; transmissão inalterada', 'checagem de vigência', 'Despacho ANEEL nº 1.174/2026', 'raw/aneel/atos/ANEEL__cedoc__dsp20261174ti.pdf', 'texto integral', 'https://www2.aneel.gov.br/cedoc/dsp20261174ti.pdf', REG),
 ('Regra vigente da Parcela Variável', 'Módulo 4 rev.2 - REN 1.137/2025, vigência desde 30/10/2025 (REN 729/2016 revogada; consolidação pela REN 906/2020)', 'base legal da PVI', 'Regras dos Serviços de Transmissão - Módulo 4', M4, 'capa (histórico de revisões)', U4, REG),
 ('Fórmula da PVI', 'PVI = PB/(24·60·D)·(Kp·ΣPADP + Σ Ko·PAOD); Ko reduzido a Kp após o 300º minuto', 'custo de indisponibilidade', 'Módulo 4 rev.2', M4, 'Seção 4.3, item 4.2, Eq. 3 (p. 47-48)', U4, REG),
 ('Fatores do reator (REA)', 'Ko = 150; Kp = 10; padrão de frequência 1 desligamento/ano', 'PVI do reator', 'Módulo 4 rev.2', M4, 'Seção 4.3, Anexo I (p. 59)', U4, REG),
 ('Escopo da FT Controle de Reativo', 'reator manobrável + equipamentos de conexão (inclui o disjuntor do vão)', 'falha do disjuntor indisponibiliza a FT do reator', 'Módulo 4 rev.2', M4, 'Seção 4.1, Anexo I (p. 15)', U4, REG),
 ('Tetos da Parcela Variável', '50% do PB no mês (saldo diferido); 25% da soma de 12 PB; 12,5% da RAP da concessão', 'limite da PVI', 'Módulo 4 rev.2', M4, 'Seção 4.3, item 4.5', U4, REG),
 ('Franquias de PVI do reator', '3 h se substituído por reserva (5.9); 72 h p/ trazer reator de outra SE (5.14)', 'não se aplicam a falha de disjuntor', 'Módulo 4 rev.2', M4, 'Seção 4.3, itens 5.9 e 5.14', U4, REG),
 ('Manutenção preventiva de disjuntores', 'no máximo a cada 72 meses (tolerância 12 meses)', 'periodicidade mínima regulatória', 'Módulo 4 rev.2', M4, 'Seção 4.2, item 6.1 e Tabela 8 (p. 38-39)', U4, REG),
 ('Manutenção condicionada ao nº de operações', 'abertura da câmara e troca de contatos avaliadas a partir do número de operações do disjuntor', 'fundamenta L (operações até intervenção)', 'Módulo 4 rev.2', M4, 'Seção 4.2, item 6.6 (p. 39)', U4, REG),
 ('Chaveamento diário 2026', '~140 reatores de barra (16.400 Mvar) + ~60 capacitores (5.100 Mvar) entre carga mínima e máxima', 'corrobora ~1 ciclo/dia por equipamento = ~2 operações de disjuntor/dia', 'ONS - PAR/PEL 2025', PL, f'p. {pag("140 reatores")}', UPL, OPE),
 ('Chaveamento diário 2030', '~170 reatores (19.200 Mvar) + 70 capacitores (6.500 Mvar); manobras 200 -> 240 (+20%)', 'tendência de alta das manobras', 'ONS - PAR/PEL 2025', PL, f'p. {pag("170 reatores")}-{pag("200 para 240")}', UPL, OPE),
 ('Abertura de linhas p/ controle de tensão', '26 linhas abertas em 10/08/2025; ONS cita "desgaste prematuro" dos equipamentos de manobra', 'evidência qualitativa do desgaste', 'ONS - PAR/PEL 2025', PL, f'p. {pag("desgaste prematuro")}', UPL, OPE),
 ('Novos reatores de barra', '~6.900 Mvar SE/CO; 4.600 NE; 1.200 S; 500 N; ~12.000 Mvar manobráveis em 500 kV', 'mercado endereçável', 'ONS - PAR/PEL 2025', PL, f'p. {pag("6.900")}', UPL, OPE),
 ('Equipamentos em fim de vida útil', '318 equipamentos de grande porte cadastrados', 'contexto de substituição', 'ONS - PAR/PEL 2025', PL, f'p. {pag("318 equipamentos")}', UPL, OPE),
 ('Recursos reativos flexíveis', 'ONS pede recursos "mais flexíveis, adaptativos e dotados de maior grau de automação"', 'argumento qualitativo', 'ONS - PAR/PEL 2025', PL, f'p. {pag("flexíveis, adaptativos")}', UPL, OPE),
 ('Degraus do VSR', '33 posições de tap; 50-250 Mvar; 400 kV; faixa de 80%; 1ª unidade em 2016', 'taps = 33', 'Siemens - Amprion VSR (2017)', '-', 'folheto, dados técnicos', 'https://assets.new.siemens.com/siemens/assets/api/uuid:5b992c0e14405f78b85c97c447d74f2d717f971e/version:1542790208/2017-01-27-amprion-vsr-final-en.pdf', FAB),
 ('Menos operações do disjuntor externo', 'disjuntores externos terão menos operações e precisarão de menos manutenção', 'mecanismo central do modelo', 'Bengtsson, ABB Review Special Report - Variable shunt reactors for network stability control', '-', 'p. 41-44', 'https://library.e.abb.com/public/b9950e8daa93c268c1257ab8003b1097/41-44%20sr109_72dpi.pdf', FAB),
 ('Frota VSR na Noruega', '10 VSR 420 kV 90-200 Mvar (Statnett e BKK), 1º em 2012', 'referência de maturidade', 'Hitachi Energy - customer story Noruega', '-', 'página web', 'https://www.hitachienergy.com/news-and-events/customer-stories/ensuring-power-quality-and-reliability-in-norway', FAB),
 ('Vida nominal de reator a óleo', '30 anos (9% da frota já acima)', 'horizonte de 30 anos', 'Transgrid - Substations Renewal and Maintenance Strategy (nov/2021), publicado pelo AER', '-', '§5.4.1, p. 58', TG, 'A - regulador (documento tarifário público)'),
 ('Reatores manobrados diariamente', 'reatores podem ser manobrados diariamente, com esforços internos adicionais', 'corrobora ciclo diário', 'Transgrid (2021), via AER', '-', '§5.4.1, p. 57', TG, 'A - regulador (documento tarifário público)'),
 ('Disjuntores de reator', 'disjuntores de reatores sujeitos a regime de manobra "muito oneroso"', 'corrobora desgaste do disjuntor do fixo', 'Transgrid (2021), via AER', '-', '§3.3, p. 26', TG, 'A - regulador (documento tarifário público)'),
 ('Desempenho das concessionárias (ANEEL)', 'descartado: CSV não atualizado desde 30/11/2021 e download bloqueado (CORS)', '-', 'ANEEL Dados Abertos', 'raw/aneel/ANEEL__desempenho-das-concessionarias-de-transmissao__dd_ig_6_4.pdf', 'dicionário apenas', 'https://dadosabertos.aneel.gov.br/dataset/desempenho-das-concessionarias-de-transmissao', '-'),
 ('Custo de manutenção do disjuntor (% do preço)', 'sem fonte aberta localizada', 'permanece premissa declarada (10%, ajustável no slider)', '-', '-', '-', '-', PRE),
]
fr = pd.DataFrame(F, columns=['parametro', 'valor', 'uso_no_modelo', 'fonte', 'arquivo_local', 'localizacao', 'url', 'nivel_fonte'])
fr.to_csv(P + 'fontes_reforcadas.csv', index=False, sep=';', encoding='utf-8-sig'); print(len(fr), 'fatos documentais')

# ---------- 4. Manifesto ----------
runpy.run_path(os.path.join(os.path.dirname(__file__), '00_manifesto_fontes.py'))
MAN = B + '/FONTES_manifesto.csv'; man = pd.read_csv(MAN, sep=';', encoding='utf-8-sig', dtype=str); have = set(man.arquivo_local)
SG = 'https://dadosabertos.aneel.gov.br/dataset/beefe870-7452-4830-a7b0-6611e3d5eff6/resource/'
NEW = {
 'raw/aneel/ANEEL__siget__siget-lista-modulos-previa-reajuste-rap.csv': ('ANEEL', 'SIGET - Lista de Módulos Prévia - Reajuste RAP', SG + '5e4e4916-fd70-44c7-a0eb-92bfb4efad6b/download/siget-lista-modulos-previa-reajuste-rap.csv'),
 'raw/aneel/ANEEL__siget__dm-siget-lista-de-modulos-previa-reajuste-receita-anual-permitida-rap.pdf': ('ANEEL', 'SIGET - dicionário (Lista de Módulos Prévia)', SG + 'f662316a-3873-4d01-904f-3e162b0a05a1/download/dm-siget-lista-de-modulos-previa-reajuste-receita-anual-permitida-rap.pdf'),
 'raw/aneel/ANEEL__siget__siget-contrato-moduloequipamento-subestacao.csv': ('ANEEL', 'SIGET - Contrato Módulo Equipamento Subestação', SG + 'caec5e88-c904-45e5-bde4-d7e96ef139b6/download/siget-contrato-moduloequipamento-subestacao.csv'),
 'raw/aneel/ANEEL__siget__dm-siget-contrato-modulo-equipamento-subestacao.pdf': ('ANEEL', 'SIGET - dicionário (Contrato Módulo Equipamento)', SG + '5954ec2b-34b8-4e0f-bd3b-48bacd40df8c/download/dm-siget-contrato-modulo-equipamento-subestacao.pdf'),
 'raw/aneel/ANEEL__siget__siget-resolucao-moduloequipamento-subestacao.csv': ('ANEEL', 'SIGET - Resolução Módulo Equipamento Subestação', SG + '1d342bc9-4cbd-4c07-9cd4-02f6927175b9/download/siget-resolucao-moduloequipamento-subestacao.csv'),
 'raw/aneel/ANEEL__siget__dm-siget-resolucao-modulo-equipamento-subestacao.pdf': ('ANEEL', 'SIGET - dicionário (Resolução Módulo Equipamento)', SG + 'fe9c6173-6ff8-4615-860c-bfb85f347c81/download/dm-siget-resolucao-modulo-equipamento-subestacao.pdf'),
 'raw/aneel/ANEEL__desempenho-das-concessionarias-de-transmissao__dd_ig_6_4.pdf': ('ANEEL', 'Desempenho das concessionárias de transmissão - dicionário', 'https://dadosabertos.aneel.gov.br/dataset/2b26eeff-b2c2-4511-8fd5-1e6920d7d7be/resource/e369459d-2fd6-40b7-a55c-79076ffa0222/download/dd_ig_6_4.pdf'),
 DS: ('ANEEL', 'Despacho nº 675/2026 - WACC regulatório 2026', UDS),
 'raw/aneel/atos/ANEEL__cedoc__dsp20261174ti.pdf': ('ANEEL', 'Despacho nº 1.174/2026', 'https://www2.aneel.gov.br/cedoc/dsp20261174ti.pdf'),
 'raw/aneel/atos/ANEEL__cedoc__ren2016729.pdf': ('ANEEL', 'REN nº 729/2016 (revogada; histórico da PV)', 'https://www2.aneel.gov.br/cedoc/ren2016729.pdf'),
 'raw/aneel/atos/ANEEL__cedoc__aren2020906_1.pdf': ('ANEEL', 'Voto - REN 906/2020 (aprovação do Módulo 4)', 'https://www2.aneel.gov.br/cedoc/aren2020906_1.pdf'),
 'raw/aneel/atos/ANEEL__cedoc__aren2020906_2.pdf': ('ANEEL', 'Regras de Transmissão - Módulo 1 Glossário (REN 906/2020)', 'https://www2.aneel.gov.br/cedoc/aren2020906_2.pdf'),
 'raw/aneel/atos/ANEEL__cedoc__aren20231069_2.pdf': ('ANEEL', 'Regras de Transmissão - Módulo 5 Acesso (consultado, não usado)', 'https://www2.aneel.gov.br/cedoc/aren20231069_2.pdf'),
 M4: ('ANEEL', 'Regras de Transmissão - Módulo 4 Prestação dos Serviços rev.2 (REN 1.137/2025)', U4),
 PL: ('ONS', 'PAR/PEL 2025 (ciclo 2026-2030) - Revista', UPL),
 'raw/ons/parpel2025/ONS__PARPEL2025__sumario_executivo_pagina_web.txt': ('ONS', 'PAR/PEL 2025 - texto da página do sumário executivo', 'https://www.ons.org.br/Paginas/energia-no-futuro/suprimento-eletrico/parpel2025/sumario-executivo/index.aspx'),
 'raw/ons/parpel2025/parpel_pdf.txt': ('ONS', 'PAR/PEL 2025 - texto extraído (pdftotext -layout) da Revista', UPL)}
INST = {'ANEEL': 'ANEEL - Agência Nacional de Energia Elétrica', 'ONS': 'ONS - Operador Nacional do Sistema Elétrico'}
add = []
for f, (i, ds, url) in NEW.items():
    p = B + '/' + f
    if f in have or not os.path.exists(p):
        continue
    add.append(dict(arquivo_local=f, instituicao=INST[i], conjunto=ds,
                    pagina_portal=url.split('/resource/')[0] if '/resource/' in url else url, url_origem=url,
                    data_acesso='2026-10-09', bytes=str(os.path.getsize(p)), sha256=hashlib.sha256(open(p, 'rb').read()).hexdigest(),
                    licenca='Dados abertos / ato público ANEEL' if i == 'ANEEL' else 'Publicação pública ONS'))
man = pd.concat([man, pd.DataFrame(add)], ignore_index=True); man.to_csv(MAN, index=False, sep=';', encoding='utf-8-sig')
print(len(add), 'arquivos acrescentados; manifesto com', len(man), 'entradas')

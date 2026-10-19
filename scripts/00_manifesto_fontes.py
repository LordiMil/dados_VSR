"""Gera o catálogo de fontes (FONTES_manifesto.csv) com URL de origem, tamanho e SHA-256 de cada arquivo bruto."""
import hashlib, os, csv, datetime
RAW = os.path.join(os.path.dirname(__file__), '..', 'raw', 'ons')
OUT = os.path.join(os.path.dirname(__file__), '..', 'FONTES_manifesto.csv')
S3 = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/'
PORTAL = {
 'equipamento_controle_reativo':'equipamento-controle-reativo','ind_disponibilidade_ft_reativo_me':'ind_disponibilidade_ft_reativo',
 'curva-carga-ho':'curva-carga','demanda_maxima_di':'demanda_maxima_di','linha_transmissao':'linha-transmissao',
 'usi_servicoancilar_sandbox':'usi_servicoancilar_sandbox','ind_confiarb_energianaosuprida':'ind_confiarb_energianaosuprida',
 'subestacao':'subestacao','balanco_dessem_geral':'balanco_dessem_geral','balanco_dessem_detalhe':'balanco_dessem_detalhe','carga_verificada_tm':'carga-energia-verificada'}
rows=[]
for f in sorted(os.listdir(RAW)):
    if not f.startswith('ONS__'): continue
    p=os.path.join(RAW,f); h=hashlib.sha256(open(p,'rb').read()).hexdigest()
    _, ds, name = f.split('__',2)
    consol = 'CONSOLIDADO' in name
    url = (S3+ds+'/ (499 arquivos diários BALANCO_DESSEM_*_AAAA_MM_DD.csv concatenados; coluna arquivo_fonte)') if consol else S3+ds+'/'+name
    rows.append(dict(arquivo_local='raw/ons/'+f, instituicao='ONS - Operador Nacional do Sistema Elétrico', conjunto=ds,
        pagina_portal='https://dados.ons.org.br/dataset/'+PORTAL.get(ds,ds), url_origem=url,
        data_acesso='2026-10-09', bytes=os.path.getsize(p), sha256=h, licenca='Creative Commons Atribuição (cc-by), conforme metadados do portal'))
with open(OUT,'w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]),delimiter=';'); w.writeheader(); w.writerows(rows)
print(len(rows),'arquivos catalogados')

# ---- ANEEL e BCB ----
EXTRA={
 'ANEEL__relacao-de-empreendimentos-de-geracao-distribuida__empreendimento-geracao-distribuida.zip':('ANEEL','relacao-de-empreendimentos-de-geracao-distribuida','https://dadosabertos.aneel.gov.br/dataset/relacao-de-empreendimentos-de-geracao-distribuida','https://dadosabertos.aneel.gov.br/dataset/5e0fafd2-21b9-4d5b-b622-40438d40aba2/resource/b1bd71e7-d0ad-4214-9053-cbd58e9564a7/download/empreendimento-geracao-distribuida.zip','ODbL (Open Data Commons)'),
 'ANEEL__relacao-de-empreendimentos-de-geracao-distribuida__dm-geracao-distribuida-relacao-de-empreendimentos.pdf':('ANEEL','relacao-de-empreendimentos-de-geracao-distribuida','https://dadosabertos.aneel.gov.br/dataset/relacao-de-empreendimentos-de-geracao-distribuida','https://dadosabertos.aneel.gov.br/dataset/5e0fafd2-21b9-4d5b-b622-40438d40aba2/resource/3fabb9e8-668a-4f94-8f0e-ed9cd2682979/download/dm-geracao-distribuida-relacao-de-empreendimentos.pdf','ODbL (Open Data Commons)'),
}
BPR='https://dadosabertos.aneel.gov.br/dataset/7981fa38-867f-4447-8bf0-775939705a6c/resource/'
for rid,fn in [('b3a41102-9ee0-43bd-ba8e-48c3ed082266','banco-preco-referencia-item-infraestrutura-manobra.csv'),('baffda83-011a-4999-abc1-c4747766bd1d','banco-preco-referencia-item-modulo-equipamento.csv'),('bd74c7b9-d6b7-4bec-927d-c12aad551201','banco-preco-referencia-item-modulo-manobra.csv'),('194d009d-119c-41da-be4d-0683d8a916c3','dm-bpr-banco-de-precos-de-referencia-item-modulo-equipamento.pdf'),('da5f1246-c968-48f2-9d9c-cf5c29463fa6','dm-bpr-banco-de-precos-de-referencia-item-modulo-manobra.pdf')]:
    EXTRA['ANEEL__bpr-subestacao__'+fn]=('ANEEL','bpr-banco-de-precos-de-referencia-subestacao','https://dadosabertos.aneel.gov.br/dataset/bpr-banco-de-precos-de-referencia-subestacao',BPR+rid+'/download/'+fn,'ODbL (Open Data Commons)')
BCB={'433':'IPCA - variação mensal (%)','4390':'Taxa Selic acumulada no mês (%)','189':'IGP-M - variação mensal (%)','3698':'Dólar venda - média mensal (R$)','432':'Meta Selic (% a.a.), diário 2016-2026','21619':'Euro venda - diário (R$), 2016-2026'}
for f in sorted(os.listdir(os.path.join(RAW,'..','bcb'))):
    sid=f.split('_')[3]
    EXTRA[f]=('BCB','SGS '+sid+' - '+BCB.get(sid,''),'https://www3.bcb.gov.br/sgspub/','https://api.bcb.gov.br/dados/serie/bcdata.sgs.'+sid+'/dados?formato=json&dataInicial=...&dataFinal=...','Dados abertos BCB')
for f,(inst,ds,pg,url,lic) in EXTRA.items():
    sub='aneel' if inst=='ANEEL' else 'bcb'; p=os.path.join(RAW,'..',sub,f)
    if not os.path.exists(p): continue
    rows.append(dict(arquivo_local=f'raw/{sub}/'+f,instituicao={'ANEEL':'ANEEL - Agência Nacional de Energia Elétrica','BCB':'Banco Central do Brasil'}[inst],conjunto=ds,pagina_portal=pg,url_origem=url,data_acesso='2026-10-09',bytes=os.path.getsize(p),sha256=hashlib.sha256(open(p,'rb').read()).hexdigest(),licenca=lic))
with open(OUT,'w',newline='',encoding='utf-8-sig') as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]),delimiter=';'); w.writeheader(); w.writerows(rows)
print(len(rows),'arquivos no manifesto final')

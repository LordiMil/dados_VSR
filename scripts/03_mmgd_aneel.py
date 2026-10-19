"""Série mensal de MMGD (ANEEL, relação de empreendimentos de geração distribuída).
Só agrega: nenhum dado pessoal (CPF/CNPJ, nome do titular, CEP) é lido ou salvo.
Data usada: DthAtualizaCadastralEmpreend (o dicionário v2.3 a descreve como 'última atualização cadastral';
na prática é a única data da base e é usada como proxy da data de conexão -> declarar como premissa)."""
import pandas as pd, zipfile, os
B=os.path.join(os.path.dirname(__file__),'..'); P=B+'/processed/'
z=zipfile.ZipFile(B+'/raw/aneel/ANEEL__relacao-de-empreendimentos-de-geracao-distribuida__empreendimento-geracao-distribuida.zip')
use=['AnmPeriodoReferencia','SigAgente','SigUF','NomRegiao','DthAtualizaCadastralEmpreend','SigTipoGeracao','DscPorte','MdaPotenciaInstaladaKW']
parts=[]; n=0
for ch in pd.read_csv(z.open('empreendimento-geracao-distribuida.csv'),sep=';',usecols=use,dtype=str,encoding='utf-8',chunksize=500_000):
    n+=len(ch)
    ch['kw']=pd.to_numeric(ch.MdaPotenciaInstaladaKW.str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce')
    ch['mes']=pd.to_datetime(ch.DthAtualizaCadastralEmpreend,errors='coerce').dt.to_period('M')
    parts.append(ch.groupby(['mes','SigUF','NomRegiao','SigAgente','SigTipoGeracao','DscPorte'],dropna=False).agg(qtd=('kw','size'),kw=('kw','sum')).reset_index())
G=pd.concat(parts).groupby(['mes','SigUF','NomRegiao','SigAgente','SigTipoGeracao','DscPorte'],dropna=False).sum().reset_index()
ref=ch.AnmPeriodoReferencia.iloc[0]
G.to_csv(P+'mmgd_aneel_mensal_UF_distribuidora.csv',sep=';',index=False,encoding='utf-8-sig',float_format='%.2f')
M=G.groupby(['mes','NomRegiao']).kw.sum().unstack().fillna(0)/1e6
M['Brasil']=M.sum(axis=1)
A=M.cumsum().round(3)  # GW acumulado
A.index=A.index.astype(str); A.to_csv(P+'mmgd_aneel_GW_acumulado_mensal_regiao.csv',sep=';',encoding='utf-8-sig')
U=G.groupby('SigUF').agg(qtd=('qtd','sum'),GW=('kw',lambda x:x.sum()/1e6)).sort_values('GW',ascending=False).round(3)
U.to_csv(P+'mmgd_aneel_estoque_por_UF.csv',sep=';',encoding='utf-8-sig')
D=G.groupby('SigAgente').agg(qtd=('qtd','sum'),GW=('kw',lambda x:x.sum()/1e6)).sort_values('GW',ascending=False).round(3)
D.to_csv(P+'mmgd_aneel_estoque_por_distribuidora.csv',sep=';',encoding='utf-8-sig')
yr=M.groupby(M.index.year).sum()[['Brasil']].rename(columns={'Brasil':'GW_adicionados'}).round(3)
yr['GW_acumulado']=yr.GW_adicionados.cumsum().round(3); yr['cresc_estoque_pct']=(yr.GW_acumulado.pct_change()*100).round(1)
yr.to_csv(P+'mmgd_aneel_anual.csv',sep=';',encoding='utf-8-sig')
print('linhas lidas',n,'| período de referência',ref,'| sem data:',G[G.mes.isna()].kw.sum()/1e6,'GW')
print('total GW',round(G.kw.sum()/1e6,3),'| empreendimentos',int(G.qtd.sum()))
print(G.groupby('SigTipoGeracao').kw.sum().div(1e6).round(3)); print(yr.tail(10)); print(U.head(10)); print(A.tail(3))

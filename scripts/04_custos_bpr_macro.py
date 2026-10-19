"""Custos de referência ANEEL (BPR, módulos de manobra de reator e preço unitário de disjuntor) e séries macro do BCB (IPCA, Selic, câmbio)."""
import pandas as pd, numpy as np, os
B=os.path.join(os.path.dirname(__file__),'..'); RA=B+'/raw/aneel/'; RB=B+'/raw/bcb/'; P=B+'/processed/'
num=lambda s:pd.to_numeric(s.astype(str).str.strip().str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce')
# ---------- BCB ----------
def sgs(f): d=pd.read_csv(RB+f,sep=';'); d['data']=pd.to_datetime(d.data); d['valor']=pd.to_numeric(d.valor); return d
ipca=sgs('BCB__SGS_433__IPCA_var_mensal_pct.csv'); ipca['indice']=(1+ipca.valor/100).cumprod()  # base dez/2009=1
ipca['mes']=ipca.data.dt.to_period('M')
selic=sgs('BCB__SGS_4390__Selic_acumulada_mes_pct.csv'); usd=sgs('BCB__SGS_3698__Dolar_venda_media_mensal_BRL.csv')
eur=sgs('BCB__SGS_21619__Euro_venda_diario_BRL.csv'); igpm=sgs('BCB__SGS_189__IGPM_var_mensal_pct.csv')
mac=ipca[['mes','valor','indice']].rename(columns={'valor':'ipca_mes_pct','indice':'ipca_indice_base_dez2009'})
for nm,d in [('selic_mes_pct',selic),('usd_brl_media',usd),('igpm_mes_pct',igpm)]:
    mac=mac.merge(d.assign(mes=d.data.dt.to_period('M'))[['mes','valor']].rename(columns={'valor':nm}),on='mes',how='outer')
mac=mac.merge(eur.assign(mes=eur.data.dt.to_period('M')).groupby('mes').valor.mean().rename('eur_brl_media').reset_index(),on='mes',how='outer')
mac=mac.sort_values('mes'); mac['ipca_12m_pct']=((1+mac.ipca_mes_pct/100).rolling(12).apply(np.prod,raw=True)-1)*100
mac['selic_12m_pct']=((1+mac.selic_mes_pct/100).rolling(12).apply(np.prod,raw=True)-1)*100
mac['juro_real_12m_pct']=((1+mac.selic_12m_pct/100)/(1+mac.ipca_12m_pct/100)-1)*100
mac['mes']=mac.mes.astype(str); mac.round(4).to_csv(P+'macro_bcb_mensal.csv',sep=';',index=False,encoding='utf-8-sig')
last=ipca.mes.max(); idx=ipca.set_index('mes').indice
def fator_ipca(base):  # base 'M/AAAA' -> fator até o último IPCA publicado
    m,a=base.strip().split('/'); p=pd.Period(f'{a}-{int(m):02d}','M'); return idx[last]/idx[p]
# ---------- BPR ----------
m=pd.read_csv(RA+'ANEEL__bpr-subestacao__banco-preco-referencia-item-modulo-manobra.csv',sep=';',dtype=str)
m=m.apply(lambda s:s.str.strip()); m['preco']=num(m.VlrPrecoBrasil); m['qtd']=num(m.VlrQuantidade); m['custo']=m.preco*m.qtd
dj=m[(m.NomItemModulo=='Disjuntor')&(m.SigClasse=='UAR')&(m.preco>0)].groupby(['NomTipoTensao','IndiceReferencia']).preco.first().reset_index()
dj['fator_IPCA_ate_'+str(last)]=dj.IndiceReferencia.map(fator_ipca).round(4)
dj['preco_corrigido_IPCA']=(dj.preco*dj['fator_IPCA_ate_'+str(last)]).round(2)
dj['kv']=pd.to_numeric(dj.NomTipoTensao); dj=dj.sort_values('kv')
dj.to_csv(P+'bpr_disjuntor_preco_unitario.csv',sep=';',index=False,encoding='utf-8-sig')
mods=m[m.SigTipoModuloManobra.isin(['CRB','CRL','CRLn','EL'])]
tot=mods.groupby(['SigTipoModuloManobra','NomTipoTensao','DscTipoArranjo']).agg(custo_total=('custo','sum'),itens=('custo','size')).reset_index()
tot['kv']=pd.to_numeric(tot.NomTipoTensao); tot=tot.sort_values(['SigTipoModuloManobra','kv','DscTipoArranjo'])
tot.round(2).to_csv(P+'bpr_modulos_manobra_reator_custo.csv',sep=';',index=False,encoding='utf-8-sig')
# participação do disjuntor no módulo CRB
crb=mods[mods.SigTipoModuloManobra=='CRB']
sh=crb.assign(dj=crb.NomItemModulo.eq('Disjuntor')&crb.SigClasse.eq('UAR')).groupby(['NomTipoTensao','DscTipoArranjo']).apply(lambda g:pd.Series({'custo_modulo':g.custo.sum(),'custo_disjuntores':g[g.dj].custo.sum()}))
sh['pct_disjuntor']=(sh.custo_disjuntores/sh.custo_modulo*100).round(1); sh.round(2).to_csv(P+'bpr_CRB_participacao_disjuntor.csv',sep=';',encoding='utf-8-sig')
pd.set_option('display.width',250)
print('último IPCA:',last); print(dj); print(tot[tot.kv.isin([230,500])]); print(sh.loc[['230','500']] if '230' in sh.index.get_level_values(0) else sh)
print(mac.tail(3).T)

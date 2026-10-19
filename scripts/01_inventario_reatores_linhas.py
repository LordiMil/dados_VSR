"""Inventário de reatores shunt (cadastro ONS), parâmetros de linhas (carregamento capacitivo) e disponibilidade das FT de reativos."""
import pandas as pd, numpy as np, os, glob
B=os.path.join(os.path.dirname(__file__),'..'); R=B+'/raw/ons/'; P=B+'/processed/'
HOJE=pd.Timestamp('2026-10-09')
# ---------- 1. Reatores ----------
d=pd.read_csv(R+'ONS__equipamento_controle_reativo__EQP_CONTROLE_REATIVO.csv',sep=';',dtype=str)
d=d.apply(lambda s:s.str.strip())
d['mvar']=pd.to_numeric(d.val_potreativanominal_mvar)
d['entrada']=pd.to_datetime(d.dat_entradaoperacao,errors='coerce'); d['desativ']=pd.to_datetime(d.dat_desativacao,errors='coerce')
d['kv']=d.nom_equipamento.str.extract(r'^\S+\s+(\S+)\s*kV')[0].str.replace('P','.',regex=False).astype(float)
d['ativo']=d.desativ.isna() & (d.entrada<=HOJE)
d['idade_anos']=((HOJE-d.entrada).dt.days/365.25).round(1)
# 1990-12-31 aparece 238x: data-padrão do cadastro para equipamentos anteriores a 1991 -> idade é um LIMITE INFERIOR
d['data_padrao_pre1991']=d.dat_entradaoperacao.eq('1990-12-31')
r=d[d.nom_tipoequipamento=='Reator'].copy()
ra=r[r.ativo].copy()
ra['faixa_kv']=pd.cut(ra.kv,[0,100,250,400,600,800],labels=['<100 kV','138-230 kV','345 kV','440-525 kV','765 kV'])
ra.to_csv(P+'reatores_ativos_ONS.csv',sep=';',index=False,encoding='utf-8-sig',
  columns=['cod_equipamento','nom_equipamento','id_subsistema','id_estado','nom_subestacao','nom_agente_proprietario','nom_tipoderede','kv','faixa_kv','mvar','dat_entradaoperacao','idade_anos','data_padrao_pre1991'])
res=[]
def add(sec,k,v,un,nota=''): res.append(dict(secao=sec,indicador=k,valor=v,unidade=un,nota=nota))
add('Reatores','Reatores no cadastro (todos os registros)',len(r),'un')
add('Reatores','Reatores ativos (sem data de desativação)',len(ra),'un')
add('Reatores','Reatores ativos ≥ 230 kV',int((ra.kv>=230).sum()),'un','comparar com ~1.100 bancos do CIGRÉ A3-10747 (2026)')
add('Reatores','Potência total ativa ≥ 230 kV',round(ra[ra.kv>=230].mvar.sum()),'Mvar')
add('Reatores','Idade mediana (ativos ≥ 230 kV)',ra[ra.kv>=230].idade_anos.median(),'anos')
add('Reatores','Reatores ativos ≥ 230 kV com 30+ anos',int(((ra.kv>=230)&(ra.idade_anos>=30)).sum()),'un','inclui os com data-padrão 1990-12-31 (idade real ≥ 35,8 anos)')
add('Reatores','Reatores ativos ≥ 230 kV com data-padrão 1990-12-31 (pré-1991)',int(((ra.kv>=230)&ra.data_padrao_pre1991).sum()),'un','idade é limite inferior')
add('Reatores','Potência mediana por reator (≥ 230 kV)',ra[ra.kv>=230].mvar.median(),'Mvar')
g=ra[ra.kv>=230]
tab=g.pivot_table(index='id_subsistema',columns='faixa_kv',values='mvar',aggfunc=['count','sum'],observed=True).fillna(0)
tab.columns=[f'{a}_{b}' for a,b in tab.columns]; tab=tab.rename(columns=lambda c:c.replace('count','qtd').replace('sum','Mvar'))
tab.to_csv(P+'reatores_por_subsistema_tensao.csv',sep=';',encoding='utf-8-sig')
uf=g.groupby('id_estado').agg(qtd=('mvar','size'),Mvar=('mvar','sum'),idade_mediana=('idade_anos','median')).sort_values('qtd',ascending=False)
uf.to_csv(P+'reatores_por_UF.csv',sep=';',encoding='utf-8-sig')
# série anual de entradas/desativações (todos os níveis ≥230 kV)
r230=r[r.kv>=230]
ent=r230.groupby(r230.entrada.dt.year).agg(entradas=('mvar','size'),Mvar_entrada=('mvar','sum'))
des=r230.groupby(r230.desativ.dt.year).agg(desativacoes=('mvar','size'))
serie=ent.join(des,how='outer').fillna(0); serie.index=serie.index.astype(int); serie.index.name='ano'
serie['estoque_fim_ano']=(serie.entradas-serie.desativacoes).cumsum()
serie.to_csv(P+'reatores_serie_anual_entradas.csv',sep=';',encoding='utf-8-sig')
fx=pd.cut(g.idade_anos,[0,10,20,30,80],right=False,labels=['0-9','10-19','20-29','30+ (data real)']).astype(str)
fx[g.data_padrao_pre1991]='pré-1991 (data-padrão 1990-12-31)'
idade=fx.value_counts().reindex(['0-9','10-19','20-29','30+ (data real)','pré-1991 (data-padrão 1990-12-31)']).fillna(0).astype(int)
idade.rename_axis('faixa_idade_anos').rename('qtd_reatores').to_csv(P+'reatores_distribuicao_idade.csv',sep=';',encoding='utf-8-sig')
# ---------- 2. Linhas: carregamento capacitivo ----------
L=pd.read_csv(R+'ONS__linha_transmissao__LINHA_TRANSMISSAO.csv',sep=';',dtype=str).apply(lambda s:s.str.strip())
for c in ['val_niveltensao_kv','val_comprimento','val_shunt','val_reatancia','val_resistencia']: L[c]=pd.to_numeric(L[c],errors='coerce')
L['entrada']=pd.to_datetime(L.dat_entradaoperacao,errors='coerce'); L['desativ']=pd.to_datetime(L.dat_desativacao,errors='coerce')
La=L[L.desativ.isna()&(L.entrada<=HOJE)&(L.nom_tipolinha.str.contains('TRANSMISS',na=False))&(L.val_comprimento>5)&(L.val_shunt>0)].copy()
La['Mvar_por_km']=La.val_shunt/La.val_comprimento
q=La.groupby('val_niveltensao_kv').agg(linhas=('Mvar_por_km','size'),km_total=('val_comprimento','sum'),
   Mvar_carregamento_total=('val_shunt','sum'),Mvar_km_p10=('Mvar_por_km',lambda x:x.quantile(.1)),
   Mvar_km_mediana=('Mvar_por_km','median'),Mvar_km_p90=('Mvar_por_km',lambda x:x.quantile(.9)),
   comprimento_mediano_km=('val_comprimento','median'),comprimento_p90_km=('val_comprimento',lambda x:x.quantile(.9)))
q=q[q.linhas>=10].round(3); q.to_csv(P+'linhas_carregamento_capacitivo_por_tensao.csv',sep=';',encoding='utf-8-sig')
add('Linhas','Linhas CA ativas analisadas (com susceptância)',len(La),'un','LINHA_TRANSMISSAO.csv; val_shunt = Mvar de carregamento (convenção ANAREDE)')
add('Linhas','Extensão total das linhas analisadas',round(La.val_comprimento.sum()),'km')
# grau de compensação sistêmico = Mvar de reatores ativos / Mvar de carregamento das linhas, por nível
for lab,kvs in [('230 kV',[230]),('345 kV',[345]),('440-525 kV',[440,500,525]),('765 kV',[765])]:
    ch=La[La.val_niveltensao_kv.isin(kvs)].val_shunt.sum(); re_=ra[ra.kv.isin(kvs)].mvar.sum()
    if ch>0: add('Linhas',f'Grau de compensação shunt sistêmico {lab} (reatores ÷ carregamento)',round(re_/ch,3),'pu',f'reatores {re_:.0f} Mvar / carregamento {ch:.0f} Mvar')
# ---------- 3. Disponibilidade FT reativo ----------
fs=sorted(glob.glob(R+'*IND_DISPONIBILIDADE_FT_REATIVO_*.csv'))
D=pd.concat([pd.read_csv(f,sep=';') for f in fs]); D.columns=['caracteristica','data','disp_pct']
D['caracteristica']=D.caracteristica.str.strip(); D['data']=pd.to_datetime(D.data)
D['tipo']=D.caracteristica.str.split(' - ').str[0]; D['kv']=pd.to_numeric(D.caracteristica.str.split(' - ').str[1])
D['indisp_pct']=100-D.disp_pct; D['horas_indisp_mes']=D.indisp_pct/100*D.data.dt.days_in_month*24
D.sort_values(['caracteristica','data']).to_csv(P+'disponibilidade_FT_reativo_mensal.csv',sep=';',index=False,encoding='utf-8-sig')
rt=D[(D.tipo=='FTRT')&(D.kv>=230)]
st=rt.groupby('caracteristica').agg(meses=('disp_pct','size'),inicio=('data','min'),fim=('data','max'),disp_media=('disp_pct','mean'),
   disp_dp=('disp_pct','std'),disp_min=('disp_pct','min'),indisp_horas_mes_media=('horas_indisp_mes','mean'),indisp_horas_mes_p95=('horas_indisp_mes',lambda x:x.quantile(.95))).round(4)
st.to_csv(P+'disponibilidade_FTRT_estatisticas.csv',sep=';',encoding='utf-8-sig')
an=rt.groupby([rt.data.dt.year.rename('ano'),'caracteristica']).disp_pct.mean().unstack().round(4)
an.to_csv(P+'disponibilidade_FTRT_media_anual.csv',sep=';',encoding='utf-8-sig')
for c,s in st.iterrows(): add('Disponibilidade',f'{c}: disponibilidade média mensal',s.disp_media,'%',f'{s.meses} meses, {s.inicio:%Y-%m} a {s.fim:%Y-%m}; dp {s.disp_dp}')
pd.DataFrame(res).to_csv(P+'resumo_01_reatores_linhas_disp.csv',sep=';',index=False,encoding='utf-8-sig')
print(pd.DataFrame(res).to_string()); print(tab); print(q); print(serie.tail(12)); print(idade); print(an.tail(6))

"""Séries de carga (ONS curva de carga horária 2015-2026) e carga líquida semi-horária (ONS DESSEM detalhado, mai/2025-out/2026).
Carga líquida (definição do estudo) = demanda - (eólica + fotovoltaica centralizada + MMGD)."""
import pandas as pd, numpy as np, os, glob
B=os.path.join(os.path.dirname(__file__),'..'); R=B+'/raw/ons/'; P=B+'/processed/'
# ---------- A. DESSEM detalhado ----------
d=pd.read_csv(glob.glob(R+'*balanco_dessem_detalhe__CONSOLIDADO*.csv')[0],sep=';')
d['data']=pd.to_datetime(d.din_programacaodia); d['hora']=(d.num_patamar-1)*0.5
d['vre']=d.val_ger_eolica+d.val_ger_fotovoltaica+d.val_ger_mmgd
d['liquida']=d.val_demanda-d.vre
# completude
comp=d.groupby(['data','cod_subsistema']).size().unstack()
inc=comp[(comp!=48).any(axis=1)]
# SIN = soma dos 4 subsistemas (apenas dias completos)
okdays=comp[(comp==48).all(axis=1)].index
cols=['val_demanda','val_ger_eolica','val_ger_fotovoltaica','val_ger_mmgd','vre','liquida']
sin=d[d.data.isin(okdays)].groupby(['data','num_patamar','hora'])[cols].sum().reset_index(); sin['cod_subsistema']='SIN'
dd=pd.concat([d[cols+['data','num_patamar','hora','cod_subsistema']],sin])
dd.to_csv(P+'dessem_semihorario_carga_liquida.csv',sep=';',index=False,encoding='utf-8-sig',float_format='%.1f')
def daily(g):
    g=g.sort_values('num_patamar'); x=g.liquida.values; h=g.hora.values
    imin=x.argmin(); imax=x.argmax()
    ramp3=(pd.Series(x).diff(6)).max()       # maior subida em 3 h (6 semi-horas)
    queda3=(pd.Series(x).diff(6)).min()
    return pd.Series(dict(demanda_media=g.val_demanda.mean(),liquida_media=x.mean(),liquida_min=x[imin],hora_liquida_min=h[imin],
        liquida_max=x[imax],hora_liquida_max=h[imax],amplitude_liquida=x[imax]-x[imin],
        vale_vs_media_dia=x.mean()-x[imin],rampa_max_3h=ramp3,descida_max_3h=queda3,
        mmgd_pico=g.val_ger_mmgd.max(),fv_pico=g.val_ger_fotovoltaica.max(),
        fracao_vre_no_vale=g.vre.values[imin]/g.val_demanda.values[imin],
        variacao_semihoraria_dp=pd.Series(x).diff().std()))
D=dd.groupby(['cod_subsistema','data']).apply(daily).reset_index()
D['dia_semana']=D.data.dt.dayofweek; D['fim_de_semana']=D.dia_semana>=5; D['mes']=D.data.dt.to_period('M').astype(str)
D.to_csv(P+'dessem_diario_curva_pato_por_subsistema.csv',sep=';',index=False,encoding='utf-8-sig',float_format='%.2f')
q=lambda p:(lambda x:x.quantile(p))
S=D.groupby('cod_subsistema').agg(dias=('data','size'),inicio=('data','min'),fim=('data','max'),
  amplitude_media=('amplitude_liquida','mean'),amplitude_dp=('amplitude_liquida','std'),amplitude_p05=('amplitude_liquida',q(.05)),
  amplitude_p50=('amplitude_liquida',q(.5)),amplitude_p95=('amplitude_liquida',q(.95)),
  rampa3h_media=('rampa_max_3h','mean'),rampa3h_p95=('rampa_max_3h',q(.95)),rampa3h_max=('rampa_max_3h','max'),
  vale_vs_media_media=('vale_vs_media_dia','mean'),liquida_min_absoluta=('liquida_min','min'),
  hora_min_moda=('hora_liquida_min',lambda x:x.mode().iloc[0]),pct_dias_min_entre_10e15h=('hora_liquida_min',lambda x:((x>=10)&(x<15)).mean()*100),
  cv_amplitude=('amplitude_liquida',lambda x:x.std()/x.mean())).round(2)
S.to_csv(P+'dessem_estatisticas_curva_pato.csv',sep=';',encoding='utf-8-sig')
M=D.groupby(['cod_subsistema','mes']).agg(amplitude_media=('amplitude_liquida','mean'),rampa3h_media=('rampa_max_3h','mean'),
  liquida_min_media=('liquida_min','mean'),mmgd_pico_medio=('mmgd_pico','mean'),pct_dias_min_10a15h=('hora_liquida_min',lambda x:((x>=10)&(x<15)).mean()*100)).round(1)
M.to_csv(P+'dessem_mensal_por_subsistema.csv',sep=';',encoding='utf-8-sig')
# perfil médio mês x hora (curvas de pato) por subsistema
dd['mes']=dd.data.dt.to_period('M').astype(str)
perf=dd.groupby(['cod_subsistema','mes','hora']).liquida.mean().round(0).reset_index()
perf.to_csv(P+'dessem_perfil_medio_mes_hora.csv',sep=';',index=False,encoding='utf-8-sig')
W=D.groupby(['cod_subsistema','fim_de_semana']).agg(amplitude_media=('amplitude_liquida','mean'),liquida_min_media=('liquida_min','mean')).round(0)
# ---------- B. Curva de carga horária 2015-2026 ----------
fs=sorted(glob.glob(R+'*CURVA_CARGA_20*.csv'))
C=pd.concat([pd.read_csv(f,sep=';') for f in fs]); C['t']=pd.to_datetime(C.din_instante); C['data']=C.t.dt.normalize(); C['hora']=C.t.dt.hour
C=C.rename(columns={'val_cargaenergiahomwmed':'carga'})
sinC=C.groupby(['t','data','hora']).carga.sum().reset_index(); sinC['id_subsistema']='SIN'
CC=pd.concat([C[['id_subsistema','t','data','hora','carga']],sinC])
cnt=CC.groupby(['id_subsistema','data']).size(); 
def dl(g):
    x=g.sort_values('hora').carga.values; h=g.sort_values('hora').hora.values
    return pd.Series(dict(media=x.mean(),minimo=x.min(),hora_min=h[x.argmin()],maximo=x.max(),hora_max=h[x.argmax()],
                          amplitude=x.max()-x.min(),fator_carga=x.mean()/x.max(),rampa_max_3h=pd.Series(x).diff(3).max()))
CD=CC.groupby(['id_subsistema','data']).apply(dl).reset_index()
CD=CD.merge(cnt.rename('horas').reset_index(),on=['id_subsistema','data'])
CD.to_csv(P+'carga_horaria_diario_2015_2026.csv',sep=';',index=False,encoding='utf-8-sig',float_format='%.1f')
CD['ano']=CD.data.dt.year
A=CD[CD.horas==24].groupby(['id_subsistema','ano']).agg(carga_media=('media','mean'),amplitude_media=('amplitude','mean'),
  amplitude_p95=('amplitude',q(.95)),fator_carga=('fator_carga','mean'),rampa3h_media=('rampa_max_3h','mean'),
  pct_dias_min_10a15h=('hora_min',lambda x:((x>=10)&(x<15)).mean()*100),dias=('media','size')).round(1)
A.to_csv(P+'carga_horaria_anual_2015_2026.csv',sep=';',encoding='utf-8-sig')
CC.to_csv(P+'carga_horaria_2015_2026_longo.csv',sep=';',index=False,encoding='utf-8-sig',float_format='%.1f',columns=['id_subsistema','t','carga'])
pd.set_option('display.width',250); pd.set_option('display.max_columns',30)
print('DESSEM dias incompletos:',len(inc),'| dias completos SIN:',len(okdays))
print(S.T); print(W); print(A.loc['SIN']); print(A.loc['NE'])

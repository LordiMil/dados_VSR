"""Calibra a regra de manobra dos reatores fixos a partir das séries semi-horárias do DESSEM e exporta as séries dos cenários.
Regra (declarada): o banco i é inserido quando a carga 'vista' pela barra cai abaixo do limiar T_i e retirado quando sobe acima de T_i + h.
Limiares T_i espaçados entre os percentis 10 e 40 da série; histerese h = 3% da média. Cada entrada = 2 operações do disjuntor (fechar + abrir)."""
import pandas as pd, numpy as np, os, json, glob
B=os.path.join(os.path.dirname(__file__),'..'); R=B+'/raw/ons/'; P=B+'/processed/'
d=pd.read_csv(glob.glob(R+'*balanco_dessem_detalhe__CONSOLIDADO*.csv')[0],sep=';')
d['data']=pd.to_datetime(d.din_programacaodia)
S={'urbano':('NE',lambda g:g.val_demanda-g.val_ger_mmgd-g.val_ger_fotovoltaica,'NE: demanda − MMGD − fotovoltaica (GD local; eólica é remota)'),
   'campo':('N',lambda g:g.val_demanda-g.val_ger_mmgd-g.val_ger_fotovoltaica-g.val_ger_eolica,'PROVISÓRIO – N: demanda − MMGD − FV − eólica (carga líquida); trocar pelo fluxo medido N–NE'),
   'polo_eolico':('NE',lambda g:g.val_demanda-g.val_ger_mmgd-g.val_ger_fotovoltaica-g.val_ger_eolica,'NE: demanda − MMGD − FV − eólica (carga líquida, dominada pela eólica; antigo cenário Indústria)')}
def ops_por_dia(x,n_bancos=1,k=1.0):
    x=np.asarray(x,float); days=len(x)//48; x=x[:days*48]
    tr=pd.Series(x).rolling(6,center=True,min_periods=1).mean().values  # tendência de 3 h
    y=tr+k*(x-tr)                                                       # volatilidade escalada
    qs=np.linspace(10,40,n_bancos) if n_bancos>1 else [25]
    T=np.percentile(x,qs); h=0.03*x.mean()
    ops=np.zeros(days)
    for t in T:
        on=False
        for i,v in enumerate(y):
            if not on and v<t: on=True; ops[i//48]+=1
            elif on and v>t+h: on=False; ops[i//48]+=1
    return ops/n_bancos   # operações por disjuntor por dia
out={'meta':{'fonte':'ONS – BALANCO_DESSEM_DETALHE, 23/05/2025 a 09/10/2026 (semi-horário)','regra':__doc__.strip()}}
for k,(sub,f,desc) in S.items():
    g=d[d.cod_subsistema==sub].sort_values(['data','num_patamar'])
    cnt=g.groupby('data').size(); ok=cnt[cnt==48].index; g=g[g.data.isin(ok)]
    x=f(g).round(0).astype(int).values
    res={nb:ops_por_dia(x,nb).mean() for nb in (1,2,3)}
    resk={kk:ops_por_dia(x,2,kk).mean() for kk in (0.5,1.5,2.0)}
    o1=ops_por_dia(x,1)
    print(k,sub,'dias',len(ok),'| ops/disj/dia por nº bancos',{a:round(b,2) for a,b in res.items()},'| vol k:',{a:round(b,2) for a,b in resk.items()},'| dist 1 banco: p10/p50/p90',np.percentile(o1,[10,50,90]))
    out[k]={'subsistema':sub,'descricao':desc,'dias':len(ok),'inicio':str(ok.min().date()),'fim':str(ok.max().date()),'serie_MW':x.tolist()}
json.dump(out,open(P+'cenarios_series_semihorarias.json','w'),separators=(',',':'))
r=pd.read_csv(P+'reatores_ativos_ONS.csv',sep=';')
for kv in (230,500): print(kv,'kV: Mvar por reator mediana',r[r.kv==kv].mvar.median(),'p25',r[r.kv==kv].mvar.quantile(.25),'p75',r[r.kv==kv].mvar.quantile(.75),'n',int((r.kv==kv).sum()))
print(os.path.getsize(P+'cenarios_series_semihorarias.json'),'bytes')

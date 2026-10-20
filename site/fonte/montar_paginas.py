"""Monta as páginas "O Custo do Fixo" (calculadora) e "Monte Carlo" a partir dos modelos desta pasta e dos dados em processed/.

Uso (a partir de qualquer pasta):
  python site/fonte/montar_paginas.py
      -> site/o-custo-do-fixo.html e site/monte-carlo.html (páginas completas, links relativos entre si).
         São estas que vão para o site Next.js em public/calculadora/ (o site as abre com ?embed=1).
  python site/fonte/montar_paginas.py --artefatos <URL_CALCULADORA> <URL_MONTE_CARLO> <PASTA_SAIDA>
      -> versões para publicar como artefato no claude.ai (links absolutos entre os dois artefatos, abrem em nova aba).

Dados: processed/site_calculadora.json (script 11) e processed/site_monte_carlo.json (script 12)."""
import sys, os, json

AQUI = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(os.path.dirname(AQUI))                      # pasta PoliVSR-dados
PROC = os.path.join(BASE, 'processed')
T_CALC = os.path.join(AQUI, 'calculadora.template.html')
T_MC = os.path.join(AQUI, 'monte-carlo.template.html')


def so_histograma(d):
    """A página de Monte Carlo não usa as trajetórias ano a ano; tira do arquivo embutido."""
    for c in d['cenarios'].values():
        for v in c['visoes'].values():
            for k in ('anos', 'linhas', 'faixa', 'exemplo'):
                v.pop(k)
    return d


def monta(tpl, dados, subs, filtro=None):
    t = open(tpl, encoding='utf-8').read()
    d = open(dados, encoding='utf-8').read()
    if filtro:
        d = json.dumps(filtro(json.loads(d)), ensure_ascii=False, separators=(',', ':'))
    d = d.replace('</', '<\\/')
    assert t.count('__DADOS__') == 1
    t = t.replace('__DADOS__', d)
    for k, v in subs.items():
        alvo = v + '" target="_blank" rel="noopener' if v.startswith('https://') else v
        assert t.count('href="' + k + '"') >= 1
        t = t.replace('href="' + k + '"', 'href="' + alvo + '"')
        assert k not in t
    return t


def documento(h):
    return ('<!doctype html>\n<html lang="pt-BR"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + h + '\n</html>')


def grava(caminho, texto):
    with open(caminho, 'w', encoding='utf-8', newline='\n') as f:
        f.write(texto)
    print('ok', os.path.relpath(caminho, BASE), round(len(texto.encode('utf-8')) / 1e3), 'kB')


J_CALC = os.path.join(PROC, 'site_calculadora.json')
J_MC = os.path.join(PROC, 'site_monte_carlo.json')
if len(sys.argv) > 1 and sys.argv[1] == '--artefatos':
    url_calc, url_mc, saida = sys.argv[2:5]
    os.makedirs(saida, exist_ok=True)
    grava(os.path.join(saida, 'o-custo-do-fixo.html'), monta(T_CALC, J_CALC, {'__MC__': url_mc}))
    grava(os.path.join(saida, 'monte-carlo.html'), monta(T_MC, J_MC, {'__CALC__': url_calc}, so_histograma))
else:
    SITE = os.path.join(BASE, 'site')
    grava(os.path.join(SITE, 'o-custo-do-fixo.html'), documento(monta(T_CALC, J_CALC, {'__MC__': 'monte-carlo.html'})))
    grava(os.path.join(SITE, 'monte-carlo.html'), documento(monta(T_MC, J_MC, {'__CALC__': 'o-custo-do-fixo.html'}, so_histograma)))

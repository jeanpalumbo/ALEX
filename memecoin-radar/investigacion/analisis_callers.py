# Análisis a fondo de los tuiteros de calls (Ben y otros), solo simulación.
# Para cada call (primer post de una cuenta con una CA): entrar d min después del post y salir a w min,
# o con take-profit / stop-loss recorriendo las velas en orden. Por cuenta, por ventana y por orden (quién lo dijo primero).
# Comprueba si lo que gana se repite en dos mitades de días distintos (2-3 nov vs 4-5 nov).
import json, os, sys, statistics as st
from collections import defaultdict, Counter
from datetime import datetime

RAIZ = sys.argv[1]
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache_calls')
COSTE = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05      # ida+vuelta
CORTE = int(datetime(2026, 11, 4).timestamp())                    # mitad A: antes; mitad B: después
RETRASOS = (0, 1, 2, 5)
VENTANAS = (5, 15, 30, 60, 240, 1440)
REGLAS = [(1.3, 0.8, 30), (1.5, 0.7, 60), (2.0, 0.6, 60), (1.2, 0.9, 15)]   # (TP, SL, minutos máx)

def ts(s): return int(datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())

rows = [json.loads(l) for l in open(os.path.join(RAIZ, 'data/callhunter/calls.jsonl'), encoding='utf8')]
rows = [r for r in rows if r['chain'] == 'solana']
# primera aparición de cada (cuenta, CA) = la call de esa cuenta
calls = {}
for r in sorted(rows, key=lambda r: r['created_at_utc']):
    k = (r['author'], r['ca'])
    if k not in calls: calls[k] = {'author': r['author'], 'ca': r['ca'], 't': ts(r['created_at_utc']), 'tipo': r['tipo'], 'url': r['url']}
calls = list(calls.values())
# orden entre cuentas por CA (la "matriz": quién lo publica primero y quién detrás)
por_ca = defaultdict(list)
for c in calls: por_ca[c['ca']].append(c)
for ca, lst in por_ca.items():
    lst.sort(key=lambda c: c['t'])
    for i, c in enumerate(lst):
        c['orden'] = i + 1; c['n_cuentas'] = len(lst); c['retraso_vs_primero'] = (c['t'] - lst[0]['t']) / 60

velas, velas15 = {}, {}
def V(ca):
    if ca not in velas:
        f = os.path.join(CACHE, ca + '.json')
        d = json.load(open(f)) if os.path.exists(f) else {}
        velas[ca] = d.get('v', []); velas15[ca] = d.get('v15', [])
    return velas[ca]

def entrada(v, t):
    for row in v:
        if row[0] >= t: return (row[0], row[1]) if row[0] - t <= 300 else (None, None)   # abre la vela siguiente
    return None, None

def precio_hasta(v, t):
    p = None
    for row in v:
        if row[0] > t: break
        p = row[4]
    return p

def precio_previo(v, t):
    return precio_hasta(v, t)

for c in calls:
    v = V(c['ca']); c['ok'] = bool(v)
    if not v: continue
    c['min_desde_primera_vela'] = (c['t'] - v[0][0]) / 60
    p0, p30 = precio_hasta(v, c['t']), precio_hasta(v, c['t'] - 1800)
    c['subida_30min_antes'] = p0 / p30 if p0 and p30 else None
    for d in RETRASOS:
        te, pe = entrada(v, c['t'] + d * 60)
        if not pe: continue
        for w in VENTANAS:
            serie = v if w < 1440 else velas15[c['ca']]   # 24 h con velas de 15 min
            if not serie: continue
            pf = precio_hasta(serie, te + w * 60)
            if pf: c[f'r_{d}_{w}'] = pf / pe * (1 - COSTE) - 1
        for tp, sl, mx in REGLAS:
            res = None
            for row in v:
                if row[0] < te: continue
                if row[0] > te + mx * 60: break
                if row[3] <= pe * sl: res = sl; break      # el stop cuenta primero (pesimista)
                if row[2] >= pe * tp: res = tp; break
            if res is None:
                pf = precio_hasta(v, te + mx * 60); res = pf / pe if pf else None
            if res: c[f'tp_{d}_{tp}_{sl}_{mx}'] = res * (1 - COSTE) - 1

ok = [c for c in calls if c['ok']]
def stats(vals):
    if not vals: return None
    return {'n': len(vals), 'media': st.mean(vals), 'mediana': st.median(vals), 'gana': sum(x > 0 for x in vals) / len(vals)}

def fila(nombre, sub, k):
    a = [c[k] for c in sub if k in c and c['t'] < CORTE]; b = [c[k] for c in sub if k in c and c['t'] >= CORTE]
    t = stats(a + b); sa, sb = stats(a), stats(b)
    if not t: return None
    return {'grupo': nombre, 'regla': k, **t, 'A': sa, 'B': sb}

claves = [f'r_{d}_{w}' for d in RETRASOS for w in VENTANAS] + [f'tp_{d}_{tp}_{sl}_{mx}' for d in RETRASOS for tp, sl, mx in REGLAS]
grupos = {'TODAS': ok, 'primero en publicarlo': [c for c in ok if c['orden'] == 1],
          'detrás de otro (copia)': [c for c in ok if c['orden'] > 1],
          'tipo mención (no presume)': [c for c in ok if c['tipo'].startswith('menci')],
          'token < 30 min de vida': [c for c in ok if c['min_desde_primera_vela'] < 30],
          'no había subido >2x en 30 min previos': [c for c in ok if c.get('subida_30min_antes') and c['subida_30min_antes'] < 2],
          '2+ cuentas lo publican (consenso)': [c for c in ok if c['n_cuentas'] >= 2 and c['orden'] == 2]}
for a in sorted(set(c['author'] for c in ok)):
    sub = [c for c in ok if c['author'] == a]
    if len(sub) >= 8: grupos['@' + a] = sub

todas = [f for g, sub in grupos.items() for k in claves if (f := fila(g, sub, k))]
# Consistente = gana en las dos mitades por separado, con muestra mínima
def consistente(f, nmin=8):
    return f['A'] and f['B'] and f['A']['n'] >= nmin and f['B']['n'] >= nmin and \
           f['A']['media'] > 0 and f['B']['media'] > 0 and f['A']['gana'] >= 0.5 and f['B']['gana'] >= 0.5

out = {'coste': COSTE, 'n_calls': len(calls), 'n_con_velas': len(ok), 'filas': todas,
       'consistentes': [f for f in todas if consistente(f)],
       'casi': sorted([f for f in todas if f['n'] >= 15], key=lambda f: -f['media'])[:25]}
# matriz: quién publica primero, quién copia a quién
lider = Counter(c['author'] for c in ok if c['orden'] == 1 and c['n_cuentas'] >= 2)
pares = Counter(); lag = defaultdict(list)
for ca, lst in por_ca.items():
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            pares[(lst[i]['author'], lst[j]['author'])] += 1; lag[(lst[i]['author'], lst[j]['author'])].append((lst[j]['t'] - lst[i]['t']) / 60)
out['lideres'] = lider.most_common(15)
out['pares'] = [(a, b, n, st.median(lag[(a, b)])) for (a, b), n in pares.most_common(25)]
out['subida_previa'] = stats([c['subida_30min_antes'] for c in ok if c.get('subida_30min_antes')])
out['min_desde_inicio'] = stats([c['min_desde_primera_vela'] for c in ok])
json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), f'resultado_callers_{int(COSTE*100)}.json'), 'w'), indent=1, default=str)

pct = lambda x: f"{x*100:+.0f}%"
print(f"calls (cuenta+token): {len(calls)} | con velas: {len(ok)} | coste {COSTE*100:.0f}% ida+vuelta")
print("Antes de la call el token ya había subido (precio en la call / 30 min antes): mediana", round(out['subida_previa']['mediana'], 2))
print("Minutos desde el inicio del token hasta la call: mediana", round(out['min_desde_inicio']['mediana']))
print("\nLíderes (primeros en publicar tokens que luego publican otros):", out['lideres'][:8])
print("Pares más repetidos (A primero -> B después, veces, retraso mediano min):"); [print('  ', p) for p in out['pares'][:10]]
print(f"\nCombinaciones que ganan en LAS DOS mitades (2-3 nov y 4-5 nov), n>=8 cada una: {len(out['consistentes'])}")
for f in sorted(out['consistentes'], key=lambda f: -f['media']):
    print(f"  {f['grupo']:38s} {f['regla']:22s} n={f['n']:3d} media={pct(f['media'])} gana={f['gana']*100:.0f}% | A {pct(f['A']['media'])}/{f['A']['gana']*100:.0f}% (n{f['A']['n']}) B {pct(f['B']['media'])}/{f['B']['gana']*100:.0f}% (n{f['B']['n']})")
print("\nTop 25 por media (n>=15), sin exigir consistencia:")
for f in out['casi']:
    ab = f" | A {pct(f['A']['media'])} B {pct(f['B']['media'])}" if f['A'] and f['B'] else ''
    print(f"  {f['grupo']:38s} {f['regla']:22s} n={f['n']:3d} media={pct(f['media'])} mediana={pct(f['mediana'])} gana={f['gana']*100:.0f}%{ab}")
print("\nResumen por cuenta: mejor regla de salida a ventana fija, entrando 1 min después del post")
for g in [g for g in grupos if g.startswith('@')]:
    best = max((f for f in todas if f['grupo'] == g and f['regla'].startswith('r_1_')), key=lambda f: f['media'], default=None)
    if best: print(f"  {g:22s} n={best['n']:3d} mejor ventana {best['regla'][4:]} min: media={pct(best['media'])} gana={best['gana']*100:.0f}%")

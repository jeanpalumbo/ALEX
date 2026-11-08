# Regla con salida: take-profit / stop-loss recorriendo las velas en orden (sin mirar el futuro).
import json, os, statistics as st
R = json.load(open('resultados_origen.json'))
def sim(r, retraso, tp, sl, coste=0.05):
    d = json.load(open(os.path.join('cache', r['ca'] + '.json'))); v = d['v']
    te = r['t0'] + retraso * 60 if r['grupo'] == 'BASE' else None
    pe = r.get(f'e{retraso}')
    if not pe: return None
    if te is None:  # G7: entrada tras la publicacion; reconstruir te desde la vela de entrada
        te = min((x[0] for x in v if abs(x[4] - pe) < 1e-18), default=None)
        if te is None: return None
    for x in v:
        if x[0] <= te: continue
        if x[0] > te + 3600: break
        if x[3] <= pe * sl: return sl * (1 - coste) - 1   # el stop primero (pesimista)
        if x[2] >= pe * tp: return tp * (1 - coste) - 1
    last = [x[4] for x in v if te < x[0] <= te + 3600]
    return (last[-1] / pe if last else 1) * (1 - coste) - 1
for g in ('G7', 'BASE'):
    sub = [r for r in R if r['grupo'] == g]
    for tp, sl in ((1.3, 0.8), (1.5, 0.7), (2.0, 0.5), (3.0, 0.5)):
        v = [p for p in (sim(r, 2, tp, sl) for r in sub) if p is not None]
        print(f"{g:4s} entrada 2 min, TP x{tp} SL x{sl}: n={len(v)} media={st.mean(v)*100:+.1f}% ganan={sum(p>0 for p in v)/len(v)*100:.0f}%")

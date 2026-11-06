# Backtest de las calls de X (datos G6 de Gold/Lolo): ¿seguirlas da dinero? Solo simulación.
import json, sys, random, statistics as st
from collections import defaultdict
SRC = sys.argv[1]
rows = [json.loads(l) for l in open(SRC, encoding='utf8')]
ev = [r for r in rows if r['estado'] == 'EVALUABLE' and r.get('ret_1h') is not None]

def pnl(r, h, coste, tp=None):
    x = r[f'ret_{h}']
    if x is None: return None
    if tp and r.get(f'max_{h}') and r[f'max_{h}'] >= tp: x = tp   # vende al tocar TP (optimista: ignora orden max/min)
    return x * (1 - coste) - 1                                      # coste = ida+vuelta (comisión + deslizamiento)

def resumen(nombre, sub, h, coste, tp=None):
    v = [p for p in (pnl(r, h, coste, tp) for r in sub) if p is not None]
    if not v: return
    boot = sorted(st.mean(random.choices(v, k=len(v))) for _ in range(2000))
    print(f"{nombre:38s} n={len(v):4d}  media={st.mean(v)*100:+6.1f}%  mediana={st.median(v)*100:+6.1f}%  "
          f"ganan={sum(p>0 for p in v)/len(v)*100:4.0f}%  IC90 media=[{boot[100]*100:+.1f}%, {boot[1900]*100:+.1f}%]")

random.seed(1)
print(f"Fuente {SRC}: {len(rows)} calls, {len(ev)} evaluables\n")
for coste in (0.03, 0.08):
    print(f"=== Coste ida+vuelta {coste*100:.0f}% ===")
    for h in ('1h', '24h'):
        resumen(f"Todas, vender a {h}", ev, h, coste)
    resumen("Todas, TP 2x en 1h si no a 1h (optimista)", ev, '1h', coste, tp=2)
    resumen("Solo primer caller observado, 1h", [r for r in ev if r.get('rango_obs') == 1], '1h', coste)
    resumen("Solo mención_CA (no 'resultado'), 1h", [r for r in ev if r.get('tipo') == 'mención_CA'], '1h', coste)
    resumen("Liquidez: vol 15m previo >= 50k$, 1h", [r for r in ev if (r.get('vol_usd_15m_previo') or 0) >= 50000], '1h', coste)
    resumen("Token < 30 min de vida al call, 1h", [r for r in ev if r.get('min_desde_creacion_pumpfun') is not None and r['min_desde_creacion_pumpfun'] < 30], '1h', coste)
    print()
print("=== Por cuenta (coste 3%, vender a 1h, n>=10) ===")
por = defaultdict(list)
for r in ev: por[r['author']].append(r)
for a, sub in sorted(por.items(), key=lambda kv: -len(kv[1])):
    if len(sub) >= 10: resumen(a, sub, '1h', 0.03)

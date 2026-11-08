# Backtest con precios reales (GeckoTerminal, velas 1 min) de:
#   G7 = tokens cuya CA publicó el proyecto o un tuit de narrativa en <=10 min
#   BASE = muestra aleatoria del recolector (todos los tokens nuevos de pump.fun), para comparar.
# Solo simulación. Uso: python backtest_origen.py <ruta memecoin-radar> [n_base]
import csv, gzip, json, os, random, sys, time
from datetime import datetime, timezone
sys.path.insert(0, sys.argv[1])
from radar import gecko
RAIZ = sys.argv[1]; NBASE = int(sys.argv[2]) if len(sys.argv) > 2 else 250
CACHE = os.path.join(os.path.dirname(__file__), 'cache')

def ts(s): return int(datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())

def velas(ca, t0):
    f = os.path.join(CACHE, ca + '.json')
    if os.path.exists(f): return json.load(open(f))
    out = {'pool': None, 'v': []}
    try:
        pools = (gecko.get(f'/networks/solana/tokens/{ca}/pools?page=1').get('data') or [])[:2]
        out['pool'] = [p['relationships']['dex']['data']['id'] for p in pools]
        porminuto = {}
        for p in pools:  # curva de pump.fun + pool tras graduarse: por minuto, la vela con más volumen
            for row in gecko.candles('solana', p['attributes']['address'], 'minute', 1, t0 + 1000 * 60, 1000):
                if row[0] not in porminuto or row[5] > porminuto[row[0]][5]: porminuto[row[0]] = row
        out['v'] = [porminuto[k] for k in sorted(porminuto)]
    except Exception as e:
        out['error'] = str(e)
    json.dump(out, open(f, 'w'))
    return out

def precio_en(v, t):
    """close de la primera vela >= t; si no hay vela en [t, t+5min] -> None (no habría liquidez)"""
    for row in v:
        if row[0] >= t: return row[4] if row[0] - t <= 300 else None
    return None

def ultimo_hasta(v, t):
    prev = None
    for row in v:
        if row[0] > t: break
        prev = row[4]
    return prev  # sin velas nuevas = nadie opera: el precio se queda en la última vela

g7 = list(csv.DictReader(open(os.path.join(RAIZ, 'data/origen_proyecto.csv'), encoding='utf8')))
col = list(csv.DictReader(gzip.open(os.path.join(RAIZ, 'data/collector/tokens_2026-11-06.csv.gz'), 'rt', encoding='utf8')))
random.seed(7)
ahora = time.time()
base = [r for r in col if ahora - int(r['created_utc']) > 26 * 3600] or col
base = random.sample(base, min(NBASE, len(base)))

res = []
todo = [('G7', r['ca'], ts(r['hora_creacion_utc']), float(r['min_desde_creacion'] or 0), r) for r in g7] + \
       [('BASE', r['mint'], int(r['created_utc']), 0.0, r) for r in base]
for i, (grupo, ca, t0, mins, r) in enumerate(todo):
    d = velas(ca, t0)
    v = d['v']
    fila = {'grupo': grupo, 'ca': ca, 't0': t0, 'pool': d['pool'], 'n_velas': len(v)}
    if grupo == 'BASE':
        fila['twitter'] = bool(r.get('twitter')); fila['j7'] = r.get('j7')
    for nombre, retraso in (('e2', 2), ('e5', 5), ('e15', 15)):
        te = t0 + int((max(mins, 0) + retraso) * 60)
        pe = precio_en(v, te)
        fila[nombre] = pe
        if pe:
            for h, s in (('1h', 3600), ('6h', 6 * 3600), ('16h', 16 * 3600)):
                pf = ultimo_hasta(v, te + s)
                fila[f'{nombre}_{h}'] = pf / pe if pf else None
            mx = max((row[2] for row in v if te < row[0] <= te + 3600), default=None)
            fila[f'{nombre}_max1h'] = mx / pe if mx else None
    res.append(fila)
    if i % 25 == 0: print(i, len(todo), flush=True)
json.dump(res, open(os.path.join(os.path.dirname(__file__), 'resultados_origen.json'), 'w'))
print('hecho', len(res))

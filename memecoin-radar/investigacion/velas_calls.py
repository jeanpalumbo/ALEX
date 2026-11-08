# Descarga velas de 1 min (GeckoTerminal) de cada CA de calls.jsonl, desde 30 min antes de la primera call hasta +26 h.
import json, os, sys, time
from datetime import datetime
sys.path.insert(0, sys.argv[1])
from radar import gecko
RAIZ = sys.argv[1]; CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache_calls')
rows = [json.loads(l) for l in open(os.path.join(RAIZ, 'data/callhunter/calls.jsonl'), encoding='utf8')]
primera = {}
for r in rows:
    if r['chain'] != 'solana': continue
    t = int(datetime.fromisoformat(r['created_at_utc'].replace('Z', '+00:00')).timestamp())
    primera[r['ca']] = min(t, primera.get(r['ca'], t))
for i, (ca, t0) in enumerate(sorted(primera.items())):
    f = os.path.join(CACHE, ca + '.json')
    if os.path.exists(f): continue
    out = {'pools': [], 'v': []}
    try:
        pools = (gecko.get(f'/networks/solana/tokens/{ca}/pools?page=1').get('data') or [])[:2]
        porminuto = {}
        for p in pools:
            out['pools'].append(p['relationships']['dex']['data']['id'])
            time.sleep(0.8)   # margen bajo el límite público para no comer esperas de 429
            for row in gecko.candles('solana', p['attributes']['address'], 'minute', 1, t0 + 970 * 60, 1000):   # -30 min .. +16 h
                if row[0] not in porminuto or row[5] > porminuto[row[0]][5]: porminuto[row[0]] = row
        out['v'] = [porminuto[k] for k in sorted(porminuto)]
        if pools:   # velas de 15 min del pool principal para la ventana de 24 h
            time.sleep(0.8)
            out['v15'] = gecko.candles('solana', pools[0]['attributes']['address'], 'minute', 15, t0 + 30 * 3600, 150)
    except Exception as e:
        out['error'] = str(e)
    json.dump(out, open(f, 'w'))
    if i % 20 == 0: print(i, len(primera), flush=True)
print('hecho', len(primera))

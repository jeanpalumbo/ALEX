import json, statistics as st, random
R = json.load(open('resultados_origen.json'))
random.seed(3)
def res(nombre, sub, k, coste=0.05):
    v = [r[k] * (1 - coste) - 1 for r in sub if r.get(k) is not None]
    if not v: print(f"{nombre:44s} sin datos"); return
    b = sorted(st.mean(random.choices(v, k=len(v))) for _ in range(2000))
    cap = st.mean([min(x, 4) for x in v])
    print(f"{nombre:44s} n={len(v):4d} media={st.mean(v)*100:+7.1f}% mediana={st.median(v)*100:+6.1f}% ganan={sum(x>0 for x in v)/len(v)*100:3.0f}% x2+={sum(x>=1 for x in v)/len(v)*100:3.0f}% techo5x={cap*100:+6.1f}% IC90=[{b[100]*100:+.0f}%,{b[1900]*100:+.0f}%]")
G7 = [r for r in R if r['grupo'] == 'G7']; B = [r for r in R if r['grupo'] == 'BASE']
print('G7 total', len(G7), 'con velas', sum(1 for r in G7 if r['n_velas']), '| BASE', len(B), 'con velas', sum(1 for r in B if r['n_velas']))
for e in ('e2', 'e5', 'e15'):
    print(f'--- entrada {e} (coste 5% ida+vuelta)')
    for h in ('1h', '6h', '16h'):
        res(f'G7 proyecto/narrativa {e} -> {h}', G7, f'{e}_{h}')
        res(f'BASE aleatoria       {e} -> {h}', B, f'{e}_{h}')
    res(f'G7 max en 1h (techo teórico) {e}', G7, f'{e}_max1h')
    res(f'BASE max en 1h (techo teórico) {e}', B, f'{e}_max1h')
print('--- BASE con link X vs sin')
res('BASE con X e5->1h', [r for r in B if r.get('twitter')], 'e5_1h')
res('BASE sin X e5->1h', [r for r in B if not r.get('twitter')], 'e5_1h')

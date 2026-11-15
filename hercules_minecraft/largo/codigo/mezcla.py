# Mezcla final: voz + música propia por capítulo (generada por código, sin copyright) con ducking bajo la voz + efectos sincronizados.
import json, numpy as np, soundfile as sf
SR = 48000; rng = np.random.default_rng(7)
B = json.load(open("bloques.json", encoding="utf-8")); PAL = json.load(open("palabras.json", encoding="utf-8"))
v, sr = sf.read("vo.wav", dtype="float32"); v = v if v.ndim == 1 else v.mean(1); N = len(v); DUR = N / SR
def xs(d): return np.arange(int(d * SR)) / SR
def sm(x, k): return np.convolve(x, np.ones(k) / k, "same")
def at(b, s, t, g=1.0):
    k = int(t * SR); e = min(N, k + len(s))
    if 0 <= k < e: b[k:e] += (s[:e - k] * g).astype(np.float32)
nz = lambda n: rng.standard_normal(n).astype(np.float32)
# ---------------- efectos
def paso(): x = xs(0.1); return (sm(nz(len(x)), 3) * 0.8 + np.sin(2 * np.pi * 120 * x) * 0.4) * np.exp(-x * 50)
def golpe(): x = xs(0.6); return (np.sin(2 * np.pi * 60 * x) * 1.2 + sm(nz(len(x)), 4)) * np.exp(-x * 8)
def corte(): x = xs(0.45); return (np.sin(2 * np.pi * 900 * np.exp(-x * 3) * x * 3) * 0.3 + (nz(len(x)) - sm(nz(len(x)), 3)) * 0.5) * np.exp(-x * 9)
def whoosh(d=0.35): x = xs(d); return sm(nz(len(x)), 8) * np.sin(np.pi * x / d) ** 2 * 1.2
def rugido(d=1.0): x = xs(d); f = 90 + 30 * np.sin(x * 11); b = np.sin(np.cumsum(2 * np.pi * f / SR)); return (np.sign(b) * np.abs(b) ** 0.5 * sm(np.abs(nz(len(x))), 20) * 3 + sm(nz(len(x)), 6) * 0.3) * np.minimum(1, x / 0.1) * np.exp(-np.maximum(0, x - 0.4) * 4) * 0.6
def siseo(d=1.2): x = xs(d); n = nz(len(x)); return (n - sm(n, 3)) * 0.35 * np.minimum(1, x / 0.2) * np.minimum(1, (d - x) / 0.3)
def pop(): x = xs(0.35); return (sm(nz(len(x)), 6) * 1.2 + np.sin(2 * np.pi * 180 * x * 8 * np.exp(-x * 6))) * np.exp(-x * 12)
def risa(): x = xs(1.0); f = 520 + 120 * np.sin(2 * np.pi * 7 * x); g = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 6.5 * x)); return np.sin(np.cumsum(2 * np.pi * f / SR)) * g * np.exp(-x * 1.5) * 0.4
def magia(): x = xs(1.2); f = 900 + 600 * np.sin(2 * np.pi * 3 * x); return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-x * 2.5) * 0.4
def rayo(): x = xs(1.2); return (sm(nz(len(x)), 2) * np.exp(-x * 3) + np.sin(2 * np.pi * 40 * x) * np.exp(-x * 2) * 0.8)
def boing(): x = xs(0.45); f = 220 + 160 * np.sin(2 * np.pi * 6 * x) * np.exp(-x * 4); return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-x * 5)
def tin(): x = xs(0.8); return (np.sin(2 * np.pi * 340 * x) + 0.6 * np.sin(2 * np.pi * 870 * x)) * np.exp(-x * 5) * 0.6
def agua_(d=3.0): x = xs(d); return sm(nz(len(x)), 20) * 1.5 * np.minimum(1, x / 0.5) * np.minimum(1, (d - x) / 0.5)
def flecha(): x = xs(0.3); n = nz(len(x)); return (n - sm(n, 4)) * np.sin(np.pi * x / 0.3) * 0.6
def piar(): x = xs(0.25); f = 2400 - 1600 * x; return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-x * 10) * 0.3
def fuego(d=2.0): x = xs(d); return sm(nz(len(x)), 10) * (0.6 + 0.4 * (rng.random(len(x)) > 0.995)) * np.minimum(1, x / 0.3) * np.minimum(1, (d - x) / 0.3) * 1.5
def campanas(): x = xs(1.6); return sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 2) for f in (880, 1108, 1318)) * 0.25
def piedra(): x = xs(1.0); return (sm(nz(len(x)), 30) * 2 + np.sin(2 * np.pi * 45 * x)) * np.exp(-x * 4)
def ladrido(): x = xs(0.5); f = 300 - 200 * x; return np.sign(np.sin(np.cumsum(2 * np.pi * f / SR))) * np.exp(-x * 8) * 0.4
FX = dict(paso=paso, golpe=golpe, corte=corte, whoosh=whoosh, rugido=rugido, siseo=siseo, pop=pop, risa=risa, magia=magia, rayo=rayo, boing=boing, tin=tin, agua=agua_, flecha=flecha, piar=piar, fuego=fuego, campanas=campanas, piedra=piedra, ladrido=ladrido)
# efectos por escena: (tiempo relativo al bloque, efecto, ganancia)
EV = {
 "hidra_frio": [(0.2, "siseo", .6), (1.6, "corte", .9), (2.3, "siseo", .7), (2.5, "pop", .6)], "hidra_frio2": [(0.3, "siseo", .5), (2.6, "boing", .5)],
 "tinaja_frio": [(0.4, "paso", .3), (0.9, "paso", .3), (1.4, "paso", .3), (1.9, "paso", .3), (4.0, "tin", .8), (4.4, "boing", .5)],
 "intro": [(0.2, "whoosh", .8), (0.6, "golpe", .8), (1.3, "campanas", .6)],
 "olimpo_zeus": [(2.5, "rayo", .7)], "zeus_disfraz": [(4.1, "magia", .6), (9.2, "boing", .4)], "olimpo_hera": [(1.7, "golpe", .3)],
 "hera_serpientes": [(1.0, "magia", .7), (1.4, "siseo", .5)], "bebe_serpientes": [(0.2, "siseo", .6), (1.1, "boing", .3), (2.2, "pop", .9), (2.34, "pop", .9), (2.5, "risa", .7)],
 "bebe_juega": [(0.3, "risa", .6), (2.0, "risa", .5)], "hera_rabia": [(0.5, "golpe", .3), (1.0, "golpe", .3)],
 "lino_lira": [(0.5, "tin", .3), (6.6, "golpe", .9), (6.7, "tin", .6)], "lino_chiste": [(0.1, "piedra", .4)],
 "quiron": [(5.0, "flecha", .6), (6.6, "flecha", .6), (8.2, "flecha", .6), (5.05, "golpe", .3)], "tebas_familia": [(0.5, "risa", .4)],
 "hera_locura": [(2.0, "magia", .8), (2.4, "rayo", .5)], "delfos": [(0.1, "fuego", .4)], "euristeo_presenta": [(2.2, "boing", .5)],
 "nemea_flechas": [(0.5, "rugido", .6), (0.75, "flecha", .6), (2.85, "flecha", .6), (4.95, "flecha", .6)], "nemea_cueva": [(1.0, "rugido", .8), (4.2, "golpe", .9), (4.6, "piedra", .5)],
 "nemea_piel": [(2.6, "tin", .5), (6.0, "corte", .5)], "nemea_casco": [(0.3, "campanas", .4)], "nemea_vuelta": [(0.5, "risa", .3)],
 "euristeo_miedo": [(2.2, "boing", .6), (2.5, "paso", .4), (2.7, "paso", .4)],
 "hidra_llega": [(3.0, "siseo", .8), (3.3, "rugido", .5)], "hidra_corta": [(0.8, "corte", .9), (2.2, "corte", .9), (3.6, "corte", .9), (1.2, "pop", .5), (2.6, "pop", .5), (4.0, "pop", .5)],
 "hidra_yolao": [(0.2, "fuego", .6), (0.6, "corte", .7), (2.2, "corte", .7), (3.8, "corte", .7), (5.4, "corte", .7)], "hidra_roca": [(1.4, "whoosh", .7), (2.5, "piedra", 1.0)],
 "cangrejo": [(3.0, "boing", .6), (3.6, "pop", .8), (6.2, "campanas", .5)], "cancer_chiste": [(1.0, "campanas", .3)],
 "cierva": [(0.2, "paso", .2), (0.6, "paso", .2), (4.5, "magia", .5)], "jabali": [(0.5, "rugido", .5), (2.0, "rugido", .4), (4.0, "golpe", .6)],
 "tinaja": [(4.2, "boing", .6), (4.9, "tin", .9)], "tinaja_chiste": [(0.4, "tin", .4)],
 "establos": [(1.0, "piar", .2), (3.0, "paso", .2)], "rios": [(2.6, "golpe", 1.0), (2.7, "piedra", .7), (3.0, "agua", 1.0)], "no_cuenta": [(0.5, "tin", .3)],
 "pajaros": [(4.6, "tin", .6), (5.0, "tin", .6), (5.4, "tin", .6), (5.0, "piar", .5), (5.5, "piar", .5), (8.6, "flecha", .6), (9.1, "flecha", .6), (9.6, "flecha", .6), (10.1, "flecha", .6)], "pajaros_chiste": [(0.2, "tin", .3)],
 "toro": [(0.2, "rugido", .5), (2.0, "golpe", .6), (6.0, "paso", .3)], "yeguas": [(0.5, "rugido", .4), (4.8, "golpe", 1.0), (8.0, "risa", .3)],
 "amazonas": [(4.0, "campanas", .3)], "amazonas_hera": [(5.5, "rugido", .4), (6.5, "golpe", .6), (7.0, "golpe", .6), (7.5, "golpe", .6)],
 "columnas": [(8.0, "piedra", 1.0)], "gerion": [(3.3, "golpe", .9), (3.5, "ladrido", .5)], "atlas": [(4.0, "rayo", .3)],
 "atlas_trato": [(4.0, "piedra", .5)], "atlas_cojin": [(5.0, "piedra", .5), (6.2, "risa", .4)],
 "inframundo": [(0.1, "fuego", .5), (1.0, "ladrido", .6), (1.5, "ladrido", .6), (2.0, "ladrido", .6)], "hades": [(0.1, "fuego", .4)],
 "cerbero": [(1.6, "golpe", .8), (1.8, "ladrido", .5)], "cerbero_tinaja": [(0.5, "ladrido", .7), (1.0, "ladrido", .7), (0.7, "tin", .6)],
 "camisa": [(6.5, "magia", .4), (9.0, "fuego", .6)], "pira": [(2.5, "fuego", .8), (4.0, "campanas", .7)], "hebe": [(4.0, "campanas", .8)],
 "final_chiste": [(4.5, "boing", .4)], "cierre": [(4.0, "pop", .6), (5.2, "campanas", .5)],
}
fx = np.zeros(N, np.float32)
for b in B:
    for (lt, k, g) in EV.get(b["esc"], []): at(fx, FX[k](), b["t0"] + lt, g)
    # cortes de plano: whoosh suave (mismo algoritmo que index.html)
    ws = [w["t"] for w in PAL if w["b"] == b["i"]]; cur = b["t0"]
    while b["t1"] - cur > 4.6:
        obj = cur + 3.0; cand = [w for w in ws if cur + 2.0 < w < cur + 4.4 and b["t1"] - w > 1.6]
        cur = (min(cand, key=lambda w: abs(w - obj)) - 0.08) if cand else obj; at(fx, whoosh(0.25), cur - 0.1, 0.12)
    at(fx, whoosh(0.4), b["t0"] - 0.15, 0.2)
# ---------------- música por capítulo: escala, tempo, instrumento y ánimo propios
ESTILOS = {  # raíz Hz, modo, bpm, timbre, ánimo
 0: (110.0, "menor", 132, "cuerdas", "tenso"), 1: (146.83, "mayor", 120, "metal", "epico"), 2: (130.81, "mayor", 108, "pizz", "juguete"),
 3: (123.47, "menor", 96, "cuerdas", "triste"), 4: (110.0, "menor", 120, "metal", "epico"), 5: (98.0, "menor", 126, "cuerdas", "tenso"),
 6: (146.83, "mayor", 116, "pizz", "juguete"), 7: (130.81, "mayor", 112, "pizz", "juguete"), 8: (110.0, "menor", 118, "metal", "epico"),
 9: (138.59, "mayor", 110, "cuerdas", "epico"), 10: (123.47, "mayor", 104, "pizz", "juguete"), 11: (87.31, "menor", 100, "cuerdas", "tenso"), 12: (146.83, "mayor", 92, "metal", "triste")}
ESC = {"mayor": [0, 2, 4, 5, 7, 9, 11, 12], "menor": [0, 2, 3, 5, 7, 8, 10, 12]}
def nota(buf, f, d, g, t0, tim):
    x = xs(d)
    if tim == "pizz": s = (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(4 * np.pi * f * x)) * np.exp(-x * 9)
    elif tim == "metal": s = (np.sign(np.sin(2 * np.pi * f * x)) * 0.25 + np.sin(2 * np.pi * f * x) * 0.7 + 0.3 * np.sin(6 * np.pi * f * x)) * np.minimum(1, x / 0.03) * np.exp(-x * 2.5)
    else: s = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(4 * np.pi * f * x) + 0.25 * np.sin(6 * np.pi * f * x)) * np.minimum(1, x / 0.08) * np.exp(-x * 1.6)
    at(buf, s * g, t0)
mus = np.zeros(N, np.float32)
caps = sorted({b["cap"] for b in B})
for c in caps:
    bs = [b for b in B if b["cap"] == c]; a, z = bs[0]["t0"], bs[-1]["t1"] + 0.6; r, modo, bpm, tim, an = ESTILOS[c]; esc = ESC[modo]; beat = 60 / bpm
    prog = [0, 5, 3, 4] if modo == "mayor" else [0, 5, 3, 6]
    seg = np.zeros(N, np.float32)
    for j, t0 in enumerate(np.arange(a, z, beat / 2)):            # ostinato / arpegio
        grado = prog[(j // 8) % 4]; paso_ = [0, 2, 4, 2, 0, 4, 2, 4][j % 8]; e = esc[(grado + paso_) % 7] + 12 * ((grado + paso_) // 7)
        if an == "triste" and j % 2: continue
        nota(seg, r * 2 * 2 ** (e / 12), 0.35, 0.10 if tim != "metal" else 0.07, t0, tim)
    for j, t0 in enumerate(np.arange(a, z, beat * 2)):            # bajo
        grado = prog[(j // 2) % 4]; nota(seg, r / 2 * 2 ** (esc[grado % 7] / 12), beat * 2.2, 0.32, t0, "cuerdas")
    if an in ("epico", "tenso"):
        for t0 in np.arange(a, z, beat): x = xs(0.4); at(seg, np.sin(2 * np.pi * 55 * x * np.exp(-x * 2)) * np.exp(-x * 7) * (0.5 if an == "epico" else 0.3), t0)
    tt = np.arange(N) / SR; env = np.clip((tt - a) / 0.8, 0, 1) * np.clip((z - tt) / 0.8, 0, 1)
    mus += seg * env
# ---------------- niveles: música a -20 dB bajo la voz con ducking, efectos a ~-9 dB
rms = lambda a: float(np.sqrt(np.mean(a.astype(np.float64) ** 2)) + 1e-12)
vr = rms(v[np.abs(v) > 0.02]); mus *= vr * 10 ** (-20 / 20) / rms(mus)
e = sm(np.abs(v), SR // 8); duck = 1 - 0.45 * np.clip(e / (np.percentile(e, 95) * 0.5 + 1e-9), 0, 1)
mus *= (0.6 + 0.4 * duck) * 1.4                                     # sin voz la música sube; con voz baja
fx *= vr * 10 ** (-9 / 20) / (np.percentile(np.abs(fx[np.abs(fx) > 1e-4]), 99.5) + 1e-9)
mix = v + mus + fx
pk = np.abs(mix).max(); mix = np.tanh(mix / pk * 1.2) / np.tanh(1.2) * 0.95 if pk > 0.98 else mix
sf.write("mezcla.wav", mix.astype(np.float32), SR)
print("ok mezcla.wav", round(DUR, 1), "s; música", round(20 * np.log10(rms(mus) / vr), 1), "dB bajo voz; pico", round(float(np.abs(mix).max()), 3))

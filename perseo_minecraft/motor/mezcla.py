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
def aleteo(): return np.concatenate([whoosh(0.15) * 0.8 for _ in range(6)])
def crujido(): x = xs(1.6); n = nz(len(x)); cr = (rng.random(len(x)) > 0.997).astype(np.float32); return (sm(cr * 6, 40) * n * 0.8 + sm(n, 40) * 1.5 + np.sin(2 * np.pi * 50 * x) * 0.5) * np.minimum(1, x / 0.05) * np.exp(-x * 1.8)
def olas(d=4.0): x = xs(d); return sm(nz(len(x)), 60) * 3 * (0.5 + 0.5 * np.sin(2 * np.pi * x / 2.6) ** 2) * np.minimum(1, x / 0.6) * np.minimum(1, (d - x) / 0.6)
def viento(d=4.0): x = xs(d); return sm(nz(len(x)), 120) * 6 * (0.6 + 0.4 * np.sin(2 * np.pi * x * 0.3)) * np.minimum(1, x / 0.8) * np.minimum(1, (d - x) / 0.8)
def trueno(): x = xs(2.5); return (sm(nz(len(x)), 50) * 4 * (0.4 + 0.6 * np.exp(-x * 1.5)) + sm(nz(len(x)), 3) * np.exp(-x * 12)) * np.minimum(1, x / 0.02)
def grito(): x = xs(0.8); f = 700 + 300 * np.sin(2 * np.pi * 9 * x); return np.sign(np.sin(np.cumsum(2 * np.pi * f / SR))) * 0.25 * np.exp(-x * 2)
FX.update(aleteo=aleteo, crujido=crujido, olas=olas, viento=viento, trueno=trueno, grito=grito)
# efectos por escena: (tiempo relativo al bloque o palabra, efecto, ganancia)
EV = {
 "gancho_cueva": [(0.3, "siseo", .5), (2.5, "siseo", .5), (4.0, "crujido", .5)], "gancho_mirada": [(0.3, "crujido", .7), (2.0, "siseo", .6)],
 "gancho_escudo": [("cortarle", "corte", .7), ("espejo", "tin", .8), (1.0, "siseo", .5)], "gancho_casco": [("invisible", "magia", .7), ("lío", "boing", .5)],
 "intro": [(0.2, "whoosh", .8), (0.6, "golpe", .8), (1.3, "campanas", .6), (0.4, "aleteo", .6)],
 "argos": [(0.3, "campanas", .3)], "oraculo": [(0.1, "fuego", .5), ("matar", "golpe", .7)], "oraculo_chiste": [(0.3, "boing", .4)],
 "danae_plan": [("Fácil", "pop", .4)], "torre": [(0.3, "golpe", .6), ("perfecto", "tin", .5)], "torre_dentro": [("Zeus", "rayo", .6)],
 "lluvia_oro": [(0.3, "magia", .8), (1.5, "tin", .4), (2.5, "tin", .4)], "nace_perseo": [("bebé", "risa", .4), ("profecía", "trueno", .6)],
 "acrisio_panico": [("corona", "tin", .6), ("corona", "boing", .4)], "cofre_mete": [("cofre", "golpe", .6), ("mar", "agua", .8)],
 "cofre_mar": [(0.0, "trueno", .8), (0.0, "olas", .9), (2.5, "olas", .9)], "zeus_vigila": [(0.5, "rayo", .4)],
 "dictis_red": [(0.0, "olas", .5), ("abrió", "golpe", .4), ("bebé", "risa", .3)], "crece": [(0.0, "olas", .4), ("chulito", "boing", .4)],
 "estorbo": [("perro", "ladrido", .4)], "plan_banquete": [(0.2, "campanas", .3)], "sin_caballo": [("oveja", "boing", .4)],
 "frase": [("Medusa", "trueno", .8)], "silencio": [("sonrió", "risa", .3)], "tarde": [("tarde", "boing", .5)],
 "gorgonas": [(0.0, "trueno", .5), (1.0, "siseo", .6), (4.0, "siseo", .5)], "castigo": [("Atenea", "rayo", .5)],
 "transforma": [(1.0, "magia", .9), (1.4, "siseo", .8)], "petrifica": [(1.6, "crujido", 1.0), (0.2, "siseo", .5)],
 "perseo_fatal": [(0.0, "olas", .4), ("fatal", "boing", .3)], "dioses_llegan": [(0.5, "magia", .7), (1.5, "rayo", .3)],
 "regalos": [("escudo", "tin", .8), ("espada", "corte", .6)], "inventario1": [("sandalias", "pop", .5), ("casco", "pop", .5), ("bolsa", "pop", .5)],
 "ninfas_dir": [("nadie", "boing", .4)], "greas": [(0.0, "viento", .7), (5.0, "viento", .6)], "greas_pelea": [(0.3, "grito", .4), (2.0, "grito", .4)],
 "ojo_robo": [("zas", "whoosh", 1.0), ("zas", "pop", .7)], "greas_ciegas": [(0.0, "viento", .5), (1.0, "boing", .3)],
 "ninfas": [(0.0, "piar", .3), (1.0, "agua", .4), ("sandalias", "magia", .6)],
 "vuelo_arbol": [("salto", "aleteo", .8), ("Directo", "golpe", 1.0), ("Directo", "boing", .5)], "vuelo_nubes": [(0.0, "viento", .7), (0.2, "aleteo", .6), (3.5, "aleteo", .6)],
 "isla": [(0.0, "trueno", .5), (0.5, "aleteo", .5)], "estatuas": [(0.5, "viento", .5), (3.0, "crujido", .3)],
 "casco_invisible": [("invisible", "magia", .8), (0.3, "siseo", .4)], "reflejo": [("escudo", "tin", .7), (1.0, "siseo", .5)],
 "atras": [(1.0, "paso", .4), (2.2, "paso", .4), (3.4, "paso", .4), ("ojo", "siseo", .9)], "corte": [("cayó", "whoosh", .9), ("golpe", "corte", 1.0), ("golpe", "golpe", .8)],
 "bolsa": [("bolsa", "pop", .5), ("criaturas", "magia", .6)], "pegaso": [("Pegaso", "aleteo", .9), ("Crisaor", "golpe", .5)],
 "hermanas": [(0.3, "grito", .6), (0.6, "siseo", .7), (3.0, "aleteo", .5)], "huida": [(0.0, "trueno", .4), (0.3, "aleteo", .7), (2.5, "aleteo", .6), (0.0, "olas", .6)],
 "arma": [(0.0, "viento", .6), (2.0, "magia", .5), (6.0, "crujido", .5)],
 "atlas": [(0.0, "viento", .4), (2.0, "golpe", .3)], "atlas_largo": [("largara", "rugido", .5)], "atlas_piedra": [("sacó", "magia", .7), ("piedra", "crujido", 1.0), ("montaña", "piedra", .9)],
 "atlas_chiste": [("favor", "boing", .4)], "andromeda": [(0.0, "olas", .7), (0.5, "aleteo", .6)], "casiopea": [("guapa", "tin", .3)],
 "poseidon": [(0.0, "olas", .8), ("monstruo", "rugido", .8)], "trato_boda": [(0.0, "olas", .5), ("Hecho", "campanas", .5)],
 "ceto": [(0.0, "agua", 1.0), (0.3, "rugido", 1.0)],
 "combate": [(0.0, "olas", .6), (0.3, "aleteo", .6), (1.2, "rugido", .6), (1.8, "whoosh", .7), (2.0, "corte", .9), (3.2, "whoosh", .7), (3.4, "golpe", .9), (4.4, "corte", .9), (5.4, "rugido", .8), (6.4, "agua", .9)],
 "boda": [(0.3, "campanas", .5), ("ejército", "paso", .4)], "boda_cabeza": [("gritó", "grito", .4), ("sacó", "magia", .6), (4.3, "crujido", 1.0)],
 "boda_chiste": [(0.2, "crujido", .4)], "vuelta": [(0.0, "olas", .4), (1.0, "aleteo", .5)], "banquete2": [("rio", "risa", .5)],
 "pues_si": [(0.3, "magia", .7)], "corte_piedra": [(0.0, "crujido", 1.0), ("Literalmente", "boing", .4)],
 "dictis_rey": [("rey", "campanas", .6)], "devuelve": [(1.0, "pop", .4), (2.0, "pop", .4), (3.0, "pop", .4), ("Atenea", "magia", .5)],
 "huye_abuelo": [(0.5, "paso", .4), (0.8, "paso", .4), (1.1, "paso", .4)], "juegos": [(0.5, "campanas", .4)],
 "disco": [("lanzó", "whoosh", .9), ("ráfaga", "viento", .7)], "disco_golpe": [("cabeza", "golpe", 1.0), ("cabeza", "tin", .5)],
 "destino": [(0.3, "trueno", .4)], "constelaciones": [("cielo", "magia", .6)], "estrellas": [(1.0, "tin", .3), (3.0, "tin", .3)],
 "casiopea_abajo": [("abajo", "boing", .5)], "cierre": [(4.0, "pop", .6), (5.2, "campanas", .5)],
}
def tev(b, k):
    if not isinstance(k, str): return k
    n = k.lower(); ws = [w for w in PAL if w["b"] == b["i"] and w["w"].lower().strip("¡!¿?.,…:;\"'").startswith(n.lower())]
    return (ws[0]["t"] - b["t0"]) if ws else None
fx = np.zeros(N, np.float32)
for b in B:
    for (lt, k, g) in EV.get(b["esc"], []):
        r = tev(b, lt)
        if r is None: print("aviso: palabra no encontrada", b["esc"], lt); continue
        at(fx, FX[k](), b["t0"] + r, g)
    # cortes de plano: whoosh suave (mismo algoritmo que index.html)
    ws = [w["t"] for w in PAL if w["b"] == b["i"]]; cur = b["t0"]
    while b["t1"] - cur > 4.6:
        obj = cur + 3.0; cand = [w for w in ws if cur + 2.0 < w < cur + 4.4 and b["t1"] - w > 1.6]
        cur = (min(cand, key=lambda w: abs(w - obj)) - 0.08) if cand else obj; at(fx, whoosh(0.25), cur - 0.1, 0.12)
    at(fx, whoosh(0.4), b["t0"] - 0.15, 0.2)
# ---------------- música por capítulo: escala, tempo, instrumento y ánimo propios
ESTILOS = {  # raíz Hz, modo, bpm, timbre, ánimo (0 gancho, 1 intro, 2-14 capítulos, 15 cierre)
 0: (110.0, "menor", 132, "cuerdas", "tenso"), 1: (146.83, "mayor", 120, "metal", "epico"), 2: (130.81, "mayor", 108, "pizz", "juguete"),
 3: (123.47, "menor", 96, "cuerdas", "triste"), 4: (138.59, "mayor", 112, "pizz", "juguete"), 5: (98.0, "menor", 120, "cuerdas", "tenso"),
 6: (146.83, "mayor", 116, "metal", "epico"), 7: (116.54, "menor", 104, "pizz", "juguete"), 8: (130.81, "mayor", 118, "pizz", "juguete"),
 9: (103.83, "menor", 126, "cuerdas", "tenso"), 10: (110.0, "menor", 132, "metal", "epico"), 11: (123.47, "mayor", 100, "pizz", "juguete"),
 12: (98.0, "menor", 128, "metal", "epico"), 13: (146.83, "mayor", 112, "metal", "epico"), 14: (87.31, "menor", 96, "cuerdas", "triste"),
 15: (130.81, "mayor", 88, "cuerdas", "triste")}
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

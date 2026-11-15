# Banda sonora completa generada por código (música propia por capítulo + efectos + ambiente) y mezcla con la voz de Jorge.
import json, subprocess, numpy as np, soundfile as sf
SR = 48000
L = json.load(open("linea.json", encoding="utf-8")); DUR = L["dur"] + 0.5; N = int(DUR * SR)
rng = np.random.default_rng(7)
def xs(d): return np.arange(int(d * SR)) / SR
def sm(x, k):
    k = int(k)
    if k <= 1: return x
    c = np.cumsum(np.concatenate([[0.0], x])); y = (c[k:] - c[:-k]) / k
    a = (len(x) - len(y)) // 2; return np.concatenate([np.full(a, y[0]), y, np.full(len(x) - len(y) - a, y[-1])])
def at(b, s, t, g=1.0):
    k = int(t * SR); e = min(len(b), k + len(s))
    if 0 <= k < e: b[k:e] += (s[:e - k] * g).astype(np.float32)
from scipy.signal import lfilter
def lp(x, a): return lfilter([a], [1, a - 1], x).astype(np.float32)   # paso bajo de un polo
noise = lambda d: rng.standard_normal(int(d * SR))

# ------------------------------------------------------------------ voz
voz = np.zeros(N, np.float32)
for a in L["audio"]:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"voz/{a['id']}.mp3", "-ar", str(SR), "-ac", "1", "/tmp/v.wav"], check=True)
    v, _ = sf.read("/tmp/v.wav", dtype="float32"); at(voz, v, a["t"])
vact = np.abs(voz) > 0.015
env = sm(vact.astype(np.float32), int(0.25 * SR)); env = np.clip(env * 3, 0, 1)   # 1 = hay voz

# ------------------------------------------------------------------ instrumentos
def nota(buf, f, d, g, t0, timbre="cuerda", at_=0.02):
    x = xs(d)
    if timbre == "cuerda": s = (np.sin(2*np.pi*f*x) + 0.5*np.sin(2*np.pi*2*f*x) + 0.25*np.sin(2*np.pi*3*f*x)) * np.minimum(1, x/at_) * np.exp(-x*2.2)
    elif timbre == "pulso": s = sum(np.sin(2*np.pi*f*k*x) * np.exp(-x*(2 + k*1.6)) / k for k in range(1, 7)) * np.minimum(1, x/0.004)   # arpa/laúd
    elif timbre == "pad": s = (np.sin(2*np.pi*f*x) + 0.35*np.sin(2*np.pi*2.005*f*x) + 0.2*np.sin(2*np.pi*0.997*f*x*3)) * np.minimum(1, x/0.35) * np.minimum(1, (d - x)/0.4)
    elif timbre == "flauta": s = (np.sin(2*np.pi*f*x + 0.1*np.sin(2*np.pi*5*x)) + 0.12*np.sin(2*np.pi*2*f*x)) * np.minimum(1, x/0.06) * np.minimum(1, (d - x)/0.08)
    elif timbre == "metal": s = (np.sin(2*np.pi*f*x) + 0.6*np.sin(2*np.pi*2.76*f*x) + 0.3*np.sin(2*np.pi*5.4*f*x)) * np.exp(-x*3) * np.minimum(1, x/0.002)
    at(buf, s * g, t0)
def timbal(buf, t0, g=0.6, f=55):
    x = xs(0.6); at(buf, np.sin(2*np.pi*f*x*np.exp(-x*2)) * np.exp(-x*6) * g, t0)
def tambor(buf, t0, g=0.3):
    x = xs(0.18); at(buf, (sm(rng.standard_normal(len(x)), 3)*0.6 + np.sin(2*np.pi*180*x)) * np.exp(-x*28) * g, t0)
def latido(buf, t0, g=0.6):
    for dt, gg in [(0, 1), (0.22, 0.7)]: x = xs(0.25); at(buf, np.sin(2*np.pi*48*x) * np.exp(-x*16) * g * gg, t0 + dt)

MOD = {  # tónica, escala de acordes (semitonos sobre la tónica), tempo, estilo
  "epico":   (146.83, [(0, 3, 7), (-4, 0, 3), (-2, 2, 5), (-5, -1, 2)], 100, "epico"),
  "comico":  (196.00, [(0, 4, 7), (5, 9, 12), (7, 11, 14), (0, 4, 7)], 118, "comico"),
  "tension": (110.00, [(0, 3, 7), (1, 4, 8), (0, 3, 7), (-1, 3, 6)], 72, "tension"),
  "intriga": (130.81, [(0, 3, 7), (-4, 0, 3), (5, 8, 12), (-5, -2, 2)], 92, "intriga"),
  "mar":     (164.81, [(0, 4, 7), (-3, 0, 4), (5, 9, 12), (7, 11, 14)], 96, "mar"),
  "amor":    (174.61, [(0, 4, 7), (-3, 0, 4), (5, 9, 12), (7, 11, 14)], 80, "amor"),
  "triste":  (130.81, [(0, 3, 7), (-4, 0, 3), (5, 8, 12), (-5, -1, 2)], 64, "triste"),
  "triunfo": (196.00, [(0, 4, 7), (5, 9, 12), (-3, 0, 4), (7, 11, 14)], 108, "epico"),
}
ST = 2 ** (1 / 12)
def pista(estilo, t0, t1):
    tonica, acordes, bpm, sty = MOD[estilo]; b = 60 / bpm; m = np.zeros(int((t1 - t0 + 2) * SR) + 1, np.float32)
    nb = int((t1 - t0) / b) + 1
    for j in range(nb):
        t = j * b; ac = acordes[(j // 8) % 4]; fr = [tonica * ST ** s for s in ac]
        if j % 8 == 0: [nota(m, f / 2, b * 8.2, 0.10 if sty != "tension" else 0.14, t, "pad") for f in fr]
        if sty == "epico":
            for h in range(2): nota(m, fr[(j * 2 + h) % 3] * (2 if (j * 2 + h) % 4 == 3 else 1), b * 0.6, 0.16, t + h * b / 2)
            nota(m, fr[0] / 4, b * 1.1, 0.32, t, at_=0.05)
            if j % 2 == 0: timbal(m, t, 0.45)
            if j % 4 == 3: tambor(m, t + b / 2, 0.25)
        elif sty == "comico":
            nota(m, fr[j % 3] * 2, b * 0.5, 0.18, t, "pulso"); nota(m, fr[(j + 1) % 3] * 2, b * 0.4, 0.12, t + b / 2, "pulso")
            nota(m, fr[0] / 2 if j % 2 == 0 else fr[2] / 2, b * 0.45, 0.28, t, "pulso")
            if j % 2 == 1: tambor(m, t, 0.18)
            if j % 16 in (6, 7): nota(m, fr[2] * 4, b * 0.4, 0.06, t + b / 2, "metal")
        elif sty == "tension":
            if j % 4 == 0: latido(m, t, 0.55)
            if j % 8 == 4: nota(m, fr[1] * 4, b * 2, 0.05, t, "metal")
            nota(m, tonica / 4, b * 1.05, 0.18, t, "pad")
        elif sty == "intriga":
            nota(m, fr[j % 3] * 2, b * 0.35, 0.14, t, "pulso");
            if j % 2 == 0: nota(m, fr[0] / 2, b * 0.9, 0.22, t, "cuerda", 0.05)
            if j % 4 == 2: tambor(m, t, 0.12)
        elif sty == "mar":
            for h in range(3): nota(m, fr[h] * 2, b * 0.9, 0.12, t + h * b / 3, "pulso")
            if j % 2 == 0: nota(m, fr[0] / 2, b * 2, 0.24, t, "cuerda", 0.08)
            if j % 4 == 0: nota(m, fr[2] * 2, b * 1.8, 0.08, t, "flauta")
        elif sty == "amor":
            nota(m, fr[j % 3] * 2, b * 1.2, 0.13, t, "pulso"); nota(m, fr[(j + 2) % 3] * 4, b * 0.9, 0.06, t + b / 2, "pulso")
            if j % 4 == 0: nota(m, fr[0] * 2, b * 3.6, 0.08, t, "flauta")
        elif sty == "triste":
            if j % 2 == 0: nota(m, fr[j // 2 % 3] * 2, b * 1.8, 0.14, t, "pulso")
            if j % 4 == 0: nota(m, fr[0], b * 3.8, 0.07, t, "flauta")
    m *= np.clip((np.arange(len(m)) / SR) / 0.8, 0, 1) * np.clip((t1 - t0 + 1.2 - np.arange(len(m)) / SR) / 1.2, 0, 1)
    return m
# capítulos -> estilo
EST = {"gancho": "tension", "c1": "comico", "c2": "comico", "c3": "intriga", "c4": "intriga", "c5": "epico", "c6": "triste", "c7": "amor", "c8": "tension", "c9": "mar", "c10": "triste", "cierre": "triunfo"}
mus = np.zeros(N, np.float32)
ini = {a["id"]: a["t"] for a in L["audio"]}; cap_t = {c["n"]: c["t"] for c in L["caps"]}
orden = [a["id"] for a in L["audio"]]
starts = []
for k, bid in enumerate(orden):
    t0 = ini[bid] - (1.3 if bid.startswith("c") and bid != "cierre" else 0.3); t1 = ini[orden[k + 1]] - 1.3 if k + 1 < len(orden) else DUR
    if bid == "gancho": t0 = 0
    starts.append((bid, t0, t1))
# pelea del laberinto: épico en vez de tensión a partir del Minotauro
for bid, t0, t1 in starts:
    if bid == "c8":
        tm = next(p["s0"] for p in L["planos"] if p["tx"].startswith("¡El Minotauro"))
        at(mus, pista("tension", t0, tm), t0); at(mus, pista("epico", tm, t1), tm)
    else: at(mus, pista(EST[bid], t0, t1 + 0.6), t0)
# golpe del título: acorde + timbales
tt = next(p["s0"] for p in L["planos"] if p.get("ov") == "titulo")
for f in (73.42, 146.83, 220.0, 293.66): nota(mus, f, 3.8, 0.22, tt, "cuerda", 0.01)
for k in range(6): timbal(mus, tt - 0.6 + k * 0.1, 0.25 + k * 0.08)
timbal(mus, tt, 1.0, 45)
# silencios dramáticos
for p in L["planos"]:
    if p.get("silencio"): a, b = int(p["s0"] * SR), int(p["s1"] * SR); mus[a:b] *= np.linspace(1, 0.05, b - a) ** 0.3
# ------------------------------------------------------------------ efectos
fx = np.zeros(N, np.float32)
def paso(): x = xs(0.1); return (sm(noise(0.1), 3) * 0.8 + np.sin(2*np.pi*120*x) * 0.4) * np.exp(-x*50)
def whoosh(d=0.35): x = xs(d); return sm(noise(d), 8) * np.sin(np.pi*x/d) ** 2 * 1.2
def golpe(): x = xs(0.5); return (np.sin(2*np.pi*70*x*np.exp(-x*3)) * 1.3 + sm(noise(0.5), 3) * 0.8) * np.exp(-x*12)
def clang(): x = xs(0.8); return (np.sin(2*np.pi*1200*x) + 0.7*np.sin(2*np.pi*1850*x) + 0.4*np.sin(2*np.pi*2900*x)) * np.exp(-x*7) * 0.5 + sm(noise(0.8), 2) * np.exp(-x*40) * 0.6
def rugido(d=1.4): x = xs(d); f = 80 + 35*np.sin(x*9); bb = np.sin(np.cumsum(2*np.pi*f/SR)); return (np.sign(bb)*np.abs(bb)**0.5 * sm(np.abs(noise(d)), 20) * 3 + sm(noise(d), 6)*0.4) * np.minimum(1, x/0.1) * np.exp(-np.maximum(0, x - d*0.5)*4) * 0.7
def resoplido(): x = xs(0.9); return sm(noise(0.9), 14) * np.sin(np.pi*x/0.9) ** 3 * 2.2
def chapoteo(): x = xs(1.4); return (sm(noise(1.4), 4) * np.exp(-x*3) * 1.4 + np.sin(2*np.pi*90*x*np.exp(-x*4)) * np.exp(-x*10))
def magia(): x = xs(1.4); f = 900 + 600*np.sin(2*np.pi*3*x); return np.sin(np.cumsum(2*np.pi*f/SR)) * np.exp(-x*2.5) * 0.4 + sm(noise(1.4), 2)*0.05*np.exp(-x*3)
def pop(): x = xs(0.25); return np.sin(2*np.pi*(600 + 900*x)*x) * np.exp(-x*20) * 0.8
def corazon(): x = xs(0.5); return (np.sin(2*np.pi*880*x) + np.sin(2*np.pi*1320*x)*0.6) * np.exp(-x*7) * 0.35
def piedra(d=1.2): x = xs(d); return sm(noise(d), 30) * 3 * (0.6 + 0.4*np.sin(2*np.pi*13*x)) * np.minimum(1, x/0.1) * np.minimum(1, (d - x)/0.2)
def derrumbe(): x = xs(1.2); return (sm(noise(1.2), 6) * 1.5 + np.sin(2*np.pi*50*x)) * np.exp(-x*3.5)
def trueno(): x = xs(2.5); return sm(noise(2.5), 40) * 4 * np.exp(-x*1.4) * np.minimum(1, x/0.02)
def grito(): x = xs(1.0); f = 500 + 300*np.exp(-x*2); return np.sin(np.cumsum(2*np.pi*f/SR)) * np.sign(np.sin(np.cumsum(2*np.pi*f*1.01/SR))) * 0.2 * np.exp(-x*1.5) * np.minimum(1, x/0.05)
def vitores(d=1.8): x = xs(d); return sm(noise(d), 5) * 0.7 * np.minimum(1, x/0.3) * np.minimum(1, (d - x)/0.6) * (0.7 + 0.3*np.sin(2*np.pi*3*x))
def brillo(): x = xs(0.9); return sum(np.sin(2*np.pi*f*x) * np.exp(-x*5) for f in (2093, 2637, 3136)) * 0.15
def cristal(): x = xs(0.6); return (np.sin(2*np.pi*2400*x) + np.sin(2*np.pi*3700*x)) * np.exp(-x*9) * 0.3 + sm(noise(0.6), 2) * np.exp(-x*25) * 0.4
def disco(): x = xs(0.5); return np.sin(2*np.pi*(1400 - 1200*x)*x) * 0.4 * np.exp(-x*3)   # sonido cómico de "piiiu"
def muelle(): x = xs(0.7); return np.sin(2*np.pi*(220 + 160*np.sin(2*np.pi*14*x))*x) * np.exp(-x*4) * 0.5
FX = {"golpe": golpe, "temblor": derrumbe, "rugido": rugido, "resoplido": resoplido, "salpicar_mar": chapoteo, "chispas_moradas": magia, "chispas_doradas": magia, "corazones": corazon,
      "puerta": lambda: piedra(1.0), "muro": derrumbe, "trueno": trueno, "brillo": brillo, "flash": derrumbe, "bloques": derrumbe, "polvo": derrumbe, "hojas": whoosh, "copa_vuela": whoosh, "veneno_suelo": cristal, "estrellas": muelle, "vapor": resoplido, "humo_tripode": None, "zoom": disco, "veneno": None, "rayos": brillo, "zzz": None}
GAN = {"golpe": 0.9, "temblor": 0.6, "rugido": 0.9, "resoplido": 0.7, "salpicar_mar": 0.8, "corazones": 0.6, "trueno": 0.8, "flash": 0.9, "bloques": 0.8, "polvo": 0.35, "muro": 0.9, "zoom": 0.5, "estrellas": 0.5, "brillo": 0.6}
hecho = set()
for p in L["planos"]:
    for nm, ta in p["fxa"]:
        k = (nm, round(ta, 2))
        if k in hecho: continue
        hecho.add(k); f = FX.get(nm)
        if f: at(fx, f(), ta, GAN.get(nm, 0.6))
# acciones -> sonidos
for p in L["planos"]:
    if p.get("sub"): continue
    d = p["s1"] - p["s0"]
    for a in p["act"]:
        acc = a["acc"]
        if acc in ("andar", "correr", "embestir", "agachado") and a.get("to"):
            per = {"andar": 0.32, "correr": 0.2, "embestir": 0.18, "agachado": 0.45}[acc]
            for t in np.arange(p["s0"] + 0.05, p["s0"] + d * 0.92, per): at(fx, paso(), t, 0.22 if acc != "embestir" else 0.6)
        if acc == "golpe": at(fx, whoosh(0.25), p["s0"] + d * 0.25, 0.4)
        if acc == "maza_golpe": at(fx, whoosh(0.3), p["s0"] + d * 0.35, 0.5); at(fx, golpe(), p["s0"] + d * 0.45, 0.9)
        if acc == "patada": at(fx, whoosh(0.25), p["s0"] + d * 0.35, 0.5); at(fx, golpe(), p["s0"] + d * 0.42, 0.6)
        if acc == "espadazo": [at(fx, clang(), p["s0"] + 0.31 + k * 0.62, 0.55) for k in range(int(d / 0.62))]
        if acc == "lanzado": at(fx, whoosh(0.6), p["s0"] + 0.05, 0.6); at(fx, grito(), p["s0"] + 0.1, 0.5)
        if acc == "caer_acantilado": at(fx, whoosh(0.8), p["s0"] + d * 0.38, 0.6)
        if acc in ("caer", "caer_grande", "desmayo"): at(fx, golpe(), p["s0"] + d * {"caer": 0.55, "caer_grande": 0.43, "desmayo": 0.63}[acc], 0.7)
        if acc == "celebrar" and a["n"].startswith(("aldeano", "joven")): at(fx, vitores(min(2.2, d)), p["s0"] + 0.1, 0.35)
        if acc == "levantar": at(fx, piedra(0.8), p["s0"] + d * 0.3, 0.6)
        if acc == "sacar_espada": at(fx, clang(), p["s0"] + d * 0.38, 0.4)
        if acc == "aparecer": at(fx, magia(), p["s0"], 0.6)
        if acc == "volar_carro": at(fx, magia(), p["s0"] + 0.2, 0.5); at(fx, whoosh(1.0), p["s0"] + d * 0.4, 0.5)
        if a.get("ico") in ("!", "?"): at(fx, pop(), p["s0"] + 0.15, 0.5)
        if acc == "rugir": at(fx, rugido(), p["s0"] + d * 0.06, 0.8)
    if p.get("ov") == "spoiler": at(fx, golpe(), p["s0"] + 0.45, 0.6); at(fx, disco(), p["s0"] + 0.5, 0.5)
    if p.get("pinos") == "soltar": at(fx, muelle(), p["s0"] + d * 0.15, 0.8)
    if p.get("barco_mueve"): at(fx, whoosh(1.2), p["s0"] + d * 0.4, 0.2)
# woosh suave en algunos cortes de cámara + tarjetas de capítulo
for c in L["caps"]: at(fx, whoosh(0.4), c["t"], 0.5); at(fx, pop(), c["t"] + 0.32, 0.3)
for p in L["planos"][1::3]: at(fx, whoosh(0.25), max(0, p["t0"] - 0.1), 0.12)
# ------------------------------------------------------------------ ambiente por escenario
amb = np.zeros(N, np.float32)
def olas(d): x = xs(d); return lp(noise(d).astype(np.float32), 0.02) * 6 * (0.6 + 0.4*np.sin(2*np.pi*0.13*x))
def viento(d): x = xs(d); return lp(noise(d).astype(np.float32), 0.008) * 10 * (0.5 + 0.5*np.sin(2*np.pi*0.07*x + 1))
def pajaros(d):
    b = np.zeros(int(d * SR), np.float32)
    for t in np.arange(0, d - 0.5, 0.9):
        if rng.random() < 0.55:
            x = xs(0.18); f0 = 2600 + rng.random()*1400; s = np.sin(np.cumsum(2*np.pi*(f0 + 800*np.sin(2*np.pi*18*x))/SR)) * np.sin(np.pi*x/0.18) * 0.12; at(b, s, t + rng.random()*0.4)
    return b
def grillos(d): x = xs(d); return np.sin(2*np.pi*4300*x) * (np.sin(2*np.pi*28*x) > 0.6) * (np.sin(2*np.pi*0.7*x) > -0.2) * 0.04
def gotas(d):
    b = np.zeros(int(d * SR), np.float32)
    for t in np.arange(0, d - 0.3, 0.7):
        if rng.random() < 0.5: x = xs(0.12); at(b, np.sin(2*np.pi*(1400 - 3000*x)*x) * np.exp(-x*40) * 0.25, t + rng.random()*0.3)
    return b
def fuego(d): n = noise(d); c = (np.abs(n) > 3.0) * n * 0.25; return (lp(n.astype(np.float32), 0.05) * 1.2 + c).astype(np.float32)
AMB = {"laberinto": [(gotas, 0.6), (viento, 0.25)], "trecen": [(pajaros, 0.8), (viento, 0.12)], "delfos": [(viento, 0.25), (pajaros, 0.4)], "camino": [(viento, 0.35), (pajaros, 0.5)],
       "atenas": [(pajaros, 0.5), (vitores, 0.0)], "creta": [(pajaros, 0.5)], "mar": [(olas, 0.5), (viento, 0.2)], "naxos": [(olas, 0.5), (grillos, 0.6), (fuego, 0.15)], "mapa": [(olas, 0.25)]}
for p in L["planos"]:
    d = p["t1"] - p["t0"]; lst = list(AMB.get(p["set"], []))
    if p["spot"] in ("puerto", "acantilado"): lst.append((olas, 0.5))
    if p["spot"] in ("trono", "banquete", "taller"): lst = [(fuego, 0.12)]
    if (p.get("luz") or "") == "noche" and p["set"] != "naxos": lst.append((grillos, 0.5))
    if (p.get("luz") or "") == "tormenta": lst.append((viento, 0.4))
    for f, g in lst:
        if g <= 0: continue
        s = f(d + 0.3).astype(np.float32); s *= np.clip(np.arange(len(s)) / (0.15 * SR), 0, 1) * np.clip((len(s) - np.arange(len(s))) / (0.15 * SR), 0, 1)
        at(amb, s, p["t0"], g)
# ------------------------------------------------------------------ mezcla (música bajo la voz, ducking)
rms = lambda a: float(np.sqrt(np.mean(a.astype(np.float64) ** 2)) + 1e-12)
vr = rms(voz[vact])
mus *= vr * 10 ** (-17 / 20) / rms(mus[mus != 0])
duck = 1 - 0.55 * env                       # -7 dB bajo la voz
mus *= duck
fx *= vr * 10 ** (-9 / 20) / (np.percentile(np.abs(fx[fx != 0]), 99.5) * 0.5 + 1e-9)
amb *= vr * 10 ** (-26 / 20) / rms(amb[amb != 0])
mix = voz + mus + fx * (1 - 0.3 * env) + amb
pk = np.abs(mix).max(); mix = mix / pk * 0.95 if pk > 0.95 else mix
# limitador suave
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
sf.write("mezcla.wav", np.stack([mix, mix], 1), SR)
print("ok", round(DUR, 1), "s · pico", round(float(np.abs(mix).max()), 3), "· rms voz", round(vr, 3))

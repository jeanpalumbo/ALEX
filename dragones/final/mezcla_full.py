# Mezcla del vídeo completo de dragones: voz de Jorge (full/vo.wav) + música generada (-20 dB bajo la voz) + SFX.
# SFX: los del gancho (timeline.json) reajustados al tiempo nuevo, whoosh en cada cambio de sección,
# rugido/boom en la primera aparición de cada dragón (silueta->color) y boing en los chistes (punch-in).
# Uso: python mezcla_full.py  -> full/mezcla_full.wav
import json, numpy as np, soundfile as sf, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import mezcla as M0  # noqa: reutiliza los generadores de SFX (se ejecuta el módulo de 15 s; es rápido)
SR = 48000
P = json.load(open("full/planos.json", encoding="utf-8"))
FR = json.load(open("full/frases.json", encoding="utf-8"))
TL = json.load(open("timeline.json", encoding="utf-8"))
v, sr = sf.read("full/vo.wav", dtype="float32")
if v.ndim > 1: v = v.mean(1)
v = np.interp(np.arange(0, len(v), sr / SR), np.arange(len(v)), v).astype(np.float32)
TOTAL = len(v) / SR; N = len(v)
rng = np.random.default_rng(5)
def xs(d): return np.arange(int(d * SR)) / SR
def sm(x, k): return np.convolve(x, np.ones(k) / k, "same")
def at(buf, sig, t0, g=1.0):
    k = int(t0 * SR); e = min(N, k + len(sig))
    if 0 <= k < e: buf[k:e] += (sig[:e - k] * g).astype(np.float32)

LEAD = 0.12
t0s = [0.0 if i == 0 else max(0.0, p["t0"] - LEAD) for i, p in enumerate(P)]
t1s = [t0s[i + 1] if i + 1 < len(P) else TOTAL for i in range(len(P))]

# ---- SFX
GAIN = dict(whoosh=0.30, boom=0.55, roar=0.45, thump=0.45, ding_nosignal=0.5, boing=0.35)
sfx = np.zeros(N, np.float32)
OLD = {s["k"]: (s["t0"], s["t1"]) for s in TL["shots"]}
for s in TL["sfx"]:                                           # gancho reajustado
    for i, p in enumerate(P):
        if p["sec"] == 1 and p["n"] in OLD and OLD[p["n"]][0] <= s["t"] < OLD[p["n"]][1]:
            o0, o1 = OLD[p["n"]]; t = t0s[i] + (s["t"] - o0) / (o1 - o0) * (t1s[i] - t0s[i])
            at(sfx, M0.FX[s["s"]](), t, GAIN[s["s"]]); break
DRAGONES = {"08", "09", "11", "26", "29", "37", "43", "46"}
CHISTE = {"09": -1, "22": -1, "27": 0, "33": -1, "40": -1, "42": 0, "47": -1, "51": -1, "54": -1}
vistos = set()
for i, p in enumerate(P):
    if p["sec"] == 1: continue
    if i > 0 and P[i - 1]["sec"] != p["sec"]: at(sfx, M0.whoosh(), t0s[i] - 0.2, GAIN["whoosh"])
    if p["img"] in DRAGONES and p["img"] not in vistos and p["img"] == p["n"]:
        vistos.add(p["img"]); at(sfx, M0.roar() if len(vistos) % 2 else M0.boom(), t0s[i] + 0.4, 0.35)
    if p["n"] in CHISTE:
        fr = [f for f in FR if f["plano"] == p["n"]]
        if fr: at(sfx, M0.boing(), fr[CHISTE[p["n"]]]["t0"] - 0.05, GAIN["boing"])

# ---- música: pad + arpegio pentatónico + pulso suave; cambia de tonalidad en cada sección
mus = np.zeros(N, np.float32)
beat = 60 / 92
BASE = [[146.83, 220.0, 293.66], [116.54, 174.61, 233.08], [130.81, 196.0, 261.63], [110.0, 164.81, 220.0]]
PENT = [293.66, 349.23, 392.0, 440.0, 523.25, 587.33]
secs = sorted({p["sec"] for p in P})
sec_t = {s: (min(t0s[i] for i, p in enumerate(P) if p["sec"] == s), max(t1s[i] for i, p in enumerate(P) if p["sec"] == s)) for s in secs}
TRANS = [1.0, 1.0, 2 ** (2 / 12), 2 ** (-3 / 12), 2 ** (5 / 12), 1.0, 2 ** (-2 / 12), 2 ** (3 / 12), 1.0, 1.0]
def pad(freqs, t0, d, g):
    x = xs(d); env = np.minimum(1, x / 0.6) * np.minimum(1, (d - x) / 0.6)
    s = sum(np.sin(2 * np.pi * f * x + np.sin(2 * np.pi * 0.3 * x) * 0.3) + 0.3 * np.sin(2 * np.pi * 2.003 * f * x) for f in freqs)
    at(mus, s * env * g / len(freqs), t0)
for si, s in enumerate(secs):
    a, b = sec_t[s]; tr = TRANS[si % len(TRANS)]
    for i, t0 in enumerate(np.arange(a, b, beat * 4)):
        pad([f * tr for f in BASE[i % 4]], t0, min(beat * 4 + 0.6, b - t0 + 0.6), 0.16)
    for j, t0 in enumerate(np.arange(a, b - 0.3, beat / 2)):
        if (j // 16) % 2 and s != 1: continue                 # el arpegio entra y sale para no cansar
        f0 = PENT[(j * 3 + j // 4) % len(PENT)] * tr; x = xs(0.5)
        at(mus, (np.sin(2 * np.pi * f0 * x) + 0.4 * np.sin(4 * np.pi * f0 * x)) * np.exp(-x * 7) * 0.08, t0)
    for t0 in np.arange(a, b, beat * (1 if s == 1 else 2)):
        x = xs(0.4); at(mus, np.sin(2 * np.pi * 65 * x) * np.exp(-x * 12) * 0.2, t0)
tt = np.arange(N) / SR
mus *= np.minimum(1, tt / 0.05) * np.clip((TOTAL - tt) / 1.5, 0, 1)

# ---- niveles: música a -20 dB respecto a la voz (RMS de las partes habladas), ducking suave
def rms(x): return float(np.sqrt(np.mean(x.astype(np.float64) ** 2)) + 1e-12)
habla = np.abs(v) > 0.02
vr = rms(v[habla]); mus *= (vr * 10 ** (-20 / 20)) / rms(mus)
e = sm(np.abs(v), SR // 10); duck = 1 - 0.35 * np.clip(e / (e.max() * 0.15 + 1e-9), 0, 1)
sfx *= (vr * 10 ** (-10 / 20)) / max(1e-9, float(np.abs(sfx).max()) * 0.5)
mix = v + mus * duck + sfx
mix = mix / max(1e-6, np.abs(mix).max()) * 0.95
sf.write("full/mezcla_full.wav", mix, SR)
print("ok full/mezcla_full.wav", round(TOTAL, 2), "s; música", round(20 * np.log10(rms(mus) / vr), 1), "dB bajo voz")

# Música épica sencilla + efectos por código + voz de Jorge -> mezcla.wav (música -20 dB bajo la voz)
import numpy as np, soundfile as sf
SR = 48000; DUR = 17.2; N = int(DUR * SR); rng = np.random.default_rng(5)
def xs(d): return np.arange(int(d * SR)) / SR
def sm(x, k): return np.convolve(x, np.ones(k) / k, "same")
def at(b, s, t, g=1.0):
    k = int(t * SR); e = min(N, k + len(s))
    if 0 <= k < e: b[k:e] += (s[:e - k] * g).astype(np.float32)
def paso(): x = xs(0.1); return (sm(rng.standard_normal(len(x)), 3) * 0.8 + np.sin(2 * np.pi * 120 * x) * 0.4) * np.exp(-x * 50)
def magia(): x = xs(1.2); f = 900 + 600 * np.sin(2 * np.pi * 3 * x); return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-x * 2.5) * 0.4 + sm(rng.standard_normal(len(x)), 2) * 0.05 * np.exp(-x * 3)
def siseo(d=1.6): x = xs(d); n = rng.standard_normal(len(x)); return (n - sm(n, 3)) * 0.35 * np.minimum(1, x / 0.2) * np.minimum(1, (d - x) / 0.3) * (0.6 + 0.4 * np.sin(2 * np.pi * 5 * x))
def pop(): x = xs(0.35); return (sm(rng.standard_normal(len(x)), 6) * 1.2 + np.sin(2 * np.pi * 180 * np.exp(-x * 6) * x * 8)) * np.exp(-x * 12)
def risa(): x = xs(1.2); f = 520 + 120 * np.sin(2 * np.pi * 7 * x); g = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 6.5 * x)); return np.sin(np.cumsum(2 * np.pi * f / SR)) * g * np.exp(-x * 1.2) * 0.45
def rugido(): x = xs(1.0); f = 90 + 30 * np.sin(x * 11); b = np.sin(np.cumsum(2 * np.pi * f / SR)); return (np.sign(b) * np.abs(b) ** 0.5 * sm(np.abs(rng.standard_normal(len(x))), 20) * 3 + sm(rng.standard_normal(len(x)), 6) * 0.3) * np.minimum(1, x / 0.1) * np.exp(-np.maximum(0, x - 0.4) * 4) * 0.6
def golpe(): x = xs(0.7); return (np.sin(2 * np.pi * 60 * x) * 1.2 + sm(rng.standard_normal(len(x)), 4)) * np.exp(-x * 8)
def whoosh(): x = xs(0.35); n = rng.standard_normal(len(x)); return sm(n, 8) * np.sin(np.pi * x / 0.35) ** 2 * 1.2
fx = np.zeros(N, np.float32)
for k in np.arange(0.1, 1.3, 0.3): at(fx, paso(), k, 0.25)                     # Hera camina
at(fx, magia(), 3.75, 0.6); at(fx, siseo(1.9), 4.8, 0.5); at(fx, siseo(1.0), 6.8, 0.4)
at(fx, pop(), 8.3, 0.9); at(fx, pop(), 8.45, 0.9); at(fx, risa(), 8.6, 0.7)
for k in np.arange(10.85, 12.3, 0.29): at(fx, paso(), k, 0.35)                 # Hércules camina
at(fx, rugido(), 11.6, 0.6); at(fx, whoosh(), 12.75, 0.6); at(fx, golpe(), 12.95, 1.0); at(fx, rugido()[:int(0.4 * SR)], 13.0, 0.4)
for w in [0.0, 1.55, 3.3, 4.8, 6.7, 8.15, 9.25, 10.75, 12.35, 14.4]: at(fx, whoosh(), max(0, w - 0.12), 0.18)   # cortes
# música: ostinato de cuerdas en re menor + timbales; tensa y oscura en la noche, épica en la pelea y el final
mus = np.zeros(N, np.float32); beat = 60 / 100; tt = np.arange(N) / SR
def nota(f, d, g, t0, ataque=0.02):
    x = xs(d); s = (np.sin(2 * np.pi * f * x) + 0.5 * np.sin(2 * np.pi * 2 * f * x) + 0.25 * np.sin(2 * np.pi * 3 * f * x)) * np.minimum(1, x / ataque) * np.exp(-x * 2.2)
    at(mus, s * g, t0)
acordes = [(146.83, 174.61, 220.0), (116.54, 146.83, 174.61), (130.81, 164.81, 196.0), (110.0, 138.59, 164.81)]
for j, t0 in enumerate(np.arange(0, DUR, beat / 2)):
    a = acordes[(j // 8) % 4]; nota(a[j % 3] * (2 if j % 4 == 3 else 1), 0.3, 0.12 if 4.8 < t0 < 10.7 else 0.18, t0)
for j, t0 in enumerate(np.arange(0, DUR, beat)):
    a = acordes[(j // 4) % 4]; nota(a[0] / 2, beat * 1.1, 0.3, t0, 0.05)
    if t0 > 10.7 or j % 2 == 0: x = xs(0.5); at(mus, np.sin(2 * np.pi * 55 * x * np.exp(-x * 2)) * np.exp(-x * 7) * (0.7 if t0 > 10.7 else 0.35), t0)
mus *= np.where((tt > 4.8) & (tt < 10.7), 0.6, 1.0) * np.clip((DUR - tt) / 1.0, 0, 1)
v, sr = sf.read("vo.wav", dtype="float32"); v = v if v.ndim == 1 else v.mean(1)
voz = np.zeros(N, np.float32); voz[:min(N, len(v))] = v[:N]
rms = lambda a: float(np.sqrt(np.mean(a.astype(np.float64) ** 2)) + 1e-12)
vr = rms(voz[np.abs(voz) > 0.02]); mus *= vr * 10 ** (-20 / 20) / rms(mus)
fx *= vr * 10 ** (-8 / 20) / (np.abs(fx).max() * 0.5)
mix = voz + mus + fx
sf.write("mezcla.wav", mix / np.abs(mix).max() * 0.95, SR); print("ok")

# Música y efectos generados por código + voz de Jorge -> mezcla.wav (música a -20 dB bajo la voz)
import numpy as np, soundfile as sf
SR = 48000; DUR = 16.5; N = int(DUR * SR); rng = np.random.default_rng(3)
def xs(d): return np.arange(int(d * SR)) / SR
def sm(x, k): return np.convolve(x, np.ones(k) / k, "same")
def at(b, s, t, g=1.0):
    k = int(t * SR); e = min(N, k + len(s))
    if 0 <= k < e: b[k:e] += (s[:e - k] * g).astype(np.float32)
def paso():  x = xs(0.12); return (np.sin(2 * np.pi * 90 * x) * 0.7 + sm(rng.standard_normal(len(x)), 4) * 0.5) * np.exp(-x * 45)
def pop():   x = xs(0.18); f = 520 * np.exp(-x * 9) + 180; return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-x * 22)
def swish(): x = xs(0.22); n = rng.standard_normal(len(x)); return (n - sm(n, 5)) * np.sin(np.pi * x / 0.22) ** 2 * 0.5
def golpe(): x = xs(0.6); return (np.sin(2 * np.pi * 55 * x) + sm(rng.standard_normal(len(x)), 12) * 0.6) * np.exp(-x * 9)
def chirrido(): x = xs(0.55); f = 300 + 180 * np.sin(x * 9); return np.sign(np.sin(np.cumsum(2 * np.pi * f / SR))) * 0.15 * np.exp(-x * 2) * np.minimum(1, x / 0.05)
def boing(): x = xs(0.45); f = 220 + 160 * np.sin(2 * np.pi * 6 * x) * np.exp(-x * 4); return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-x * 5)
def trago(): x = xs(0.25); f = 300 - 500 * x; return np.sin(np.cumsum(2 * np.pi * f / SR)) * np.exp(-((x - 0.1) / 0.06) ** 2)
def tic():   x = xs(0.06); return np.sin(2 * np.pi * 1800 * x) * np.exp(-x * 90)
fx = np.zeros(N, np.float32)
for i in range(1, 10):                                          # pasos de los nueve
    t0, d = 0.45 + i * 0.07, 1.6 + i * 0.12
    for k in np.arange(t0 + 0.1, t0 + d - 0.2, 0.26): at(fx, paso(), k + 0.03 * i, 0.12)
at(fx, golpe(), 2.95, 0.5)                                      # el retrato cae
for k in np.arange(3.95, 4.8, 0.32): at(fx, paso(), k, 0.45)   # pasos del guardia
for k in range(10):
    t0 = 5.6 + k * 0.17; at(fx, swish(), t0, 0.35); at(fx, pop(), t0 + 0.42, 0.45)
at(fx, chirrido(), 10.0, 0.6)                                   # se abre la puerta
at(fx, boing(), 11.2, 0.45)                                     # salto de alegría
at(fx, golpe(), 12.65, 0.9)                                     # portazo
at(fx, trago(), 13.1, 0.6)
for k in range(2): at(fx, tic(), 14.7 + k, 0.7); at(fx, tic(), 15.2 + k, 0.35)
# música: pizzicato juguetón en re menor + bajo, se apaga en «Si fallas…» y vuelve tensa con el reloj
mus = np.zeros(N, np.float32); beat = 60 / 112
esc = [293.66, 349.23, 392.0, 440.0, 523.25, 440.0, 392.0, 349.23]
for j, t0 in enumerate(np.arange(0, 12.6, beat / 2)):
    x = xs(0.3); f0 = esc[(j * 3) % 8] * (1 if j % 8 < 4 else 0.75)
    at(mus, np.sin(2 * np.pi * f0 * x) * np.exp(-x * 14) * 0.5, t0)
for j, t0 in enumerate(np.arange(0, 12.6, beat)):
    x = xs(0.4); at(mus, np.sin(2 * np.pi * [73.4, 87.3, 98.0, 110.0][j // 2 % 4] * x) * np.exp(-x * 6) * 0.8, t0)
x = xs(DUR - 12.7); dr = (np.sin(2 * np.pi * 55 * x) + 0.5 * np.sin(2 * np.pi * 82.4 * x)) * np.minimum(1, x / 0.8) * 0.5
at(mus, dr, 12.7)
v, sr = sf.read("vo.wav", dtype="float32"); v = v if v.ndim == 1 else v.mean(1)
voz = np.zeros(N, np.float32); voz[:min(N, len(v))] = v[:N]
rms = lambda a: float(np.sqrt(np.mean(a.astype(np.float64) ** 2)) + 1e-12)
vr = rms(voz[np.abs(voz) > 0.02]); mus *= vr * 10 ** (-20 / 20) / rms(mus)
fx *= vr * 10 ** (-9 / 20) / (np.abs(fx).max() * 0.5)
tt = np.arange(N) / SR; mix = voz + mus * np.clip((DUR - tt) / 0.6, 0, 1) + fx
sf.write("mezcla.wav", mix / np.abs(mix).max() * 0.95, SR); print("ok mezcla.wav")

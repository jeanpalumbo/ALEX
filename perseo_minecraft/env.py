# Envolvente de la voz a 60 Hz (0..1) para mover bocas: env.json
import json, numpy as np, soundfile as sf
v, sr = sf.read("vo.wav", dtype="float32"); v = v if v.ndim == 1 else v.mean(1); h = sr // 60
e = np.sqrt(np.convolve(v ** 2, np.ones(h) / h, "same"))[::h]; e = np.clip(e / (np.percentile(e, 97) + 1e-9), 0, 1)
json.dump([round(float(x), 2) for x in e], open("env.json", "w"))
print(len(e), "muestras")

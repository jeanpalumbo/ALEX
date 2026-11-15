# Voz de Jorge bloque a bloque con tiempos por palabra -> vo.wav (48 kHz), bloques.json (t0,t1 de cada bloque), palabras.json
import json, os, re, io, asyncio, subprocess, numpy as np, soundfile as sf, edge_tts
from guion import B
import aiohttp, aiohttp.resolver, aiohttp.connector  # c-ares (aiodns) no resuelve en este PC: usar el resolvedor del sistema
aiohttp.resolver.DefaultResolver = aiohttp.connector.DefaultResolver = aiohttp.resolver.ThreadedResolver
SR = 48000; VOZ = "es-MX-JorgeNeural"; RATE = "+5%"
os.makedirs("cache", exist_ok=True)
async def tts(texto, f):
    c = edge_tts.Communicate(texto, VOZ, rate=RATE, boundary="WordBoundary"); a, w = bytearray(), []
    async for ch in c.stream():
        if ch["type"] == "audio": a += ch["data"]
        elif ch["type"] == "WordBoundary": w.append({"w": ch["text"], "t": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
    open(f + ".mp3", "wb").write(a); json.dump(w, open(f + ".json", "w", encoding="utf-8"), ensure_ascii=False)
def cargar(texto, k):
    f = f"cache/f{k:03d}_{abs(hash(texto)) % 10**8}"
    for i in range(5):
        if os.path.exists(f + ".json"): break
        try: asyncio.run(tts(texto, f))
        except Exception as e: print("reintento", i, e)
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", f + ".mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    a = np.frombuffer(pcm, np.float32).copy(); w = json.load(open(f + ".json", encoding="utf-8"))
    i = np.where(np.abs(a) > 0.008)[0]; s = max(0, i[0] - int(0.01 * SR)) if len(i) else 0; e = i[-1] + int(0.05 * SR) if len(i) else len(a)
    return a[s:e], w, s / SR
INTRO = 4.2                      # duración del título animado (sin voz)
out, t, bloques, palabras, k = [np.zeros(int(0.3 * SR), np.float32)], 0.3, [], [], 0
for bi, (esc, cap, texto) in enumerate(B):
    b0 = t
    if not texto:
        out.append(np.zeros(int(INTRO * SR), np.float32)); t += INTRO
        bloques.append(dict(i=bi, esc=esc, cap=cap, t0=round(b0, 3), t1=round(t, 3), frases=[])); continue
    frases = [f.strip() for f in re.split(r"(?<=[.!?…:])\s+", texto) if f.strip()]; fr = []
    for f in frases:
        a, w, off = cargar(f, k); k += 1
        for x in w: palabras.append({"w": x["w"], "t": round(t + x["t"] - off, 3), "e": round(t + x["e"] - off, 3), "b": bi})
        fr.append({"txt": f, "t0": round(t, 3), "t1": round(t + len(a) / SR, 3)})
        pausa = 0.55 if f.endswith(("…", "...")) else (0.38 if f[-1] in ".!?:" else 0.2)
        out += [a, np.zeros(int(pausa * SR), np.float32)]; t += len(a) / SR + pausa
    if cap != B[bi + 1][1] if bi + 1 < len(B) else True: out.append(np.zeros(int(0.5 * SR), np.float32)); t += 0.5   # respiro entre capítulos
    bloques.append(dict(i=bi, esc=esc, cap=cap, t0=round(b0, 3), t1=round(t, 3), frases=fr))
out.append(np.zeros(int(2.5 * SR), np.float32)); t += 2.5
y = np.concatenate(out); y = y / np.abs(y).max() * 0.9
sf.write("vo.wav", y, SR)
json.dump(bloques, open("bloques.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(palabras, open("palabras.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(bloques), "bloques;", len(palabras), "palabras; duración", round(t / 60, 2), "min")


# Cuadra los planos a la voz: guion.json + voz/*.json -> linea.json (planos con tiempos absolutos, palabras, audio)
import json, math, re
B = json.load(open("guion.json", encoding="utf-8"))
LEAD, GAP_CAP, TAIL = 0.35, 1.3, 0.35
toks = lambda s: [w for w in s.split() if re.search(r"\w", w)]
VAR = {"primer": "medio", "medio": "primer", "contra": "primer", "general": "medio", "travel": "primer", "paisaje": "general",
       "picado": "medio", "orbita": "primer", "dos": "primer", "hombro": "primer", "cenital": "general"}

def variante(cam, seg):
    tipo, foco, ang = (cam.split(":") + ["0"])[:3]
    if "," in foco: foco = foco.split(",")[1]
    if foco in ("spot",) and seg["act"]: foco = seg["act"][0]["n"]
    nt = VAR.get(tipo, "medio")
    if nt in ("primer", "medio") and not any(a["n"] == foco for a in seg["act"]):
        nt = "general" if tipo != "general" else "picado"
    return f"{nt}:{foco}:{int(float(ang)) + (30 if float(ang) <= 0 else -35)}"

T = LEAD; planos, palabras, audio, caps = [], [], [], []
ncap = 0
for b in B:
    if b.get("pausa"):
        s = b["segs"][0]; s.update(t0=T, t1=T + b["pausa"], s0=T, s1=T + b["pausa"]); planos.append(s); T += b["pausa"]; continue
    w = json.load(open(f"voz/{b['id']}.json", encoding="utf-8"))
    dur = json.load(open(f"voz/{b['id']}.json"))[-1]["e"]
    b0 = T
    if b.get("cap"):
        ncap += 1; caps.append({"t": T, "n": ncap, "tit": b["cap"]}); T += GAP_CAP
    v0 = T; audio.append({"id": b["id"], "t": v0})
    k = 0; starts = []
    for i, s in enumerate(b["segs"]):
        n = len(toks(s["tx"]))
        ws = w[k:k + n]; k += n
        starts.append(b0 if i == 0 else v0 + ws[0]["t"] - 0.12)
        for x in ws: palabras.append({"w": x["w"], "t": v0 + x["t"], "e": v0 + x["e"], "seg": len(planos) + i})
        s["_ws"] = ws
    assert k == len(w), (b["id"], k, len(w))
    fin = v0 + w[-1]["e"] + TAIL
    for i, s in enumerate(b["segs"]):
        s0 = starts[i]; s1 = starts[i + 1] if i + 1 < len(starts) else fin
        s.pop("_ws"); s.update(s0=s0, s1=s1, t0=s0, t1=s1); planos.append(s)
    T = fin
# fin: cola con la tarjeta de suscripción
planos[-1]["s1"] = planos[-1]["t1"] = T + 2.6; T += 2.6
# trocear planos largos en subplanos (nunca más de ~4.6 s con la misma cámara)
out = []
for p in planos:
    d = p["s1"] - p["s0"]; cams = list(p["cam"])
    n = max(len(cams) if d > 2.2 * len(cams) else 1, math.ceil(d / 4.4))
    while len(cams) < n: cams.append(variante(cams[len(cams) % len(p["cam"])] if len(cams) >= len(p["cam"]) else cams[-1], p))
    for j in range(n):
        q = dict(p); q["cam1"] = cams[j]; q["t0"] = p["s0"] + d * j / n; q["t1"] = p["s0"] + d * (j + 1) / n; q["sub"] = j
        out.append(q)
# efectos con tiempo absoluto
for q in out:
    q["fxa"] = []
    for f in q.get("fx", []):
        nm, _, fr = f.partition("@"); q["fxa"].append([nm, q["s0"] + float(fr or 0) * (q["s1"] - q["s0"])])
json.dump({"dur": T, "planos": out, "palabras": palabras, "audio": audio, "caps": caps}, open("linea.json", "w", encoding="utf-8"), ensure_ascii=False)
ds = [q["t1"] - q["t0"] for q in out]
print(f"duración {T:.1f}s = {T/60:.2f} min · {len(out)} planos · medio {sum(ds)/len(ds):.2f}s · máx {max(ds):.2f}s · mín {min(ds):.2f}s")

# Subtítulos palabra a palabra sin solapes (mismo estilo que dragones) + comprobación automática
import json, re
P = json.load(open("palabras.json", encoding="utf-8"))
CLAVE = re.compile(r"sombrero|blanco|negro|libre|diez|segundos|rey|guardia", re.I)
G, cur = [], []
for w in P:
    if cur and w["t"] - cur[-1]["e"] > 0.45: G.append(cur); cur = []
    cur.append(w)
    if re.search(r"[.!?:…,;]$", w["w"]) or len(cur) == 3: G.append(cur); cur = []
if cur: G.append(cur)
ev = []
for i, g in enumerate(G):
    gend = g[-1]["e"] + 0.6
    if i + 1 < len(G): gend = min(gend, G[i + 1][0]["t"] - 0.02)
    for k, w in enumerate(g):
        a = w["t"] - 0.02; b = g[k + 1]["t"] - 0.02 if k + 1 < len(g) else gend
        parts = []
        for j, x in enumerate(g):
            col = r"\c&H00D6FF&" if CLAVE.search(x["w"]) else r"\c&HFFFFFF&"
            if j < k: parts.append("{" + col + r"\alpha&H00&}" + x["w"])
            elif j == k: parts.append("{" + col + r"\alpha&H00&\fscy125\t(0,120,\fscy100)}" + x["w"])
            else: parts.append(r"{\alpha&HFF&}" + x["w"])
        ev.append([round(a * 100), round(b * 100), " ".join(parts)])
ev.sort(key=lambda e: e[0])
for i in range(len(ev) - 1): ev[i][1] = min(ev[i][1], ev[i + 1][0])
ev = [e for e in ev if e[1] - e[0] >= 3]
sol = sum(1 for i in range(len(ev) - 1) if ev[i][1] > ev[i + 1][0]); assert sol == 0
def cs(c): return f"{c // 360000}:{c // 6000 % 60:02d}:{c // 100 % 60:02d}.{c % 100:02d}"
L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "", "[V4+ Styles]",
     "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
     "Style: S,Montserrat,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,4,2,60,60,40,1", "",
     "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
L += [f"Dialogue: 0,{cs(a)},{cs(b)},S,,0,0,0,,{t}" for a, b, t in ev]
open("subs.ass", "w", encoding="utf-8").write("\n".join(L) + "\n")
print(len(ev), "eventos; solapes", sol)

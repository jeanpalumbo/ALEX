# Subtítulos palabra a palabra del vídeo completo -> full/subs.ass (se queman con ffmpeg/libass).
# Mismo estilo que subs.py: Montserrat Bold 92, blanco con contorno negro, palabras clave en amarillo, pop de entrada,
# grupos de hasta 3 palabras (corta tras puntuación fuerte). Las palabras aún no dichas ocupan su sitio pero invisibles.
import json, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open("full/palabras.json", encoding="utf-8"))
CLAVE = re.compile(r"china|europa|m[ée]xico|australia|drag[oó]n|dragones|imposible|whatsapp|bicho|f[óo]sil|f[óo]siles|grecia|zeus|volc[áa]n|geomitolog[íi]a|dientes|quimera|cr[áa]neo", re.I)
G, cur = [], []
for w in P:
    cur.append(w)
    if re.search(r"[.!?:…,;]$", w["w"]) or len(cur) == 3: G.append(cur); cur = []
if cur: G.append(cur)
def ts(t):
    t = max(0.0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
def esc(s): return s.replace("{", "(").replace("}", ")")
out = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "",
       "[V4+ Styles]",
       "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: S,Montserrat,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,4,2,60,60,130,1", "",
       "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i, g in enumerate(G):
    nxt = G[i + 1][0]["t"] if i + 1 < len(G) else g[-1]["e"] + 1.0
    gend = min(nxt, g[-1]["e"] + 0.6)
    for k, w in enumerate(g):
        a = w["t"] - 0.02; b = g[k + 1]["t"] - 0.02 if k + 1 < len(g) else gend
        if b <= a: continue
        parts = []
        for j, x in enumerate(g):
            col = r"\c&H00D6FF&" if CLAVE.search(x["w"]) else r"\c&HFFFFFF&"
            if j < k: parts.append("{" + col + r"\alpha&H00&\fscx100\fscy100}" + esc(x["w"]))
            elif j == k: parts.append("{" + col + r"\alpha&H00&\fscx118\fscy118\t(0,120,\fscx100\fscy100)}" + esc(x["w"]))
            else: parts.append(r"{\alpha&HFF&\fscx100\fscy100}" + esc(x["w"]))
        out.append(f"Dialogue: 0,{ts(a)},{ts(b)},S,,0,0,0,," + " ".join(parts))
open("full/subs.ass", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("ok full/subs.ass", len(G), "grupos")

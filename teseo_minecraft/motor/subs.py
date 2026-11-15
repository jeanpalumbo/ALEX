# Subtítulos palabra a palabra (ASS) desde linea.json + guion.json
import json, re
L = json.load(open("linea.json")); G = json.load(open("guion.json"))
segs = [s["tx"] for b in G for s in b["segs"]]
NOMBRES = {"teseo","minotauro","egeo","ariadna","medea","minos","dédalo","atenas","creta","laberinto","naxos","etra","delfos","trecén","procusto","escirón","perifetes","sinis","dioniso","egeo:"}
toks = {}
for k, t in enumerate(segs):
    toks[k] = [x for x in t.split() if re.search(r"\w", x)]
W = []
cnt = {}
for w in L["palabras"]:
    i = cnt.get(w["seg"], 0); cnt[w["seg"]] = i + 1
    tk = toks[w["seg"]][i] if i < len(toks[w["seg"]]) else w["w"]
    W.append({**w, "tk": tk})
# trozos de 1-4 palabras, cortando en puntuación
chunks, cur = [], []
for j, w in enumerate(W):
    cur.append(w)
    fin = re.search(r"[.,;:!?…]$", w["tk"]) or len(cur) >= 4 or sum(len(x["tk"]) for x in cur) > 18
    nxt = W[j + 1] if j + 1 < len(W) else None
    if nxt and nxt["t"] - w["e"] > 0.45: fin = True
    if fin or not nxt: chunks.append(cur); cur = []
def ts(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60; return f"{h}:{m:02d}:{s:05.2f}"
def esc(t): return t.replace("{", "(").replace("}", ")")
out = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "WrapStyle: 2", "",
       "[V4+ Styles]", "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
       "Style: S,Lilita One,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,1,0,1,7,4,2,80,80,110,1", "",
       "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for ci, ch in enumerate(chunks):
    nx = chunks[ci + 1][0]["t"] if ci + 1 < len(chunks) else ch[-1]["e"] + 1
    fin = min(ch[-1]["e"] + 0.35, nx)
    for k, w in enumerate(ch):
        a = w["t"] if k else w["t"] - 0.05
        b = ch[k + 1]["t"] if k + 1 < len(ch) else fin
        if b - a < 0.04: continue
        parts = []
        for q, x in enumerate(ch):
            limpio = re.sub(r"[^\wáéíóúüñÁÉÍÓÚÜÑ]", "", x["tk"]).lower()
            base = "&H1A8CFF&" if limpio in NOMBRES else "&HFFFFFF&"
            if q == k: parts.append("{\\c&H00E6FF&\\fscx115\\fscy115}" + esc(x["tk"].upper()) + "{\\c" + "&HFFFFFF&" + "\\fscx100\\fscy100}")
            else: parts.append("{\\c" + base + "}" + esc(x["tk"].upper()) + "{\\c&HFFFFFF&}")
        pop = "{\\fad(60,0)}" if k == 0 else ""
        out.append(f"Dialogue: 0,{ts(max(0,a))},{ts(b)},S,,0,0,0,,{pop}" + " ".join(parts))
open("subs.ass", "w", encoding="utf-8").write("\n".join(out) + "\n")
print("trozos", len(chunks), "eventos", len(out) - 12)

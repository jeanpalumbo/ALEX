# 6 Shorts verticales 1080x1920 del vídeo animado de dragones (v2).
# - Imagen grande: recorte 4:5 (864x1080 del 1920x1080) escalado a 1080x1350, encuadrado plano a plano en el sujeto;
#   en los planos anchos (el sujeto no cabe) el recorte recorre la escena de lado a lado.
# - Fondo: el mismo vídeo desenfocado y oscurecido. Título arriba, subtítulos grandes sobre la imagen (0 solapes).
# - Final: cada Short corta 0,15 s después de la última palabra de una frase; la voz se cierra, sigue solo la música
#   1,9 s con la imagen congelada y el CTA «Vídeo completo en el canal».
# Uso: python shorts_anim.py  -> ../final/shorts_animados/short_NN.mp4
import os, sys, json, re, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); os.chdir(AQUI)
sys.path.insert(0, os.path.dirname(AQUI))
import subs_full as S
os.chdir(AQUI)
P = json.load(open("../full/planos.json", encoding="utf-8"))
PAL = json.load(open("../full/palabras.json", encoding="utf-8"))
INFO = json.load(open("../img_full/mask/info.json"))
LEAD = 0.12
t0 = {p["n"]: max(0.0, p["t0"] - LEAD) for p in P}
fin = {P[i]["n"]: (P[i + 1]["t0"] - LEAD if i + 1 < len(P) else 302.5) for i in range(len(P))}
ORDEN = [p["n"] for p in P]
CW = 864                                             # ancho del recorte 4:5 en el vídeo 1920x1080
ANCHOS = {"gag", "09", "28", "31", "43", "46", "17", "20", "mosaico"}
SH = [  # (desde, hasta incl., gancho grande 0-2 s, título fijo con {acento})
    ("china", "10", "TODOS dibujaron\\Nel MISMO monstruo", "¿Por qué todos dibujaron {DRAGONES}?"),
    ("07", "10", "3 dragones.\\N3 culturas.", "Dragones de todo el {MUNDO}"),
    ("29", "35", "¿Dientes de\\NDRAGÓN?", "Los «dientes de dragón» eran {FÓSILES}"),
    ("41", "43", "¿Por qué escupen\\NFUEGO?", "El secreto del {FUEGO} de dragón"),
    ("44", "47", "Zeus contra\\Nun monstruo", "La tierra quemada por {ZEUS}"),
    ("50", "55", "El Valle del\\NDragón Amarillo", "Un valle lleno de {HUELLAS}"),
]

def encuadre(n):
    """(x_ini, x_fin) del centro del recorte (px del 1920x1080) para el plano n."""
    img = next((p["img"] for p in P if p["n"] == n), n)
    if n in ANCHOS or img in ANCHOS:
        if img in INFO: x0, _, x1, _ = INFO[img]["bbox"]; a, b = x0 * 1.5 + CW / 2, x1 * 1.5 - CW / 2
        else: a, b = 560, 1360
        a, b = max(CW / 2, min(a, 1920 - CW / 2)), max(CW / 2, min(b, 1920 - CW / 2))
        return (a, b) if b > a else ((a + b) / 2,) * 2
    c = INFO[img]["c"][0] * 1.5 if img in INFO else 960
    c = max(CW / 2, min(c, 1920 - CW / 2)); return c, c

def ass(a, c, d, gancho, titulo, f):
    G = [g for g in S.G if a - 0.05 <= g[0]["t"] < c]
    def txt(g, k):
        out = []
        for j, x in enumerate(g):
            col = r"\c&H00D6FF&" if S.CLAVE.search(x["w"]) else r"\c&HFFFFFF&"
            if j < k: out.append("{" + col + r"\alpha&H00&}" + S.esc(x["w"]))
            elif j == k: out.append("{" + col + r"\alpha&H00&\fscy125\t(0,120,\fscy100)}" + S.esc(x["w"]))
            else: out.append(r"{\alpha&HFF&}" + S.esc(x["w"]))
        return " ".join(out)
    ev = S.eventos(G, c + 0.35, txt)                  # assert interno: 0 solapes
    cs = lambda v: S.cs(max(0, v))
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: S,Montserrat,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,8,5,8,40,40,1330,1",
         "Style: T,Montserrat,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,4,8,50,50,120,1",
         "Style: H,Montserrat,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,10,6,5,50,50,0,1",
         "Style: C,Montserrat,78,&H0000D6FF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,8,5,2,50,50,120,1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    L.append(f"Dialogue: 2,{cs(0)},{cs(220)},H,,0,0,0,,{{\\fad(0,200)\\fscx130\\fscy130\\t(0,180,\\fscx100\\fscy100)}}{gancho}")
    tit = re.sub(r"\{(.+?)\}", r"{\\c&H00D6FF&}\1{\\c&HFFFFFF&}", titulo)
    L.append(f"Dialogue: 1,{cs(230)},{cs(round(d * 100))},T,,0,0,0,,{{\\fad(200,0)}}{tit}")
    L.append(f"Dialogue: 1,{cs(round((c - a + 0.25) * 100))},{cs(round(d * 100))},C,,0,0,0,,{{\\fad(150,0)\\fscx120\\fscy120\\t(0,200,\\fscx100\\fscy100)}}▶ Vídeo completo en el canal")
    sa = round(a * 100)
    for x0, x1, tx in ev:
        if x1 - sa > 0: L.append(f"Dialogue: 0,{cs(x0 - sa)},{cs(x1 - sa)},S,,0,0,0,,{tx}")
    open(f, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return len(ev)

def tramos(pa, pb):
    """Planos (nombre, ini, fin) del Short en tiempo absoluto (el gancho se trata como planos propios)."""
    i0, i1 = ORDEN.index(pa), ORDEN.index(pb)
    return [(n, t0[n], fin[n]) for n in ORDEN[i0:i1 + 1]]

os.makedirs("../final/shorts_animados", exist_ok=True)
for i, (pa, pb, gancho, tit) in enumerate(SH, 1):
    a, b = t0[pa], fin[pb]
    c = max(w["e"] for w in PAL if a <= w["t"] < b) + 0.15   # fin de la última palabra (fin de frase)
    d = c - a + 1.9                                         # + cola con música y CTA
    vis = min(b, c + 0.3) - a                               # vídeo vivo hasta aquí; después, imagen congelada
    # expresión de recorte x(t) plano a plano (t local del Short)
    expr = "960"
    for n, x, y in reversed(tramos(pa, pb)):
        xa, xb = encuadre(n); la, lb = x - a, y - a
        xe = f"{xa:.0f}+({xb - xa:.0f})*(t-{la:.3f})/{max(0.1, lb - la):.3f}"
        expr = f"if(lt(t,{lb:.3f}),{xe}-{CW // 2},{expr})" if expr != "960" else f"{xe}-{CW // 2}"
    f = f"short_{i:02d}.ass"; n = ass(a, c, d, gancho, tit, f)
    vf = (f"[0:v]trim=0:{vis:.3f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={d - vis + 0.1:.3f},split[x][y];"
          f"[x]scale=3413:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.25[bg];"
          f"[y]crop={CW}:1080:'max(0,min(1920-{CW},{expr}))':0,scale=1080:1350[fg];"
          f"[bg][fg]overlay=0:285,subtitles={f},fade=t=in:st=0:d=0.2,fade=t=out:st={d - 0.3:.2f}:d=0.3[v]")
    af = (f"[1:a]volume='if(lt(t,{c - a:.3f}),1,max(0,1-(t-{c - a:.3f})/0.12))':eval=frame[va];"
          f"[2:a]volume='if(lt(t,{c - a:.3f}),0,min(1,(t-{c - a:.3f})/0.12))':eval=frame[fa];"
          f"[va][fa]amix=inputs=2:normalize=0,afade=t=in:st=0:d=0.1,afade=t=out:st={d - 0.5:.2f}:d=0.5[a]")
    out = f"../final/shorts_animados/short_{i:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{vis + 0.2:.3f}", "-i", "visual_full.mp4",
                    "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", "../full/mezcla_full.wav",
                    "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", "../full/fondo_full.wav",
                    "-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]", "-t", f"{d:.3f}",
                    "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "30",
                    "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    ult = " ".join(w["w"] for w in PAL if a <= w["t"] < b)[-60:]
    print(f"{out} {d:.1f} s | {n} subtítulos, 0 solapes | termina: …{ult}")

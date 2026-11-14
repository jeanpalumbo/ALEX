# 6 Shorts verticales 1080x1920 del vídeo animado de dragones.
# Fondo: el plano ampliado, desenfocado y oscurecido; encima el plano animado a 1600 de ancho (recorte central 1080x900).
# 0-2,2 s: gancho de texto grande; después título fijo arriba. Subtítulos palabra a palabra sin solapes (subs_full.eventos).
# Últimos 3 s: CTA «Vídeo completo en el canal». Uso: python shorts_anim.py -> ../final/shorts_animados/short_NN.mp4
import os, sys, json, re, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); os.chdir(AQUI)
sys.path.insert(0, os.path.dirname(AQUI))
import subs_full as S
os.chdir(AQUI)
P = json.load(open("../full/planos.json", encoding="utf-8"))
LEAD = 0.12
t0 = {p["n"]: max(0.0, p["t0"] - LEAD) for p in P}
fin = {P[i]["n"]: (P[i + 1]["t0"] - LEAD if i + 1 < len(P) else 302.5) for i in range(len(P))}
SH = [  # (desde, hasta incl., gancho grande 0-2 s, título fijo con {acento})
    ("china", "10", "TODOS dibujaron\nel MISMO monstruo", "¿Por qué todos dibujaron {DRAGONES}?"),
    ("07", "10", "3 dragones.\n3 culturas.", "Dragones de todo el {MUNDO}"),
    ("29", "35", "¿Dientes de\nDRAGÓN?", "Los «dientes de dragón» eran {FÓSILES}"),
    ("41", "43", "¿Por qué escupen\nFUEGO?", "El secreto del {FUEGO} de dragón"),
    ("44", "47", "Zeus contra\nun monstruo", "La tierra quemada por {ZEUS}"),
    ("50", "55", "El Valle del\nDragón Amarillo", "Un valle lleno de {HUELLAS}"),
]
def esc(s): return s.replace("{", "(").replace("}", ")")
def ass(a, b, gancho, titulo, f):
    d = b - a
    G = [g for g in S.G if a - 0.05 <= g[0]["t"] < b - 0.15]
    def txt(g, k):
        out = []
        for j, x in enumerate(g):
            col = r"\c&H00D6FF&" if S.CLAVE.search(x["w"]) else r"\c&HFFFFFF&"
            if j < k: out.append("{" + col + r"\alpha&H00&}" + esc(x["w"]))
            elif j == k: out.append("{" + col + r"\alpha&H00&\fscy125\t(0,120,\fscy100)}" + esc(x["w"]))
            else: out.append(r"{\alpha&HFF&}" + esc(x["w"]))
        return " ".join(out)
    ev = S.eventos(G, b - 0.05, txt)                       # comprueba 0 solapes (assert)
    cs = lambda c: S.cs(max(0, c))
    L = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 0", "", "[V4+ Styles]",
         "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
         "Style: S,Montserrat,88,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,7,4,8,40,40,1420,1",
         "Style: T,Montserrat,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H78000000,-1,0,0,0,100,100,0,0,1,6,4,8,60,60,250,1",
         "Style: H,Montserrat,112,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,9,6,5,60,60,0,1",
         "Style: C,Montserrat,70,&H0000D6FF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,4,2,60,60,230,1", "",
         "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    g = gancho.replace("\n", r"\N")
    L.append(f"Dialogue: 2,{cs(0)},{cs(220)},H,,0,0,0,,{{\\fad(0,200)\\fscx130\\fscy130\\t(0,180,\\fscx100\\fscy100)}}{g}")
    tit = re.sub(r"\{(.+?)\}", r"{\\c&H00D6FF&}\1{\\c&HFFFFFF&}", titulo)
    L.append(f"Dialogue: 1,{cs(230)},{cs(round(d * 100))},T,,0,0,0,,{{\\fad(200,0)}}{tit}")
    L.append(f"Dialogue: 1,{cs(round((d - 3.0) * 100))},{cs(round(d * 100))},C,,0,0,0,,{{\\fad(200,0)}}▶ Vídeo completo en el canal")
    for x0, x1, tx in ev:
        x0 -= round(a * 100); x1 -= round(a * 100)
        if x1 > 0: L.append(f"Dialogue: 0,{cs(x0)},{cs(x1)},S,,0,0,0,,{tx}")
    open(f, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return len(ev)
os.makedirs("../final/shorts_animados", exist_ok=True)
for i, (pa, pb, gancho, tit) in enumerate(SH, 1):
    a, b = t0[pa], fin[pb]; d = b - a; f = f"short_{i:02d}.ass"; n = ass(a, b, gancho, tit, f)
    vf = (f"[0:v]split[x][y];[x]scale=3413:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.2[bg];"
          f"[y]scale=1600:900,crop=1080:900[fg];[bg][fg]overlay=0:480,subtitles={f},"
          f"fade=t=in:st=0:d=0.2,fade=t=out:st={d - 0.35:.2f}:d=0.35[v]")
    out = f"../final/shorts_animados/short_{i:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", "visual_full.mp4",
                    "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", "../full/mezcla_full.wav",
                    "-filter_complex", vf, "-map", "[v]", "-map", "1:a",
                    "-af", f"afade=t=in:st=0:d=0.12,afade=t=out:st={d - 0.35:.2f}:d=0.35", "-c:v", "libx264", "-crf", "20", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
    print(out, round(d, 1), "s", n, "subtítulos, 0 solapes", round(os.path.getsize(out) / 1e6, 1), "MB")

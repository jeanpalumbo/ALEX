# Montaje final: capa visual + subtítulos quemados + mezcla -> final/dragones_es_1080p.mp4,
# copia comprimida <95 MB (final/dragones_es_1080p_web.mp4) y hoja de revisión cada 5 s (final/hoja_revision.jpg).
import os, subprocess, math, json
from PIL import Image, ImageDraw, ImageFont
os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.makedirs("final", exist_ok=True)
V, A, S = "full/capa_visual_full.mp4", "full/mezcla_full.wav", "full/subs.ass"
OUT, WEB = "final/dragones_es_1080p.mp4", "final/dragones_es_1080p_web.mp4"
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
run("-i", V, "-i", A, "-map", "0:v", "-map", "1:a", "-vf", f"subtitles={S}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT)
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT]).decode())
mb = os.path.getsize(OUT) / 1e6; print("final", round(dur, 2), "s", round(mb, 1), "MB")
if mb > 95:
    vb = int((90e6 * 8 / dur - 160e3) / 1000)              # kbps de vídeo para ~90 MB
    for p in (1, 2):
        run("-i", OUT, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{vb}k", "-pass", str(p), "-passlogfile", "full/x264pass",
            "-pix_fmt", "yuv420p", *(["-an", "-f", "mp4", "NUL"] if p == 1 else ["-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", WEB]))
    print("web", round(os.path.getsize(WEB) / 1e6, 1), "MB")
# hoja de revisión: un fotograma cada 5 s
os.makedirs("full/hoja", exist_ok=True)
run("-i", OUT, "-vf", "fps=1/5,scale=384:216", "full/hoja/%03d.jpg")
fs = sorted(os.listdir("full/hoja")); cols = 8; rows = math.ceil(len(fs) / cols)
H = Image.new("RGB", (cols * 388, rows * 240), "white"); d = ImageDraw.Draw(H)
F = ImageFont.truetype(r"C:\Windows\Fonts\Montserrat-Bold.ttf", 16)
for i, f in enumerate(fs):
    x, y = (i % cols) * 388, (i // cols) * 240
    H.paste(Image.open(f"full/hoja/{f}"), (x + 2, y + 2)); t = i * 5
    d.text((x + 6, y + 220), f"{t // 60}:{t % 60:02d}", fill="black", font=F)
H.save("final/hoja_revision.jpg", quality=85); print("hoja", len(fs), "fotogramas")

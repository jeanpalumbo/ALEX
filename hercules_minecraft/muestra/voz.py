import asyncio, json, edge_tts, subprocess
T = ("Hera odiaba a Hércules desde el día en que nació. "
     "Así que una noche le metió dos serpientes en la cuna. "
     "Y el bebé… las estranguló. Riéndose. "
     "Aquel niño acabaría luchando contra leones y monstruos. Esta es la historia de Hércules.")
async def main():
    c = edge_tts.Communicate(T, "es-MX-JorgeNeural", rate="+5%", boundary="WordBoundary")
    a, w = bytearray(), []
    async for ch in c.stream():
        if ch["type"] == "audio": a += ch["data"]
        elif ch["type"] == "WordBoundary": w.append({"w": ch["text"], "t": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
    open("vo.mp3", "wb").write(a); json.dump(w, open("palabras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
asyncio.run(main())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "vo.mp3", "-ar", "48000", "-ac", "1", "vo.wav"])

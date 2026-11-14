import asyncio, json, edge_tts, subprocess
T = ("Tú y otros nueve prisioneros estáis en la mazmorra de un rey. "
     "El guardia os pone en fila con un sombrero: blanco o negro. "
     "Nadie ve el suyo. Si lo aciertas, eres libre. Si fallas… "
     "Tienes diez segundos.")
async def main():
    c = edge_tts.Communicate(T, "es-MX-JorgeNeural", rate="+5%", boundary="WordBoundary")
    a, w = bytearray(), []
    async for ch in c.stream():
        if ch["type"] == "audio": a += ch["data"]
        elif ch["type"] == "WordBoundary": w.append({"w": ch["text"], "t": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
    open("vo.mp3", "wb").write(a); json.dump(w, open("palabras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
asyncio.run(main())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "vo.mp3", "-ar", "48000", "-ac", "1", "vo.wav"])

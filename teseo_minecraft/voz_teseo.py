# Genera la voz de "Teseo y el Minotauro" (edge-tts es-MX-JorgeNeural +5 %) por bloques, con tiempos palabra a palabra.
# Uso (desde la carpeta teseo_minecraft):  python voz_teseo.py   -> voz/<bloque>.mp3 + voz/<bloque>.json
import asyncio, json, os, time, edge_tts
B = json.load(open("guion.json", encoding="utf-8")); os.makedirs("voz", exist_ok=True)
async def uno(b):
    texto = " ".join(s["tx"] for s in b["segs"] if s["tx"]).strip()
    if not texto: return
    for intento in range(5):
        try:
            c = edge_tts.Communicate(texto, "es-MX-JorgeNeural", rate="+5%", boundary="WordBoundary")
            a, w = bytearray(), []
            async for ch in c.stream():
                if ch["type"] == "audio": a += ch["data"]
                elif ch["type"] == "WordBoundary": w.append({"w": ch["text"], "t": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
            if len(a) < 1000 or not w: raise RuntimeError("audio vacío")
            open(f"voz/{b['id']}.mp3", "wb").write(a); json.dump(w, open(f"voz/{b['id']}.json", "w", encoding="utf-8"), ensure_ascii=False)
            print("ok", b["id"], len(w), "palabras"); return
        except Exception as e:
            print("reintento", b["id"], e); time.sleep(3 * (intento + 1))
    raise SystemExit("FALLO " + b["id"])
async def main():
    for b in B: await uno(b)
asyncio.run(main())

// Render del HTML a MP4: Edge headless por CDP, pinta cada fotograma con window.pintar(t) y lo pasa a ffmpeg.
// Uso: node render.js escena.html salida.mp4 [desde hasta] | node render.js escena.html --fotos t1,t2,... carpeta
const { spawn } = require('child_process'); const fs = require('fs'); const path = require('path');
const EDGE = process.env.BROWSER || (process.platform === 'win32' ? 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' : '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'), PORT = +(process.env.PORT || 9555), FPS = 30;
const [html, out, a, b] = process.argv.slice(2);
(async () => {
  const prof = path.join(process.env.TEMP || require('os').tmpdir(), 'edge_render_prof_' + PORT);
  const br = spawn(EDGE, ['--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${prof}`, '--hide-scrollbars', '--force-device-scale-factor=1', '--window-size=1920,1080', '--disable-gpu-vsync', ...(process.platform === 'win32' ? ['--use-angle=d3d11', '--enable-gpu', '--ignore-gpu-blocklist'] : ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--use-gl=angle']), 'about:blank'], { stdio: 'ignore' });
  let lista; for (let k = 0; k < 60; k++) { try { lista = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); if (lista.length) break; } catch (e) {} await new Promise(r => setTimeout(r, 250)); }
  const pag = lista.find(p => p.type === 'page');
  const ws = new WebSocket(pag.webSocketDebuggerUrl); await new Promise((ok, ko) => { ws.onopen = ok; ws.onerror = ko; });
  let id = 0; const pend = new Map(); ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pend.has(m.id)) { pend.get(m.id)(m); pend.delete(m.id); } };
  const cdp = (method, params = {}) => new Promise(ok => { const i = ++id; pend.set(i, ok); ws.send(JSON.stringify({ id: i, method, params })); });
  await cdp('Emulation.setDeviceMetricsOverride', { width: 1920, height: 1080, deviceScaleFactor: 1, mobile: false });
  await cdp('Network.enable'); await cdp('Network.setCacheDisabled', { cacheDisabled: true }); await cdp('Page.enable'); await cdp('Page.navigate', { url: html.startsWith('http') ? html : 'file:///' + path.resolve(html).split(path.sep).join('/') });
  for (let k = 0; k < 60; k++) { const r0 = await cdp('Runtime.evaluate', { expression: 'window.LISTO||0', returnByValue: true }); if (r0.result.result.value) break; await new Promise(r => setTimeout(r, 500)); }
  const ev = async e => { const r = await cdp('Runtime.evaluate', { expression: e, returnByValue: true, awaitPromise: true }); if (r.result.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 400)); return r.result.result.value; };
  const dur = await ev('window.DUR');
  const shot = async t => { await ev(`window.pintar(${t}); 1`); const FMT = process.env.FMT || 'png'; const s = await cdp('Page.captureScreenshot', Object.assign({ format: FMT, clip: { x: 0, y: 0, width: 1920, height: 1080, scale: 1 } }, FMT === 'jpeg' ? { quality: 95 } : {})); return Buffer.from(s.result.data, 'base64'); };
  if (out === '--fotos') {
    fs.mkdirSync(b, { recursive: true });
    for (const t of a.split(',').map(Number)) fs.writeFileSync(path.join(b, `f_${t.toFixed(2)}.png`), await shot(t));
  } else {
    const f0 = Math.round((a ? +a : 0) * FPS), f1 = Math.round((b ? +b : dur) * FPS);
    const ENC = process.env.ENC === 'nvenc' ? ['-c:v', 'h264_nvenc', '-preset', 'p5', '-cq', '18', '-b:v', '0'] : ['-c:v', 'libx264', '-preset', 'medium', '-crf', '16']; const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', (process.env.FMT === 'jpeg' ? 'mjpeg' : 'png'), '-i', '-', ...ENC, '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = f0; f < f1; f++) { const buf = await shot(f / FPS); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); if (f % 60 === 0) process.stdout.write(`${f} `); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); console.log('\nok', out);
  }
  ws.close(); br.kill();
})().catch(e => { console.error('ERROR', e.message); process.exit(1); });

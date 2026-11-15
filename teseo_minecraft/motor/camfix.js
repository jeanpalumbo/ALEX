// node camfix.js  -> camfix.json (giro de cámara por plano para que nada tape al personaje)
const { chromium } = require('playwright'); const fs = require('fs');
(async()=>{
 const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p = await b.newPage({viewport:{width:640,height:360}});
 await fs.promises.writeFile('camfix.json','{}');
 await p.goto('http://127.0.0.1:8765/teseo.html');
 await p.waitForFunction('window.LISTO || (window.__err&&window.__err.length)',null,{timeout:180000});
 const err = await p.evaluate('window.__err'); if (err && err.length) console.log('ERR', err);
 const n = await p.evaluate('PL.length'); const out = {};
 for (let i=0;i<n;i++){ const r = await p.evaluate(i=>window.__buscaCam(i), i); if (r[0]||r[1]) console.log(i, r); out[i]=r[0]; }
 fs.writeFileSync('camfix.json', JSON.stringify(out)); await b.close(); })();

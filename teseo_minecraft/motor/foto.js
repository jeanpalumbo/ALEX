// node foto.js t1,t2,... carpeta  -> PNG de esos instantes
const { chromium } = require('playwright'); const fs = require('fs');
(async()=>{
 const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p = await b.newPage({viewport:{width:1920,height:1080}});
 p.on('console',m=>{ if(m.type()==='error') console.log('C',m.text())});
 await p.goto('http://127.0.0.1:8765/teseo.html');
 try { await p.waitForFunction('window.LISTO || (window.__err&&window.__err.length)',null,{timeout:180000}); } catch(e){}
 const err = await p.evaluate('window.__err'); if (err && err.length) { console.log('ERR', err); }
 fs.mkdirSync(process.argv[3],{recursive:true});
 for (const t of process.argv[2].split(',').map(Number)) { const t0=Date.now(); await p.evaluate(t=>window.pintar(t),t); await p.screenshot({path:`${process.argv[3]}/f_${t.toFixed(1)}.jpg`,type:'jpeg',quality:85}); console.log(t, Date.now()-t0,'ms'); }
 const err2 = await p.evaluate('window.__err'); if (err2 && err2.length) console.log('ERR2', err2.slice(0,5));
 await b.close();})();

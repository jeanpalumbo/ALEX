// node render.js f0 f1 salida.mp4  -> renderiza los fotogramas [f0,f1) a 30 fps
const { chromium } = require('playwright'); const { spawn } = require('child_process');
const [f0, f1, out] = [+process.argv[2], +process.argv[3], process.argv[4]]; const FPS = 30;
(async()=>{
 const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p = await b.newPage({viewport:{width:1920,height:1080}});
 await p.goto('http://127.0.0.1:8765/teseo.html' + (process.env.QS || ''));
 await p.waitForFunction('window.LISTO || (window.__err&&window.__err.length)',null,{timeout:300000});
 const err = await p.evaluate('window.__err'); if (err && err.length) { console.log('ERR', err); process.exit(1); }
 const ff = spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',''+FPS,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-r',''+FPS,out],{stdio:['pipe','inherit','inherit']});
 const T0 = Date.now();
 for (let f=f0; f<f1; f++){ await p.evaluate(t=>window.pintar(t), (f+0.5)/FPS); const buf = await p.screenshot({type:'jpeg',quality:92});
   if (!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
   if ((f-f0)%300===0) console.log(out, f, ((Date.now()-T0)/1000/(f-f0+1)).toFixed(2),'s/f'); }
 ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close(); console.log('FIN', out, ((Date.now()-T0)/1000).toFixed(0),'s'); })();

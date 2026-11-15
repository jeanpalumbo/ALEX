// node thumb.js -> mini/plate_*.png y mini/cut_*.png (recortes sobre verde)
const { chromium } = require('playwright');
(async()=>{
 const b = await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const p = await b.newPage({viewport:{width:1920,height:1080}});
 await p.goto('http://127.0.0.1:8765/teseo.html'); await p.waitForFunction('window.LISTO',null,{timeout:300000});
 await p.addStyleTag({content:'#cap,#titulo,#spoiler,#suscribete,#etiquetas,#flash{display:none!important}'});
 // fondos
 for (const [nm,t] of []) { await p.evaluate(t=>{ window.pintar(t); const T=window.__T; for (const n in T.CAST) T.CAST[n].root.visible=false; T.renderer.render(T.scene,T.cam); }, t); await p.screenshot({path:`mini/plate_${nm}.png`}); }
 const cortes = { _x:0, 
  teseo_espada: {n:'teseo', e:'grito', q:{bR:[-172,-8],cR:6,bL:[-60,40],cL:40,lean:-6,cabX:-8,pR:-12,pL:12,ry:-25}, prop:'espada', cam:[0,30,85, 0,32,0], fov:40},
  minotauro: {n:'minotauro', e:'enfado', q:{cabX:-22,bR:[-130,-45],bL:[-130,45],cR:50,cL:50,lean:-10,ry:10}, cam:[0,36,90, 0,36,0], fov:40, luz:1.9},
  teseo_ovillo: {n:'teseo', e:'sorpresa', q:{bR:[-95,-20],cR:30,bL:[-30,20],cL:40,cabX:-4,ry:15}, prop:'ovillo', cam:[0,24,46, 0,24,0], fov:40},
 };
 for (const nm in cortes) { const c = cortes[nm]; if (!c.n || nm!=='teseo_espada') continue;
  await p.evaluate(c=>{ const T=window.__T; window.pintar(5.5);
   T.scene.traverse(o=>{ if (o.parent===T.scene && !o.isLight) o.visible=false; });
   const ch=T.CAST[c.n]; ch.root.visible=true; T.ocultaProps(ch); const q=Object.assign({x:0,z:0,y:0},c.q); T.pose(ch,q,1); T.cara(ch,c.e);
   if (c.prop){ const pr=T.prop(ch,c.prop); pr.visible=true; if (c.prop==='espada') { pr.rotation.set(0,0,0); pr.scale.setScalar(1.5); } }
   ch.root.updateMatrixWorld(true);
   T.scene.background=new T.THREE.Color('#00ff00'); const f=T.scene.fog; T.scene.fog=null;
   T.hemi.intensity=c.luz||1.3; T.hemi.color.set('#fff0dd'); T.sol.intensity=2.4; T.sol.position.set(80,160,200); T.sol.target.position.set(0,20,0); T.sol.target.updateMatrixWorld();
   T.rim.intensity=3; T.rim.color.set('#ff9a3a'); T.rim.position.set(-60,120,-200); T.rim.target.position.set(0,20,0); T.rim.target.updateMatrixWorld();
   T.cam.position.set(c.cam[0],c.cam[1],c.cam[2]); T.cam.fov=c.fov; T.cam.updateProjectionMatrix(); T.cam.lookAt(c.cam[3],c.cam[4],c.cam[5]);
   T.renderer.toneMappingExposure=1.15; T.renderer.render(T.scene,T.cam); T.scene.fog=f; }, c);
  await p.screenshot({path:`mini/cut_${nm}.png`}); }
 await b.close(); })();

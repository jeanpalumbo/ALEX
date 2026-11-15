// Librería de escenarios: cada uno con primer plano, plano medio, fondo lejano, elementos vivos y su cielo/luz.
import { THREE, M, MAT, T, tex, fill, liso, caja, rnd, personaje, pose, cara, cuadrupedo, animaCuadrupedo, pajaro, serpienteCadena, colocaCadena, D, shade } from "./motor.js";
const BL = 16;
// ---- acumulador de bloques instanciados (rápido)
class Blq {
  constructor(g) { this.g = g; this.m = new Map(); }
  add(x, y, z, mat, s = BL) { const k = mat.uuid ? mat.uuid + s : mat.map(m => m.uuid).join() + s; if (!this.m.has(k)) this.m.set(k, { mat, s, pos: [] }); this.m.get(k).pos.push(x, y, z); }
  fin() { for (const { mat, s, pos } of this.m.values()) { const n = pos.length / 3, im = new THREE.InstancedMesh(new THREE.BoxGeometry(s, s, s), mat, n), mm = new THREE.Matrix4();
      for (let i = 0; i < n; i++) { mm.makeTranslation(pos[i * 3], pos[i * 3 + 1] + s / 2, pos[i * 3 + 2]); im.setMatrixAt(i, mm); } im.castShadow = true; im.receiveShadow = true; this.g.add(im); } this.m.clear(); }
}
// ---- piezas de decorado
function suelo(b, n, mat, relieve = 0, cx = 0, cz = 0, s = BL) {
  for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) { const x = cx + (i - n / 2) * s, z = cz + (j - n / 2) * s;
    const d = Math.hypot(x - cx, z - cz), h = relieve && d > 330 ? Math.floor(rnd(i * 37 + j * 11) * relieve * (d - 330) / 200) : 0;
    for (let k = 0; k <= h; k++) b.add(x, (k - 1) * s, z, k === h ? mat : liso("#7a5532")); } }
function roble(b, x, z, k, hoja = MAT.hoja, tronco = MAT.tronco) { const h = 4 + Math.floor(rnd(k) * 2);
  for (let j = 0; j < h; j++) b.add(x, j * BL, z, tronco);
  for (let dy = 0; dy < 2; dy++) for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) { if (Math.abs(i) === 2 && Math.abs(j) === 2 && rnd(k + i * 3 + j) < 0.6) continue; b.add(x + i * BL, (h - 2 + dy) * BL, z + j * BL, hoja); }
  for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) if (!(Math.abs(i) === 1 && Math.abs(j) === 1) || rnd(k + 9 + i + j) < 0.5) b.add(x + i * BL, h * BL, z + j * BL, hoja); b.add(x, (h + 1) * BL, z, hoja); }
function pino(b, x, z, k, hoja = liso("#2f5f2a", 0.2, 16, 35), nieve = null) { const h = 5 + Math.floor(rnd(k) * 3);
  for (let j = 0; j < h; j++) b.add(x, j * BL, z, MAT.tronco);
  for (let c = 0; c < 4; c++) { const r = 2 - Math.floor(c / 2), y = (2 + c * 1.2) * BL; for (let i = -r; i <= r; i++) for (let j = -r; j <= r; j++) if (Math.abs(i) + Math.abs(j) <= r + 1) b.add(x + i * BL, y, z + j * BL, nieve && c % 2 ? nieve : hoja); }
  b.add(x, (h + 1) * BL, z, nieve || hoja); }
function montanas(b, cz, n = 9, ancho = 2400, alto = 9, mat = liso("#7d8a96", 0.12, 16, 51), nieve = liso("#f2f6fa", 0.03, 16, 52), s = 48) {
  for (let m = 0; m < n; m++) { const cx = -ancho / 2 + (m + 0.5) * ancho / n + (rnd(m * 3) - 0.5) * 120, H = Math.floor(alto * (0.6 + 0.6 * rnd(m))), z = cz - rnd(m + 9) * 300;
    for (let y = 0; y < H; y++) { const r = H - y; for (let i = -r; i <= r; i++) for (let j = -1; j <= 1; j++) if (Math.abs(i) + Math.abs(j) * 2 <= r) b.add(cx + i * s, y * s, z + j * s, y > H * 0.66 && nieve ? nieve : mat, s); } } }
function nubes(b, n, y0, cz, rango = 2000, s = 30, mat = MAT.nube) {
  for (let k = 0; k < n; k++) { const x = (rnd(k * 7) - 0.5) * rango, z = cz - rnd(k * 3) * 500, y = y0 + rnd(k + 4) * 120;
    for (let i = 0; i < 4 + Math.floor(rnd(k) * 4); i++) b.add(x + i * s * 0.9, y + (i % 2) * s * 0.3, z + (i % 3) * s * 0.6, mat, s); } }
function columna(b, x, z, h = 6, base = MAT.marmol) { for (let k = 0; k < h; k++) b.add(x, k * BL, z, MAT.columna); b.add(x, h * BL, z, base, 20); }
function templo(b, x, z, ancho = 7, prof = 4, h = 6) {
  for (let i = -ancho; i <= ancho; i++) for (let j = -prof; j <= prof; j++) b.add(x + i * BL, -BL + 8, z + j * BL, MAT.marmol);
  for (let i = -ancho; i <= ancho; i += 2) { columna(b, x + i * BL, z + prof * BL, h); columna(b, x + i * BL, z - prof * BL, h); }
  for (let i = -ancho - 1; i <= ancho + 1; i++) for (let j = -prof - 1; j <= prof + 1; j++) b.add(x + i * BL, (h + 1) * BL + 4, z + j * BL, MAT.marmol);
  for (let r = 0; r < 3; r++) for (let i = -ancho + r * 2; i <= ancho - r * 2; i++) b.add(x + i * BL, (h + 2 + r) * BL + 4, z + (prof + 1) * BL, MAT.marmol); }
function casa(b, x, z, k, pared = MAT.ladrillo, techo = liso("#a8503a", 0.12, 16, 60)) { const w = 3 + Math.floor(rnd(k) * 2), h = 3;
  for (let y = 0; y < h; y++) for (let i = -w; i <= w; i++) for (const j of [-2, 2]) if (!(y < 2 && i === 0 && j === 2)) b.add(x + i * BL, y * BL, z + j * BL, pared);
  for (let y = 0; y < h; y++) for (let j = -1; j <= 1; j++) for (const i of [-w, w]) b.add(x + i * BL, y * BL, z + j * BL, pared);
  for (let r = 0; r < 3; r++) for (let i = -w - 1 + r; i <= w + 1 - r; i++) for (let j = -3 + r; j <= 3 - r; j++) if (Math.abs(i) === w + 1 - r || Math.abs(j) === 3 - r || r === 2) b.add(x + i * BL, (h + r) * BL, z + j * BL, techo); }
function rocas(b, n, cx, cz, rango, mat = MAT.piedra, s = 6) { for (let k = 0; k < n; k++) b.add(cx + (rnd(k * 5 + 1) - 0.5) * rango, 0, cz - 120 - rnd(k * 7 + 2) * rango * 0.5, mat, s + rnd(k) * 6); }
// plantas cruzadas (hierba alta, flores, juncos, setas)
const _pl = {};
function planta(g, tipo, x, z, s = 10, y = 0) {
  if (!_pl[tipo]) _pl[tipo] = new THREE.MeshLambertMaterial({ map: tex(8, 8, (px, w, h, r) => { const T2 = {
    hierba: () => { for (let x = 0; x < 8; x++) { const top = 2 + Math.floor(r(x, 1) * 5); for (let y = top; y < 8; y++) px(x, y, shade("#5f9e3a", 0.85 + 0.3 * r(x, y))); } },
    seca: () => { for (let x = 0; x < 8; x++) { const top = 3 + Math.floor(r(x, 1) * 4); for (let y = top; y < 8; y++) px(x, y, shade("#b8a050", 0.85 + 0.3 * r(x, y))); } },
    junco: () => { for (const x of [1, 3, 5, 6]) { for (let y = 1; y < 8; y++) px(x, y, "#4f7a2a"); px(x, 1, "#6b4424"); px(x, 2, "#6b4424"); } },
    seta: () => { for (let y = 4; y < 8; y++) { px(3, y, "#e8e0d0"); px(4, y, "#e8e0d0"); } for (let x = 1; x < 7; x++) { px(x, 3, "#c8302a"); px(x, 2, x > 1 && x < 6 ? "#c8302a" : "#0000"); } px(2, 3, "#fff"); px(5, 2, "#fff"); },
    roja: () => { for (let y = 3; y < 8; y++) px(4, y, "#3f7f2e"); px(4, 1, "#d33a2f"); px(3, 2, "#d33a2f"); px(5, 2, "#d33a2f"); px(4, 2, "#ffe04a"); },
    amarilla: () => { for (let y = 3; y < 8; y++) px(4, y, "#3f7f2e"); px(4, 1, "#f2c84a"); px(3, 2, "#f2c84a"); px(5, 2, "#f2c84a"); px(4, 2, "#a06a10"); },
    azul: () => { for (let y = 3; y < 8; y++) px(4, y, "#3f7f2e"); px(4, 1, "#5a7ad8"); px(3, 2, "#5a7ad8"); px(5, 2, "#5a7ad8"); px(4, 2, "#ffffff"); },
    nenufar: () => { for (let x = 1; x < 7; x++) for (let y = 3; y < 7; y++) if ((x - 3.5) ** 2 + (y - 5) ** 2 < 7) px(x, y, "#3f8f3a"); px(4, 4, "#f2a0c0"); px(3, 4, "#f2a0c0"); },
    hueso: () => { for (let x = 1; x < 7; x++) px(x, 6, "#e8e2d0"); px(1, 5, "#e8e2d0"); px(1, 7, "#e8e2d0"); px(6, 5, "#e8e2d0"); px(6, 7, "#e8e2d0"); },
  }; T2[tipo](); }, tipo.length * 13), transparent: true, alphaTest: 0.5, side: THREE.DoubleSide });
  for (const r of [0.78, -0.78]) { const p = new THREE.Mesh(new THREE.PlaneGeometry(s, s), _pl[tipo]); p.position.set(x, y + s / 2, z); p.rotation.y = r; g.add(p); } }
function alfombra(g, tipos, n, cx, cz, rango, excluye = () => false, smin = 7, sv = 6) { for (let k = 0; k < n; k++) { const x = cx + (rnd(k * 7 + 1) - 0.5) * rango, z = cz + (rnd(k * 11 + 2) - 0.5) * rango; if (excluye(x, z)) continue; planta(g, tipos[Math.floor(rnd(k * 3) * tipos.length)], x, z, smin + rnd(k + 5) * sv); } }
// antorcha con luz que parpadea
function antorcha(g, vivos, x, y, z, k, luz = true, inten = 1) { const a = new THREE.Group(); a.add(caja(2, 10, 2, MAT.madera, 0, 5, 0)); const f = caja(3, 4, 3, MAT.brillo("#ffb347"), 0, 12, 0); a.add(f); a.add(caja(1.6, 2, 1.6, MAT.brillo("#fff1a0"), 0, 12.6, 0)); a.position.set(x, y, z); g.add(a);
  let l = null; if (luz) { l = new THREE.PointLight("#ffa040", 2200 * inten, 180, 1.6); l.position.set(x, y + 14, z); g.add(l); }
  vivos.push(t => { const s = 1 + 0.25 * Math.sin(t * 19 + k) + 0.1 * Math.sin(t * 31 + k * 2); f.scale.set(1, s, 1); if (l) l.intensity = 2200 * inten * (0.85 + 0.15 * s); }); }
function hoguera(g, vivos, x, z, k) { for (const [dx, dz] of [[-4, 0], [4, 0], [0, -4], [0, 4]]) g.add(caja(3, 2, 8, MAT.tronco, x + dx, 1, z + dz)); const fs = [];
  for (let i = 0; i < 6; i++) { const f = caja(3, 6, 3, MAT.brillo(i % 2 ? "#ffb347" : "#ff7a2a"), x + (rnd(i) - 0.5) * 6, 4, z + (rnd(i + 3) - 0.5) * 6); g.add(f); fs.push(f); }
  const l = new THREE.PointLight("#ff9a40", 5000, 260, 1.5); l.position.set(x, 16, z); g.add(l);
  vivos.push(t => { fs.forEach((f, i) => { const s = 1 + 0.4 * Math.sin(t * 15 + i * 2); f.scale.set(1, s, 1); f.position.y = 3 * s; }); l.intensity = 5000 * (0.85 + 0.15 * Math.sin(t * 13)); }); }
// pájaros volando en bandada (fondo vivo)
function bandada(g, vivos, n, y, z, color = "#3a3a4a", vel = 40, rango = 1600, k0 = 0) { const ps = []; for (let i = 0; i < n; i++) { const p = pajaro(color); p.g.scale.setScalar(1.2); g.add(p.g); ps.push(p); }
  vivos.push(t => ps.forEach((p, i) => { const x = ((t * vel + i * 47 + k0 * 300) % rango) - rango / 2; p.g.position.set(x, y + 20 * Math.sin(i * 1.7 + t * 0.5), z + i * 12 - 40); p.g.rotation.y = Math.PI / 2; const a = 0.6 * Math.sin(t * 10 + i); p.aL.rotation.z = a; p.aR.rotation.z = -a; })); }
// partículas de ambiente (hojas, nieve, cenizas, almas, luciérnagas): cubitos que caen/flotan en bucle
function ambiente(g, vivos, n, tipo, cx, cz, rango, y0 = 0, alto = 160) {
  const col = { hojas: ["#5f9e3a", "#d9a03c", "#a6c050"], nieve: ["#ffffff"], cenizas: ["#ff7a2a", "#ffb347", "#555"], almas: ["#9ad8ff", "#cfefff"], luciernagas: ["#e8ff7a"], polvo: ["#d9c290"], esporas: ["#b0ff8a"] }[tipo];
  const geo = new THREE.BoxGeometry(1, 1, 1), ms = [];
  for (let i = 0; i < n; i++) { const m = new THREE.Mesh(geo, tipo === "almas" || tipo === "luciernagas" || tipo === "cenizas" || tipo === "esporas" ? MAT.brillo(col[i % col.length]) : liso(col[i % col.length], 0.05, 2)); m.scale.setScalar(tipo === "almas" ? 2.4 : (tipo === "nieve" ? 1.1 : 0.9)); g.add(m); ms.push(m); }
  vivos.push(t => ms.forEach((m, i) => { const ph = rnd(i * 3), v = 0.5 + rnd(i * 5);
    const sube = tipo === "almas" || tipo === "cenizas" || tipo === "luciernagas" || tipo === "esporas", q = ((t * 0.05 * v * (sube ? 1.4 : 1) + ph) % 1);
    const y = sube ? y0 + q * alto : y0 + alto * (1 - q);
    m.position.set(cx + (rnd(i * 7) - 0.5) * rango + 12 * Math.sin(t * (0.7 + v) + i), y, cz + (rnd(i * 11) - 0.5) * rango + 10 * Math.cos(t * 0.6 + i));
    m.rotation.set(t * 2 + i, t * 1.5, 0); })); }
// agua animada (textura que se desplaza) y cascada
function agua(g, vivos, x, z, w, d, y = 0.6, mat = MAT.agua) { const tx = mat.map.clone(); tx.needsUpdate = true; tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.repeat.set(w / 16, d / 16);
  const m = mat.clone(); m.map = tx; const p = caja(w, 1.2, d, m, x, y, z); p.castShadow = false; g.add(p); vivos.push(t => { tx.offset.set(t * 0.08, Math.sin(t * 0.7) * 0.05); }); return p; }
function cascada(g, vivos, x, y0, z, alto, ancho = 32) { const tx = T.agua.clone(); tx.needsUpdate = true; tx.wrapS = tx.wrapT = THREE.RepeatWrapping; tx.repeat.set(ancho / 16, alto / 16);
  const m = new THREE.MeshLambertMaterial({ map: tx, transparent: true, opacity: 0.85, emissive: "#203a60" }); const c = caja(ancho, alto, 4, m, x, y0 + alto / 2, z); c.castShadow = false; g.add(c);
  vivos.push(t => { tx.offset.y = t * 0.9; }); ambiente(g, vivos, 30, "nieve", x, z + 10, ancho, y0 - 10, 30); }
// extras que pasean (aldeanos) entre dos puntos
const ROPAS = ["#b5452f", "#3f6fb5", "#d9a630", "#5f9e3a", "#7f5aa8", "#c96f52", "#8a8a8a", "#e9dcc0"];
const PIELES = ["#f0c8a0", "#d39a6a", "#a8704a", "#e8b88e", "#8a5a3a"];
const PELOS = ["#3a2414", "#1f1b17", "#c27a3a", "#e8e8e8", "#7a4b2c", "#2b1e16"];
export function extra(k, opts = {}) { return personaje(Object.assign({ seed: 300 + k * 17, piel: PIELES[k % 5], pelo: PELOS[k % 6], ropa: ROPAS[k % 8], cinto: "#6b4424", falda: k % 3 !== 0, faldaLarga: k % 3 === 0, melena: k % 4 === 1, barba: k % 5 === 2 ? PELOS[k % 6] : undefined, sandalia: "#5a3a1a" }, opts), opts.escala || 0.92); }
function paseantes(g, vivos, n, puntos, k0 = 0, opts = {}) { const xs = []; for (let i = 0; i < n; i++) { const e = extra(k0 + i, opts); g.add(e.root); xs.push(e); }
  vivos.push(t => xs.forEach((e, i) => { const [a, b] = puntos[i % puntos.length], per = 14 + rnd(i + k0) * 8, ph = ((t / per + rnd(i * 5 + k0)) % 1), ida = ph < 0.5, q = ida ? ph * 2 : 2 - ph * 2;
    const x = a[0] + (b[0] - a[0]) * q, z = a[1] + (b[1] - a[1]) * q, ang = Math.atan2(b[0] - a[0], b[1] - a[1]) / D + (ida ? 0 : 180);
    pose(e, { x, z, ry: ang, andar: (x + z) / 5, amp: 1, seed: i, cabY: 15 * Math.sin(t * 0.7 + i) }, t); cara(e, Math.sin(t * 0.3 + i) > 0.7 ? "habla" : "normal"); })); return xs; }
function quietos(g, vivos, lista, k0 = 0, opts = {}) { const xs = []; lista.forEach(([x, z, ry, accion], i) => { const e = extra(k0 + i, opts); g.add(e.root); xs.push(e);
  vivos.push(t => { const s = Math.sin(t * 2 + i * 1.7); const p = { x, z, ry, seed: i, cabY: 20 * Math.sin(t * 0.8 + i) };
    if (accion === "charla") { p.bR = [-30 + 20 * s, 10]; p.cR = 40; cara(e, Math.sin(t * 4 + i) > 0 ? "habla" : "risa"); }
    else if (accion === "vende") { p.bR = [-60, 0]; p.bL = [-60, 0]; p.cR = 50; p.cL = 50; p.cabX = 8 * s; cara(e, "habla"); }
    else if (accion === "aplaude") { p.bR = [-80, 25 + 15 * Math.sin(t * 12 + i)]; p.bL = [-80, -25 - 15 * Math.sin(t * 12 + i)]; p.cR = 60; p.cL = 60; cara(e, "risa"); }
    else if (accion === "sentado") { p.sentado = 1; cara(e, "normal"); }
    else if (accion === "trabaja") { p.bR = [-90 + 50 * Math.abs(s), 0]; p.bL = [-90 + 50 * Math.abs(s), 0]; p.lean = 25; cara(e, "sudor"); }
    pose(e, p, t); }); }); return xs; }
function animales(g, vivos, n, o, cx, cz, rango, k0 = 0) { const as = []; for (let i = 0; i < n; i++) { const a = cuadrupedo(Object.assign({ seed: 200 + i + k0 }, o)); g.add(a.g); as.push(a); }
  vivos.push(t => as.forEach((a, i) => { const ph = t * 0.15 + rnd(i * 3 + k0) * 6, x = cx + (rnd(i * 5 + k0) - 0.5) * rango + 30 * Math.sin(ph), z = cz + (rnd(i * 9 + k0) - 0.5) * rango * 0.6 + 20 * Math.cos(ph * 0.7);
    a.g.position.set(x, 0, z); a.g.rotation.y = Math.atan2(Math.cos(ph), -0.7 * Math.sin(ph)) + (i % 2) * 0.3; animaCuadrupedo(a, t + i, Math.abs(Math.sin(ph)) > 0.3 ? 0.4 : 0, { cabX: Math.sin(t + i) > 0.5 ? 35 : 0 }); })); return as; }
// estrellas y constelaciones (cielo de noche)
function estrellas(g, vivos, n = 400, r = 1500) { const geo = new THREE.BufferGeometry(), p = []; for (let i = 0; i < n; i++) { const th = rnd(i) * Math.PI * 2, ph = rnd(i + 7) * 0.45 * Math.PI; p.push(Math.cos(th) * Math.cos(ph) * r, Math.sin(ph) * r + 80, Math.sin(th) * Math.cos(ph) * r); }
  geo.setAttribute("position", new THREE.Float32BufferAttribute(p, 3)); const m = new THREE.PointsMaterial({ color: "#ffffff", size: 4, sizeAttenuation: false, fog: false }); const s = new THREE.Points(geo, m); g.add(s); vivos.push(t => m.opacity = 1); return s; }
function luna(g, x, y, z, s = 60) { const l = caja(s, s, 4, new THREE.MeshBasicMaterial({ color: "#f5f0d6", fog: false }), x, y, z); l.castShadow = false; l.lookAt(0, 30, 0); g.add(l); }
function sol_(g, x, y, z, s = 90, col = "#fff2b0") { const l = caja(s, s, 4, new THREE.MeshBasicMaterial({ color: col, fog: false }), x, y, z); l.castShadow = false; l.lookAt(0, 30, 0); g.add(l); }
// ======================= ESCENARIOS
// cada uno: { cielo, luz, build(g, vivos) -> anclas }
export const SETS = {
  olimpo: { cielo: "dia_alto", build(g, v) { const b = new Blq(g);
    suelo(b, 30, MAT.marmol); templo(b, 0, -170, 9, 4, 7); for (const x of [-140, -90, 90, 140]) columna(b, x, -30, 6);
    
    nubes(b, 60, -120, 200, 2400, 34); nubes(b, 40, -60, -300, 2400, 40); nubes(b, 30, 120, -500, 2600, 48);
    for (let i = -14; i <= 14; i++) b.add(i * BL, -2 * BL, 260, MAT.nube, 20);
    templo(b, -520, -520, 6, 3, 6); templo(b, 560, -460, 5, 3, 5);
    b.fin();
    cascada(g, v, -300, -220, -150, 230, 40); cascada(g, v, 320, -220, -200, 230, 36);
    const tr = new THREE.Group(); tr.add(caja(28, 20, 22, MAT.oro, 0, 10, 0)); tr.add(caja(28, 40, 6, MAT.oro, 0, 40, -10)); tr.add(caja(4, 30, 4, MAT.oro, -12, 35, -10)); tr.add(caja(4, 30, 4, MAT.oro, 12, 35, -10)); tr.position.set(40, 0, -60); g.add(tr);
    alfombra(g, ["roja", "amarilla", "azul", "hierba"], 120, 0, 120, 500, (x, z) => Math.abs(x) < 120 && z < 120);
    quietos(g, v, [[-120, -100, 20, "charla"], [-100, -110, -160, "charla"], [140, -90, -30, "aplaude"], [170, -100, -40, "charla"]], 0, { faldaLarga: 1, ropa: "#f2efe6", laurel: 1 });
    bandada(g, v, 7, 180, -260, "#ffffff", 50); ambiente(g, v, 50, "polvo", 0, 0, 400, 0, 200);
    for (const x of [-60, 60]) { antorcha(g, v, x, 0, 20, x, true, 0.6); }
    return { centro: [0, 0], trono: [40, -60] }; } },
  cuna: { cielo: "noche_interior", build(g, v) { const b = new Blq(g);
    suelo(b, 16, MAT.madera); for (let i = -7; i <= 7; i++) for (let k = 0; k < 7; k++) { b.add(i * BL, k * BL, -110, MAT.ladrillo); }
    for (let j = -6; j <= 7; j++) for (let k = 0; k < 7; k++) { b.add(-118, k * BL, j * BL, MAT.ladrillo); b.add(118, k * BL, j * BL, MAT.ladrillo); }
    b.fin(); const c = new THREE.Group(); for (const [x, z] of [[-14, -10], [14, -10], [-14, 10], [14, 10]]) c.add(caja(3, 22, 3, MAT.madera, x, 11, z));
    c.add(caja(30, 4, 22, MAT.madera, 0, 9, 0)); c.add(caja(28, 3, 20, MAT.tela, 0, 12, 0)); for (let x = -12; x <= 12; x += 4) { c.add(caja(1.4, 10, 1.4, MAT.madera, x, 18, -10)); c.add(caja(1.4, 10, 1.4, MAT.madera, x, 18, 10)); }
    c.add(caja(31, 2, 2, MAT.madera, 0, 23, -10)); c.add(caja(31, 2, 2, MAT.madera, 0, 23, 10)); g.add(c);
    g.add(caja(34, 34, 2, MAT.brillo("#1b2a55"), 40, 70, -101)); g.add(caja(10, 10, 1, MAT.brillo("#f5f0d6"), 47, 77, -100));
    for (const [x, y, w, h] of [[40, 88, 38, 3], [40, 52, 38, 3], [22, 70, 3, 38], [58, 70, 3, 38], [40, 70, 2, 34], [40, 70, 34, 2]]) g.add(caja(w, h, 3, MAT.madera, x, y, -99));
    g.add(caja(60, 0.6, 46, M(tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#8a2f2f", r, 0.08); for (let i = 0; i < 16; i++) { px(i, 0, "#d9a630"); px(i, 15, "#d9a630"); px(0, i, "#d9a630"); px(15, i, "#d9a630"); } }, 81)), 0, 0.3, 14));
    for (let k = 0; k < 3; k++) { g.add(caja(30, 3, 10, MAT.madera, -60, 36 + k * 18, -100)); for (let j = 0; j < 4; j++) g.add(caja(5, 8, 5, liso(["#b5452f", "#3f6fb5", "#d9a630", "#5f9e3a"][(k + j) % 4], 0.1, 4), -72 + j * 8, 41.5 + k * 18, -100)); }
    g.add(caja(24, 30, 14, MAT.madera, 80, 15, -90)); g.add(caja(8, 6, 8, liso("#c8a060", 0.1, 4), 80, 33, -90));
    antorcha(g, v, -60, 40, -102, 1, true, 1.3); antorcha(g, v, 100, 40, -102, 2, true, 1.0); ambiente(g, v, 30, "polvo", 0, 0, 200, 0, 100);
    const vela = new THREE.PointLight("#ffb050", 4500, 260, 1.6); vela.position.set(30, 55, 50); vela.castShadow = true; g.add(vela); v.push(t => vela.intensity = 4500 * (1 + 0.08 * Math.sin(t * 17)));
    return { cuna: [0, 0] }; } },
  tebas: { cielo: "dia", build(g, v) { const b = new Blq(g);
    suelo(b, 40, liso("#c9b58a", 0.1, 16, 62)); for (let i = -20; i <= 20; i++) for (let j = -1; j <= 1; j++) b.add(i * BL, -BL + 1, 40 + j * BL, liso("#a89a80", 0.12, 16, 63));
    for (let k = 0; k < 10; k++) casa(b, -280 + k * 64 + (k % 2) * 10, -110 - (k % 3) * 40, k);
    for (let k = 0; k < 6; k++) casa(b, -260 + k * 110, 200 + (k % 2) * 30, k + 20, liso("#e8dcc0", 0.08, 16, 64), liso("#c8603a", 0.12, 16, 65));
    templo(b, 0, -420, 6, 3, 6); montanas(b, -900, 10, 2600, 7, liso("#8a9a6a", 0.12, 16, 53), null);
    for (let k = 0; k < 8; k++) roble(b, -500 + k * 140, -300 - (k % 2) * 60, k + 50);
    nubes(b, 25, 260, -700, 2600, 34); b.fin();
    // mercado: puestos con toldos
    for (let k = 0; k < 4; k++) { const x = -150 + k * 100; g.add(caja(30, 10, 14, MAT.madera, x, 5, -30)); g.add(caja(34, 2, 18, liso(["#d33a2f", "#3f6fb5", "#d9a630", "#5f9e3a"][k], 0.08, 8), x, 26, -30)); for (const s of [-1, 1]) g.add(caja(2, 22, 2, MAT.madera, x + s * 15, 11, -22));
      for (let j = 0; j < 5; j++) g.add(caja(4, 4, 4, liso(["#e0302a", "#f2c84a", "#7fbf4a", "#ff8a2a"][j % 4], 0.1, 4), x - 10 + j * 5, 12, -30)); }
    paseantes(g, v, 9, [[[-300, -70], [300, -70]], [[-250, -90], [260, -80]], [[200, -60], [-220, -75]]], 10);
    quietos(g, v, [[-150, -14, 0, "vende"], [-50, -14, 0, "vende"], [50, -14, 0, "vende"], [150, -14, 0, "vende"], [-220, -50, 120, "charla"], [230, -50, -120, "charla"]], 40);
    animales(g, v, 4, { color: "#e8e8e8", largo: 14, alto: 8, patas: 6, ancho: 8, orejas: 1, cola: 2 }, 0, -80, 400, 5);
    bandada(g, v, 6, 200, -300); ambiente(g, v, 40, "polvo", 0, 0, 500, 0, 120);
    return { plaza: [0, 40] }; } },
  campo: { cielo: "amanecer", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.hierba, 4); for (let k = 0; k < 26; k++) { const x = (rnd(k * 3) - 0.5) * 1100, z = -160 - rnd(k * 5) * 500; roble(b, x, z, k); }
    for (let k = 0; k < 10; k++) roble(b, (rnd(k * 13) > 0.5 ? 1 : -1) * (300 + rnd(k * 7) * 300), 180 + rnd(k * 7) * 200, k + 30);
    montanas(b, -1100, 11, 3000, 9); nubes(b, 30, 280, -800, 2800, 36); rocas(b, 14, 0, 60, 600); b.fin();
    alfombra(g, ["hierba", "hierba", "roja", "amarilla", "azul"], 420, 0, 0, 640, (x, z) => Math.abs(z) < 50 && Math.abs(x) < 120);
    // dianas de tiro con arco
    for (const x of [-120, 0, 120]) { g.add(caja(2, 24, 2, MAT.madera, x, 12, -120)); g.add(caja(18, 18, 2, M(tex(8, 8, (px, w, h, r) => { for (let y = 0; y < 8; y++) for (let x2 = 0; x2 < 8; x2++) { const d = Math.max(Math.abs(x2 - 3.5), Math.abs(y - 3.5)); px(x2, y, d > 3 ? "#e9dcc0" : d > 2 ? "#d33a2f" : d > 1 ? "#e9dcc0" : "#d33a2f"); } }, 66)), x, 26, -119)); }
    bandada(g, v, 8, 170, -400); ambiente(g, v, 50, "hojas", 0, 0, 600, 0, 120); animales(g, v, 3, { color: "#8a6a4a", largo: 16, alto: 9, patas: 9, astas: "#c8b080", orejas: 1, cola: 2 }, 260, -60, 200, 1);
    return {}; } },
  delfos: { cielo: "atardecer", build(g, v) { const b = new Blq(g);
    suelo(b, 40, liso("#9a8a70", 0.15, 16, 67), 6); templo(b, 0, -190, 6, 4, 6);
    
    montanas(b, -700, 9, 2400, 10, liso("#8a7a6a", 0.12, 16, 54)); for (let k = 0; k < 16; k++) pino(b, (rnd(k * 3) - 0.5) * 1000, -260 - rnd(k) * 300, k); nubes(b, 20, 300, -800, 2600, 36, liso("#ffd0a0", 0.05, 8)); b.fin();
    // grieta con humo del oráculo + trípode
    g.add(caja(10, 18, 10, MAT.oro, 0, 9, -30)); hoguera(g, v, 0, -40, 1); ambiente(g, v, 70, "esporas", 0, -40, 30, 10, 140);
    quietos(g, v, [[-60, -40, 30, "charla"], [60, -40, -30, "charla"]], 60, { faldaLarga: 1, ropa: "#f2efe6", melena: 1 });
    for (const x of [-80, 80]) antorcha(g, v, x, 0, -20, x, true, 0.8); bandada(g, v, 5, 200, -300, "#2a2a2a", 30);
    return {}; } },
  palacio: { cielo: "interior", build(g, v) { const b = new Blq(g);
    suelo(b, 24, M(tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade((Math.floor(x / 8) + Math.floor(y / 8)) % 2 ? "#e8e2d4" : "#8a3a3a", 0.95 + 0.1 * r(x, y))); }, 68)));
    for (let i = -11; i <= 11; i++) for (let k = 0; k < 9; k++) b.add(i * BL, k * BL, -180, k === 4 ? MAT.oro : MAT.marmol);
    for (let j = -11; j <= 6; j++) for (let k = 0; k < 9; k++) { b.add(-184, k * BL, j * BL, MAT.marmol); b.add(184, k * BL, j * BL, MAT.marmol); }
    for (const x of [-120, -60, 60, 120]) for (const z of [-120, -20]) columna(b, x, z, 7, MAT.oro);
    for (let k = 0; k < 2; k++) for (let i = -2; i <= 2; i++) b.add(i * BL, k * BL, -150, MAT.oro); b.fin();
    g.add(caja(40, 60, 2, liso("#7f2a3a", 0.08, 8), -100, 90, -170)); g.add(caja(40, 60, 2, liso("#7f2a3a", 0.08, 8), 100, 90, -170)); g.add(caja(16, 16, 2, MAT.oro, 0, 120, -170));
    g.add(caja(60, 1, 160, liso("#a8303a", 0.06, 8), 0, 0.6, -60));
    for (const x of [-160, -100, 100, 160]) antorcha(g, v, x, 40, -176, x, true, 1.0);
    // la tinaja de bronce (enterrada a medias)
    const tin = new THREE.Group(); const br = liso("#b07a3a", 0.12, 8, 69); tin.add(caja(22, 18, 22, br, 0, 9, 0)); tin.add(caja(18, 4, 18, br, 0, 20, 0)); tin.add(caja(24, 2, 24, liso("#8a5a2a", 0.1, 8), 0, 22, 0)); tin.position.set(70, 0, -70); tin.name = "tinaja"; g.add(tin);
    quietos(g, v, [[-150, -40, 60, "charla"], [-150, 10, 70, "charla"], [150, -40, -60, "aplaude"]], 70, { cascoPenacho: "#c83a2f", casco: "#a8afbd", ropa: "#8a3b3b", peto: "#c8a040" });
    ambiente(g, v, 40, "polvo", 0, -40, 300, 0, 140);
    return { tinaja: [70, -70], trono: [0, -150] }; } },
  nemea: { cielo: "tarde", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.hierba, 5);
    for (let k = 0; k < 40; k++) { const x = (rnd(k * 3) - 0.5) * 1200, z = -100 - rnd(k * 5) * 500; if (Math.abs(x - 150) < 90 && z > -200) continue; roble(b, x, z, k, liso("#2f6a26", 0.22, 16, 36)); }
    for (let k = 0; k < 14; k++) roble(b, (rnd(k * 17) > 0.5 ? 1 : -1) * (300 + rnd(k * 7) * 300), 160 + rnd(k * 7) * 250, k + 60, liso("#2f6a26", 0.22, 16, 36));
    // cueva: montaña de piedra con agujero
    for (let y = 0; y < 7; y++) for (let i = -8 + y; i <= 8 - y; i++) for (let j = -4; j <= 3; j++) { if (y < 3 && Math.abs(i) < 2 && j > -2) continue; b.add(200 + i * BL, y * BL, -150 + j * BL, MAT.piedra); }
    for (let i = -1; i <= 1; i++) for (let y = 0; y < 3; y++) b.add(200 + i * BL, y * BL, -210, liso("#1a1612", 0.1));
    montanas(b, -1100, 10, 3000, 9, liso("#6a7a5a", 0.12, 16, 55)); nubes(b, 20, 300, -900, 2600, 36, liso("#ffd8b0", 0.05, 8)); rocas(b, 20, 0, 40, 700); b.fin();
    alfombra(g, ["hierba", "hierba", "hierba", "seta", "hueso", "seca"], 500, 0, 0, 700, (x, z) => Math.abs(z) < 40 && Math.abs(x) < 140);
    ambiente(g, v, 70, "hojas", 0, 0, 700, 0, 150); bandada(g, v, 6, 190, -300, "#2a2a2a", 35); ambiente(g, v, 30, "luciernagas", 0, -60, 400, 5, 60);
    return { cueva: [200, -120] }; } },
  lerna: { cielo: "niebla_verde", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.barro, 3); for (let k = 0; k < 30; k++) { const x = (rnd(k * 3) - 0.5) * 1200, z = -160 - rnd(k * 5) * 500; roble(b, x, z, k, liso("#4a5a2a", 0.25, 16, 37), liso("#3a3020", 0.2, 16, 38)); }
    for (let k = 0; k < 12; k++) roble(b, (rnd(k * 19) > 0.5 ? 1 : -1) * (300 + rnd(k) * 300), 200 + rnd(k) * 200, k + 40, liso("#4a5a2a", 0.25, 16, 37), liso("#3a3020", 0.2, 16, 38));
    montanas(b, -1100, 9, 3000, 8, liso("#4a5a4a", 0.12, 16, 56), null); rocas(b, 16, 0, 80, 600, liso("#5a5a4a", 0.15)); b.fin();
    agua(g, v, 0, -30, 700, 260, 0.6, MAT.pantano); alfombra(g, ["junco", "junco", "hierba", "seca"], 300, 0, 120, 800, (x, z) => z < 110 && z > -170);
    for (let k = 0; k < 40; k++) { const p = caja(8 + rnd(k) * 6, 0.6, 8 + rnd(k) * 6, liso("#3f8f3a", 0.15, 4, 82), (rnd(k * 3) - 0.5) * 600, 1.4, -30 + (rnd(k * 7) - 0.5) * 240); g.add(p); if (k % 3 === 0) g.add(caja(3, 2, 3, liso("#f2a0c0", 0.05, 4), p.position.x, 2.4, p.position.z)); }
    ambiente(g, v, 70, "esporas", 0, -30, 600, 0, 60); ambiente(g, v, 40, "luciernagas", 0, 0, 600, 5, 80); bandada(g, v, 4, 160, -300, "#1a1a1a", 25);
    return {}; } },
  cielo_noche: { cielo: "noche_estrellas", build(g, v) { const b = new Blq(g);
    suelo(b, 40, liso("#2a3a2a", 0.15, 16, 70), 3); montanas(b, -900, 10, 2600, 8, liso("#1f2a3a", 0.12, 16, 57), liso("#c8d0e0", 0.05, 16, 58)); for (let k = 0; k < 20; k++) pino(b, (rnd(k * 3) - 0.5) * 1100, -200 - rnd(k) * 300, k, liso("#1a2f1a", 0.2)); b.fin();
    estrellas(g, v, 700); luna(g, -400, 600, -1200, 90);
    // constelación de Cáncer: cubos brillantes unidos
    const pts = [[0, 420], [60, 470], [120, 440], [60, 380], [180, 500], [-60, 500]]; const cons = new THREE.Group(); pts.forEach(([x, y]) => cons.add(caja(26, 26, 26, MAT.brillo("#fff6b0"), x, y, -700))); for (let i = 0; i < pts.length - 1; i++) { const [a1, b1] = pts[i], [a2, b2] = pts[i + 1]; for (let k = 1; k < 6; k++) cons.add(caja(6, 6, 6, MAT.brillo("#c8d8ff"), a1 + (a2 - a1) * k / 6, b1 + (b2 - b1) * k / 6, -700)); }
    cons.name = "constelacion"; g.add(cons); ambiente(g, v, 40, "luciernagas", 0, 0, 500, 5, 100); hoguera(g, v, -80, 60, 3);
    return {}; } },
  nieve: { cielo: "invierno", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.nieve, 5); for (let k = 0; k < 40; k++) { const x = (rnd(k * 3) - 0.5) * 1300, z = -120 - rnd(k * 5) * 520; pino(b, x, z, k, undefined, liso("#f2f6fa", 0.03, 16, 52)); }
    for (let k = 0; k < 12; k++) pino(b, (rnd(k * 21) > 0.5 ? 1 : -1) * (300 + rnd(k) * 300), 200 + rnd(k) * 220, k + 50, undefined, liso("#f2f6fa", 0.03, 16, 52));
    montanas(b, -1100, 10, 3000, 11); rocas(b, 14, 0, 60, 600, liso("#9aa0a8", 0.12)); b.fin();
    ambiente(g, v, 160, "nieve", 0, 0, 700, 0, 220); bandada(g, v, 5, 220, -300, "#2a2a2a", 30);
    return {}; } },
  establos: { cielo: "dia", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.hierba, 4);
    for (let i = -10; i <= 10; i++) for (let j = -5; j <= 5; j++) b.add(i * BL, -BL + 0.5, -120 + j * BL, MAT.estiercol);
    for (let i = -11; i <= 11; i++) for (let k = 0; k < 3; k++) { b.add(i * BL, k * BL, -210, MAT.madera); if (Math.abs(i) > 2 || k > 1) b.add(i * BL, k * BL, -30, MAT.madera); }
    for (let j = -5; j <= 5; j++) for (let k = 0; k < 3; k++) { b.add(-184, k * BL, -120 + j * BL, MAT.madera); b.add(184, k * BL, -120 + j * BL, MAT.madera); }
    for (let r = 0; r < 4; r++) for (let i = -12 + r; i <= 12 - r; i++) b.add(i * BL, (3 + r) * BL, -260 + r * 0, liso("#8a3a2a", 0.12, 16, 71));
    for (let k = 0; k < 8; k++) b.add(-260 + (k % 2) * 16, Math.floor(k / 2) * BL, 40, MAT.paja);
    for (let k = 0; k < 20; k++) roble(b, (rnd(k * 3) - 0.5) * 1300, -330 - rnd(k) * 350, k + 70); montanas(b, -1200, 9, 3000, 8, liso("#7a8a6a", 0.12, 16, 59), null); nubes(b, 25, 280, -800, 2600, 34); b.fin();
    // ríos que cruzan el establo (se activan en la escena)
    const r1 = agua(g, v, -320, -120, 120, 600); r1.name = "rio1"; const r2 = agua(g, v, 320, -120, 120, 600); r2.name = "rio2";
    animales(g, v, 9, { color: "#f2f2f2", lomo: "#2a2a2a", largo: 20, alto: 11, patas: 9, ancho: 11, cuernos: "#e8e0c8", hocico: "#e8a0a0", cola: 4 }, 0, -120, 300, 3);
    alfombra(g, ["hierba", "amarilla", "hierba", "seca"], 300, 0, 120, 800, (x, z) => z < 20 && Math.abs(x) < 220);
    ambiente(g, v, 60, "polvo", 0, -120, 400, 0, 60); bandada(g, v, 7, 200, -400); quietos(g, v, [[-220, 40, 90, "trabaja"], [240, 30, -90, "charla"]], 80);
    return {}; } },
  lago: { cielo: "tormenta", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.hierba, 4); for (let k = 0; k < 30; k++) { const x = (rnd(k * 3) - 0.5) * 1300, z = -360 - rnd(k) * 400; pino(b, x, z, k); }
    montanas(b, -1100, 10, 3000, 9, liso("#5a6a7a", 0.12, 16, 60), null); b.fin(); agua(g, v, 0, -160, 900, 340);
    alfombra(g, ["junco", "hierba", "junco"], 260, 0, 60, 900, (x, z) => z < 20 || (Math.abs(x) < 100 && z < 90)); ambiente(g, v, 60, "hojas", 0, 0, 700, 0, 160);
    return {}; } },
  creta: { cielo: "dia", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.arena, 2); for (let k = 0; k < 14; k++) { const x = (rnd(k * 3) - 0.5) * 1100, z = -40 - rnd(k) * 100; if (Math.abs(x) < 160) continue; for (let j = 0; j < 6; j++) b.add(x + j * 2, j * BL, z, MAT.tronco); for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1], [2, 0], [-2, 0]]) b.add(x + dx * BL, 6 * BL - Math.abs(dx) * 4, z + dz * BL, MAT.hoja); }
    for (let k = 0; k < 8; k++) casa(b, -500 + k * 140, -260, k + 30, liso("#f2efe6", 0.05, 16, 72), liso("#3f6fb5", 0.1, 16, 73)); montanas(b, -1100, 8, 3000, 6, liso("#9a8a6a", 0.12, 16, 61), null); nubes(b, 25, 260, -800, 2600, 34); b.fin();
    agua(g, v, 0, 380, 2400, 520); bandada(g, v, 6, 140, -100, "#f2f2f2", 45); alfombra(g, ["seca", "hierba"], 160, 0, -60, 900, (x, z) => Math.abs(x) < 200);
    return {}; } },
  tracia: { cielo: "noche_estrellas", build(g, v) { const b = new Blq(g);
    suelo(b, 50, liso("#5a5a3a", 0.15, 16, 74), 4); for (let i = -8; i <= 8; i++) { b.add(i * BL, 0, -100, MAT.madera); b.add(i * BL, 0, 60, MAT.madera); } for (let j = -5; j <= 4; j++) { b.add(-136, 0, j * BL, MAT.madera); b.add(136, 0, j * BL, MAT.madera); }
    casa(b, -260, -220, 5, liso("#5a4a3a", 0.12, 16, 75)); casa(b, 220, -240, 6, liso("#5a4a3a", 0.12, 16, 75)); for (let k = 0; k < 24; k++) pino(b, (rnd(k * 3) - 0.5) * 1300, -320 - rnd(k) * 400, k, liso("#1a2f1a", 0.2)); montanas(b, -1200, 9, 3000, 8, liso("#2a3040", 0.12, 16, 62), null); b.fin();
    estrellas(g, v, 500); luna(g, 400, 500, -1200, 80); hoguera(g, v, -60, 100, 5); for (const x of [-136, 136]) antorcha(g, v, x, 16, 60, x, true, 1);
    animales(g, v, 4, { color: "#2a2a2a", largo: 20, alto: 11, patas: 14, ancho: 9, ojosRojos: 1, dientes: 1, melena: "#1a1a1a", cola: 5, hocico: "#3a3a3a" }, 0, -20, 180, 7);
    ambiente(g, v, 40, "cenizas", -60, 100, 60, 5, 120);
    return {}; } },
  amazonas: { cielo: "dia", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.hierba, 4); for (let k = 0; k < 7; k++) { const x = -300 + k * 100, z = -140 - (k % 2) * 50; for (let r = 0; r < 3; r++) for (let i = -2 + r; i <= 2 - r; i++) for (let j = -2 + r; j <= 2 - r; j++) if (Math.abs(i) === 2 - r || Math.abs(j) === 2 - r || r === 2) b.add(x + i * BL, r * BL, z + j * BL, liso(["#c83a2f", "#e9dcc0", "#d9a630"][k % 3], 0.1, 16, 76 + k % 3)); }
    for (let k = 0; k < 24; k++) roble(b, (rnd(k * 3) - 0.5) * 1300, -330 - rnd(k) * 350, k + 90); montanas(b, -1200, 9, 3000, 9); nubes(b, 25, 280, -800, 2600, 34); b.fin();
    for (const x of [-200, 200]) { g.add(caja(2, 40, 2, MAT.madera, x, 20, -40)); g.add(caja(14, 10, 1, liso("#c83a2f", 0.1, 4), x + 8, 34, -40)); }
    hoguera(g, v, 0, -40, 2); quietos(g, v, [[-120, -60, 30, "charla"], [-90, -80, 40, "aplaude"], [120, -60, -30, "charla"], [150, -80, -40, "charla"], [-180, 20, 70, "trabaja"]], 90, { faldaLarga: 0, falda: 1, ropa: "#c83a2f", cascoPenacho: "#2a2a2a", casco: "#c8a040", melena: 1 });
    alfombra(g, ["hierba", "roja", "hierba"], 300, 0, 100, 900, (x, z) => z < 40 && Math.abs(x) < 220); bandada(g, v, 6, 200, -400);
    return {}; } },
  gibraltar: { cielo: "atardecer", build(g, v) { const b = new Blq(g);
    suelo(b, 30, MAT.arena, 2, 0, 140);
    for (const x of [-260, 260]) { for (let y = 0; y < 14; y++) for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) if (Math.abs(i) + Math.abs(j) < 2 || y > 12) b.add(x + i * BL, y * BL, -120 + j * BL, MAT.columna); }
    for (const x of [-700, 700]) for (let y = 0; y < 10; y++) for (let i = -6 + Math.floor(y / 2); i <= 6 - Math.floor(y / 2); i++) for (let j = -3; j <= 3; j++) b.add(x + i * 32, y * 32, -400 + j * 32, liso("#8a7a5a", 0.12, 16, 63), 32);
    nubes(b, 25, 300, -900, 2600, 36, liso("#ffd0a0", 0.05, 8)); b.fin();
    agua(g, v, 0, -300, 2600, 800); sol_(g, 0, 160, -1400, 160, "#ffb860"); bandada(g, v, 6, 160, -200, "#f2f2f2", 45);
    animales(g, v, 5, { color: "#a83a2a", largo: 20, alto: 11, patas: 9, ancho: 11, cuernos: "#e8e0c8", hocico: "#d07070", cola: 4 }, 0, 160, 300, 9);
    return {}; } },
  jardin: { cielo: "amanecer", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.hierba, 4); const t0 = 0; for (let j = 0; j < 6; j++) b.add(t0, j * BL, -100, MAT.tronco);
    for (let dy = 0; dy < 3; dy++) for (let i = -3; i <= 3; i++) for (let j = -3; j <= 3; j++) if (Math.abs(i) + Math.abs(j) < 5 - dy) b.add(i * BL, (5 + dy) * BL, -100 + j * BL, liso("#3f8f2e", 0.2, 16, 39));
    for (let k = 0; k < 26; k++) roble(b, (rnd(k * 3) - 0.5) * 1300, -280 - rnd(k) * 400, k + 110, liso("#4a9a3a", 0.22, 16, 40)); montanas(b, -1200, 9, 3000, 9); b.fin();
    for (let k = 0; k < 14; k++) g.add(caja(5, 5, 5, MAT.brillo("#ffcf3a"), (rnd(k) - 0.5) * 90, 82 + rnd(k + 3) * 30, -100 + (rnd(k + 6) - 0.5) * 90));
    const s = serpienteCadena("#3f8f3a", "#d9a630", 26, 4, 64); g.add(s.g); v.push(t => colocaCadena(s, u => [Math.cos(u * 9 + t) * 12, 10 + u * 70, -100 + Math.sin(u * 9 + t) * 12]));
    quietos(g, v, [[-90, -60, 40, "charla"], [90, -60, -40, "charla"], [-60, -150, 20, "aplaude"]], 120, { faldaLarga: 1, ropa: "#f2a0c0", melena: 1 });
    cascada(g, v, 300, 0, -260, 120, 30); alfombra(g, ["roja", "amarilla", "azul", "hierba", "hierba"], 420, 0, 0, 800, (x, z) => Math.abs(z + 20) < 50 && Math.abs(x) < 140);
    ambiente(g, v, 50, "luciernagas", 0, -60, 400, 10, 120); bandada(g, v, 6, 180, -300, "#e04a4a", 40);
    return {}; } },
  atlas: { cielo: "atardecer", build(g, v) { const b = new Blq(g);
    suelo(b, 40, liso("#7a7060", 0.15, 16, 77), 7); for (let y = 0; y < 4; y++) for (let i = -4 + y; i <= 4 - y; i++) for (let j = -3; j <= 3; j++) b.add(i * BL, y * BL, -80 + j * BL, MAT.piedra);
    montanas(b, -1000, 11, 3000, 10, liso("#4a4a5a", 0.12, 16, 64), liso("#d0d8e8", 0.05, 16, 65)); b.fin();
    estrellas(g, v, 600); const cieloB = new THREE.Group(); const mt = M(tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#1b2a6a", r, 0.15); for (let k = 0; k < 20; k++) px(Math.floor(r(k, 3) * 16), Math.floor(r(3, k) * 16), "#ffffff"); }, 83));
    for (let i = -3; i <= 3; i++) for (let j = -3; j <= 3; j++) for (let k = -3; k <= 3; k++) if (i * i + j * j + k * k <= 10) cieloB.add(caja(16, 16, 16, mt, i * 16, j * 16, k * 16)); 
    ambiente(g, v, 50, "luciernagas", 0, -80, 500, 10, 200);
    return {}; } },
  inframundo: { cielo: "inframundo", build(g, v) { const b = new Blq(g);
    suelo(b, 50, MAT.rocaInfra, 6); for (let k = 0; k < 30; k++) { const x = (rnd(k * 3) - 0.5) * 1200, z = -160 - rnd(k) * 500, h = 3 + Math.floor(rnd(k + 2) * 8); for (let y = 0; y < h; y++) b.add(x, y * BL, z, MAT.rocaInfra); b.add(x, h * BL, z, liso("#5a2a1a", 0.2)); }
    for (let i = -10; i <= 10; i++) for (let k = 0; k < 8; k++) if (Math.abs(i) > 2 || k > 4) b.add(i * BL, k * BL, -320, liso("#2a1a1a", 0.15, 16, 66));
    b.fin(); const lv = agua(g, v, 0, -200, 1400, 160, 0.4, MAT.lava); const ll = new THREE.PointLight("#ff6a2a", 9000, 700, 1.3); ll.position.set(0, 40, -200); g.add(ll);
    for (let k = 0; k < 10; k++) { const ch = new THREE.Group(); for (let j = 0; j < 12; j++) ch.add(caja(2, 3, 2, liso("#4a4a4a", 0.2, 4), 0, -j * 3.5, 0)); ch.position.set(-300 + k * 66, 300, -150 - (k % 3) * 60); g.add(ch); v.push(t => ch.rotation.z = 0.08 * Math.sin(t * 0.8 + k)); }
    // barca de Caronte con barquero
    const barca = new THREE.Group(); barca.add(caja(40, 6, 16, MAT.tronco, 0, 3, 0)); const car = personaje({ seed: 701, piel: "#9aa0a8", pelo: "#2a2a2a", ropa: "#1a1a1a", faldaLarga: 1, capa: "#1a1a1a" }); car.root.position.y = 6; barca.add(car.root); barca.position.set(0, 0, -200); g.add(barca);
    v.push(t => { barca.position.x = -200 + ((t * 15) % 400); pose(car, { y: 6, bR: [-60 + 30 * Math.sin(t * 2), 10], cR: 30, bL: [-60 + 30 * Math.sin(t * 2), -10], cL: 30, cabY: 10 * Math.sin(t) }, t); car.root.position.y = 6; cara(car, "malvado"); });
    ambiente(g, v, 90, "almas", 0, -60, 700, 0, 200); ambiente(g, v, 90, "cenizas", 0, -200, 900, 0, 180); alfombra(g, ["hueso", "seca"], 140, 0, 60, 700, (x, z) => Math.abs(x) < 120 && Math.abs(z) < 60);
    // trono de Hades
    for (let k = 0; k < 4; k++) g.add(caja(30, 10, 20, liso("#2a2a3a", 0.1, 8), 220, 5 + k * 10 - (k > 1 ? 0 : 0), -120 + (k > 1 ? -10 : 0))); g.add(caja(30, 60, 6, liso("#2a2a3a", 0.1, 8), 220, 30, -134));
    return { trono: [220, -110] }; } },
  pira: { cielo: "atardecer_rojo", build(g, v) { const b = new Blq(g);
    suelo(b, 40, MAT.hierba, 6); for (let y = 0; y < 3; y++) for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) b.add(i * BL, y * 10, -60 + j * BL, MAT.tronco, 14);
    for (let k = 0; k < 20; k++) pino(b, (rnd(k * 3) - 0.5) * 1200, -280 - rnd(k) * 300, k + 80); montanas(b, -1000, 10, 3000, 9, liso("#6a5a5a", 0.12, 16, 67)); nubes(b, 25, 260, -800, 2600, 36, liso("#ff9a6a", 0.05, 8)); b.fin();
    sol_(g, 300, 120, -1300, 140, "#ff9a40"); bandada(g, v, 6, 200, -300, "#2a2a2a", 30); alfombra(g, ["hierba", "seca", "amarilla"], 260, 0, 60, 700, (x, z) => Math.abs(x) < 120 && Math.abs(z + 40) < 80);
    return {}; } },
};
export const CIELOS = {   // [arriba, horizonte, niebla, cerca, lejos, hemiCielo, hemiSuelo, hemiI, solColor, solI, exposición, sol[x,y,z]]
  dia: ["#4f9ce8", "#cfe6ff", "#cfe6ff", 500, 2200, "#cfe6ff", "#6b5a3a", 1.1, "#fff1d8", 2.6, 1.05, [300, 520, 300]],
  dia_alto: ["#3f8ce0", "#e8f4ff", "#e8f4ff", 600, 2600, "#e8f4ff", "#c8c0b0", 1.25, "#fff6e0", 2.6, 1.05, [300, 600, 300]],
  amanecer: ["#6a8ad8", "#ffd0a0", "#ffd8b0", 500, 2200, "#ffe0c0", "#6b5a3a", 1.0, "#ffd0a0", 2.4, 1.05, [-500, 260, 200]],
  tarde: ["#5a90d8", "#ffe0b0", "#f0d8b0", 450, 2000, "#ffe8c8", "#5a4a2a", 1.0, "#ffd8a0", 2.6, 1.05, [400, 300, 200]],
  atardecer: ["#e0703a", "#ffd8a0", "#ffc890", 450, 2000, "#ffd9b0", "#6b4a3a", 1.0, "#ffb070", 2.8, 1.05, [-200, 200, -600]],
  atardecer_rojo: ["#a8302a", "#ffa060", "#ff9a6a", 400, 1800, "#ffb080", "#4a2a2a", 0.9, "#ff8a50", 2.6, 1.1, [300, 160, -600]],
  noche_interior: ["#0d1530", "#26365e", "#1a2240", 200, 900, "#6a7fb8", "#3a2a2a", 0.35, "#8fa8ff", 0.4, 1.2, [-200, 300, 200]],
  interior: ["#2a1a14", "#5a3a2a", "#3a2a20", 300, 1200, "#ffe0c0", "#5a3a2a", 0.7, "#ffe0b0", 1.4, 1.1, [200, 400, 300]],
  noche_estrellas: ["#0a1430", "#2a3a6a", "#18203a", 350, 1700, "#8a9ad8", "#303040", 0.95, "#b0c0ff", 1.6, 1.3, [-300, 400, 200]],
  niebla_verde: ["#5a7a5a", "#a8c0a0", "#8aa88a", 120, 900, "#c8e0c0", "#3a4a2a", 0.9, "#e0f0c0", 1.6, 1.1, [300, 400, 200]],
  invierno: ["#8aa8d0", "#eef4fa", "#e8f0f8", 300, 1500, "#eef4fa", "#c8d0d8", 1.1, "#ffffff", 2.0, 1.05, [300, 400, 300]],
  tormenta: ["#3a4050", "#7a8090", "#6a7080", 250, 1400, "#a0a8b8", "#3a3a3a", 0.8, "#c0c8d8", 1.2, 1.15, [300, 400, 200]],
  inframundo: ["#2a0505", "#8a2a10", "#4a1008", 200, 1100, "#ff8a5a", "#2a0a0a", 0.55, "#ff6a3a", 0.8, 1.2, [0, 400, 200]],
};

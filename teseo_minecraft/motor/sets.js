// Librería de escenarios griegos en 3 capas (delante: plantas/rocas; medio: decorado y extras; fondo: montañas, ciudad, mar, cielo).
// Cada set vive lejos de los demás (X = i*5000) y solo es visible el activo.
import { THREE, Vox, Plantas, MAT, M, MB, T, tex, fill, caja, rnd, hacerProp, D } from "./motor.js";
const BL = 16;

// ------------------------------------------------------------------ piezas
function suelo(V, cx, cz, nx, nz, mk, y = 0, alt) { for (let i = 0; i < nx; i++) for (let j = 0; j < nz; j++) { const x = cx + (i - nx / 2 + 0.5) * BL, z = cz + (j - nz / 2 + 0.5) * BL; const m = typeof mk === "function" ? mk(x, z, i, j) : mk; if (m) V.cubo(m, x, y - BL, z); } }
function montanas(V, cx, cz, rIn, rOut, n, seed, mats = ["roca", "hierba", "nieve"], base = 0, arco = [0, 360]) {
  for (let k = 0; k < n; k++) {
    const a = (arco[0] + (arco[1] - arco[0]) * (k + rnd(seed + k) * 0.6) / n) * D, r = rIn + rnd(seed + k * 7) * (rOut - rIn);
    const mx = cx + Math.sin(a) * r, mz = cz + Math.cos(a) * r, L = 3 + Math.floor(rnd(seed + k * 3) * 5), S = 40;
    for (let l = 0; l < L; l++) { const rad = (L - l) * S * 0.9 + rnd(seed + k + l) * 20;
      for (let i = -Math.ceil(rad / S); i <= Math.ceil(rad / S); i++) for (let j = -Math.ceil(rad / S); j <= Math.ceil(rad / S); j++) {
        if (Math.hypot(i, j) * S > rad) continue;
        const m = l >= L - 1 && L > 5 ? mats[2] : (l >= L - 2 ? mats[0] : mats[1]);
        V.add(m === "hierba" ? "hierbaM" : m, mx + i * S, base + l * S + S / 2, mz + j * S, S);
      } }
  }
}
MAT.hierbaM = MAT.hierba;
function arbol(V, P, x, z, tipo = "roble", k = 0, y = 0) {
  const h = tipo === "cipres" ? 3 : 3 + Math.floor(rnd(k) * 3);
  if (tipo === "palma") { for (let j = 0; j < 6; j++) V.cubo("tronco", x + j * 2, y + j * 10, z, 8); for (const [dx, dz] of [[1, 0], [-1, 0], [0, 1], [0, -1], [0.7, 0.7], [-0.7, -0.7]]) for (let s = 1; s <= 3; s++) V.cubo("palma", x + 10 + dx * s * 10, y + 60 - s * s * 2, z + dz * s * 10, 10); return; }
  for (let j = 0; j < h; j++) V.cubo("tronco", x, y + j * BL, z);
  if (tipo === "pino" || tipo === "cipres") { const w = tipo === "pino" ? 3 : 1; for (let l = 0; l < (tipo === "pino" ? 5 : 6); l++) { const rr = tipo === "pino" ? Math.max(0, w - Math.floor(l / 2)) : (l < 4 ? 1 : 0); for (let i = -rr; i <= rr; i++) for (let j = -rr; j <= rr; j++) if (Math.abs(i) + Math.abs(j) <= rr + 1) V.cubo(tipo === "pino" ? "pino" : "pino", x + i * BL, y + (h - 1 + l) * BL, z + j * BL); } return; }
  const hm = tipo === "olivo" ? "olivo" : "hoja";
  for (let dy = 0; dy < 2; dy++) for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) { if (Math.abs(i) === 2 && Math.abs(j) === 2 && rnd(k + i * 3 + j) < 0.7) continue; V.cubo(hm, x + i * BL, y + (h - 2 + dy) * BL, z + j * BL); }
  for (let i = -1; i <= 1; i++) for (let j = -1; j <= 1; j++) if (!(Math.abs(i) === 1 && Math.abs(j) === 1) || rnd(k + 9 + i + j) < 0.5) V.cubo(hm, x + i * BL, y + h * BL, z + j * BL);
}
function casa(V, x, z, w, d, h, y = 0, pared = "cal", techo = "teja") {
  for (let i = 0; i < w; i++) for (let j = 0; j < d; j++) for (let k = 0; k < h; k++) { const borde = i === 0 || j === 0 || i === w - 1 || j === d - 1; if (!borde) continue;
    const xx = x + (i - (w - 1) / 2) * BL, zz = z + (j - (d - 1) / 2) * BL;
    const puerta = j === d - 1 && i === Math.floor(w / 2) && k < 2, ventana = k === 1 && (i === 1 || i === w - 2) && (j === d - 1 || j === 0);
    V.cubo(puerta ? "maderaOsc" : (ventana ? "vidrio" : pared), xx, y + k * BL, zz); }
  for (let l = 0; l < Math.ceil(d / 2) + 1; l++) for (let i = -1; i <= w; i++) { const dd = Math.ceil(d / 2) - l; for (const s of [-1, 1]) V.cubo(techo, x + (i - (w - 1) / 2) * BL, y + (h + l) * BL, z + s * dd * BL * 0.999 - (s < 0 ? 0 : 0)); }
}
MAT.vidrio = MB("#22334f");
function templo(V, x, z, nx, nz, y = 0, col = "columna", cap = "marmol", h = 5) {
  for (let i = -1; i <= nx; i++) for (let j = -1; j <= nz; j++) { V.cubo("marmol", x + i * BL, y, z + j * BL); if (i >= 0 && i < nx && j >= 0 && j < nz) V.cubo("marmol", x + i * BL, y + BL, z + j * BL); }
  for (let i = 0; i < nx; i += 2) for (const j of [0, nz - 1]) { for (let k = 0; k < h; k++) V.cubo(col, x + i * BL, y + (2 + k) * BL, z + j * BL); V.cubo(cap, x + i * BL, y + (2 + h) * BL, z + j * BL); }
  for (let j = 0; j < nz; j += 2) for (const i of [0, nx - 1]) { for (let k = 0; k < h; k++) V.cubo(col, x + i * BL, y + (2 + k) * BL, z + j * BL); }
  for (let i = -1; i <= nx; i++) for (let j = -1; j <= nz; j++) V.cubo("marmol", x + i * BL, y + (3 + h) * BL, z + j * BL);
  for (let l = 1; l <= Math.ceil(nz / 2); l++) for (let i = -1; i <= nx; i++) for (let j = l - 1; j <= nz - l; j++) V.cubo(l === 1 && (j === 0 || j === nz - 1) ? "oro" : "marmol", x + i * BL, y + (3 + h + l) * BL, z + j * BL);
}
function brasero(g, V, x, y, z, llamas) { V.cubo("bronce", x, y, z, 8); V.cubo("bronce", x, y + 8, z, 8); const f = caja(7, 8, 7, MAT.fuego, x, y + 20, z); g.add(f); const f2 = caja(4, 5, 4, MAT.brasa, x, y + 25, z); g.add(f2); llamas.push(f, f2); }
function antorchaPared(g, x, y, z, llamas) { g.add(caja(2, 10, 2, MAT.madera, x, y, z)); const f = caja(3.4, 4.4, 3.4, MAT.fuego, x, y + 7, z); g.add(f); llamas.push(f); }
function barcoGrupo() {
  const g = new THREE.Group(), cas = new THREE.Group(); g.add(cas);
  const V = new Vox(cas);
  for (let i = -4; i <= 4; i++) { const w = i === -4 || i === 4 ? 0 : (Math.abs(i) === 3 ? 1 : 2); for (let j = -w; j <= w; j++) { V.add("maderaOsc", i * 14, 6, j * 10, 14, 12, 10); if (Math.abs(j) === w) V.add("madera", i * 14, 16, j * 10, 14, 8, 10); } }
  V.add("madera", 0, 12.5, 0, 112, 1, 44); V.add("madera", 68, 18, 0, 14, 24, 8); V.add("madera", -66, 16, 0, 12, 20, 8);
  for (let i = -3; i <= 3; i++) for (const s of [-1, 1]) V.add("maderaOsc", i * 14, 4, s * 30, 2, 2, 22);
  V.hacer(true);
  cas.add(caja(4, 100, 4, MAT.maderaOsc, 0, 60, 0)); cas.add(caja(80, 3, 3, MAT.maderaOsc, 0, 100, 0));
  const ojo = M(tex(4, 4, (px, w, h, r) => { fill(px, 4, 4, "#f2ead8", r, 0.02); px(1, 1, "#2a5aa0"); px(2, 1, "#2a5aa0"); px(1, 2, "#111"); px(2, 2, "#2a5aa0"); }, 710));
  cas.add(caja(6, 6, 0.6, ojo, 52, 12, 22.5)); cas.add(caja(6, 6, 0.6, ojo, 52, 12, -22.5));
  const vela = new THREE.Group(); vela.position.set(0, 64, 2); cas.add(vela);
  const velaM = caja(78, 70, 1.2, MAT.telaNegra, 0, 0, 0); vela.add(velaM);
  return { g, cas, vela, velaM, cubierta: 13 };
}
function mar(g, y, size = 7000, oscuro = false) { const t = (oscuro ? T.aguaOsc : T.agua).clone(); t.needsUpdate = true; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(size / 32, size / 32); const m = new THREE.Mesh(new THREE.PlaneGeometry(size, size), new THREE.MeshLambertMaterial({ map: t })); m.rotation.x = -Math.PI / 2; m.position.y = y; m.receiveShadow = true; g.add(m); return t; }
function escatter(P, cx, cz, rx, rz, n, tipos, seed, evita = () => false, y = 0, sz = [6, 12]) {
  for (let k = 0; k < n; k++) { const x = cx + (rnd(seed + k * 7.1) - 0.5) * 2 * rx, z = cz + (rnd(seed + k * 3.3) - 0.5) * 2 * rz; if (evita(x, z)) continue; P.add(tipos[Math.floor(rnd(seed + k) * tipos.length)], x, y, z, sz[0] + rnd(seed + k * 5) * (sz[1] - sz[0])); }
}

// ------------------------------------------------------------------ construcción de todos los sets
export function construirSets(scene) {
  const SETS = {}, llamas = [], idx = { trecen: 0, delfos: 1, camino: 2, atenas: 3, creta: 4, laberinto: 5, mar: 6, naxos: 7, mapa: 8 };
  const nuevo = (n, luz) => { const g = new THREE.Group(); g.visible = false; scene.add(g); const ox = idx[n] * 5000; SETS[n] = { g, ox, luz, spots: {}, aguas: [], vida: {} }; return SETS[n]; };
  const spot = (s, n, x, y, z, pts = {}, extra = {}) => { s.spots[n] = Object.assign({ x: s.ox + x, y, z, pts: Object.fromEntries(Object.entries(pts).map(([k, v]) => [k, [s.ox + x + v[0], y + v[1], z + v[2]]])) }, extra); };

  // ========== TRECÉN: pueblo, prado con la roca, olivos, mar al fondo, montañas
  { const s = nuevo("trecen", "dia"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o, 0, 70, 56, (x, z) => z < -380 ? "arena" : "hierba");
    s.aguas.push(mar(s.g, -6, 7000)); s.g.children.at(-1).position.set(o, -6, -2600);
    montanas(V, o, 0, 900, 1300, 16, 11, undefined, 0, [100, 300]);
    for (let k = 0; k < 7; k++) casa(V, o - 380 + k * 110 + rnd(k) * 30, 200 + rnd(k + 9) * 140, 4 + (k % 2), 4, 3);
    casa(V, o - 160, -40, 5, 4, 3); // casa de Etra
    for (let k = 0; k < 26; k++) { const x = o + (rnd(k * 3) - 0.5) * 1000, z = -330 + rnd(k * 5) * 260; if (Math.abs(x - o) < 120 && z > -150) continue; arbol(V, P, x, z, k % 3 ? "olivo" : "roble", k); }
    for (let k = 0; k < 10; k++) arbol(V, P, o + 300 + rnd(k) * 300, 60 + rnd(k + 4) * 300, "cipres", k + 40);
    // la roca
    const roca = new THREE.Group(); for (const [x, y, z, w, h, d] of [[0, 9, 0, 34, 18, 26], [4, 22, 2, 24, 10, 18], [-6, 4, -6, 22, 10, 14]]) roca.add(caja(w, h, d, MAT.roca, x, y, z)); roca.position.set(o, 0, -20); roca.name = "roca"; s.g.add(roca);
    const esp = hacerProp("espada"); esp.rotation.z = Math.PI / 2; esp.position.set(o - 6, 1, -16); esp.name = "espada_suelo"; esp.visible = false; s.g.add(esp);
    const sand = new THREE.Group(); sand.add(caja(4, 1, 8, MAT.madera, 0, 0.5, 0)); sand.add(caja(4, 1, 8, MAT.madera, 6, 0.5, 2)); sand.position.set(o + 8, 0, -20); sand.name = "sandalias"; sand.visible = false; s.g.add(sand);
    // valla y camino
    for (let k = -30; k <= 30; k++) V.cubo("camino", o + k * BL, -BL + 0.2, 20);
    for (let k = -12; k <= 12; k++) if (k % 2) V.add("madera", o + k * 32, 6, 70, 2, 12, 2);
    V.add("madera", o, 10, 70, 800, 2, 2);
    escatter(P, o, 0, 520, 330, 900, ["hierba", "hierba", "hierba", "roja", "amarilla", "morada", "arbusto", "helecho"], 101, (x, z) => (Math.abs(x - o) < 60 && Math.abs(z - 0) < 50) || Math.abs(z - 20) < 10);
    V.hacer(); P.hacer();
    s.vida = { pajaros: "pajaro", humo: [[o - 160 + 40, 80, -40], [o - 380 + 110 * 3, 70, 260]], hojas: 1, aldeanos: [[o - 300, 120, o + 300, 120], [o + 100, 260, o - 200, 260]] };
    spot(s, "roca", 0, 0, 0, { roca: [0, 14, -20], espada_suelo: [0, 2, -16] });
    spot(s, "casa", -160, 0, 30);
    spot(s, "camino", 0, 0, 0);
  }
  // ========== DELFOS: templo en la ladera del Parnaso, trípode con humo
  { const s = nuevo("delfos", "dia"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o, 0, 50, 50, (x, z) => (Math.abs(x - o) < 120 && z > -140 && z < 120) ? "marmol" : "hierbaSeca");
    templo(V, o - 64, -170, 9, 6);
    for (let l = 0; l < 4; l++) for (let i = -30; i <= 30; i++) V.cubo("roca", o + i * BL, l * BL, -330 - l * 40);
    montanas(V, o, -200, 500, 900, 12, 21, ["roca", "roca", "nieve"], 0, [120, 240]); montanas(V, o, 0, 900, 1300, 10, 23, undefined, 0, [0, 360]);
    for (const x of [-100, 100]) for (let k = 0; k < 4; k++) V.cubo("columna", o + x, k * BL, 60);
    V.cubo("bronce", o, 0, -10, 8); V.cubo("bronce", o, 8, -10, 8); V.add("bronce", o, 18, -10, 16, 2, 16);
    for (let k = 0; k < 14; k++) arbol(V, P, o + (rnd(k * 2) - 0.5) * 900, 200 + rnd(k * 9) * 250, k % 2 ? "cipres" : "olivo", k + 60);
    escatter(P, o, 0, 400, 300, 500, ["seca", "seca", "hierba", "arbusto", "amarilla"], 202, (x, z) => Math.abs(x - o) < 130 && z > -150 && z < 130);
    const ll = []; brasero(s.g, V, o - 60, 0, 30, ll); brasero(s.g, V, o + 60, 0, 30, ll); llamas.push(...ll);
    V.hacer(); P.hacer();
    s.vida = { pajaros: "pajaro", humo: [[o, 22, -10], [o, 22, -10]], humoDenso: 1 };
    spot(s, "templo", 0, 0, 0, { tripode: [0, 18, -10] });
  }
  // ========== CAMINO: maza (rocas), pinos, acantilado sobre el mar con tortuga, cabaña de Procusto
  { const s = nuevo("camino", "dia"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o + 600, 0, 120, 40, (x, z) => (x > o + 680 && x < o + 960 && z < -40) ? null : (Math.abs(z - 30) < 14 ? "camino" : "hierbaSeca"));
    s.aguas.push(mar(s.g, -150, 7000)); s.g.children.at(-1).position.set(o + 800, -150, -1200);
    for (let x = o + 680; x < o + 970; x += BL) for (let l = 1; l < 10; l++) V.cubo("roca", x, -l * BL, -40 + (l % 2) * 4);    // pared del acantilado
    for (let z = -40; z > -400; z -= BL) for (let l = 1; l < 10; l++) { V.cubo("roca", o + 680, -l * BL, z); V.cubo("roca", o + 970, -l * BL, z); }
    montanas(V, o + 600, 0, 1150, 1600, 18, 31, ["roca", "hierbaSeca", "nieve"]); MAT.hierbaSeca = MAT.hierbaSeca;
    // rocas grandes del tramo de Perifetes
    for (let k = 0; k < 12; k++) { const x = o - 200 + rnd(k) * 400, z = -60 - rnd(k + 3) * 200; for (let l = 0; l < 1 + Math.floor(rnd(k * 7) * 3); l++) V.cubo("roca", x + l * 6, l * BL, z); }
    // bosque de pinos
    for (let k = 0; k < 30; k++) { const x = o + 250 + (rnd(k * 3) - 0.5) * 400, z = -80 - rnd(k * 5) * 300; arbol(V, P, x, z, "pino", k + 80); }
    for (let k = 0; k < 10; k++) { const x = o + 250 + (rnd(k * 9) - 0.5) * 400, z = 90 + rnd(k * 2) * 200; arbol(V, P, x, z, "pino", k + 130); }
    // dos pinos doblables (grupos animables)
    const pinos = []; for (const sx of [-34, 34]) { const pg = new THREE.Group(); pg.position.set(o + 400 + sx, 0, 0); for (let j = 0; j < 6; j++) pg.add(caja(10, 16, 10, MAT.tronco, 0, j * 16 + 8, 0)); for (let l = 0; l < 3; l++) pg.add(caja(36 - l * 10, 14, 36 - l * 10, MAT.pino, 0, 96 + l * 14, 0)); pg.children.forEach(c => c.castShadow = true); s.g.add(pg); pinos.push(pg); }
    s.pinos = pinos;
    // asiento de Escirón en el borde del acantilado + tortuga
    V.cubo("roca", o + 800, 0, -30); V.cubo("roca", o + 816, 0, -30);
    const tort = new THREE.Group(); const capa = M(tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, "#4a7a3a", r, 0.1); for (let i = 0; i < 8; i++) { px(i, 3, "#2f5a2a"); px(3, i, "#2f5a2a"); } }, 720)), piel = M(tex(4, 4, (px, w, h, r) => fill(px, 4, 4, "#8ab05a", r, 0.1), 721));
    tort.add(caja(60, 16, 70, capa, 0, 4, 0)); const cab = new THREE.Group(); cab.position.set(0, 6, 40); tort.add(cab); cab.add(caja(16, 14, 18, piel, 0, 0, 6));
    const ojoT = MB("#111"); cab.add(caja(2, 3, 2, ojoT, -8.2, 3, 10)); cab.add(caja(2, 3, 2, ojoT, 8.2, 3, 10)); const boca = caja(14, 2, 1, MB("#3a1a10"), 0, -3, 15.2); cab.add(boca);
    tort.position.set(o + 820, -150, -140); tort.rotation.y = Math.PI; s.g.add(tort); s.tortuga = { g: tort, cab };
    // cabaña de Procusto con porche y la cama
    casa(V, o + 1300, -90, 6, 5, 3, 0, "roca", "paja");
    for (const x of [-48, 48]) for (let k = 0; k < 3; k++) V.cubo("maderaOsc", o + 1300 + x, k * BL, -20);
    for (let i = -4; i <= 4; i++) for (let j = 0; j < 3; j++) V.cubo("paja", o + 1300 + i * BL, 3 * BL, -20 - j * BL);
    const cama = new THREE.Group(); cama.add(caja(44, 6, 18, MAT.maderaOsc, 0, 6, 0)); cama.add(caja(40, 3, 16, M(tex(8, 4, (px, w, h, r) => { fill(px, 8, 4, "#8a2a2a", r, 0.1); for (let x = 0; x < 8; x += 2) px(x, 1, "#5a1a1a"); }, 722)), 0, 10, 0));
    for (const x of [-21, 21]) for (const z of [-8, 8]) cama.add(caja(3, 6, 3, MAT.maderaOsc, x, 3, z)); cama.add(caja(3, 14, 18, MAT.maderaOsc, -22, 10, 0)); cama.add(caja(3, 10, 18, MAT.maderaOsc, 22, 8, 0)); cama.add(caja(8, 3, 12, MAT.tela, -16, 13, 0));
    cama.position.set(o + 1300, 0, 0); s.g.add(cama);
    // herramientas siniestras
    V.add("bronce", o + 1340, 26, -24, 2, 14, 10); V.add("maderaOsc", o + 1340, 12, -24, 2, 24, 2);
    escatter(P, o + 600, 0, 900, 300, 1100, ["seca", "seca", "hierba", "arbusto", "amarilla", "helecho"], 303, (x, z) => Math.abs(z - 30) < 14 || (x > o + 680 && x < o + 970 && z < -30) || (Math.abs(x - o - 1300) < 70 && z < 30 && z > -140) || (Math.abs(x - o - 400) < 60 && Math.abs(z) < 30));
    V.hacer(); P.hacer();
    s.vida = { pajaros: "pajaro", hojas: 1, humo: [[o + 1330, 70, -110]] };
    spot(s, "maza", 0, 0, 0); spot(s, "pinos", 400, 0, 0); spot(s, "acantilado", 800, 0, 0, { tortuga: [20, -150, -140] }, { vida: { pajaros: "gaviota" } }); spot(s, "cama", 1300, 0, 0, { cama: [0, 10, 0] });
  }
  // ========== ATENAS: acrópolis, casas, mercado, palacio (trono y banquete), puerto, acantilado
  { const s = nuevo("atenas", "dia"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o, 0, 110, 70, (x, z) => { if (z < -420 && x < o + 400) return null; if (x > o + 520 && z < -100) return null; if (x > o + 520 && z > 140 && z < 460) return null; return (Math.abs(x - o) < 220 && Math.abs(z - 100) < 160) ? "piedra" : "hierbaSeca"; });
    s.aguas.push(mar(s.g, -8, 8000)); s.g.children.at(-1).position.set(o, -8, -3500);
    const mAc = mar(s.g, -160, 4000); s.aguas.push(mAc); s.g.children.at(-1).position.set(o + 2500, -160, 300);
    // acrópolis (colina con el Partenón) al fondo
    for (let l = 0; l < 5; l++) for (let i = -10 + l; i <= 10 - l; i++) for (let j = -6 + l; j <= 6 - l; j++) V.cubo("roca", o - 200 + i * BL * 1.4, l * BL, 520 + j * BL * 1.4);
    templo(V, o - 270, 470, 10, 6, 5 * BL);
    // barrio de casas blancas alrededor
    for (let k = 0; k < 26; k++) { const a = rnd(k * 4) * Math.PI * 2, r = 330 + rnd(k * 9) * 260; const x = o + Math.sin(a) * r, z = 100 + Math.cos(a) * r * 0.8; if (z < -300 || x > o + 500 || (x > o + 200 && z < 140) || (Math.abs(x - o) < 260 && z < 290)) continue; casa(V, x, z, 3 + Math.floor(rnd(k) * 3), 3 + Math.floor(rnd(k + 1) * 2), 2 + Math.floor(rnd(k + 2) * 2)); }
    // muralla con puerta (spot puerta en z=0 mirando a +z)
    for (let i = -25; i <= 25; i++) for (let k = 0; k < 6; k++) { if (Math.abs(i) <= 2 && k < 4) continue; V.cubo("piedra", o + i * BL, k * BL, -150); }
    for (const sx of [-1, 1]) for (let k = 0; k < 8; k++) for (let i = 0; i < 3; i++) V.cubo("piedra", o + sx * (4 + i) * BL, k * BL, -150 + BL);
    // mercado: puestos con toldos de colores
    const toldo = c => M(tex(8, 8, (px, w, h, r) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) px(x, y, (x >> 1) % 2 ? c : "#f2ead8"); }, 730 + c.length));
    for (let k = 0; k < 6; k++) { const x = o - 160 + k * 64, z = 200; const tg = new THREE.Group(); tg.add(caja(36, 2, 24, toldo(["#c0392b", "#2f6fb5", "#d9a630", "#3f8f5a", "#7f5aa8", "#e07a2a"][k]), 0, 34, 0)); for (const [dx, dz] of [[-16, -10], [16, -10], [-16, 10], [16, 10]]) tg.add(caja(2, 34, 2, MAT.madera, dx, 17, dz)); tg.add(caja(32, 12, 10, MAT.madera, 0, 6, 6)); for (let f = 0; f < 4; f++) tg.add(caja(5, 5, 5, MB(["#d33a2f", "#f2c84a", "#5f9e3a", "#7f3a9a"][(f + k) % 4]), -10 + f * 7, 14.5, 6)); tg.position.set(x, 0, z); s.g.add(tg); }
    // fuente en la plaza
    for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) if (Math.abs(i) === 2 || Math.abs(j) === 2) V.cubo("marmol", o + i * 12, 0, 100 + j * 12, 12);
    const fAg = caja(40, 2, 40, MAT.agua, o, 9, 100); s.g.add(fAg); V.cubo("marmol", o, 0, 100, 8); V.cubo("marmol", o, 8, 100, 6);
    // palacio (sala del trono y banquete) a la derecha: x+260..+480
    const px0 = o + 380, pz0 = -40;
    for (let i = -8; i <= 8; i++) for (let j = -6; j <= 6; j++) V.cubo("marmol", px0 + i * BL, -BL + 0.5, pz0 + j * BL);
    for (let i = -8; i <= 8; i++) for (let k = 0; k < 6; k++) { V.cubo(k === 4 ? "friso" : "cal", px0 + i * BL, k * BL, pz0 - 6 * BL); }
    for (let j = -6; j <= 4; j++) for (let k = 0; k < 6; k++) { const v = k > 1 && k < 4 && j % 3 === 0; V.cubo(v ? "vidrio" : (k === 4 ? "friso" : "cal"), px0 - 8 * BL, k * BL, pz0 + j * BL); V.cubo(v ? "vidrio" : (k === 4 ? "friso" : "cal"), px0 + 8 * BL, k * BL, pz0 + j * BL); }
    for (let i = -8; i <= 8; i++) for (let j = -6; j <= 6; j += 2) if (Math.abs(i) % 4 === 0) V.cubo("maderaOsc", px0 + i * BL, 6 * BL, pz0 + j * BL);
    for (const x of [-112, 112]) for (let k = 0; k < 5; k++) V.cubo("columna", px0 + x, k * BL, pz0 + 60);
    const est = M(tex(4, 10, (px, w, h, r) => { fill(px, 4, 10, "#2f5fa0", r, 0.1); for (let y = 0; y < 10; y++) { px(0, y, "#e0b040"); px(3, y, "#e0b040"); } px(1, 4, "#e0b040"); px(2, 4, "#e0b040"); px(1, 5, "#f2ead8"); px(2, 5, "#f2ead8"); }, 731));
    for (const x of [-60, 60]) s.g.add(caja(16, 44, 1, est, px0 + x, 50, pz0 - 6 * BL + 8.6));
    const tr = new THREE.Group(); tr.add(caja(22, 12, 18, MAT.oro, 0, 6, 0)); tr.add(caja(24, 36, 5, MAT.oro, 0, 18, -9)); tr.add(caja(4, 20, 18, MAT.oro, -11, 10, 0)); tr.add(caja(4, 20, 18, MAT.oro, 11, 10, 0)); tr.add(caja(18, 3, 14, M(T.alfombra), 0, 13, 2)); tr.position.set(px0, 0, pz0 - 10); s.g.add(tr);
    s.g.add(caja(40, 0.6, 120, M(T.alfombra), px0, 0.4, pz0 + 50));
    const ll = []; for (const x of [-90, 90]) brasero(s.g, V, px0 + x, 0, pz0 - 50, ll); llamas.push(...ll);
    // banquete (en la misma sala, más adelante): mesa con comida
    const mesa = new THREE.Group(); mesa.add(caja(110, 4, 26, MAT.madera, 0, 14, 0)); for (const x of [-48, 48]) for (const z of [-10, 10]) mesa.add(caja(3, 14, 3, MAT.maderaOsc, x, 7, z));
    for (let f = 0; f < 9; f++) { const c = ["#c88a3a", "#7f3a9a", "#d33a2f", "#f2c84a", "#e8e2cc"][f % 5]; mesa.add(caja(5 + (f % 3), 4, 5, MB(c), -44 + f * 11, 18, (f % 2) * 6 - 3)); }
    mesa.position.set(px0, 0, pz0 + 50); mesa.name = "mesa"; s.g.add(mesa);
    // puerto (a la izquierda, borde del agua en z=-420)
    for (let i = -6; i <= 6; i++) for (let j = 0; j < 8; j++) V.add("madera", o - 300 + i * BL, -2, -440 - j * BL, BL, 4, BL);
    for (let i = -6; i <= 6; i += 3) for (let j = 0; j < 8; j += 3) V.add("maderaOsc", o - 300 + i * BL, -20, -440 - j * BL, 4, 36, 4);
    for (let k = 0; k < 6; k++) V.cubo("madera", o - 380 + rnd(k) * 40, 0, -400 + rnd(k + 2) * 30, 10);
    // acantilado de Egeo (x+700) con templete
    for (let l = 1; l < 11; l++) for (let j = -10; j <= 10; j++) V.cubo("roca", o + 520 + (l % 2) * 3, -l * BL, 300 + j * BL);
    for (const z of [260, 340]) for (const x of [500, 460]) for (let k = 0; k < 4; k++) V.cubo("columna", o + x, k * BL, z);
    for (let i = 0; i < 4; i++) for (let j = -3; j <= 3; j++) V.cubo("marmol", o + 452 + i * BL, 4 * BL, 300 + j * BL);
    montanas(V, o, 0, 1100, 1500, 14, 41, ["roca", "hierbaSeca", "nieve"], 0, [60, 300]);
    for (let k = 0; k < 30; k++) { const x = o + (rnd(k * 5) - 0.5) * 1100, z = 100 + (rnd(k * 6) - 0.5) * 800; if (Math.abs(x - o) < 240 && Math.abs(z - 100) < 180) continue; if (x > o + 230 && x < o + 540 && z < 120) continue; if (x > o + 360 && Math.abs(z - 300) < 140) continue; if (z < -330) continue; arbol(V, P, x, z, k % 4 ? "olivo" : "cipres", k + 150); }
    escatter(P, o, 0, 520, 420, 1000, ["seca", "hierba", "arbusto", "roja", "amarilla", "hierba"], 404, (x, z) => (Math.abs(x - o) < 230 && Math.abs(z - 100) < 170) || (x > o + 230 && x < o + 520 && z < 70 && z > -150) || z < -330 || Math.abs(x - o) < 60 && z < -100 || (x > o + 400 && Math.abs(z - 300) < 60));
    V.hacer(); P.hacer();
    s.vida = { pajaros: "pajaro", humo: [[o - 400, 60, 300], [o + 200, 60, 520], [o - 100, 50, 420]], aldeanos: [[o - 200, 160, o + 200, 160], [o - 180, 60, o + 150, 60], [o + 160, 240, o - 220, 240]], fuente: fAg };
    spot(s, "plaza", 0, 0, 0, {}, { vida: { aldeanosOn: 1, aldeanos: [[o - 160, -70, o + 160, -70], [o + 170, -120, o - 170, -120], [o - 140, -180, o + 140, -180], [o + 120, -40, o + 120, -220]] } });
    spot(s, "puerta", 0, 0, -80, {}, { vida: { aldeanosOn: 1, aldeanos: [[o - 140, -60, o - 60, -60], [o + 60, -50, o + 150, -50], [o - 120, 30, o - 50, 30], [o + 50, 40, o + 130, 40]] } });
    spot(s, "trono", 380, 0, -40, {}, { luz: "interior" });
    spot(s, "banquete", 380, 0, 40, { mesa: [0, 16, -30], copa: [0, 20, -30], veneno_suelo: [-10, 0, 0] }, { luz: "interior" });
    spot(s, "puerto", -300, 0, -380, { barco: [0, 10, -180] }, { vida: { pajaros: "gaviota" }, barco: [-300, -8, -560, 0] });
    spot(s, "acantilado", 500, 0, 300, {}, { vida: { pajaros: "gaviota" }, barcoLejos: [1500, -160, 0, 0] });
  }
  // ========== CRETA: palacio de Cnosos (columnas rojas, cuernos), sala del trono con grifos, taller de Dédalo, puerta del laberinto
  { const s = nuevo("creta", "dia"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o, 0, 100, 70, (x, z) => (Math.abs(x - o) < 260 && Math.abs(z) < 200) ? "piedra" : "hierba");
    // fachada del palacio (z=-120), dos pisos, columnas rojas con capitel negro, friso y cuernos de consagración
    for (let i = -16; i <= 16; i++) for (let k = 0; k < 9; k++) V.cubo(k === 4 || k === 8 ? "friso" : "ocre", o + i * BL, k * BL, -200);
    for (let i = -16; i <= 16; i += 2) { for (let k = 0; k < 3; k++) V.add("rojo", o + i * BL, k * BL + 8, -150, 12, 16, 12); V.add("negro", o + i * BL, 3 * BL + 4, -150, 16, 8, 16); for (let k = 0; k < 3; k++) V.add("rojo", o + i * BL, (5 + k) * BL - 8, -150, 12, 16, 12); V.add("negro", o + i * BL, 8 * BL - 4, -150, 16, 8, 16); }
    for (let i = -16; i <= 16; i++) for (let j = 0; j < 4; j++) { V.cubo("ocre", o + i * BL, 4 * BL, -150 - j * BL); V.cubo("ocre", o + i * BL, 8 * BL, -150 - j * BL); }
    for (let i = -16; i <= 16; i += 4) { V.cubo("cal", o + i * BL - 6, 9 * BL, -150, 6); V.cubo("cal", o + i * BL - 6, 9 * BL + 6, -150, 6); V.cubo("cal", o + i * BL + 6, 9 * BL, -150, 6); V.cubo("cal", o + i * BL + 6, 9 * BL + 6, -150, 6); V.cubo("cal", o + i * BL, 9 * BL, -150, 6); }
    // escalinata
    for (let l = 0; l < 3; l++) for (let i = -4; i <= 4; i++) V.add("marmol", o + i * BL, l * 5 + 2.5, -110 - l * 10, BL, 5, 20);
    // jardín con cipreses, palmeras y estanque
    for (let k = 0; k < 12; k++) arbol(V, P, o + (k < 6 ? -1 : 1) * (300 + (k % 6) * 40), -100 + (k % 3) * 80, k % 2 ? "cipres" : "palma", k + 200);
    s.aguas.push(mar(s.g, -10, 7000)); s.g.children.at(-1).position.set(o, -10, 4200);
    montanas(V, o, 0, 1350, 1800, 16, 51, ["roca", "hierba", "nieve"], 0, [150, 330]);
    suelo(V, o + 1500, 60, 50, 36, (x, z) => (Math.abs(x - o - 1500) < 120 && z > -100) ? "camino" : "hierba");
    // sala del trono (x-700)
    const tx = o - 700;
    for (let i = -7; i <= 7; i++) for (let j = -5; j <= 5; j++) V.cubo("ocre", tx + i * BL, -BL + 0.5, j * BL);
    const grifo = M(tex(32, 16, (px, w, h, r) => { fill(px, 32, 16, "#b8302a", r, 0.05); for (let x = 0; x < 32; x++) { px(x, 14, "#2f5f9f"); px(x, 15, "#2f5f9f"); } const G = ["00000000000000110000", "00000000000001111000", "00000000000011111100", "00001111111111110000", "00111111111111110000", "01111111111111100000", "00110111111110000000", "00010010001001000000", "00010010001001000000"]; G.forEach((row, y) => [...row].forEach((c, x) => { if (c === "1") px(x + 6, y + 3, "#e8d8a8"); })); px(23, 4, "#111"); for (let k = 0; k < 8; k++) px(4 + k * 3, 1, "#e0b040"); }, 740));
    for (let i = -7; i <= 7; i++) for (let k = 0; k < 6; k++) V.cubo(k === 5 ? "friso" : "rojo", tx + i * BL, k * BL, -6 * BL);
    for (const sx of [-60, 60]) s.g.add(caja(64, 32, 1, grifo, tx + sx, 34, -6 * BL + 8.6));
    for (let j = -6; j <= 3; j++) for (let k = 0; k < 6; k++) { V.cubo(k === 5 ? "friso" : "rojo", tx - 7 * BL, k * BL, j * BL); V.cubo(k === 5 ? "friso" : "rojo", tx + 7 * BL, k * BL, j * BL); }
    for (const x of [-64, 64]) for (const z of [-30, 30]) { for (let k = 0; k < 4; k++) V.add("rojo", tx + x, k * BL + 8, z, 12, 16, 12); V.add("negro", tx + x, 4 * BL + 4, z, 16, 8, 16); }
    const tro = new THREE.Group(); tro.add(caja(20, 12, 16, MAT.marmol, 0, 6, 0)); tro.add(caja(20, 34, 4, MAT.marmol, 0, 17, -8)); for (let k = 0; k < 5; k++) tro.add(caja(4, 4, 4, MAT.marmol, -8 + k * 4, 36 + (k % 2 ? 2 : 0) - Math.abs(k - 2) * 2, -8)); tro.position.set(tx, 0, -14); s.g.add(tro);
    const ll = []; for (const x of [-80, 80]) brasero(s.g, V, tx + x, 0, -60, ll); llamas.push(...ll);
    // taller de Dédalo (x+700): mesas, ruedas, alas colgadas, maqueta del laberinto
    const dx = o + 700;
    for (let i = -6; i <= 6; i++) for (let j = -5; j <= 5; j++) V.cubo("madera", dx + i * BL, -BL + 0.5, j * BL);
    for (let i = -6; i <= 6; i++) for (let k = 0; k < 5; k++) V.cubo(k === 2 && Math.abs(i) % 3 === 1 ? "vidrio" : "ocre", dx + i * BL, k * BL, -5 * BL);
    for (let j = -5; j <= 3; j++) for (let k = 0; k < 5; k++) { V.cubo("ocre", dx - 6 * BL, k * BL, j * BL); V.cubo("ocre", dx + 6 * BL, k * BL, j * BL); }
    const plumas = M(tex(8, 4, (px, w, h, r) => { fill(px, 8, 4, "#f2ead8", r, 0.08); for (let x = 0; x < 8; x += 2) { px(x, 3, "#d8c8a0"); px(x + 1, 2, "#e8dcc0"); } }, 741));
    for (const sx of [-1, 1]) { const ala = caja(30, 14, 1, plumas, dx + sx * 24, 46, -5 * BL + 8.8); ala.rotation.z = sx * 0.25; s.g.add(ala); }
    const mesaD = new THREE.Group(); mesaD.add(caja(50, 3, 30, MAT.madera, 0, 16, 0)); for (const x of [-22, 22]) for (const z of [-12, 12]) mesaD.add(caja(3, 16, 3, MAT.maderaOsc, x, 8, z));
    for (let i = 0; i < 7; i++) for (let j = 0; j < 4; j++) if (rnd(i * 4 + j) < 0.55) mesaD.add(caja(4, 4, 4, MAT.piedraOsc, -15 + i * 5, 19.5, -8 + j * 5)); mesaD.position.set(dx - 40, 0, -40); s.g.add(mesaD);
    for (const [x, z, r] of [[50, -60, 10], [60, -50, 6]]) { const rueda = new THREE.Group(); for (let k = 0; k < 8; k++) { const a = k / 8 * Math.PI * 2; rueda.add(caja(3, 3, 3, MAT.madera, Math.cos(a) * r, Math.sin(a) * r, 0)); } rueda.position.set(dx + x, 30, z); rueda.name = "rueda"; s.g.add(rueda); }
    const ll2 = []; antorchaPared(s.g, dx - 6 * BL + 10, 40, -20, ll2); antorchaPared(s.g, dx + 6 * BL - 10, 40, -20, ll2); llamas.push(...ll2);
    // puerta del laberinto (x+1500): muros enormes y una gran puerta con hacha doble
    const lx = o + 1500;
    for (let i = -20; i <= 20; i++) for (let k = 0; k < 7; k++) { if (Math.abs(i) <= 2 && k < 5) continue; V.cubo(k === 6 ? "musgo" : "piedraOsc", lx + i * BL, k * BL, -100); }
    const labrys = M(tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, "#55524c", r, 0.1); for (let y = 1; y < 7; y++) { px(1, y, "#d9a630"); px(6, y, "#d9a630"); } for (let y = 2; y < 6; y++) { px(2, y, "#d9a630"); px(5, y, "#d9a630"); } for (let y = 0; y < 8; y++) { px(3, y, "#8a6028"); px(4, y, "#8a6028"); } }, 742));
    s.g.add(caja(32, 32, 1, labrys, lx, 96, -91));
    const puerta = new THREE.Group(); puerta.add(caja(40, 76, 6, MAT.maderaOsc, 0, 38, 0)); for (const y of [16, 60]) puerta.add(caja(42, 4, 7, MAT.bronce, 0, y, 0)); puerta.position.set(lx, 0, -100); s.g.add(puerta); s.puertaLab = puerta;
    escatter(P, o, 0, 900, 500, 900, ["hierba", "hierba", "roja", "amarilla", "arbusto", "helecho", "morada"], 505, (x, z) => (Math.abs(x - o) < 270 && Math.abs(z) < 210) || Math.abs(x - tx) < 130 || Math.abs(x - dx) < 110 || (Math.abs(x - lx) < 340 && z > -110 && z < 120));
    V.hacer(); P.hacer();
    s.vida = { pajaros: "pajaro", aldeanos: [[o - 200, 40, o + 200, 40], [o + 200, -80, o - 200, -80]], humo: [] };
    spot(s, "palacio", 0, 0, 0, {}, { vida: { aldeanosOn: 1, aldeanos: [[o - 160, -60, o + 160, -60], [o + 150, -110, o - 150, -110], [o - 90, -30, o - 90, -150], [o + 90, -150, o + 90, -30]] } });
    spot(s, "trono", -700, 0, 0, {}, { luz: "interior" });
    spot(s, "taller", 700, 0, 0, {}, { luz: "interior" });
    spot(s, "puerta_lab", 1500, 0, -40, {}, {});
  }
  // ========== LABERINTO: pasillos de piedra con musgo, antorchas, huesos; sala central
  { const s = nuevo("laberinto", "laberinto"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o, 0, 90, 90, "piedraOsc");
    const muro = (x, z, h = 5) => { for (let k = 0; k < h; k++) V.cubo(rnd(x * 0.3 + z * 0.7 + k) < 0.3 ? "musgo" : "piedraOsc", x, k * BL, z); };
    // pasillo principal (z = 0): pared alta detrás (z=-48) y pared baja delante (z=+48) para que la cámara vea por encima
    for (let x = -640; x <= 640; x += BL) { if ((Math.floor(x / BL) % 13) !== 5) muro(o + x, -48, 5); muro(o + x, 48, 1); if ((Math.floor(x / BL) % 7) === 2) muro(o + x, 48, 2); }
    // laberinto alrededor (para el plano cenital), dejando libre la franja de cámara delante del pasillo y de la sala
    const cz = 400;
    for (let i = -18; i <= 18; i++) for (let j = -18; j <= 18; j++) { const x = o + i * 48, z = j * 48; if (z > -90 && z < 230) continue; if (Math.abs(i * 48) < 150 && z > 250) continue; if (rnd(i * 31 + j * 17) < 0.5) for (let q = 0; q < 3; q++) muro(x + q * BL - BL, z, 4); else for (let q = 0; q < 3; q++) muro(x, z + q * BL - BL, 4); }
    // sala central (z = 400): muros altos atrás y a los lados, bajo delante
    for (let i = -7; i <= 7; i++) { muro(o + i * BL, cz - 7 * BL, 6); muro(o + i * BL, cz + 7 * BL, i % 3 === 0 ? 2 : 1); muro(o - 7 * BL, cz + i * BL, 6); muro(o + 7 * BL, cz + i * BL, 6); }
    for (let i = -6; i <= 6; i++) for (let j = -6; j <= 6; j++) V.add("piedra", o + i * BL, 0.3, cz + j * BL, BL, 0.6, BL);
    // columnas rotas y cadenas en la sala
    for (const [x, z] of [[-80, -80], [80, -80], [-80, 60], [80, 60]]) { muro(o + x, cz + z, x > 0 && z > 0 ? 2 : 3); }
    // entrada (x = -660): marco
    for (let k = 0; k < 6; k++) { V.cubo("piedraOsc", o - 660, k * BL, -48); V.cubo("piedraOsc", o - 660, k * BL, 48); } for (let i = -3; i <= 3; i++) V.cubo("piedraOsc", o - 660, 6 * BL, i * BL);
    // antorchas
    for (let x = -600; x <= 600; x += 80) { antorchaPared(s.g, o + x, 40, -39, llamas); }
    for (const [x, z] of [[-60, cz - 103], [60, cz - 103], [-103, cz - 40], [103, cz - 40], [-103, cz + 40], [103, cz + 40]]) antorchaPared(s.g, o + x, 40, z, llamas);
    // huesos y calaveras
    for (let k = 0; k < 40; k++) P.add("hueso", o + (rnd(k * 3) - 0.5) * 900, 0, (rnd(k * 7) - 0.5) * 70, 6 + rnd(k) * 4);
    for (let k = 0; k < 30; k++) P.add("hueso", o + (rnd(k * 5) - 0.5) * 180, 0, cz + (rnd(k * 9) - 0.5) * 180, 7 + rnd(k) * 5);
    const calav = M(tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, "#e8e2cc", r, 0.05); px(1, 3, "#111"); px(2, 3, "#111"); px(5, 3, "#111"); px(6, 3, "#111"); px(1, 4, "#111"); px(6, 4, "#111"); px(3, 5, "#333"); px(4, 5, "#333"); for (let x = 1; x < 7; x += 2) px(x, 7, "#555"); }, 750));
    for (let k = 0; k < 10; k++) { const c = caja(6, 6, 6, [MAT.hueso, MAT.hueso, MAT.hueso, MAT.hueso, calav, MAT.hueso], o + (rnd(k * 13) - 0.5) * 700, 3, (rnd(k * 17) - 0.5) * 36); c.rotation.y = (rnd(k) - 0.5) * 1.4; s.g.add(c); }
    for (let k = 0; k < 8; k++) { const c = caja(7, 7, 7, [MAT.hueso, MAT.hueso, MAT.hueso, MAT.hueso, calav, MAT.hueso], o + (rnd(k * 19) - 0.5) * 160, 3.5, cz + (rnd(k * 23) - 0.5) * 160); c.rotation.y = (rnd(k + 3) - 0.5) * 2; s.g.add(c); }
    // telarañas y raíces
    for (let k = 0; k < 30; k++) P.add("juncos", o + (rnd(k * 29) - 0.5) * 1200, 0, -42, 8);
    V.hacer(); P.hacer();
    // hilo rojo (se dibuja por plano)
    const hilo = caja(1, 0.6, 1, MB("#e0202a"), 0, 0, 0); hilo.castShadow = false; s.g.add(hilo); s.hilo = hilo;
    // pared que se rompe (para la embestida)
    s.vida = { pajaros: "murcielago", polvo: 1 };
    spot(s, "pasillo", 0, 0, 0, { huesos: [0, 2, 8] }, { caja: [-2000, 2000, -40, 200] });
    spot(s, "entrada", -620, 0, 0, {}, { caja: [-30, 2000, -40, 200] });
    spot(s, "centro", 0, 0, cz, { centro: [0, 20, 0], muro: [0, 30, -100], laberinto_vista: [0, 0, -400] }, { caja: [-100, 100, -100, 260] });
  }
  // ========== MAR abierto: el barco, islas lejanas, delfines
  { const s = nuevo("mar", "dia"), V = new Vox(s.g), o = s.ox;
    s.aguas.push(mar(s.g, -8, 9000)); s.g.children.at(-1).position.set(o, -8, 0);
    for (let k = 0; k < 9; k++) { const a = (k / 9) * Math.PI * 2 + 0.3, r = 900 + rnd(k) * 700, x = o + Math.sin(a) * r, z = Math.cos(a) * r; for (let l = 0; l < 2 + Math.floor(rnd(k * 3) * 3); l++) for (let i = -4 + l; i <= 4 - l; i++) for (let j = -3 + l; j <= 3 - l; j++) V.add(l === 0 ? "arena" : "hierbaM", x + i * 32, -8 + l * 32 + 16, z + j * 32, 32); }
    V.hacer();
    s.vida = { pajaros: "gaviota", delfines: 1, olas: 1 };
    spot(s, "barco", 0, 0, 0, { barco: [0, 0, 0] }, { barco: [0, -8, 0, 0], navega: 1 });
  }
  // ========== NAXOS: playa, palmeras, hoguera, rocas, mar
  { const s = nuevo("naxos", "noche"), V = new Vox(s.g), P = new Plantas(s.g), o = s.ox;
    suelo(V, o, 100, 70, 40, (x, z) => z < -40 ? (z < -80 ? null : "arenaMojada") : (z > 180 ? "hierba" : "arena"));
    s.aguas.push(mar(s.g, -6, 8000)); s.g.children.at(-1).position.set(o, -6, -3800);
    for (let k = 0; k < 16; k++) arbol(V, P, o + (rnd(k * 3) - 0.5) * 900, 140 + rnd(k * 7) * 160, "palma", k + 300);
    for (let k = 0; k < 12; k++) { const x = o + (rnd(k * 11) - 0.5) * 900, z = 30 + rnd(k * 13) * 120; if (Math.abs(x - o) < 120) continue; V.cubo("roca", x, 0, z); if (rnd(k) < 0.5) V.cubo("roca", x + 8, BL, z); }
    montanas(V, o, 0, 700, 1100, 10, 61, ["roca", "hierba", "roca"], 0, [-60, 60]);
    for (let k = 0; k < 6; k++) V.cubo("roca", o + 400 + k * 30, -4, -120 - k * 20, 24);
    const fogata = new THREE.Group(); for (let k = 0; k < 5; k++) { const a = k / 5 * Math.PI * 2; fogata.add(caja(10, 3, 3, MAT.maderaOsc, Math.cos(a) * 4, 1.5, Math.sin(a) * 4)); }
    const f1 = caja(8, 10, 8, MAT.fuego, 0, 7, 0), f2 = caja(4, 6, 4, MAT.brasa, 0, 11, 0); fogata.add(f1, f2); llamas.push(f1, f2); fogata.position.set(o - 60, 0, 60); s.g.add(fogata);
    escatter(P, o, 160, 500, 120, 500, ["hierba", "arbusto", "seca", "juncos"], 606, (x, z) => z < 40);
    V.hacer(); P.hacer();
    s.vida = { pajaros: "gaviota", luciernagas: 1, olas: 1, fogata: [o - 60, 14, 60] };
    spot(s, "playa", 0, 0, 40, { teseo_barco: [80, 20, -270] }, { barco: [80, -6, -230, 0.3] });
  }
  // ========== MAPA: mar con Grecia, Peloponeso, Creta y Cícladas en bloques
  { const s = nuevo("mapa", "mapa"), V = new Vox(s.g), o = s.ox;
    s.aguas.push(mar(s.g, -2, 4000)); s.g.children.at(-1).position.set(o, -2, 0);
    const S = 12, isla = (cx, cz, f) => { for (let i = -60; i <= 60; i++) for (let j = -60; j <= 60; j++) { const x = cx + i * S, z = cz + j * S; const v = f(i, j); if (v > 0) { V.add("arena", o + x, 2, z, S, 4, S); if (v > 1) V.add("hierbaM", o + x, 8, z, S, 8, S); if (v > 2) V.add("roca", o + x, 16, z, S, 8, S); } } };
    const n = (i, j, s0) => rnd(Math.floor(i / 2) * 7 + Math.floor(j / 2) * 13 + s0);
    // Grecia continental (arriba) con Ática en punta hacia el sureste
    isla(-120, -330, (i, j) => { const d = (j < 0 ? 1 : 0) + (j >= 0 && j < 14 && i > -6 + j * 0.4 && i < 14 + j * 0.9 ? 1 : 0); return d * (1 + (n(i, j, 1) > 0.4 ? 1 : 0) + (j < -10 && n(i, j, 2) > 0.6 ? 1 : 0)) * (Math.abs(i) < 40 ? 1 : 0); });
    isla(-300, -170, (i, j) => (Math.hypot(i * 1.1, j) < 13 + n(i, j, 3) * 4 ? 1 + (n(i, j, 4) > 0.3 ? 1 : 0) + (n(i, j, 5) > 0.75 ? 1 : 0) : 0));  // Peloponeso
    isla(-40, 300, (i, j) => (Math.abs(j) < 3 + n(i, j, 6) * 2 && Math.abs(i) < 26 ? 1 + (n(i, j, 7) > 0.35 ? 1 : 0) + (Math.abs(i) < 8 && n(i, j, 8) > 0.5 ? 1 : 0) : 0)); // Creta
    for (const [x, z, r] of [[120, 20, 3], [170, -60, 2], [60, 90, 2], [210, 80, 3], [20, -10, 2], [140, 150, 2]]) isla(x, z, (i, j) => Math.hypot(i, j) < r + n(i, j, x) ? 1 + (Math.hypot(i, j) < r - 1 ? 1 : 0) : 0); // Cícladas (Naxos = 120,20)
    // Atenas y Cnosos: templete
    for (const [x, z, c] of [[-60, -200, "marmol"], [-40, 300, "rojo"]]) { V.add(c, o + x, 22, z, 10, 14, 10); V.add("oro", o + x, 32, z, 12, 4, 12); }
    V.hacer();
    // ruta punteada
    const ruta = []; const P0 = [-60, -190], P1 = [130, 40], P2 = [-40, 290];
    for (let k = 0; k <= 40; k++) { const u = k / 40, a = u < 0.5 ? u * 2 : 1, b = u < 0.5 ? 0 : (u - 0.5) * 2; const x = u < 0.5 ? P0[0] + (P1[0] - P0[0]) * a : P1[0] + (P2[0] - P1[0]) * b, z = u < 0.5 ? P0[1] + (P1[1] - P0[1]) * a : P1[1] + (P2[1] - P1[1]) * b; const m = caja(5, 2, 5, MB("#e0202a"), o + x, 4, z); m.visible = false; s.g.add(m); ruta.push(m); }
    s.ruta = ruta; s.rutaPts = [P0, P1, P2];
    const bm = barcoGrupo(); bm.g.scale.setScalar(0.32); s.g.add(bm.g); s.barcoMapa = bm;
    s.vida = { olas: 1, pajaros: "gaviota" };
    spot(s, "mapa", 0, 0, 0, { mapa: [0, 0, 40], barco_mapa: [0, 10, 0], atenas: [-60, 30, -200], creta: [-40, 30, 300], naxos: [120, 20, 20], egeo: [100, 10, 60] });
  }
  // barcos (compartidos: se colocan por plano)
  const BARCO = barcoGrupo(), BARCO2 = barcoGrupo(); scene.add(BARCO.g, BARCO2.g);
  return { SETS, llamas, BARCO, BARCO2 };
}

// Escena común: renderer, luces, cielo por escenario y construcción perezosa de escenarios.
import { THREE, Particulas } from "./motor.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { BokehPass } from "three/addons/postprocessing/BokehPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { SETS, CIELOS } from "./sets.js";
export const W = 1920, H = 1080;
export const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(1); renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping;
document.body.appendChild(renderer.domElement);
export const scene = new THREE.Scene();
export const cam = new THREE.PerspectiveCamera(40, W / H, 1, 5000);
export const hemi = new THREE.HemisphereLight("#cfe6ff", "#6b5a3a", 1.1); scene.add(hemi);
export const sol = new THREE.DirectionalLight("#fff1d8", 2.6); sol.castShadow = true; sol.shadow.mapSize.set(2048, 2048);
Object.assign(sol.shadow.camera, { left: -260, right: 260, top: 260, bottom: -260, near: 1, far: 2000 }); sol.shadow.bias = -0.0006; sol.shadow.normalBias = 0.8;
scene.add(sol, sol.target);
export const part = new Particulas(scene, 500);
const cC = document.createElement("canvas"); cC.width = 2; cC.height = 256; const cT = new THREE.CanvasTexture(cC); cT.colorSpace = THREE.SRGBColorSpace;
scene.fog = new THREE.Fog("#cfe6ff", 500, 2200);
const construidos = {}; let actual = null, vivosActual = [];
export function escenario(nombre) {
  if (actual === nombre) return construidos[nombre];
  for (const k in construidos) construidos[k].g.visible = false;
  if (!construidos[nombre]) { const g = new THREE.Group(), vivos = []; scene.add(g); const anclas = SETS[nombre].build(g, vivos) || {}; construidos[nombre] = { g, vivos, anclas }; }
  const s = construidos[nombre]; s.g.visible = true; actual = nombre; vivosActual = s.vivos;
  const c = CIELOS[SETS[nombre].cielo]; const g2 = cC.getContext("2d"), gr = g2.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, c[0]); gr.addColorStop(1, c[1]); g2.fillStyle = gr; g2.fillRect(0, 0, 2, 256); cT.needsUpdate = true; scene.background = cT;
  scene.fog.color.set(c[2]); scene.fog.near = c[3]; scene.fog.far = c[4]; hemi.color.set(c[5]); hemi.groundColor.set(c[6]); hemi.intensity = c[7]; sol.color.set(c[8]); sol.intensity = c[9]; renderer.toneMappingExposure = c[10]; s.solDir = c[11]; s.cielo = SETS[nombre].cielo;
  return s;
}
// ---- postprocesado: bloom (fuego, lava, rayos, magia), desenfoque de profundidad en primeros planos, gradación de color y viñeta por capítulo
export const composer = new EffectComposer(renderer); composer.setSize(W, H);
const rp = new RenderPass(scene, cam); composer.addPass(rp);
export const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.32, 0.4, 0.96); composer.addPass(bloom);
export const bokeh = new BokehPass(scene, cam, { focus: 100, aperture: 0.0012, maxblur: 0.006 }); composer.addPass(bokeh);
export const grado = new ShaderPass({ uniforms: { tDiffuse: { value: null }, tinte: { value: new THREE.Vector3(1, 1, 1) }, sat: { value: 1.12 }, vig: { value: 0.35 }, con: { value: 1.05 } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
  fragmentShader: `uniform sampler2D tDiffuse; uniform vec3 tinte; uniform float sat, vig, con; varying vec2 vUv;
    void main(){ vec4 c = texture2D(tDiffuse, vUv); vec3 col = c.rgb; float l = dot(col, vec3(0.299, 0.587, 0.114)); col = mix(vec3(l), col, sat); col = (col - 0.5) * con + 0.5; col *= tinte;
      float d = distance(vUv, vec2(0.5)); col *= 1.0 - vig * smoothstep(0.35, 0.85, d); gl_FragColor = vec4(col, c.a); }` });
composer.addPass(grado); composer.addPass(new OutputPass());
export function postpro(dist, cerca, tinte) { bokeh.enabled = cerca; bokeh.uniforms.focus.value = dist; grado.uniforms.tinte.value.set(...tinte); }
export function render() { composer.render(); }
export function vivos(t) { for (const f of vivosActual) f(t); }
export function solSobre(x, z, s) { const d = s.solDir; sol.position.set(x + d[0], d[1], z + d[2]); sol.target.position.set(x, 0, z); }
export function mira(px, py, pz, tx, ty, tz, fov = 40) { cam.position.set(px, py, pz); cam.fov = fov; cam.updateProjectionMatrix(); cam.lookAt(tx, ty, tz); }

// Arte pixel original (sin assets externos ni licencias): estilo RPG portatil
// clasico de vista cenital, tiles de 16x16, contorno oscuro y 2-3 tonos por
// material. Todo se dibuja a 1x en canvas fuera de pantalla y se escala sin
// suavizado.
import { TILE_SIZE as T } from './world'
import type { Dir } from './world'

export const OUT = '#2a2b3d'

type Canvas2 = HTMLCanvasElement
const make = (w = T, h = T): Canvas2 => {
  const c = document.createElement('canvas')
  c.width = w
  c.height = h
  return c
}

export function shade(hex: string, f: number): string {
  const n = parseInt(hex.slice(1), 16)
  const ch = (v: number) => Math.max(0, Math.min(255, Math.round(v * f)))
  const r = ch(n >> 16)
  const g = ch((n >> 8) & 255)
  const b = ch(n & 255)
  return `#${((1 << 24) | (r << 16) | (g << 8) | b).toString(16).slice(1)}`
}

// ---------------------------------------------------------------- personajes
// O contorno, H pelo, h pelo oscuro, S piel, s piel sombra, E ojo, W blanco,
// C camisa, c camisa sombra, P pantalon, B zapatos.
const DOWN = [
  '................',
  '....OOOOOOOO....',
  '...OHHHHHHHHO...',
  '..OHHHHHHHHHHO..',
  '..OHHhHHHHhHHO..',
  '..OHSSSSSSSSHO..',
  '..OSSSSSSSSSSO..',
  '..OSSESSSSESSO..',
  '..OSSESSSSESSO..',
  '..OSsSSSSSSsSO..',
  '...OSSSSSSSSO...',
  '....OOOWWOOO....',
  '..OCCCCCCCCCCO..',
  '..OCcCCCCCCcCO..',
  '...OPPPOOPPPO...',
  '...OBBBOOBBBO...',
]
const DOWN_W = DOWN.slice(0, 14).concat(['...OPPPO.OPPPO..', '...OBBBO.OBBBO..'])
const UP = [
  '................',
  '....OOOOOOOO....',
  '...OHHHHHHHHO...',
  '..OHHHHHHHHHHO..',
  '..OHHHHHHHHHHO..',
  '..OHHHHHHHHHHO..',
  '..OHHHHHHHHHHO..',
  '..OHHhHHHHhHHO..',
  '..OHHHHHHHHHHO..',
  '..OHHHHHHHHHHO..',
  '...OHHHHHHHHO...',
  '....OOOCCOOO....',
  '..OCCCCCCCCCCO..',
  '..OCcCCCCCCcCO..',
  '...OPPPOOPPPO...',
  '...OBBBOOBBBO...',
]
const UP_W = UP.slice(0, 14).concat(['...OPPPO.OPPPO..', '...OBBBO.OBBBO..'])
const LEFT = [
  '................',
  '....OOOOOOOO....',
  '...OHHHHHHHHO...',
  '..OHHHHHHHHHHO..',
  '..OHHHHHHHHHHO..',
  '..OSSSHHHHHHHO..',
  '..OSSSSHHHHHHO..',
  '..OSESSSSHHHHO..',
  '..OSESSSSHHHHO..',
  '..OSsSSSSHHHHO..',
  '...OSSSSSSSHO...',
  '....OOWWCCOO....',
  '...OCCCCCCCCO...',
  '...OCCcCCCCCO...',
  '...OOPPPPPPOO...',
  '...OBBBBBBBBO...',
]
const LEFT_W = LEFT.slice(0, 14).concat(['...OPPPPO.OPPO..', '...OBBBBO.OBBO..'])

const GRIDS: Record<string, string[]> = {
  'down0': DOWN, 'down1': DOWN_W, 'up0': UP, 'up1': UP_W, 'left0': LEFT, 'left1': LEFT_W,
}

export interface Look {
  hair: string
  skin: string
  shirt: string
  pants?: string
  cap?: boolean
}

const charCache = new Map<string, Canvas2>()

export function characterSprite(look: Look, dir: Dir, frame: 0 | 1): Canvas2 {
  const key = `${look.hair}${look.skin}${look.shirt}${look.pants ?? ''}${look.cap ? 'c' : ''}|${dir}|${frame}`
  const hit = charCache.get(key)
  if (hit) return hit
  const flip = dir === 'right'
  const grid = GRIDS[`${flip ? 'left' : dir}${frame}`] as string[]
  const pal: Record<string, string> = {
    O: OUT, H: look.hair, h: shade(look.hair, 0.7), S: look.skin, s: shade(look.skin, 0.85),
    E: OUT, W: '#ffffff', C: look.shirt, c: shade(look.shirt, 0.78),
    P: look.pants ?? '#3d4a6b', B: '#5a3a28',
  }
  const c = make()
  const x = c.getContext('2d') as CanvasRenderingContext2D
  grid.forEach((row, y) => {
    for (let i = 0; i < 16; i++) {
      const ch = row[flip ? 15 - i : i]
      if (!ch || ch === '.') continue
      x.fillStyle = pal[ch] ?? OUT
      x.fillRect(i, y, 1, 1)
    }
  })
  if (look.cap) {
    // gorra: visera y detalle sobre el pelo
    x.fillStyle = '#d8333a'
    for (let yy = 2; yy <= 4; yy++) for (let xx = 3; xx <= 12; xx++) {
      const px = x.getImageData(xx, yy, 1, 1).data
      if (px[3] !== 0 && !(px[0] === 42 && px[1] === 43)) x.fillRect(xx, yy, 1, 1)
    }
    x.fillStyle = '#ffffff'
    if (dir === 'down') x.fillRect(7, 3, 2, 1)
    x.fillStyle = '#9d2228'
    if (dir === 'down') x.fillRect(4, 5, 8, 1)
  }
  charCache.set(key, c)
  return c
}

export const shadowSprite = (() => {
  let c: Canvas2 | null = null
  return () => {
    if (c) return c
    c = make()
    const x = c.getContext('2d') as CanvasRenderingContext2D
    x.fillStyle = 'rgba(30,30,60,0.28)'
    x.fillRect(4, 14, 8, 2)
    x.fillRect(3, 15, 10, 1)
    return c
  }
})()

// -------------------------------------------------------------------- tiles
const px = (x: CanvasRenderingContext2D, c: string, X: number, Y: number, w = 1, h = 1) => {
  x.fillStyle = c
  x.fillRect(X, Y, w, h)
}

function floorTile(x: CanvasRenderingContext2D, tx: number, ty: number) {
  const a = (tx + ty) % 2 === 0
  px(x, a ? '#f7ecd4' : '#efe0c2', 0, 0, 16, 16)
  px(x, '#d9c59b', 0, 15, 16, 1)
  px(x, '#d9c59b', 15, 0, 1, 16)
  px(x, '#fffaf0', 1, 1, 3, 1)
  px(x, '#fffaf0', 1, 2, 1, 1)
  if (a) { px(x, '#e6d3ae', 9, 9, 1, 1); px(x, '#e6d3ae', 10, 10, 1, 1) }
}

function rugTile(x: CanvasRenderingContext2D, tx: number, ty: number, edge: { l: boolean; r: boolean; t: boolean; b: boolean }) {
  floorTile(x, tx, ty)
  px(x, '#c7414a', 0, 0, 16, 16)
  px(x, '#d9585f', 1, 1, 14, 14)
  px(x, '#c7414a', 3, 3, 10, 10)
  px(x, '#e9d6a1', 7, 7, 2, 2)
  if (edge.t) px(x, '#f1d68a', 0, 0, 16, 1)
  if (edge.b) px(x, '#f1d68a', 0, 15, 16, 1)
  if (edge.l) px(x, '#f1d68a', 0, 0, 1, 16)
  if (edge.r) px(x, '#f1d68a', 15, 0, 1, 16)
}

function wallFace(x: CanvasRenderingContext2D, tx: number) {
  px(x, '#9db6d8', 0, 0, 16, 16)
  px(x, '#b5cae6', 0, 0, 16, 2)
  px(x, '#86a0c6', 0, 6, 16, 1)
  if (tx % 2 === 0) px(x, '#86a0c6', 15, 0, 1, 12)
  px(x, '#5f7399', 0, 12, 16, 4)
  px(x, '#7388ae', 0, 12, 16, 1)
  px(x, OUT, 0, 15, 16, 1)
}

function wallCap(x: CanvasRenderingContext2D) {
  px(x, '#5f5a80', 0, 0, 16, 16)
  px(x, '#7a74a0', 0, 0, 16, 3)
  px(x, '#46425f', 0, 13, 16, 3)
  px(x, '#6a6590', 2, 5, 12, 1)
}

function windowTile(x: CanvasRenderingContext2D, left: boolean) {
  wallFace(x, 1)
  px(x, OUT, 0, 1, 16, 11)
  px(x, '#fdfbf3', 1, 2, 14, 9)
  px(x, '#8fd0ee', 2, 3, 12, 7)
  px(x, '#c7ecfa', 2, 3, 12, 2)
  px(x, '#ffffff', left ? 4 : 3, 4, 3, 1)
  px(x, '#fdfbf3', 7, 3, 2, 7)
  px(x, '#fdfbf3', 2, 6, 12, 1)
  px(x, '#d8cdb0', 0, 12, 16, 1)
}

function whiteboardTile(x: CanvasRenderingContext2D, left: boolean) {
  wallFace(x, 1)
  px(x, OUT, left ? 1 : 0, 1, left ? 15 : 15, 11)
  px(x, '#ffffff', left ? 2 : 0, 2, left ? 14 : 14, 9)
  px(x, '#5b7bd6', left ? 4 : 2, 4, 8, 1)
  px(x, '#d8683a', left ? 4 : 2, 6, 6, 1)
  px(x, '#3fa36b', left ? 4 : 2, 8, 9, 1)
}

function bookshelfTile(x: CanvasRenderingContext2D) {
  floorTile(x, 0, 0)
  px(x, OUT, 0, 1, 16, 15)
  px(x, '#a8743f', 1, 2, 14, 13)
  px(x, '#7b5129', 1, 7, 14, 1)
  px(x, '#7b5129', 1, 13, 14, 1)
  const cols = ['#d8453d', '#3f77c9', '#4ea05e', '#f2b33f', '#8c5bc0', '#e0763a']
  for (const [row, y, h] of [[0, 3, 4], [1, 8, 5]] as const) {
    let xx = 2
    let i = row * 3
    while (xx < 14) {
      const w = (i % 3) + 2
      px(x, cols[i % cols.length] as string, xx, y, Math.min(w, 14 - xx), h)
      px(x, 'rgba(255,255,255,0.35)', xx, y, 1, h)
      xx += w + 0
      i++
    }
  }
  px(x, '#5a3a1e', 1, 14, 14, 1)
}

function plantTile(x: CanvasRenderingContext2D, tx: number, ty: number) {
  floorTile(x, tx, ty)
  px(x, 'rgba(30,30,60,0.2)', 3, 14, 10, 2)
  px(x, OUT, 4, 9, 8, 7)
  px(x, '#c7683a', 5, 10, 6, 5)
  px(x, '#e08a52', 5, 10, 6, 1)
  px(x, OUT, 3, 2, 10, 8)
  px(x, '#3e9a4e', 4, 3, 8, 6)
  px(x, '#62c26d', 5, 3, 3, 3)
  px(x, '#2d7a3c', 8, 6, 3, 3)
  px(x, '#62c26d', 6, 1, 4, 3)
  px(x, OUT, 6, 0, 4, 1)
}

function deskTile(x: CanvasRenderingContext2D, left: boolean, right: boolean, tx: number, ty: number) {
  floorTile(x, tx, ty)
  px(x, 'rgba(30,30,60,0.2)', 0, 14, 16, 2)
  px(x, OUT, left ? 0 : -1, 3, 16 + (left ? 0 : 1), 12)
  px(x, '#d49a58', left ? 1 : 0, 4, 15 - (left ? 0 : 0), 6)
  px(x, '#ecb978', left ? 1 : 0, 4, 14, 1)
  px(x, '#a8723a', left ? 1 : 0, 10, 15, 4)
  px(x, '#8a5a2b', left ? 1 : 0, 13, 15, 1)
  if (right) px(x, OUT, 15, 3, 1, 12)
}

function tableTile(x: CanvasRenderingContext2D, left: boolean, right: boolean, top: boolean) {
  px(x, OUT, left ? 0 : -1, top ? 2 : -1, 16 + (right ? 0 : 1), 16)
  px(x, '#d49a58', left ? 1 : 0, top ? 3 : 0, 14 + (left ? 0 : 1) + (right ? 0 : 1), 13)
  px(x, '#ecb978', 0, top ? 3 : 0, 16, 1)
  if (!top) px(x, '#a8723a', 0, 12, 16, 3)
}

function doorTile(x: CanvasRenderingContext2D, left: boolean) {
  wallCap(x)
  px(x, '#d8c9a0', 0, 0, 16, 16)
  px(x, '#b59a62', 0, 0, 16, 2)
  px(x, '#8d6f3f', left ? 2 : 0, 4, left ? 14 : 14, 12)
  px(x, '#a98a52', left ? 3 : 1, 5, 12, 10)
  px(x, OUT, left ? 2 : 14, 4, 1, 12)
}

function chairTile(x: CanvasRenderingContext2D, tx: number, ty: number) {
  floorTile(x, tx, ty)
  px(x, 'rgba(30,30,60,0.2)', 3, 14, 10, 2)
  px(x, OUT, 3, 3, 10, 11)
  px(x, '#4e5d8f', 4, 4, 8, 9)
  px(x, '#6c7db3', 4, 4, 8, 2)
  px(x, '#3b4770', 4, 11, 8, 2)
}

const tileCache = new Map<string, Canvas2>()
function cached(key: string, draw: (x: CanvasRenderingContext2D) => void): Canvas2 {
  const hit = tileCache.get(key)
  if (hit) return hit
  const c = make()
  draw(c.getContext('2d') as CanvasRenderingContext2D)
  tileCache.set(key, c)
  return c
}

export type TileGetter = (ch: string, tx: number, ty: number, rows: readonly string[]) => Canvas2

export const tileSprite: TileGetter = (ch, tx, ty, rows) => {
  const at = (X: number, Y: number) => rows[Y]?.[X]
  const w = rows[0]?.length ?? 0
  const h = rows.length
  const parity = (tx + ty) % 2
  switch (ch) {
    case '#':
      return ty === 0 ? cached(`wf${tx % 2}`, (x) => wallFace(x, tx)) : cached('wc', wallCap)
    case 'W': return cached(`win${at(tx - 1, ty) === 'W' ? 'r' : 'l'}`, (x) => windowTile(x, at(tx - 1, ty) !== 'W'))
    case 'M': return cached(`wb${at(tx - 1, ty) === 'M' ? 'r' : 'l'}`, (x) => whiteboardTile(x, at(tx - 1, ty) !== 'M'))
    case 'B': return cached('book', bookshelfTile)
    case 'P': return cached(`plant${parity}`, (x) => plantTile(x, tx, ty))
    case 'd': return cached(`desk${at(tx - 1, ty) === 'd' ? 1 : 0}${at(tx + 1, ty) === 'd' ? 1 : 0}${parity}`, (x) => deskTile(x, at(tx - 1, ty) !== 'd', at(tx + 1, ty) !== 'd', tx, ty))
    case 'T': return cached(`tb${at(tx - 1, ty) === 'T' ? 1 : 0}${at(tx + 1, ty) === 'T' ? 1 : 0}${at(tx, ty - 1) === 'T' ? 1 : 0}`, (x) => tableTile(x, at(tx - 1, ty) !== 'T', at(tx + 1, ty) !== 'T', at(tx, ty - 1) !== 'T'))
    case 'X': return cached(`door${at(tx - 1, ty) === 'X' ? 'r' : 'l'}`, (x) => doorTile(x, at(tx - 1, ty) !== 'X'))
    case 's': return cached(`chair${parity}`, (x) => chairTile(x, tx, ty))
    case 'r': return cached(`rug${at(tx - 1, ty) === 'r' ? 1 : 0}${at(tx + 1, ty) === 'r' ? 1 : 0}${at(tx, ty - 1) === 'r' ? 1 : 0}${at(tx, ty + 1) === 'r' ? 1 : 0}${parity}`, (x) => rugTile(x, tx, ty, {
      l: at(tx - 1, ty) !== 'r' && at(tx - 1, ty) !== 'T', r: at(tx + 1, ty) !== 'r' && at(tx + 1, ty) !== 'T',
      t: at(tx, ty - 1) !== 'r' && at(tx, ty - 1) !== 'T', b: at(tx, ty + 1) !== 'r' && at(tx, ty + 1) !== 'T',
    }))
    default:
      void w; void h
      return cached(`floor${parity}`, (x) => floorTile(x, tx, ty))
  }
}

/** Renderiza el mapa estatico completo una sola vez. */
export function renderStaticMap(rows: readonly string[]): Canvas2 {
  const out = make((rows[0]?.length ?? 0) * T, rows.length * T)
  const x = out.getContext('2d') as CanvasRenderingContext2D
  rows.forEach((row, ty) => [...row].forEach((ch, tx) => {
    // objetos sobre suelo: pinta suelo debajo si el sprite tiene transparencia
    if (ch === 'T') x.drawImage(tileSprite('r', tx, ty, rows), tx * T, ty * T)
    x.drawImage(tileSprite(ch, tx, ty, rows), tx * T, ty * T)
  }))
  return out
}

// ------------------------------------------------------- objetos dinamicos
export function drawMonitor(x: CanvasRenderingContext2D, tx: number, ty: number, on: boolean, now: number) {
  const X = tx * T
  const Y = ty * T
  px(x, OUT, X + 2, Y + 0, 12, 9)
  px(x, on ? '#8fe6ff' : '#4a5870', X + 3, Y + 1, 10, 6)
  if (on) {
    px(x, '#d6f8ff', X + 3, Y + 1, 10, 1)
    const n = 3 + (Math.floor(now / 350) % 4)
    px(x, '#2a6b86', X + 4, Y + 3, n, 1)
    px(x, '#2a6b86', X + 4, Y + 5, 7 - (n % 3), 1)
  } else px(x, '#6b7a92', X + 4, Y + 2, 3, 1)
  px(x, OUT, X + 6, Y + 9, 4, 1)
  px(x, '#e9e4d6', X + 4, Y + 11, 8, 2)
  px(x, OUT, X + 4, Y + 13, 8, 1)
}

export function drawBubble(x: CanvasRenderingContext2D, tx: number, ty: number, now: number) {
  const X = Math.round(tx * T) + 9
  const Y = Math.round(ty * T) - 9
  px(x, OUT, X, Y, 9, 6)
  px(x, '#ffffff', X + 1, Y + 1, 7, 4)
  px(x, OUT, X + 2, Y + 6, 2, 1)
  const k = Math.floor(now / 300) % 3
  for (let i = 0; i < 3; i++) px(x, i === k ? '#d8683a' : OUT, X + 2 + i * 2, Y + 3, 1, 1)
}

export function drawUnknown(x: CanvasRenderingContext2D, tx: number, ty: number) {
  const X = Math.round(tx * T) + 9
  const Y = Math.round(ty * T) - 9
  px(x, OUT, X, Y, 7, 8)
  px(x, '#ffe9a8', X + 1, Y + 1, 5, 6)
  px(x, OUT, X + 2, Y + 2, 3, 1)
  px(x, OUT, X + 4, Y + 3, 1, 1)
  px(x, OUT, X + 3, Y + 4, 1, 1)
  px(x, OUT, X + 3, Y + 6, 1, 1)
}

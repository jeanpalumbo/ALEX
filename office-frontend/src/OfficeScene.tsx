import { useEffect, useRef } from 'react'
import type { OfficeAgent } from './types'
import { OFFICE_LAYOUT, OfficeWorld, TILE_SIZE as T, parseLayout, tileAt, type Dir } from './world'

const map = parseLayout(OFFICE_LAYOUT)
const SCALE = 4
const INK = '#2b2d4a'

// Arte original dibujado con rectangulos (sin assets externos ni licencias).
// Paleta de pelo/piel/camisa por agente, estable segun su indice en el roster.
const LOOKS: ReadonlyArray<readonly [string, string, string]> = [
  ['#3b2a1d', '#e8b890', '#3d6fb5'],
  ['#a0432b', '#f1c9a5', '#f6a93a'],
  ['#1d1d1d', '#b9825a', '#5b8c5a'],
  ['#141018', '#c58c64', '#a24f9a'],
  ['#5a3a22', '#e8b890', '#c0504d'],
  ['#d9a441', '#f5d2b3', '#4aa3a2'],
  ['#2a1b12', '#d9a679', '#8a6a3b'],
  ['#0f0f14', '#a8744f', '#6f5fb3'],
  ['#6b3b8a', '#f1c9a5', '#d96f8a'],
  ['#1b2b3a', '#c58c64', '#e0b030'],
]
const PLAYER_LOOK = ['#c0282d', '#f1c9a5', INK] as const

type Ctx = CanvasRenderingContext2D
const rect = (c: Ctx, x: number, y: number, w: number, h: number, color: string) => {
  c.fillStyle = color
  c.fillRect(Math.round(x), Math.round(y), w, h)
}

function drawTile(c: Ctx, ch: string, tx: number, ty: number) {
  const x = tx * T
  const y = ty * T
  if (ch === '#') {
    rect(c, x, y, T, T, '#5b4a6e')
    rect(c, x, y + T - 3, T, 3, '#3f3150')
    rect(c, x, y, T, 2, '#7a6890')
    return
  }
  rect(c, x, y, T, T, (tx + ty) % 2 === 0 ? '#e8d3a8' : '#e0c99b')
  if (ch === 'B') {
    rect(c, x, y, T, T, '#6b4a2b')
    const books = ['#c0504d', '#3d6fb5', '#5b8c5a', '#f6b24a']
    for (let r = 0; r < 3; r++) for (let k = 0; k < 4; k++) rect(c, x + 1 + k * 4, y + 2 + r * 4, 3, 3, books[(r + k) % 4] as string)
  } else if (ch === 'W') {
    rect(c, x, y, T, T, '#5b4a6e')
    rect(c, x + 1, y + 2, T - 2, T - 5, '#a8d8f0')
    rect(c, x + 7, y + 2, 2, T - 5, '#5b4a6e')
    rect(c, x + 1, y + 3, T - 2, 2, '#d8f0fb')
  } else if (ch === 'd') {
    rect(c, x, y + 3, T, T - 3, '#8a5a2b')
    rect(c, x, y + 3, T, 2, '#b07a43')
    rect(c, x, y + T - 2, T, 2, '#5e3b17')
  } else if (ch === 'P') {
    rect(c, x + 4, y + 9, 8, 6, '#a0522d')
    rect(c, x + 3, y + 3, 10, 7, '#3f8f4a')
    rect(c, x + 5, y + 1, 6, 5, '#5fb869')
  } else if (ch === 'T') {
    rect(c, x, y + 2, T, T - 3, '#a9784a')
    rect(c, x, y + 2, T, 2, '#c99562')
    rect(c, x, y + T - 2, T, 2, '#6e4a2a')
  } else if (ch === 'X') {
    rect(c, x, y, T, T, '#6b4a2b')
    rect(c, x + 2, y, T - 4, T, '#b07a43')
  } else if (ch === 's') {
    rect(c, x + 3, y + 5, 10, 8, '#4a4c6a')
    rect(c, x + 3, y + 5, 10, 2, '#6a6c8a')
  }
}

function drawChar(c: Ctx, dir: Dir, frame: number, moving: boolean, look: readonly string[], tx: number, ty: number, seated: boolean, isPlayer: boolean) {
  const [hair, skin, shirt] = look as [string, string, string]
  const x = Math.round(tx * T)
  const y = Math.round(ty * T) - 3
  const bob = moving && frame ? 1 : 0
  rect(c, x + 3, y + 14, 10, 3, 'rgba(0,0,0,.25)')
  if (!seated) {
    rect(c, x + 5, y + 12 + (moving && frame ? 1 : 0), 2, 3, INK)
    rect(c, x + 9, y + 12 + (moving && !frame ? 1 : 0), 2, 3, INK)
  }
  rect(c, x + 4, y + 7 - bob, 8, 6, shirt)
  rect(c, x + 3, y + 8 - bob, 1, 4, shirt)
  rect(c, x + 12, y + 8 - bob, 1, 4, shirt)
  rect(c, x + 4, y + 2 - bob, 8, 6, skin)
  if (dir === 'down') {
    rect(c, x + 4, y + 1 - bob, 8, 3, hair)
    rect(c, x + 6, y + 5 - bob, 1, 2, '#111')
    rect(c, x + 9, y + 5 - bob, 1, 2, '#111')
  } else if (dir === 'up') {
    rect(c, x + 4, y + 1 - bob, 8, 6, hair)
  } else {
    rect(c, x + 4, y + 1 - bob, 8, 3, hair)
    rect(c, dir === 'left' ? x + 4 : x + 11, y + 3 - bob, 1, 4, hair)
    rect(c, dir === 'left' ? x + 5 : x + 10, y + 5 - bob, 1, 2, '#111')
  }
  if (isPlayer) {
    rect(c, x + 3, y + 1 - bob, 10, 2, '#c0282d')
    rect(c, x + 6, y + 0 - bob, 4, 1, '#fff')
  }
}

function wrap(text: string, n: number): string[] {
  const lines: string[] = []
  let cur = ''
  for (const word of text.split(' ')) {
    if ((cur + ' ' + word).trim().length > n) {
      lines.push(cur)
      cur = word
    } else cur = (cur + ' ' + word).trim()
  }
  if (cur) lines.push(cur)
  return lines
}

const KEYS: Record<string, Dir> = {
  ArrowUp: 'up', w: 'up', ArrowDown: 'down', s: 'down', ArrowLeft: 'left', a: 'left', ArrowRight: 'right', d: 'right',
}

interface Dialog { name: string; text: string; shown: number }

interface Props {
  agents: OfficeAgent[]
  selectedId: string | null
  onSelect: (agentId: string) => void
}

function line(a: OfficeAgent): string {
  return a.status === 'working' ? `Estoy trabajando en: ${a.task?.title ?? '(sin detalle)'}.` : 'Sin tarea activa ahora mismo.'
}

export function OfficeScene({ agents, selectedId, onSelect }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const worldRef = useRef<OfficeWorld | null>(null)
  const agentsRef = useRef<OfficeAgent[]>(agents)
  const selectedRef = useRef<string | null>(selectedId)
  const onSelectRef = useRef(onSelect)
  const dialogRef = useRef<Dialog | null>(null)
  const heldRef = useRef<Dir[]>([])
  useEffect(() => {
    agentsRef.current = agents
    selectedRef.current = selectedId
    onSelectRef.current = onSelect
  })

  // El mundo se recrea solo si cambia el conjunto de agentes; los cambios de
  // estado/tarea se aplican sobre el mismo mundo sin mover a nadie.
  const idsKey = agents.map((a) => a.agent_id).join('|')
  useEffect(() => {
    const reduce = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
    const seeds = agentsRef.current.map((a) => ({
      id: a.agent_id, name: a.display_name, role: a.role, status: a.status, task: a.task?.title ?? null,
    }))
    worldRef.current = seeds.length ? new OfficeWorld(map, seeds, { wander: !reduce }) : null
  }, [idsKey])

  useEffect(() => {
    const w = worldRef.current
    if (!w) return
    for (const a of agents) {
      const cur = w.agents.find((x) => x.id === a.agent_id)
      const task = a.task?.title ?? null
      if (cur && (cur.status !== a.status || cur.task !== task)) w.setStatus(a.agent_id, a.status, task)
    }
  }, [agents])

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return
    canvas.width = map.width * T * SCALE
    canvas.height = map.height * T * SCALE
    let raf = 0
    let last = performance.now()

    const look = (id: string) => LOOKS[Math.max(0, agentsRef.current.findIndex((a) => a.agent_id === id)) % LOOKS.length] as readonly string[]

    const openDialog = (id: string) => {
      const a = agentsRef.current.find((x) => x.agent_id === id)
      if (!a) return
      onSelectRef.current(id)
      dialogRef.current = { name: `${a.display_name} · ${a.role}`, text: line(a), shown: 0 }
    }

    const interact = () => {
      const d = dialogRef.current
      if (d && d.shown < d.text.length) d.shown = d.text.length
      else if (d) dialogRef.current = null
      else {
        const f = worldRef.current?.facingAgent()
        if (f) openDialog(f.id)
      }
    }

    const frame = (now: number) => {
      const dt = Math.min(now - last, 100)
      last = now
      const w = worldRef.current
      const dialog = dialogRef.current
      if (w) {
        const held = heldRef.current
        if (!dialog && held.length) w.movePlayer(held[held.length - 1] as Dir)
        w.update(dt)
      }
      if (dialog) dialog.shown += dt / 25

      ctx.imageSmoothingEnabled = false
      ctx.setTransform(SCALE, 0, 0, SCALE, 0, 0)
      for (let y = 0; y < map.height; y++) for (let x = 0; x < map.width; x++) drawTile(ctx, tileAt(map, x, y) ?? '#', x, y)
      if (w) {
        for (const a of w.agents) {
          const on = w.isSeated(a) && a.status === 'working'
          const mx = a.seat.x * T
          const my = (a.seat.y - 1) * T
          rect(ctx, mx + 3, my + 1, 10, 8, '#222')
          rect(ctx, mx + 4, my + 2, 8, 6, on ? '#7fe3ff' : '#3a4a55')
          if (on) rect(ctx, mx + 5, my + 4, 4 + (Math.floor(now / 300) % 3) * 2, 1, '#fff')
        }
        const actors = [...w.agents.map((a) => ({ a, m: a.mover })), { a: null, m: w.player }]
        actors.sort((l, r) => w.renderPos(l.m).y - w.renderPos(r.m).y)
        for (const { a, m } of actors) {
          const pos = w.renderPos(m)
          const seated = a ? w.isSeated(a) : false
          drawChar(ctx, m.dir, m.walkFrame, !!m.from, a ? look(a.id) : PLAYER_LOOK, pos.x, pos.y, seated, !a)
          if (a && a.status === 'working' && seated) {
            const bx = Math.round(pos.x * T) + 10
            const by = Math.round(pos.y * T) - 8
            rect(ctx, bx, by, 5, 4, '#fff')
            rect(ctx, bx - 1, by + 1, 7, 2, '#fff')
            for (let i = 0; i < 3; i++) rect(ctx, bx + i * 2, by + (Math.floor(now / 250) % 3 === i ? 1 : 2), 1, 1, INK)
          }
          if (a && a.id === selectedRef.current) {
            ctx.strokeStyle = '#f6b24a'
            ctx.lineWidth = 1
            ctx.strokeRect(Math.round(pos.x * T) + 2.5, Math.round(pos.y * T) - 4.5, 11, 18)
          }
        }
        // Nombres en resolucion real (no escalada) para que se lean bien.
        ctx.setTransform(1, 0, 0, 1, 0, 0)
        ctx.font = 'bold 12px monospace'
        ctx.textAlign = 'center'
        for (const a of w.agents) {
          const pos = w.renderPos(a.mover)
          const label = a.name.split(' ')[0] ?? a.name
          const cx = (pos.x * T + T / 2) * SCALE
          const cy = (pos.y * T + T + 1) * SCALE
          ctx.fillStyle = 'rgba(255,255,255,.85)'
          ctx.fillRect(cx - label.length * 3.6 - 3, cy - 10, label.length * 7.2 + 6, 14)
          ctx.fillStyle = INK
          ctx.fillText(label, cx, cy)
        }
        ctx.textAlign = 'left'
      }

      ctx.setTransform(1, 0, 0, 1, 0, 0)
      if (dialog) {
        const h = 110
        const y = canvas.height - h - 14
        ctx.fillStyle = INK
        ctx.fillRect(14, y, canvas.width - 28, h)
        ctx.fillStyle = '#fff'
        ctx.fillRect(20, y + 6, canvas.width - 40, h - 12)
        ctx.fillStyle = INK
        ctx.font = 'bold 17px monospace'
        ctx.fillText(dialog.name.toUpperCase(), 34, y + 32)
        ctx.font = '16px monospace'
        wrap(dialog.text.slice(0, Math.floor(dialog.shown)), 62).forEach((l, i) => ctx.fillText(l, 34, y + 58 + i * 22))
        if (dialog.shown >= dialog.text.length && Math.floor(now / 400) % 2) ctx.fillText('▼', canvas.width - 50, y + h - 18)
      }
      raf = requestAnimationFrame(frame)
    }
    raf = requestAnimationFrame(frame)

    const onKeyDown = (e: KeyboardEvent) => {
      const dir = KEYS[e.key]
      if (dir) {
        e.preventDefault()
        if (!heldRef.current.includes(dir)) heldRef.current.push(dir)
      } else if (['z', 'Z', 'Enter', ' '].includes(e.key)) {
        e.preventDefault()
        interact()
      }
    }
    const onKeyUp = (e: KeyboardEvent) => {
      const dir = KEYS[e.key]
      if (dir) heldRef.current = heldRef.current.filter((d) => d !== dir)
    }
    const onClick = (e: MouseEvent) => {
      const w = worldRef.current
      if (!w) return
      const r = canvas.getBoundingClientRect()
      const tx = Math.floor(((e.clientX - r.left) / r.width) * map.width)
      const ty = Math.floor(((e.clientY - r.top) / r.height) * map.height)
      const a = w.agentAt(tx, ty) ?? w.agentAt(tx, ty + 1)
      if (a) openDialog(a.id)
    }
    const onBlur = () => { heldRef.current = [] }
    canvas.addEventListener('keydown', onKeyDown)
    canvas.addEventListener('keyup', onKeyUp)
    canvas.addEventListener('blur', onBlur)
    canvas.addEventListener('click', onClick)
    return () => {
      cancelAnimationFrame(raf)
      canvas.removeEventListener('keydown', onKeyDown)
      canvas.removeEventListener('keyup', onKeyUp)
      canvas.removeEventListener('blur', onBlur)
      canvas.removeEventListener('click', onClick)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      tabIndex={0}
      className="office-canvas"
      aria-label="Oficina de agentes. Flechas o WASD para moverte, Z o Enter para hablar con el agente de enfrente. La lista de abajo tiene la misma informacion."
    />
  )
}

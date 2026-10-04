import Phaser from 'phaser'
import { useEffect, useRef } from 'react'
import type { OfficeAgent } from './types'

// Placeholder pixel-art: simple drawn rectangles/labels via Phaser Graphics,
// no external image assets -- avoids any licensing question entirely while
// the real tileset/sprites (see diseno-oficina-agentes.md) don't exist yet.
// Documented explicitly as placeholder, not final art (see README.md).

const TILE = 96
const COLS = 4
const COLOR_WORKING = 0xf6b24b // warm amber -- "working"
const COLOR_IDLE = 0x8fa6b8 // neutral slate -- "idle"
const COLOR_SELECTED_RING = 0x2e2a4a

class OfficeSceneImpl extends Phaser.Scene {
  private agents: OfficeAgent[] = []
  private selectedId: string | null = null
  private deskRects = new Map<string, Phaser.GameObjects.Rectangle>()
  private onSelect: (agentId: string) => void = () => {}
  private ready = false

  constructor() {
    super('office')
  }

  setData2(agents: OfficeAgent[], onSelect: (agentId: string) => void) {
    this.agents = agents
    this.onSelect = onSelect
    if (this.ready) this.redraw()
  }

  setSelected(agentId: string | null) {
    this.selectedId = agentId
    if (this.ready) this.redraw()
  }

  create() {
    this.cameras.main.setBackgroundColor('#fbf3e3')
    this.ready = true
    this.redraw()
  }

  private redraw() {
    this.children.removeAll()
    this.deskRects.clear()

    this.agents.forEach((agent, i) => {
      const col = i % COLS
      const row = Math.floor(i / COLS)
      const x = 64 + col * (TILE + 24)
      const y = 64 + row * (TILE + 48)

      const color = agent.status === 'working' ? COLOR_WORKING : COLOR_IDLE
      const rect = this.add
        .rectangle(x, y, TILE, TILE, color)
        .setStrokeStyle(agent.agent_id === this.selectedId ? 4 : 1, COLOR_SELECTED_RING)
        .setInteractive({ useHandCursor: true })

      rect.on('pointerdown', () => this.onSelect(agent.agent_id))
      this.deskRects.set(agent.agent_id, rect)

      const initials = agent.display_name
        .split(' ')
        .map((p) => p[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
      this.add
        .text(x, y, initials, { fontSize: '28px', color: '#2e2a4a', fontStyle: 'bold' })
        .setOrigin(0.5)

      this.add
        .text(x, y + TILE / 2 + 14, agent.display_name.split(' ')[0], {
          fontSize: '13px',
          color: '#2e2a4a',
        })
        .setOrigin(0.5, 0)

      if (agent.status === 'working') {
        this.add
          .text(x + TILE / 2 - 8, y - TILE / 2 + 8, '●', { fontSize: '14px', color: '#b5490b' })
          .setOrigin(1, 0)
      }
    })
  }
}

interface Props {
  agents: OfficeAgent[]
  selectedId: string | null
  onSelect: (agentId: string) => void
}

export function OfficeScene({ agents, selectedId, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const gameRef = useRef<Phaser.Game | null>(null)
  const sceneRef = useRef<OfficeSceneImpl | null>(null)

  useEffect(() => {
    const scene = new OfficeSceneImpl()
    sceneRef.current = scene
    const game = new Phaser.Game({
      type: Phaser.AUTO,
      width: 4 * (TILE + 24) + 64,
      height: 2 * (TILE + 48) + 64,
      parent: containerRef.current ?? undefined,
      scene,
      render: { pixelArt: true },
    })
    gameRef.current = game
    return () => {
      game.destroy(true)
      gameRef.current = null
      sceneRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    sceneRef.current?.setData2(agents, onSelect)
  }, [agents, onSelect])

  useEffect(() => {
    sceneRef.current?.setSelected(selectedId)
  }, [selectedId])

  return <div ref={containerRef} aria-hidden="true" />
}

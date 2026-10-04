import type { OfficeSnapshot } from './types'

// Dev-only: the token comes from .env.local (gitignored), mirroring what the
// main console embeds server-side into its own index.html. This is NOT how
// a production build should get the token -- that's a known limitation,
// tracked rather than silently shipped (see office-frontend/README.md).
const CONSOLE_TOKEN = import.meta.env.VITE_CONSOLE_TOKEN as string | undefined

export class OfficeApiError extends Error {}

export async function fetchOfficeSnapshot(): Promise<OfficeSnapshot> {
  if (!CONSOLE_TOKEN) {
    throw new OfficeApiError(
      'VITE_CONSOLE_TOKEN is not set -- copy the real CONSOLE_TOKEN from ai-commerce-os/.env into office-frontend/.env.local'
    )
  }
  const response = await fetch('/api/office/agents', {
    headers: { 'X-Console-Token': CONSOLE_TOKEN },
  })
  if (!response.ok) {
    throw new OfficeApiError(`backend returned ${response.status}`)
  }
  return (await response.json()) as OfficeSnapshot
}

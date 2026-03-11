import type { VercelRequest, VercelResponse } from '@vercel/node'
import crypto from 'crypto'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') return res.status(405).end()

  const sig = req.headers['x-hub-signature-256'] as string
  const secret = process.env.GITHUB_WEBHOOK_SECRET
  if (secret && sig) {
    const hmac = crypto.createHmac('sha256', secret)
    hmac.update(JSON.stringify(req.body))
    const digest = `sha256=${hmac.digest('hex')}`
    if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(digest))) {
      return res.status(401).json({ error: 'Invalid signature' })
    }
  }

  const event = req.headers['x-github-event'] as string
  const payload = req.body

  // Broadcast to PartyKit if configured
  const partykitHost = process.env.VITE_PARTYKIT_HOST
  if (partykitHost) {
    const room = `pr-${payload.repository?.full_name}-${payload.pull_request?.number ?? payload.issue?.number ?? 'general'}`
    try {
      await fetch(`https://${partykitHost}/parties/main/${room}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'github_event', event, payload }),
      })
    } catch {}
  }

  res.status(200).json({ ok: true })
}

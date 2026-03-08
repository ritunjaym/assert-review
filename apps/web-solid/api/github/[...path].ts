import type { VercelRequest, VercelResponse } from '@vercel/node'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const cookie = req.cookies?.gh_session
  if (!cookie) return res.status(401).json({ error: 'Unauthorized' })

  const { accessToken } = JSON.parse(Buffer.from(cookie, 'base64').toString())
  const path = (req.query.path as string[]).join('/')
  const query = new URL(req.url!, 'http://localhost').search

  const ghRes = await fetch(`https://api.github.com/${path}${query}`, {
    method: req.method,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      Accept: 'application/vnd.github.v3+json',
      ...(req.body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(req.body ? { body: JSON.stringify(req.body) } : {}),
  })

  const rl = ghRes.headers.get('x-ratelimit-remaining')
  if (rl) res.setHeader('x-ratelimit-remaining', rl)
  const rll = ghRes.headers.get('x-ratelimit-limit')
  if (rll) res.setHeader('x-ratelimit-limit', rll)
  const rlr = ghRes.headers.get('x-ratelimit-reset')
  if (rlr) res.setHeader('x-ratelimit-reset', rlr)

  res.status(ghRes.status).json(await ghRes.json())
}

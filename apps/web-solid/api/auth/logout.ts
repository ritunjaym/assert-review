import type { VercelRequest, VercelResponse } from '@vercel/node'

export default function handler(req: VercelRequest, res: VercelResponse) {
  res.setHeader('Set-Cookie', 'gh_session=; Max-Age=0; Path=/')
  res.json({ ok: true })
}

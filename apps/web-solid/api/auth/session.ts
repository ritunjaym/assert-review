import type { VercelRequest, VercelResponse } from '@vercel/node'

export default function handler(req: VercelRequest, res: VercelResponse) {
  const cookie = req.cookies?.gh_session
  if (!cookie) return res.json(null)
  try {
    res.json(JSON.parse(Buffer.from(cookie, 'base64').toString()))
  } catch { res.json(null) }
}

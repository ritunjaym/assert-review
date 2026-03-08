import type { VercelRequest, VercelResponse } from '@vercel/node'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const code = req.query.code as string
  if (!code) return res.redirect('/login?error=no_code')

  const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({
      client_id: process.env.GITHUB_CLIENT_ID,
      client_secret: process.env.GITHUB_CLIENT_SECRET,
      code,
    }),
  })
  const { access_token } = await tokenRes.json() as { access_token: string }
  if (!access_token) return res.redirect('/login?error=no_token')

  const userRes = await fetch('https://api.github.com/user', {
    headers: { Authorization: `Bearer ${access_token}` }
  })
  const user = await userRes.json()

  const session = Buffer.from(JSON.stringify({ accessToken: access_token, user })).toString('base64')
  res.setHeader('Set-Cookie', `gh_session=${session}; HttpOnly; Secure; SameSite=Lax; Max-Age=${60 * 60 * 24 * 7}; Path=/`)
  res.redirect('/dashboard')
}

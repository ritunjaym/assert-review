import { NextRequest, NextResponse } from "next/server"

export async function GET(req: NextRequest) {
  const code = req.nextUrl.searchParams.get("code")
  if (!code) return NextResponse.redirect(new URL("/login", req.url))

  const tokenRes = await fetch(
    "https://github.com/login/oauth/access_token",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify({
        client_id: process.env.AUTH_GITHUB_ID,
        client_secret: process.env.AUTH_GITHUB_SECRET,
        code,
      }),
    }
  )
  const { access_token, error } = await tokenRes.json()
  if (error || !access_token) {
    return NextResponse.redirect(new URL("/login?error=oauth", req.url))
  }

  const userRes = await fetch("https://api.github.com/user", {
    headers: {
      Authorization: `Bearer ${access_token}`,
      Accept: "application/vnd.github+json",
    },
  })
  const user = await userRes.json()

  const session = Buffer.from(
    JSON.stringify({
      user: {
        login: user.login,
        name: user.name ?? user.login,
        avatar_url: user.avatar_url,
        email: user.email ?? "",
      },
      accessToken: access_token,
    })
  ).toString("base64")

  const res = NextResponse.redirect(new URL("/dashboard", req.url))
  res.cookies.set("gh_session", session, {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 60 * 24 * 7,
    path: "/",
  })
  return res
}

import { cookies } from "next/headers"

export interface SessionUser {
  login: string
  name: string
  avatar_url: string
  email: string
}

export interface Session {
  user: SessionUser
  accessToken: string
}

export async function getSession(): Promise<Session | null> {
  try {
    const cookieStore = await cookies()
    const raw = cookieStore.get("gh_session")?.value
    if (!raw) return null
    return JSON.parse(Buffer.from(raw, "base64").toString("utf-8"))
  } catch {
    return null
  }
}

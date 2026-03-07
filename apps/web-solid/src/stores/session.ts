import { createSignal } from 'solid-js'

export interface Session {
  accessToken: string
  user: { login: string; name: string; avatar_url: string }
}

const [session, setSession] = createSignal<Session | null>(null)
const [sessionLoaded, setSessionLoaded] = createSignal(false)

export async function loadSession() {
  try {
    const res = await fetch('/api/auth/session')
    const data = await res.json()
    setSession(data)
  } catch {}
  setSessionLoaded(true)
}

export async function logout() {
  await fetch('/api/auth/logout', { method: 'POST' })
  setSession(null)
}

export { session, sessionLoaded }

"use client"

import { useEffect, useState, useCallback, useRef } from "react"

export interface Presence {
  userId: string
  username: string
  avatarUrl: string
  currentFile: string | null
  color: string
  joinedAt: number
}

const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b", "#3b82f6", "#10b981", "#f97316"]

export function usePRRoom(
  prId: string,
  user: { name?: string | null; email?: string | null; image?: string | null } | undefined
) {
  const [presences, setPresences] = useState<Map<string, Presence>>(new Map())
  const wsRef = useRef<WebSocket | null>(null)
  const [connected, setConnected] = useState(false)

  const sendPresenceUpdate = useCallback((update: Partial<Presence>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "presence_update", ...update }))
    }
  }, [])

  const sendCommentAdded = useCallback((comment: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "comment_added", comment }))
    }
  }, [])

  useEffect(() => {
    if (!user?.name || !prId) return

    const host = process.env.NEXT_PUBLIC_PARTYKIT_HOST
    if (!host) return

    const roomId = `pr-${prId.replace(/[^a-z0-9-]/gi, "-")}`
    const ws = new WebSocket(`wss://${host}/parties/main/${roomId}`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      ws.send(JSON.stringify({
        type: "join",
        userId: user.email ?? user.name ?? "anonymous",
        username: user.name,
        avatarUrl: user.image ?? "",
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        currentFile: null,
        joinedAt: Date.now(),
      }))
    }

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data)
        if (msg.type === "presence_state") {
          setPresences(new Map(Object.entries(msg.presences)))
        } else if (msg.type === "presence_update") {
          setPresences(prev => {
            const next = new Map(prev)
            const existing = next.get(msg.connectionId) ?? {} as Presence
            next.set(msg.connectionId, { ...existing, ...msg })
            return next
          })
        } else if (msg.type === "presence_leave") {
          setPresences(prev => {
            const next = new Map(prev)
            next.delete(msg.connectionId)
            return next
          })
        }
      } catch { /* ignore parse errors */ }
    }

    ws.onclose = () => setConnected(false)

    return () => {
      ws.close()
      wsRef.current = null
    }
  }, [prId, user?.name, user?.email, user?.image])

  return { presences: Array.from(presences.values()), sendPresenceUpdate, sendCommentAdded, connected }
}

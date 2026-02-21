"use client"

import { Presence } from "@/hooks/use-pr-room"

interface PresenceBarProps {
  presences: Presence[]
}

export function PresenceBar({ presences }: PresenceBarProps) {
  if (presences.length === 0) return null

  const visible = presences.slice(0, 5)
  const overflow = presences.length - 5

  return (
    <div className="flex items-center gap-1" aria-label="Active reviewers">
      {visible.map((p, i) => {
        const isRecent = Date.now() - p.joinedAt < 30000
        return (
          <div key={p.userId} className="relative group/presence" title={`${p.username} — ${p.currentFile ?? "Idle"}`}>
            <img
              src={p.avatarUrl || `https://ui-avatars.com/api/?name=${p.username}&background=${p.color.slice(1)}`}
              alt={`${p.username}'s avatar`}
              width={28}
              height={28}
              className="rounded-full border-2"
              style={{ borderColor: p.color }}
            />
            {isRecent && (
              <span
                className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-500 rounded-full border border-background"
                aria-label="Recently active"
              />
            )}
            <div className="absolute top-8 left-0 z-50 hidden group-hover/presence:block whitespace-nowrap bg-popover border border-border rounded px-2 py-1 text-xs shadow-md">
              <span className="font-medium">{p.username}</span>
              {p.currentFile && <span className="text-muted-foreground ml-1">Viewing: {p.currentFile.split("/").pop()}</span>}
            </div>
          </div>
        )
      })}
      {overflow > 0 && (
        <span className="text-xs text-muted-foreground px-1">+{overflow}</span>
      )}
    </div>
  )
}

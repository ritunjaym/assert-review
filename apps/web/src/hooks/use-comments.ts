"use client"

import { useState, useCallback } from "react"

export interface LineComment {
  id: string
  pr_id: string
  filename: string
  line_number: number
  side: 'left' | 'right'
  author: string
  author_avatar: string
  body: string
  created_at: string
  updated_at: string
  resolved: boolean
}

// In-memory store for demo (localStorage persistence)
const STORAGE_KEY = (prId: string, filename: string) => `ar:comments:${prId}:${filename}`

function loadComments(prId: string, filename: string): LineComment[] {
  if (typeof window === "undefined") return []
  try {
    const raw = localStorage.getItem(STORAGE_KEY(prId, filename))
    return raw ? JSON.parse(raw) : []
  } catch { return [] }
}

function saveComments(prId: string, filename: string, comments: LineComment[]): void {
  if (typeof window === "undefined") return
  localStorage.setItem(STORAGE_KEY(prId, filename), JSON.stringify(comments))
}

export function useComments(prId: string, filename: string) {
  const [comments, setComments] = useState<LineComment[]>(() => loadComments(prId, filename))

  const addComment = useCallback((
    lineNumber: number,
    body: string,
    author: string,
    authorAvatar: string,
  ) => {
    const comment: LineComment = {
      id: crypto.randomUUID(),
      pr_id: prId,
      filename,
      line_number: lineNumber,
      side: "right",
      author,
      author_avatar: authorAvatar,
      body,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      resolved: false,
    }
    setComments(prev => {
      const next = [...prev, comment]
      saveComments(prId, filename, next)
      return next
    })
    return comment
  }, [prId, filename])

  const resolveComment = useCallback((id: string) => {
    setComments(prev => {
      const next = prev.map(c => c.id === id ? { ...c, resolved: true } : c)
      saveComments(prId, filename, next)
      return next
    })
  }, [prId, filename])

  const deleteComment = useCallback((id: string) => {
    setComments(prev => {
      const next = prev.filter(c => c.id !== id)
      saveComments(prId, filename, next)
      return next
    })
  }, [prId, filename])

  return { comments, addComment, resolveComment, deleteComment }
}

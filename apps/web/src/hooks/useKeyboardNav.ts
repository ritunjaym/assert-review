"use client"

import { useRef, useEffect, useState } from "react"
import { useRouter } from "next/navigation"

export function useKeyboardNav(
  files: string[],
  onSelectFile: (f: string) => void,
  onOpenComment: () => void
) {
  const router = useRouter()
  const [focusedIndex, setFocusedIndex] = useState(0)

  // Refs to avoid stale closures — updated every render
  const filesRef = useRef(files)
  const focusedIndexRef = useRef(0)
  const onSelectFileRef = useRef(onSelectFile)
  const onOpenCommentRef = useRef(onOpenComment)
  const routerRef = useRef(router)
  const pendingKeyRef = useRef<string | null>(null)
  const pendingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  filesRef.current = files
  onSelectFileRef.current = onSelectFile
  onOpenCommentRef.current = onOpenComment
  routerRef.current = router

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement
      const tag = target?.tagName?.toLowerCase()
      if (tag === "input" || tag === "textarea" || target?.getAttribute("contenteditable") === "true") return

      const { key, ctrlKey, metaKey, shiftKey } = e

      if (key === "j" && !ctrlKey && !metaKey && !shiftKey) {
        e.preventDefault()
        const next = Math.min(filesRef.current.length - 1, focusedIndexRef.current + 1)
        focusedIndexRef.current = next
        setFocusedIndex(next)
        const file = filesRef.current[next]
        if (file) onSelectFileRef.current(file)
        pendingKeyRef.current = null
      } else if (key === "k" && !ctrlKey && !metaKey && !shiftKey) {
        e.preventDefault()
        const prev = Math.max(0, focusedIndexRef.current - 1)
        focusedIndexRef.current = prev
        setFocusedIndex(prev)
        const file = filesRef.current[prev]
        if (file) onSelectFileRef.current(file)
        pendingKeyRef.current = null
      } else if (key === "c" && !ctrlKey && !metaKey && !shiftKey) {
        e.preventDefault()
        onOpenCommentRef.current()
        pendingKeyRef.current = null
      } else if (key === "g" && !ctrlKey && !metaKey && !shiftKey) {
        if (pendingTimerRef.current) clearTimeout(pendingTimerRef.current)
        pendingKeyRef.current = "g"
        pendingTimerRef.current = setTimeout(() => { pendingKeyRef.current = null }, 1000)
      } else if (key === "d" && !ctrlKey && !metaKey && !shiftKey) {
        if (pendingKeyRef.current === "g") {
          e.preventDefault()
          if (pendingTimerRef.current) clearTimeout(pendingTimerRef.current)
          pendingKeyRef.current = null
          routerRef.current.push("/dashboard")
        } else {
          pendingKeyRef.current = null
        }
      } else if (key !== "g") {
        pendingKeyRef.current = null
        if (pendingTimerRef.current) clearTimeout(pendingTimerRef.current)
      }
    }

    window.addEventListener("keydown", handler)
    return () => {
      window.removeEventListener("keydown", handler)
      if (pendingTimerRef.current) clearTimeout(pendingTimerRef.current)
    }
  }, []) // stable — all state accessed via refs

  return {
    focusedIndex,
    focusedFile: files[focusedIndex] ?? null,
  }
}

"use client"

import { useState } from "react"
import { LineComment } from "@/hooks/use-comments"
import { formatDistanceToNow } from "date-fns"

interface CommentThreadProps {
  lineNumber: number
  comments: LineComment[]
  onAddComment: (lineNumber: number, body: string) => void
  onResolve: (id: string) => void
  onDelete: (id: string) => void
  currentUser?: { name: string; image?: string }
}

function CommentItem({
  comment,
  onResolve,
  onDelete,
  isOwn,
}: {
  comment: LineComment
  onResolve: () => void
  onDelete: () => void
  isOwn: boolean
}) {
  const time = formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })

  return (
    <div className={`py-2 ${comment.resolved ? "opacity-50" : ""}`}>
      <div className="flex items-center gap-2 mb-1">
        <img
          src={comment.author_avatar || `https://ui-avatars.com/api/?name=${comment.author}`}
          alt={`${comment.author}'s avatar`}
          width={20}
          height={20}
          className="rounded-full"
        />
        <span className="text-xs font-medium">{comment.author}</span>
        <span className="text-xs text-muted-foreground">{time}</span>
        {comment.resolved && <span className="text-xs text-muted-foreground italic">resolved</span>}
      </div>
      <p className="text-xs pl-6 text-foreground/90 whitespace-pre-wrap">{comment.body}</p>
      {isOwn && !comment.resolved && (
        <div className="flex gap-2 pl-6 mt-1">
          <button
            onClick={onResolve}
            className="text-[10px] text-muted-foreground hover:text-foreground"
            aria-label="Resolve comment"
          >
            Resolve
          </button>
          <button
            onClick={onDelete}
            className="text-[10px] text-destructive hover:opacity-80"
            aria-label="Delete comment"
          >
            Delete
          </button>
        </div>
      )}
    </div>
  )
}

export function CommentThread({
  lineNumber,
  comments,
  onAddComment,
  onResolve,
  onDelete,
  currentUser,
}: CommentThreadProps) {
  const [body, setBody] = useState("")
  const [isOpen, setIsOpen] = useState(comments.length > 0)

  const lineComments = comments.filter(c => c.line_number === lineNumber)

  const handleSubmit = () => {
    if (!body.trim()) return
    onAddComment(lineNumber, body.trim())
    setBody("")
  }

  if (!isOpen && lineComments.length === 0) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="opacity-0 hover:opacity-100 focus:opacity-100 text-[10px] text-muted-foreground px-1 py-0.5 rounded hover:bg-muted transition-all"
        aria-label={`Add comment on line ${lineNumber}`}
      >
        +
      </button>
    )
  }

  return (
    <div className="border border-border rounded-lg p-3 my-1 bg-card text-xs">
      {lineComments.map(c => (
        <CommentItem
          key={c.id}
          comment={c}
          onResolve={() => onResolve(c.id)}
          onDelete={() => onDelete(c.id)}
          isOwn={currentUser?.name === c.author}
        />
      ))}
      
      {isOpen && (
        <div className="mt-2" role="form" aria-label="Add comment">
          <label htmlFor={`comment-input-${lineNumber}`} className="sr-only">
            Add a comment on line {lineNumber}
          </label>
          <textarea
            id={`comment-input-${lineNumber}`}
            value={body}
            onChange={e => setBody(e.target.value)}
            placeholder="Add a comment... (supports Markdown)"
            className="w-full text-xs p-2 border border-border rounded bg-background resize-none focus:outline-none focus:ring-1 focus:ring-primary"
            rows={3}
            aria-label={`Comment on line ${lineNumber}`}
          />
          <div className="flex gap-2 mt-1">
            <button
              onClick={handleSubmit}
              disabled={!body.trim()}
              className="text-xs px-3 py-1 bg-primary text-primary-foreground rounded disabled:opacity-50"
              aria-label="Submit comment"
            >
              Comment
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="text-xs px-3 py-1 hover:bg-muted rounded"
            >
              Cancel
            </button>
          </div>
        </div>
      )}
      
      {!isOpen && lineComments.length > 0 && (
        <button
          onClick={() => setIsOpen(true)}
          className="text-xs text-primary mt-1 hover:underline"
        >
          Add reply
        </button>
      )}
    </div>
  )
}

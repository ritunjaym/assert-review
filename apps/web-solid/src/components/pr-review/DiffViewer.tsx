import { createSignal, For, Show, createMemo } from 'solid-js'
import type { PRFile } from '@/lib/github'
import type { RankedFile } from '@/lib/ml'
import { ScoreBadge } from '@/components/ScoreBadge'

interface DiffLine {
  type: 'add' | 'remove' | 'context' | 'hunk'
  content: string
  oldLine: number | null
  newLine: number | null
}

function parsePatch(patch: string): DiffLine[] {
  const lines = patch.split('\n')
  const result: DiffLine[] = []
  let oldLine = 0, newLine = 0

  for (const line of lines) {
    if (line.startsWith('@@')) {
      const match = line.match(/@@ -(\d+)(?:,\d+)? \+(\d+)/)
      if (match) { oldLine = parseInt(match[1]); newLine = parseInt(match[2]) }
      result.push({ type: 'hunk', content: line, oldLine: null, newLine: null })
    } else if (line.startsWith('+')) {
      result.push({ type: 'add', content: line.slice(1), oldLine: null, newLine: newLine++ })
    } else if (line.startsWith('-')) {
      result.push({ type: 'remove', content: line.slice(1), oldLine: oldLine++, newLine: null })
    } else {
      result.push({ type: 'context', content: line.slice(1), oldLine: oldLine++, newLine: newLine++ })
    }
  }
  return result
}

interface Props {
  file: PRFile | null
  rank: RankedFile | null
  prId: string
  owner: string
  repo: string
  commentOpen: boolean
  onCommentClose: () => void
}

export function DiffViewer(props: Props) {
  const [activeCommentLine, setActiveCommentLine] = createSignal<number | null>(null)
  const [commentText, setCommentText] = createSignal('')
  const [comments, setComments] = createSignal<Array<{ line: number; body: string; author: string }>>([])
  const [failedLines, setFailedLines] = createSignal(new Set<number>())

  const lines = createMemo(() => {
    if (!props.file?.patch) return []
    return parsePatch(props.file.patch)
  })

  async function submitComment(line: number) {
    const body = commentText()
    if (!body.trim()) return

    setComments(prev => [...prev, { line, body, author: 'you' }])
    setCommentText('')
    setActiveCommentLine(null)

    let attempts = 0
    const delays = [1000, 2000, 4000]
    while (attempts < 3) {
      try {
        const res = await fetch('/api/github/comment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            owner: props.owner, repo: props.repo,
            pr_number: props.prId, body, path: props.file?.filename, line,
          }),
        })
        if (res.ok) return
      } catch {}
      attempts++
      if (attempts < 3) await new Promise(r => setTimeout(r, delays[attempts - 1]))
    }
    setFailedLines(prev => new Set([...prev, line]))
  }

  return (
    <Show when={props.file} fallback={
      <div class="flex items-center justify-center h-full text-slate-600">
        <div class="text-center">
          <p class="text-4xl mb-3">📂</p>
          <p>Select a file to view its diff</p>
        </div>
      </div>
    }>
      <div class="h-full overflow-auto">
        {/* File header */}
        <div class="sticky top-0 z-10 bg-slate-900 border-b border-slate-700 px-4 py-2 flex items-center gap-2">
          <span class="text-sm text-slate-200 font-mono">{props.file?.filename}</span>
          <Show when={props.rank}>
            <ScoreBadge label={props.rank!.label} />
          </Show>
          <span class="ml-auto text-xs text-slate-500">
            <span class="text-green-600">+{props.file?.additions}</span>
            {' '}
            <span class="text-red-500">-{props.file?.deletions}</span>
          </span>
        </div>

        {/* Diff table */}
        <Show when={props.file?.patch} fallback={
          <div class="p-4 text-slate-500 text-sm italic">
            {props.file?.status === 'binary' ? 'Binary file' : 'No diff available'}
          </div>
        }>
          <table class="w-full text-xs font-mono border-collapse">
            <tbody>
              <For each={lines()}>
                {(line, i) => (
                  <>
                    <tr
                      class={`group cursor-pointer
                        ${line.type === 'add' ? 'bg-green-950/30 hover:bg-green-950/50' :
                          line.type === 'remove' ? 'bg-red-950/30 hover:bg-red-950/50' :
                          line.type === 'hunk' ? 'bg-slate-800/50' :
                          'hover:bg-slate-800/30'}
                      `}
                      onClick={() => line.type !== 'hunk' && setActiveCommentLine(
                        activeCommentLine() === i() ? null : i()
                      )}
                    >
                      <td class="w-10 px-2 py-0.5 text-slate-600 select-none text-right border-r border-slate-800">
                        {line.oldLine ?? ''}
                      </td>
                      <td class="w-10 px-2 py-0.5 text-slate-600 select-none text-right border-r border-slate-800">
                        {line.newLine ?? ''}
                      </td>
                      <td class={`px-3 py-0.5 whitespace-pre-wrap
                        ${line.type === 'add' ? 'text-green-300' :
                          line.type === 'remove' ? 'text-red-400' :
                          line.type === 'hunk' ? 'text-blue-400' :
                          'text-slate-300'}
                      `}>
                        {line.type === 'add' ? '+' : line.type === 'remove' ? '-' : ' '}
                        {line.content}
                      </td>
                      <td class="w-6 px-1 opacity-0 group-hover:opacity-100">
                        <span class="text-slate-500 text-xs">💬</span>
                      </td>
                    </tr>

                    {/* Inline comments */}
                    <For each={comments().filter(c => c.line === i())}>
                      {comment => (
                        <tr>
                          <td colspan={4} class="px-4 py-2 bg-blue-950/30 border-l-2 border-blue-500">
                            <div class="flex items-start gap-2">
                              <span class="text-blue-400 text-xs font-medium">{comment.author}</span>
                              <span class="text-slate-300 text-xs">{comment.body}</span>
                              <Show when={failedLines().has(comment.line)}>
                                <span class="text-red-400 text-xs ml-auto">
                                  Failed to post ·{' '}
                                  <button
                                    class="underline"
                                    onClick={() => submitComment(comment.line)}
                                  >Retry</button>
                                </span>
                              </Show>
                            </div>
                          </td>
                        </tr>
                      )}
                    </For>

                    {/* Comment input */}
                    <Show when={activeCommentLine() === i()}>
                      <tr>
                        <td colspan={4} class="px-4 py-3 bg-slate-800/50">
                          <textarea
                            class="w-full bg-slate-900 text-slate-200 text-xs p-2 rounded border border-slate-600 resize-none focus:outline-none focus:ring-1 focus:ring-blue-500"
                            rows={3}
                            placeholder="Add a review comment..."
                            value={commentText()}
                            onInput={e => setCommentText(e.currentTarget.value)}
                            autofocus
                          />
                          <div class="flex gap-2 mt-2">
                            <button
                              class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded transition-colors"
                              onClick={() => submitComment(i())}
                            >Comment</button>
                            <button
                              class="text-xs text-slate-400 hover:text-white px-3 py-1 rounded transition-colors"
                              onClick={() => setActiveCommentLine(null)}
                            >Cancel</button>
                          </div>
                        </td>
                      </tr>
                    </Show>
                  </>
                )}
              </For>
            </tbody>
          </table>
        </Show>
      </div>
    </Show>
  )
}

import { createEffect } from 'solid-js'
import { useNavigate } from '@tanstack/solid-router'
import { session } from '@/stores/session'

export function LoginPage() {
  const navigate = useNavigate()
  createEffect(() => { if (session()) navigate({ to: '/dashboard' }) })

  return (
    <div class="flex items-center justify-center min-h-screen bg-slate-950">
      <div class="text-center space-y-6">
        <h1 class="text-4xl font-bold text-white">CodeLens</h1>
        <p class="text-slate-400">AI-powered code review</p>
        <a href="/api/auth/github"
          class="inline-flex items-center gap-3 bg-white text-slate-900 px-6 py-3 rounded-lg font-semibold hover:bg-slate-100 transition-colors">
          Sign in with GitHub
        </a>
      </div>
    </div>
  )
}

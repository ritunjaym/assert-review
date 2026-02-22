import { signIn } from "@/auth"

export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md px-4">
        <h1 className="text-4xl font-bold tracking-tight">Assert Review</h1>
        <p className="text-muted-foreground text-lg">
          AI-powered code review — ML-ranked diffs, semantic grouping, real-time collaboration.
        </p>
        <form
          action={async () => {
            "use server"
            await signIn("github", { redirectTo: "/dashboard" })
          }}
        >
          <button
            type="submit"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity"
          >
            Sign in with GitHub
          </button>
        </form>
        <p className="text-xs text-muted-foreground">
          Free to use. No data stored beyond your session.
        </p>
      </div>
    </main>
  )
}

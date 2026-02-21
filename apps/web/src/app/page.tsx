import { auth } from "@/auth"
import { redirect } from "next/navigation"
import Link from "next/link"

export default async function Home() {
  const session = await auth()
  
  if (session) {
    redirect("/dashboard")
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6 max-w-md px-4">
        <h1 className="text-4xl font-bold tracking-tight">Assert Review</h1>
        <p className="text-muted-foreground text-lg">
          AI-powered code review — ML-ranked diffs, semantic grouping, real-time collaboration.
        </p>
        <Link
          href="/api/auth/signin"
          className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:opacity-90 transition-opacity"
        >
          Sign in with GitHub
        </Link>
        <p className="text-xs text-muted-foreground">
          Free to use. No data stored beyond your session.
        </p>
      </div>
    </main>
  )
}

import { auth } from "@/auth"
import { redirect } from "next/navigation"

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await auth()
  
  if (!session) {
    redirect("/api/auth/signin")
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border px-6 py-3 flex items-center justify-between">
        <a href="/dashboard" className="font-semibold text-lg">Assert Review</a>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">{session.user?.name}</span>
          <a href="/api/auth/signout" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Sign out
          </a>
        </div>
      </header>
      <main id="main-content">{children}</main>
    </div>
  )
}

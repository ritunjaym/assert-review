import { auth } from "@/auth"

interface PageProps {
  params: Promise<{ owner: string; repo: string; number: string }>
}

export default async function PRDetailPage({ params }: PageProps) {
  const { owner, repo, number } = await params
  const session = await auth()

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-6">
        <p className="text-sm text-muted-foreground">{owner}/{repo}</p>
        <h1 className="text-2xl font-bold mt-1">PR #{number}</h1>
      </div>
      <div className="border border-border rounded-lg p-8 text-center text-muted-foreground">
        <p>Diff viewer coming in Phase 8</p>
      </div>
    </div>
  )
}

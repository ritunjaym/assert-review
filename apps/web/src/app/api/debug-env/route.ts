export const dynamic = "force-dynamic"
export async function GET() {
  return Response.json({
    AUTH_GITHUB_ID: process.env.AUTH_GITHUB_ID ?? "MISSING",
    AUTH_GITHUB_ID_len: (process.env.AUTH_GITHUB_ID ?? "").length,
    AUTH_GITHUB_SECRET_len: (process.env.AUTH_GITHUB_SECRET ?? "").length,
    AUTH_SECRET_len: (process.env.AUTH_SECRET ?? "").length,
  })
}

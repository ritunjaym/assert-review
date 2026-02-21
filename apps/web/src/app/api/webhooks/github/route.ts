import { NextRequest, NextResponse } from "next/server"
import crypto from "crypto"

export async function POST(req: NextRequest) {
  const payload = await req.text()
  const signature = req.headers.get("x-hub-signature-256") ?? ""
  const secret = process.env.GITHUB_WEBHOOK_SECRET ?? ""

  if (secret) {
    const hmac = crypto.createHmac("sha256", secret)
    hmac.update(payload)
    const expected = `sha256=${hmac.digest("hex")}`
    
    if (!crypto.timingSafeEqual(Buffer.from(expected), Buffer.from(signature.padEnd(expected.length, " ")))) {
      return NextResponse.json({ error: "Invalid signature" }, { status: 403 })
    }
  }

  const event = req.headers.get("x-github-event") ?? ""
  const body = JSON.parse(payload)

  if (event === "ping") {
    return NextResponse.json({ ok: true })
  }

  // Forward to ML API
  const mlApiUrl = process.env.ML_API_URL ?? "http://localhost:8000"
  try {
    await fetch(`${mlApiUrl}/webhooks/github`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-GitHub-Event": event,
        "X-Hub-Signature-256": signature,
      },
      body: payload,
    })
  } catch {
    // ML API may be down — don't fail the webhook
  }

  return NextResponse.json({ received: true })
}

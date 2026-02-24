import { NextRequest, NextResponse } from "next/server"

export function middleware(req: NextRequest) {
  const session = req.cookies.get("gh_session")
  const isProtected =
    req.nextUrl.pathname.startsWith("/dashboard") ||
    req.nextUrl.pathname.startsWith("/pr")
  if (isProtected && !session) {
    return NextResponse.redirect(new URL("/login", req.url))
  }
}

export const config = {
  matcher: ["/dashboard/:path*", "/pr/:path*"],
}

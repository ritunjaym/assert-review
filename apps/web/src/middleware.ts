import { NextRequest, NextResponse } from "next/server"

export function middleware(req: NextRequest) {
  const session = req.cookies.get("authjs.session-token") ??
                  req.cookies.get("__Secure-authjs.session-token")
  const isAppRoute = req.nextUrl.pathname.startsWith("/dashboard") ||
                     req.nextUrl.pathname.startsWith("/pr")
  if (isAppRoute && !session) {
    return NextResponse.redirect(new URL("/login", req.url))
  }
}

export const config = {
  matcher: ["/dashboard/:path*", "/pr/:path*"],
}

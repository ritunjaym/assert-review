import type { NextAuthConfig } from "next-auth"
import GitHub from "next-auth/providers/github"

export const authConfig = {
  providers: [GitHub],
  pages: {
    signIn: "/login",
  },
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user
      const isAppRoute =
        nextUrl.pathname.startsWith("/dashboard") ||
        nextUrl.pathname.startsWith("/pr")
      if (isAppRoute) return isLoggedIn
      return true
    },
  },
} satisfies NextAuthConfig

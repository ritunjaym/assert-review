import type { Metadata } from "next";
import { SessionProvider } from "next-auth/react"
import "./globals.css";

export const metadata: Metadata = {
  title: "Assert Review",
  description: "AI-powered code review interface",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <SessionProvider>
          {children}
        </SessionProvider>
      </body>
    </html>
  );
}

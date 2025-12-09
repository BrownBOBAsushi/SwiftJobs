/**
 * Root layout component for the Next.js 14 App Router.
 * 
 * Responsibilities:
 * - Provides global layout structure for all pages
 * - Sets up providers (Supabase, Pusher, etc.)
 * - Configures global styles and metadata
 * 
 * Required imports:
 * - React
 * - Next.js Metadata API
 * - Supabase client providers
 * - Tailwind CSS styles
 * - Global font providers (if using custom fonts)
 */

import './globals.css'

export const metadata = {
  title: 'SwiftJobs - Tinder for Jobs',
  description: 'AI-powered job matching platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}


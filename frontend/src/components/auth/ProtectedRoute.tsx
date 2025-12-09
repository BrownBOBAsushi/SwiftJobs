/**
 * Protected route wrapper component.
 * 
 * Responsibilities:
 * - Check authentication status
 * - Redirect to login if not authenticated
 * - Verify user role matches route requirements
 * - Load user profile data
 * 
 * Required imports:
 * - React
 * - Next.js navigation (useRouter, redirect)
 * - Supabase client (server-side)
 * - User context/provider
 */

export default function ProtectedRoute({
  children,
  requiredRole,
}: {
  children: React.ReactNode
  requiredRole?: 'applicant' | 'hr'
}) {
  return <>{children}</>
}


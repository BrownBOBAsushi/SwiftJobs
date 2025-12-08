import AuthForm from "@/components/auth/AuthForm"

export default function SignupPage() {
  return (
    <div className="flex h-screen items-center justify-center bg-gray-50">
      <AuthForm view="signup" />
    </div>
  )
}
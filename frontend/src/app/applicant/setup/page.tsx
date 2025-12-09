"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { createClient } from "@/lib/supabase/client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"

export default function SetupProfile() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [userId, setUserId] = useState<string | null>(null)
  const router = useRouter()
  const supabase = createClient()
  const { toast } = useToast()

  // Get current user ID on load
  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser()
      if (user) setUserId(user.id)
      else router.push("/login")
    }
    getUser()
  }, [])

  const handleUpload = async () => {
    if (!file || !userId) return

    setLoading(true)
    const formData = new FormData()
    formData.append("file", file)
    formData.append("userId", userId)

    try {
      const res = await fetch("/api/resume/parse", {
        method: "POST",
        body: formData,
      })

      if (!res.ok) throw new Error("Failed to parse resume")

      toast({
        title: "Profile Built!",
        description: "AI has analyzed your resume. Redirecting...",
      })

      // Redirect to the dashboard/swipe page
      router.push("/applicant/swipe")
      
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Could not process resume. Try a different PDF.",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Upload Your Resume</CardTitle>
          <CardDescription>
            Our AI will analyze your skills and match you with the best jobs automatically.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="resume">Resume (PDF only)</Label>
            <Input 
              id="resume" 
              type="file" 
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>
          
          <Button 
            className="w-full" 
            onClick={handleUpload} 
            disabled={!file || loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing with AI...
              </>
            ) : (
              "Build My Profile"
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
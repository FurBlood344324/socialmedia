"use client"

import { useEffect } from "react"
import { useSearchParams } from "next/navigation"
import { Hero } from "@/components/layout/hero"
import { Footer } from "@/components/layout/footer"
import { useToast } from "@/hooks/use-toast"

export default function Home() {
  const searchParams = useSearchParams()
  const { toast } = useToast()

  useEffect(() => {
    const success = searchParams.get("success")
    if (success === "login") {
      toast({
        title: "Welcome back!",
        description: "You have successfully logged in.",
      })
    } else if (success === "register") {
      toast({
        title: "Welcome to SocialHub!",
        description: "Your account has been created successfully.",
      })
    }
  }, [searchParams, toast])

  return (
    <main className="flex min-h-screen flex-col">
      <Hero />
      <Footer />
    </main>
  )
}

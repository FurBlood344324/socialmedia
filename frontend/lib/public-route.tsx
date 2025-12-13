"use client"

import type React from "react"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "./auth-context"

// HOC for public-only routes (login, register)
// If user is authenticated, redirect to home/dashboard
export function withPublicAuth<P extends object>(Component: React.ComponentType<P>) {
  return function PublicRoute(props: P) {
    const { user, isLoading } = useAuth()
    const router = useRouter()

    useEffect(() => {
      if (!isLoading && user) {
        router.push("/")
      }
    }, [user, isLoading, router])

    if (isLoading) {
      return (
        <div className="flex min-h-screen items-center justify-center">
          <div className="border-primary h-12 w-12 animate-spin rounded-full border-b-2"></div>
        </div>
      )
    }

    if (user) {
      return null
    }

    return <Component {...props} />
  }
}

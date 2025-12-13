"use client"

import { useState } from "react"
import Link from "next/link"
import { Menu, User, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useAuth } from "@/lib/auth-context"

export function Navbar() {
  const { user, logout } = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="bg-background/80 border-border sticky top-0 z-50 border-b backdrop-blur-lg">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500">
              <span className="text-lg font-bold text-white">S</span>
            </div>
            <span className="bg-gradient-to-r from-blue-500 to-cyan-500 bg-clip-text text-xl font-bold text-transparent">
              SocialHub
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden items-center gap-4 md:flex">
            {user ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-muted-foreground hover:text-foreground text-sm font-medium transition-colors"
                >
                  Dashboard
                </Link>
                <Link
                  href={`/profile/${user?.username}`}
                  className="bg-muted hover:bg-muted/80 flex items-center gap-2 rounded-lg px-3 py-2 transition-colors"
                >
                  <User className="h-4 w-4" />
                  <span className="text-sm font-medium">{user?.username}</span>
                </Link>
                <Button onClick={logout} variant="outline" size="sm">
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button asChild variant="ghost" size="sm">
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild size="sm">
                  <Link href="/register">Sign Up</Link>
                </Button>
              </>
            )}
          </div>

          {/* Mobile menu button */}
          <button className="p-2 md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Navigation */}
      {mobileMenuOpen && (
        <div className="border-border bg-background border-t md:hidden">
          <div className="space-y-3 px-4 py-4">
            {user ? (
              <>
                <Link
                  href="/dashboard"
                  className="text-foreground hover:bg-muted block rounded-lg px-3 py-2 text-sm font-medium transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link
                  href={`/profile/${user?.username}`}
                  className="bg-muted hover:bg-muted/80 flex items-center gap-2 rounded-lg px-3 py-2 transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <User className="h-4 w-4" />
                  <span className="text-sm font-medium">{user?.username}</span>
                </Link>
                <Button
                  onClick={() => {
                    logout()
                    setMobileMenuOpen(false)
                  }}
                  variant="outline"
                  className="w-full"
                >
                  Logout
                </Button>
              </>
            ) : (
              <>
                <Button
                  asChild
                  variant="ghost"
                  className="w-full"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <Link href="/login">Sign In</Link>
                </Button>
                <Button asChild className="w-full" onClick={() => setMobileMenuOpen(false)}>
                  <Link href="/register">Sign Up</Link>
                </Button>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}

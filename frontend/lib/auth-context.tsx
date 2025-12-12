"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import type { User, RegisterData } from "./types"
import { api } from "./api"

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("token")
    }
    return null
  })
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Verify token and load user if token exists
    if (token) {
      api
        .getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("token")
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      // Use setTimeout to avoid synchronous setState in effect
      setTimeout(() => setIsLoading(false), 0)
    }
  }, [token])

  const login = async (username: string, password: string) => {
    const response = await api.login(username, password)
    localStorage.setItem("token", response.token)
    setToken(response.token)
    setUser(response.user)
  }

  const register = async (data: RegisterData) => {
    const response = await api.register(data)
    localStorage.setItem("token", response.token)
    setToken(response.token)
    setUser(response.user)
  }

  const logout = () => {
    localStorage.removeItem("token")
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { api } from "./api"
import type { RegisterData, User } from "./types"

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (data: RegisterData) => Promise<void>
  logout: () => void
  refreshUser: () => Promise<void>
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token on mount
    const storedToken = typeof window !== "undefined" ? localStorage.getItem("token") : null

    if (storedToken) {
      // eslint-disable-next-line
      setToken(storedToken)
      // Verify token and load user
      api
        .getCurrentUser()
        .then(setUser)
        .catch(() => {
          localStorage.removeItem("token")
          setToken(null)
        })
        .finally(() => setIsLoading(false))
    } else {
      setIsLoading(false)
    }
  }, [])

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

  const refreshUser = async () => {
    const updatedUser = await api.getCurrentUser()
    setUser(updatedUser)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, refreshUser, isLoading }}>
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

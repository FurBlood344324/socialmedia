"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Eye, EyeOff, Loader2, Lock } from "lucide-react"
import Link from "next/link"

export function RegisterForm() {
  const router = useRouter()
  const { register } = useAuth()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    bio: "",
    profile_picture_url: "",
    is_private: false,
  })

  const getPasswordStrength = (password: string) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^a-zA-Z0-9]/.test(password)) strength++
    return strength
  }

  const passwordStrength = getPasswordStrength(formData.password)
  const strengthColors = [
    "bg-destructive",
    "bg-orange-500",
    "bg-yellow-500",
    "bg-blue-500",
    "bg-green-500",
  ]
  const strengthLabels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]

  const validateForm = () => {
    if (formData.username.length < 3) {
      return "Username must be at least 3 characters long"
    }
    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      return "Please enter a valid email address"
    }
    if (formData.password.length < 8) {
      return "Password must be at least 8 characters long"
    }
    if (formData.password !== formData.confirmPassword) {
      return "Passwords do not match"
    }
    if (formData.bio.length > 500) {
      return "Bio must be less than 500 characters"
    }
    return null
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")

    const validationError = validateForm()
    if (validationError) {
      setError(validationError)
      return
    }

    setIsLoading(true)

    try {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { confirmPassword, ...registerData } = formData
      await register(registerData)
      router.push("/?success=register")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Registration failed. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-destructive/10 border-destructive/20 text-destructive rounded-lg border p-3 text-sm">
          {error}
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="username">Username *</Label>
        <Input
          id="username"
          type="text"
          placeholder="Choose a username"
          value={formData.username}
          onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          required
          disabled={isLoading}
          minLength={3}
        />
        <p className="text-muted-foreground text-xs">Minimum 3 characters</p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="email">Email *</Label>
        <Input
          id="email"
          type="email"
          placeholder="your.email@example.com"
          value={formData.email}
          onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          required
          disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="password">Password *</Label>
        <div className="relative">
          <Input
            id="password"
            type={showPassword ? "text" : "password"}
            placeholder="Create a strong password"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
            disabled={isLoading}
            minLength={8}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="text-muted-foreground hover:text-foreground absolute top-1/2 right-3 -translate-y-1/2"
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
        {formData.password && (
          <div className="space-y-1">
            <div className="flex gap-1">
              {[...Array(4)].map((_, i) => (
                <div
                  key={i}
                  className={`h-1 flex-1 rounded-full transition-colors ${
                    i < passwordStrength ? strengthColors[passwordStrength] : "bg-muted"
                  }`}
                />
              ))}
            </div>
            <p className="text-muted-foreground text-xs">
              Strength: {strengthLabels[passwordStrength]}
            </p>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <Label htmlFor="confirmPassword">Confirm Password *</Label>
        <div className="relative">
          <Input
            id="confirmPassword"
            type={showConfirmPassword ? "text" : "password"}
            placeholder="Re-enter your password"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
            required
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowConfirmPassword(!showConfirmPassword)}
            className="text-muted-foreground hover:text-foreground absolute top-1/2 right-3 -translate-y-1/2"
          >
            {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        </div>
      </div>

      <div className="space-y-2">
        <Label htmlFor="bio">Bio (Optional)</Label>
        <Textarea
          id="bio"
          placeholder="Tell us about yourself..."
          value={formData.bio}
          onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
          disabled={isLoading}
          maxLength={500}
          rows={3}
        />
        <p className="text-muted-foreground text-right text-xs">
          {formData.bio.length}/500 characters
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="profile_picture_url">Profile Picture URL (Optional)</Label>
        <Input
          id="profile_picture_url"
          type="url"
          placeholder="https://example.com/avatar.jpg"
          value={formData.profile_picture_url}
          onChange={(e) => setFormData({ ...formData, profile_picture_url: e.target.value })}
          disabled={isLoading}
        />
      </div>

      <div className="border-border bg-muted/30 flex items-center space-x-2 rounded-lg border p-4">
        <input
          type="checkbox"
          id="is_private"
          checked={formData.is_private}
          onChange={(e) => setFormData({ ...formData, is_private: e.target.checked })}
          className="border-border rounded"
        />
        <div className="flex-1">
          <Label htmlFor="is_private" className="flex cursor-pointer items-center gap-2">
            <Lock className="h-4 w-4" />
            Private Account
          </Label>
          <p className="text-muted-foreground mt-1 text-xs">
            Only approved followers can see your posts
          </p>
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Creating account...
          </>
        ) : (
          "Create Account"
        )}
      </Button>

      <p className="text-muted-foreground text-center text-sm">
        Already have an account?{" "}
        <Link href="/login" className="text-primary font-medium hover:underline">
          Sign in
        </Link>
      </p>
    </form>
  )
}

import type React from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Users, MessageCircle, Heart, Zap } from "lucide-react"

export function Hero() {
  return (
    <div className="relative overflow-hidden">
      {/* Hero Section */}
      <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 sm:py-32 lg:px-8">
        <div className="mx-auto max-w-4xl text-center">
          <h1 className="mb-6 text-5xl font-bold tracking-tight text-balance sm:text-6xl lg:text-7xl">
            Connect, Share, and Build{" "}
            <span className="bg-gradient-to-r from-blue-500 via-cyan-500 to-teal-500 bg-clip-text text-transparent">
              Amazing Communities
            </span>
          </h1>
          <p className="text-muted-foreground mx-auto mb-8 max-w-2xl text-xl leading-relaxed text-pretty">
            Join millions of people sharing their stories, connecting with friends, and discovering
            communities that matter to them.
          </p>

          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button asChild size="lg" className="min-w-[200px] px-8 text-lg">
              <Link href="/register">Get Started</Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="min-w-[200px] bg-transparent px-8 text-lg"
            >
              <Link href="/login">Sign In</Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          <FeatureCard
            icon={<Users className="h-6 w-6" />}
            title="Connect Instantly"
            description="Find and follow friends, family, and interesting people from around the world."
          />
          <FeatureCard
            icon={<MessageCircle className="h-6 w-6" />}
            title="Real Conversations"
            description="Engage in meaningful discussions with comments and direct messages."
          />
          <FeatureCard
            icon={<Heart className="h-6 w-6" />}
            title="Share Moments"
            description="Post photos, videos, and thoughts to share your life with your community."
          />
          <FeatureCard
            icon={<Zap className="h-6 w-6" />}
            title="Join Communities"
            description="Discover and participate in communities built around your interests."
          />
        </div>
      </div>
    </div>
  )
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode
  title: string
  description: string
}) {
  return (
    <div className="border-border bg-card rounded-xl border p-6 transition-shadow hover:shadow-lg">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-muted-foreground text-sm">{description}</p>
    </div>
  )
}

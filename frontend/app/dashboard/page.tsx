"use client"

import { Bell, MessageCircle, Settings, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/lib/auth-context"
import { withAuth } from "@/lib/protected-route"

function DashboardPage() {
  const { user } = useAuth()

  return (
    <div className="bg-background min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="mb-2 text-3xl font-bold">Welcome back, {user?.username}!</h1>
          <p className="text-muted-foreground">
            Here&apos;s what&apos;s happening in your network today.
          </p>
        </div>

        {/* TODO: Phase 2 - Quick Stats */}
        <div className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Posts</CardTitle>
              <MessageCircle className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-muted-foreground text-xs">Coming soon...</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Followers</CardTitle>
              <Users className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-muted-foreground text-xs">Coming soon...</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Following</CardTitle>
              <Users className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-muted-foreground text-xs">Coming soon...</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Notifications</CardTitle>
              <Bell className="text-muted-foreground h-4 w-4" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">0</div>
              <p className="text-muted-foreground text-xs">Coming soon...</p>
            </CardContent>
          </Card>
        </div>

        {/* TODO: Phase 2 - Main Content Area */}
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Feed Placeholder */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Your Feed</CardTitle>
                <CardDescription>Posts from people you follow will appear here</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="py-12 text-center">
                  <MessageCircle className="text-muted-foreground mx-auto mb-4 h-12 w-12" />
                  <p className="text-muted-foreground mb-4">
                    No posts yet. Start following people!
                  </p>
                  <Button disabled>Create Post (Coming Soon)</Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Profile Card */}
            <Card>
              <CardHeader>
                <CardTitle>Your Profile</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 text-2xl font-bold text-white">
                    {user?.username?.charAt(0).toUpperCase() || "?"}
                  </div>
                  <div>
                    <p className="font-semibold">{user?.username}</p>
                    <p className="text-muted-foreground text-sm">{user?.email}</p>
                  </div>
                </div>
                {user?.bio && <p className="text-muted-foreground text-sm">{user.bio}</p>}
                <Button variant="outline" className="w-full bg-transparent" disabled>
                  <Settings className="mr-2 h-4 w-4" />
                  Edit Profile (Coming Soon)
                </Button>
              </CardContent>
            </Card>

            {/* TODO: Phase 3 - Communities */}
            <Card>
              <CardHeader>
                <CardTitle>Communities</CardTitle>
                <CardDescription>
                  Join communities to connect with like-minded people
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground py-4 text-center text-sm">
                  Communities feature coming soon...
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default withAuth(DashboardPage)

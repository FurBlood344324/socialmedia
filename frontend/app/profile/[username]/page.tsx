"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Users, Calendar, Lock } from "lucide-react"

// TODO: Phase 2 - Implement full profile functionality
export default function ProfilePage({ params }: { params: { username: string } }) {
  return (
    <div className="bg-background min-h-screen">
      <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6 lg:px-8">
        <Card>
          <CardHeader>
            <CardTitle>Profile Page - Coming Soon</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="py-12 text-center">
              <Users className="text-muted-foreground mx-auto mb-4 h-16 w-16" />
              <h2 className="mb-2 text-2xl font-bold">@{params.username}</h2>
              <p className="text-muted-foreground mb-6">
                User profiles are currently under development
              </p>
              <div className="mx-auto max-w-md space-y-2 text-left">
                <div className="text-muted-foreground flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4" />
                  <span>Profile details</span>
                </div>
                <div className="text-muted-foreground flex items-center gap-2 text-sm">
                  <Users className="h-4 w-4" />
                  <span>Followers & Following lists</span>
                </div>
                <div className="text-muted-foreground flex items-center gap-2 text-sm">
                  <Lock className="h-4 w-4" />
                  <span>Privacy settings</span>
                </div>
              </div>
              <Button className="mt-6" disabled>
                Follow (Coming Soon)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users } from "lucide-react"

// TODO: Phase 3 - Implement communities feature
export default function CommunitiesPage() {
  return (
    <div className="bg-background min-h-screen">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <Card>
          <CardHeader>
            <CardTitle>Communities - Coming Soon</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="py-12 text-center">
              <Users className="text-muted-foreground mx-auto mb-4 h-16 w-16" />
              <p className="text-muted-foreground">Communities feature is under development</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

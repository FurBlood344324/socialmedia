"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { MessageCircle } from "lucide-react"

// TODO: Phase 3 - Implement messaging system
export default function MessagesPage() {
  return (
    <div className="bg-background min-h-screen">
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <Card>
          <CardHeader>
            <CardTitle>Messages - Coming Soon</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="py-12 text-center">
              <MessageCircle className="text-muted-foreground mx-auto mb-4 h-16 w-16" />
              <p className="text-muted-foreground">Direct messaging feature is under development</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

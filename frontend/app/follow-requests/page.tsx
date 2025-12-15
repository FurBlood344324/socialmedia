"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { formatDistanceToNow } from "date-fns"
import { UserPlus } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import type { FollowRequest } from "@/lib/types"

export default function FollowRequestsPage() {
  const { toast } = useToast()
  const [requests, setRequests] = useState<FollowRequest[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [processingIds, setProcessingIds] = useState<Set<number>>(new Set())

  useEffect(() => {
    const loadFollowRequests = async () => {
      try {
        const response = await api.getFollowRequests()
        setRequests(response.requests)
      } catch (error) {
        console.error("Failed to load follow requests:", error)
        toast({
          title: "Error",
          description: "Failed to load follow requests",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    void loadFollowRequests()
  }, [toast])

  const handleAccept = async (followerId: number) => {
    setProcessingIds((prev) => new Set(prev).add(followerId))
    try {
      await api.acceptFollowRequest(followerId)
      setRequests((prev) => prev.filter((req) => req.follower_id !== followerId))
      toast({
        title: "Request accepted",
        description: "You are now following each other",
      })
    } catch (error) {
      console.error("Failed to accept request:", error)
      toast({
        title: "Error",
        description: "Failed to accept follow request",
        variant: "destructive",
      })
    } finally {
      setProcessingIds((prev) => {
        const newSet = new Set(prev)
        newSet.delete(followerId)
        return newSet
      })
    }
  }

  const handleReject = async (followerId: number) => {
    setProcessingIds((prev) => new Set(prev).add(followerId))
    try {
      await api.rejectFollowRequest(followerId)
      setRequests((prev) => prev.filter((req) => req.follower_id !== followerId))
      toast({
        title: "Request rejected",
        description: "Follow request has been declined",
      })
    } catch (error) {
      console.error("Failed to reject request:", error)
      toast({
        title: "Error",
        description: "Failed to reject follow request",
        variant: "destructive",
      })
    } finally {
      setProcessingIds((prev) => {
        const newSet = new Set(prev)
        newSet.delete(followerId)
        return newSet
      })
    }
  }

  if (isLoading) {
    return (
      <div className="bg-background min-h-screen">
        <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
          <Card>
            <CardContent className="py-12 text-center">
              <div className="text-muted-foreground">Loading follow requests...</div>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-background min-h-screen">
      <div className="mx-auto max-w-4xl px-4 py-8 sm:px-6 lg:px-8">
        <Card>
          <CardHeader>
            <CardTitle>Follow Requests</CardTitle>
          </CardHeader>
          <CardContent>
            {requests.length === 0 ? (
              <div className="py-12 text-center">
                <UserPlus className="text-muted-foreground mx-auto mb-4 h-16 w-16" />
                <h3 className="text-foreground mb-2 text-lg font-semibold">No pending requests</h3>
                <p className="text-muted-foreground">
                  You don&apos;t have any follow requests at the moment
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {requests.map((request) => (
                  <div
                    key={request.follower_id}
                    className="border-border flex items-center justify-between rounded-lg border p-4"
                  >
                    <div className="flex items-center gap-4">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={request.profile_picture_url || "/placeholder.svg"} />
                        <AvatarFallback>{request.username[0].toUpperCase()}</AvatarFallback>
                      </Avatar>
                      <div>
                        <Link
                          href={`/profile/${request.username}`}
                          className="font-semibold hover:underline"
                        >
                          {request.username}
                        </Link>
                        <p className="text-muted-foreground text-sm">wants to follow you</p>
                        <p className="text-muted-foreground mt-1 text-xs">
                          {request.created_at
                            ? formatDistanceToNow(
                                new Date(
                                  request.created_at.endsWith("Z")
                                    ? request.created_at
                                    : `${request.created_at}Z`
                                ),
                                { addSuffix: true }
                              )
                            : ""}
                        </p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        onClick={() => handleAccept(request.follower_id)}
                        disabled={processingIds.has(request.follower_id)}
                        size="sm"
                      >
                        Accept
                      </Button>
                      <Button
                        onClick={() => handleReject(request.follower_id)}
                        disabled={processingIds.has(request.follower_id)}
                        variant="outline"
                        size="sm"
                      >
                        Decline
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

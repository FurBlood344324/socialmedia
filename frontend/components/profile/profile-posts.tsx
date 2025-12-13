"use client"

import Image from "next/image"
import { Heart, MessageCircle, MoreHorizontal, Share2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import type { Post } from "@/lib/types"

interface ProfilePostsProps {
  posts: Post[]
  isPrivateAndNotFollowing?: boolean
}

export function ProfilePosts({ posts, isPrivateAndNotFollowing }: ProfilePostsProps) {
  if (isPrivateAndNotFollowing) {
    return (
      <Card className="p-12 text-center">
        <div className="mx-auto max-w-md space-y-3">
          <div className="bg-muted mx-auto flex h-16 w-16 items-center justify-center rounded-full">
            <Heart className="text-muted-foreground h-8 w-8" />
          </div>
          <h3 className="text-xl font-semibold">This Account is Private</h3>
          <p className="text-muted-foreground">Follow this account to see their posts</p>
        </div>
      </Card>
    )
  }

  if (posts.length === 0) {
    return (
      <Card className="p-12 text-center">
        <div className="mx-auto max-w-md space-y-3">
          <div className="bg-muted mx-auto flex h-16 w-16 items-center justify-center rounded-full">
            <MessageCircle className="text-muted-foreground h-8 w-8" />
          </div>
          <h3 className="text-xl font-semibold">No Posts Yet</h3>
          <p className="text-muted-foreground">When they post, you&apos;ll see it here</p>
        </div>
      </Card>
    )
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))

    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
  }

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <Card key={post.post_id}>
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Avatar className="h-10 w-10">
                <AvatarImage src={post.user?.profile_picture_url || "/placeholder.svg"} />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {post.user?.username.slice(0, 2).toUpperCase()}
                </AvatarFallback>
              </Avatar>

              <div className="flex-1 space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-semibold">{post.user?.username}</p>
                    <p className="text-muted-foreground text-sm">{formatDate(post.created_at)}</p>
                  </div>
                  <Button variant="ghost" size="icon">
                    <MoreHorizontal className="h-5 w-5" />
                  </Button>
                </div>

                <p className="text-foreground leading-relaxed">{post.content}</p>

                {post.image_url && (
                  <Image
                    src={post.image_url || "/placeholder.svg"}
                    alt="Post content"
                    width={500}
                    height={300}
                    className="max-h-96 w-full rounded-lg object-cover"
                  />
                )}

                <div className="flex items-center gap-6 pt-2">
                  <button className="text-muted-foreground hover:text-primary flex items-center gap-2 transition-colors">
                    <Heart className="h-5 w-5" />
                    <span className="text-sm">{post.likes_count}</span>
                  </button>
                  <button className="text-muted-foreground hover:text-primary flex items-center gap-2 transition-colors">
                    <MessageCircle className="h-5 w-5" />
                    <span className="text-sm">{post.comments_count}</span>
                  </button>
                  <button className="text-muted-foreground hover:text-primary flex items-center gap-2 transition-colors">
                    <Share2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

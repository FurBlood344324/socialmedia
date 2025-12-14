"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { Bookmark, Heart, MessageCircle, Share2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import type { Post } from "@/lib/types"

interface PostCardProps {
  post: Post
  onLikeUpdate?: (postId: number, liked: boolean, newCount: number) => void
}

export function PostCard({ post, onLikeUpdate }: PostCardProps) {
  const [isLiked, setIsLiked] = useState(post.liked_by_user)
  const [likeCount, setLikeCount] = useState(post.like_count)
  const [isLiking, setIsLiking] = useState(false)
  const { toast } = useToast()

  const handleLike = async () => {
    if (isLiking) return

    // Optimistic update
    const newLiked = !isLiked
    const newCount = newLiked ? likeCount + 1 : likeCount - 1
    setIsLiked(newLiked)
    setLikeCount(newCount)
    setIsLiking(true)

    try {
      if (newLiked) {
        await api.likePost(post.post_id)
      } else {
        await api.unlikePost(post.post_id)
      }
      onLikeUpdate?.(post.post_id, newLiked, newCount)
    } catch {
      setIsLiked(!newLiked)
      setLikeCount(likeCount)
      toast({
        title: "Error",
        description: "Failed to update like. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLiking(false)
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const seconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (seconds < 60) return `${seconds}s ago`
    const minutes = Math.floor(seconds / 60)
    if (minutes < 60) return `${minutes}m ago`
    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    if (days < 7) return `${days}d ago`
    const weeks = Math.floor(days / 7)
    if (weeks < 4) return `${weeks}w ago`
    return date.toLocaleDateString()
  }

  const username = post.username || post.user?.username || "Unknown"
  const profilePicture = post.user_profile_picture || post.user?.profile_picture_url

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-4">
        {/* Header */}
        <div className="mb-3 flex items-start justify-between">
          <Link
            href={`/profile/${username}`}
            className="flex items-center gap-3 transition-opacity hover:opacity-80"
          >
            <Avatar className="h-10 w-10">
              <AvatarImage src={profilePicture || "/placeholder.svg"} alt={username} />
              <AvatarFallback className="bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
                {username.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex flex-col">
              <span className="text-sm font-semibold">{username}</span>
              <div className="text-muted-foreground flex items-center gap-2 text-xs">
                <span>{formatTimeAgo(post.created_at)}</span>
                {post.community_name && (
                  <>
                    <span>•</span>
                    <span className="text-primary font-medium">{post.community_name}</span>
                  </>
                )}
              </div>
            </div>
          </Link>
        </div>

        {/* Content */}
        <div className="mb-3">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{post.content}</p>
        </div>

        {/* Media */}
        {post.media_url && (
          <div className="mb-3 overflow-hidden rounded-lg">
            <Image
              src={post.media_url || "/placeholder.svg"}
              alt="Post media"
              width={600}
              height={400}
              className="h-auto w-full object-cover"
              priority={false}
              unoptimized={true}
            />
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            className={`gap-2 ${isLiked ? "text-red-500 hover:text-red-600" : "text-muted-foreground"}`}
            onClick={handleLike}
            disabled={isLiking}
          >
            <Heart className={`h-4 w-4 ${isLiked ? "fill-current" : ""}`} />
            <span className="text-xs font-medium">{likeCount}</span>
          </Button>

          <Button variant="ghost" size="sm" className="text-muted-foreground gap-2">
            <MessageCircle className="h-4 w-4" />
            <span className="text-xs font-medium">{post.comment_count}</span>
          </Button>

          <Button variant="ghost" size="sm" className="text-muted-foreground ml-auto gap-2">
            <Share2 className="h-4 w-4" />
          </Button>

          <Button variant="ghost" size="sm" className="text-muted-foreground gap-2">
            <Bookmark className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

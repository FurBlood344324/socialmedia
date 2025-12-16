"use client"

import { useState } from "react"
import Image from "next/image"
import Link from "next/link"
import { parseISO } from "date-fns"
import { Heart, MessageCircle, MoreHorizontal, Pencil, Share2, Trash2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"
import type { Post } from "@/lib/types"

interface ProfilePostsProps {
  posts: Post[]
  isPrivateAndNotFollowing?: boolean
}

export function ProfilePosts({ posts: initialPosts, isPrivateAndNotFollowing }: ProfilePostsProps) {
  const [posts, setPosts] = useState(initialPosts)
  const [likingPosts, setLikingPosts] = useState<Set<number>>(new Set())
  const [editingPost, setEditingPost] = useState<Post | null>(null)
  const [editContent, setEditContent] = useState("")
  const [deleteConfirmPost, setDeleteConfirmPost] = useState<Post | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()
  const { user } = useAuth()

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
    const date = parseISO(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (seconds < 60) return seconds <= 5 ? "just now" : `${seconds}s ago`
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    const days = Math.floor(hours / 24)
    if (days < 7) return `${days}d ago`
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" })
  }

  const isWithin15Minutes = (dateString: string) => {
    const date = parseISO(dateString)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = diff / (1000 * 60)
    return minutes <= 15
  }

  const isOwnPost = (post: Post) => {
    return user?.user_id === post.user_id
  }

  const handleLike = async (postId: number) => {
    if (likingPosts.has(postId)) return

    const post = posts.find((p) => p.post_id === postId)
    if (!post) return

    const newLiked = !post.liked_by_user
    const newCount = newLiked ? post.like_count + 1 : post.like_count - 1

    setPosts((prev) =>
      prev.map((p) =>
        p.post_id === postId ? { ...p, liked_by_user: newLiked, like_count: newCount } : p
      )
    )
    setLikingPosts((prev) => new Set(prev).add(postId))

    try {
      if (newLiked) {
        await api.likePost(postId)
      } else {
        await api.unlikePost(postId)
      }
    } catch {
      setPosts((prev) =>
        prev.map((p) =>
          p.post_id === postId ? { ...p, liked_by_user: !newLiked, like_count: post.like_count } : p
        )
      )
      toast({
        title: "Error",
        description: "Failed to update like. Please try again.",
        variant: "destructive",
      })
    } finally {
      setLikingPosts((prev) => {
        const next = new Set(prev)
        next.delete(postId)
        return next
      })
    }
  }

  const handleEditClick = (post: Post) => {
    setEditingPost(post)
    setEditContent(post.content)
  }

  const handleEditSubmit = async () => {
    if (!editingPost || !editContent.trim()) return

    setIsSubmitting(true)
    try {
      await api.updatePost(editingPost.post_id, { content: editContent.trim() })
      setPosts((prev) =>
        prev.map((p) =>
          p.post_id === editingPost.post_id ? { ...p, content: editContent.trim() } : p
        )
      )
      setEditingPost(null)
      toast({
        title: "Success",
        description: "Post updated successfully.",
      })
    } catch {
      toast({
        title: "Error",
        description: "Failed to update post. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteConfirm = async () => {
    if (!deleteConfirmPost) return

    setIsSubmitting(true)
    try {
      await api.deletePost(deleteConfirmPost.post_id)
      setPosts((prev) => prev.filter((p) => p.post_id !== deleteConfirmPost.post_id))
      setDeleteConfirmPost(null)
      toast({
        title: "Success",
        description: "Post deleted successfully.",
      })
    } catch {
      toast({
        title: "Error",
        description: "Failed to delete post. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <div className="space-y-4">
        {posts.map((post) => (
          <Card key={post.post_id}>
            <CardContent className="p-6">
              <div className="flex items-start gap-3">
                <Link href={`/profile/${post.user?.username || post.username}`}>
                  <Avatar className="h-10 w-10">
                    <AvatarImage
                      src={
                        post.user_profile_picture ||
                        post.user?.profile_picture_url ||
                        "/placeholder-user.jpg"
                      }
                    />
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {(post.user?.username || post.username || "??").slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Link>

                <div className="flex-1 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <Link href={`/profile/${post.user?.username || post.username}`}>
                        <p className="font-semibold hover:underline">
                          {post.user?.username || post.username}
                        </p>
                      </Link>
                      <p className="text-muted-foreground text-sm">{formatDate(post.created_at)}</p>
                    </div>
                    {isOwnPost(post) && (
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-5 w-5" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => handleEditClick(post)}
                            disabled={!isWithin15Minutes(post.created_at)}
                            className={!isWithin15Minutes(post.created_at) ? "opacity-50" : ""}
                          >
                            <Pencil className="mr-2 h-4 w-4" />
                            {isWithin15Minutes(post.created_at) ? "Edit" : "Edit (15m expired)"}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem
                            onClick={() => setDeleteConfirmPost(post)}
                            className="text-red-600 focus:text-red-600"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    )}
                  </div>

                  <p className="text-foreground leading-relaxed">{post.content}</p>

                  {post.media_url && (
                    <Image
                      src={post.media_url || "/placeholder.svg"}
                      alt="Post content"
                      width={500}
                      height={300}
                      className="max-h-96 w-full rounded-lg object-cover"
                      unoptimized={true}
                    />
                  )}

                  <div className="flex items-center gap-6 pt-2">
                    <button
                      onClick={() => handleLike(post.post_id)}
                      disabled={likingPosts.has(post.post_id)}
                      className={`flex items-center gap-2 transition-colors ${
                        post.liked_by_user
                          ? "text-red-500"
                          : "text-muted-foreground hover:text-primary"
                      }`}
                    >
                      <Heart className={`h-5 w-5 ${post.liked_by_user ? "fill-current" : ""}`} />
                      <span className="text-sm">{post.like_count}</span>
                    </button>
                    <button className="text-muted-foreground hover:text-primary flex items-center gap-2 transition-colors">
                      <MessageCircle className="h-5 w-5" />
                      <span className="text-sm">{post.comment_count}</span>
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

      {/* Edit Dialog */}
      <Dialog open={!!editingPost} onOpenChange={(open) => !open && setEditingPost(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Post</DialogTitle>
            <DialogDescription>
              Make changes to your post. You can only edit posts within 15 minutes of creation.
            </DialogDescription>
          </DialogHeader>
          <Textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            placeholder="What's on your mind?"
            className="min-h-[120px]"
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditingPost(null)}>
              Cancel
            </Button>
            <Button onClick={handleEditSubmit} disabled={isSubmitting || !editContent.trim()}>
              {isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={!!deleteConfirmPost}
        onOpenChange={(open) => !open && setDeleteConfirmPost(null)}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Post</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this post? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmPost(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm} disabled={isSubmitting}>
              {isSubmitting ? "Deleting..." : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

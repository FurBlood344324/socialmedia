"use client"

import { useCallback, useEffect, useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { Loader2, MessageCircle, MoreVertical, Reply, Trash2 } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"
import type { Comment as ApiComment } from "@/lib/types"

interface CommentSectionProps {
  postId: number
}

export function CommentSection({ postId }: CommentSectionProps) {
  const { user } = useAuth()
  const { toast } = useToast()
  const [comments, setComments] = useState<ApiComment[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [newComment, setNewComment] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const loadComments = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await api.getPostComments(postId)
      setComments(response)
    } catch {
      toast({
        title: "Error",
        description: "Failed to load comments",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }, [postId, toast])

  useEffect(() => {
    void loadComments()
  }, [loadComments])

  const handleSubmitComment = async () => {
    if (!newComment.trim() || isSubmitting) return

    setIsSubmitting(true)
    try {
      const comment = await api.createComment(postId, { content: newComment.trim() })
      setComments([comment, ...comments])
      setNewComment("")
      toast({
        title: "Comment posted",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to post comment",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteComment = async (commentId: number) => {
    try {
      await api.deleteComment(commentId)
      setComments(comments.filter((c) => c.id !== commentId))
      toast({
        title: "Comment deleted",
      })
    } catch {
      toast({
        title: "Error",
        description: "Failed to delete comment",
        variant: "destructive",
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-start gap-3">
        <Avatar className="h-8 w-8">
          <AvatarImage
            src={user?.profile_picture_url || "/placeholder-user.jpg"}
            alt={user?.username}
          />
          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-cyan-500 text-white">
            {user?.username?.charAt(0).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1 space-y-2">
          <Textarea
            placeholder="Write a comment..."
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            disabled={isSubmitting}
            className="min-h-[80px]"
          />
          <Button
            onClick={handleSubmitComment}
            disabled={!newComment.trim() || isSubmitting}
            size="sm"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Posting...
              </>
            ) : (
              "Post Comment"
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        {comments.length === 0 ? (
          <div className="text-muted-foreground py-8 text-center">
            <MessageCircle className="mx-auto mb-2 h-8 w-8 opacity-50" />
            <p>No comments yet. Be the first to comment!</p>
          </div>
        ) : (
          comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              currentUserId={user?.user_id}
              onDelete={handleDeleteComment}
              postId={postId}
            />
          ))
        )}
      </div>
    </div>
  )
}

interface CommentItemProps {
  comment: ApiComment
  currentUserId?: number
  onDelete: (commentId: number) => void
  postId: number
  depth?: number
}

function CommentItem({ comment, currentUserId, onDelete, postId, depth = 0 }: CommentItemProps) {
  const { toast } = useToast()
  const [showReplyInput, setShowReplyInput] = useState(false)
  const [replyContent, setReplyContent] = useState("")
  const [isReplying, setIsReplying] = useState(false)
  const [replies, setReplies] = useState<ApiComment[]>(comment.replies || [])
  const [showReplies, setShowReplies] = useState(false)
  const [loadingReplies, setLoadingReplies] = useState(false)

  const replyCount = comment.reply_count || 0
  const hasReplies = replyCount > 0 || replies.length > 0

  const handleToggleReplies = async () => {
    if (!showReplies && replies.length === 0 && replyCount > 0) {
      setLoadingReplies(true)
      try {
        const fetchedReplies = await api.getCommentReplies(comment.id)
        setReplies(fetchedReplies)
      } catch {
        toast({
          title: "Error",
          description: "Failed to load replies",
          variant: "destructive",
        })
      } finally {
        setLoadingReplies(false)
      }
    }
    setShowReplies(!showReplies)
  }

  const handleReply = async () => {
    if (!replyContent.trim() || isReplying) return

    setIsReplying(true)
    try {
      const reply = await api.createComment(postId, {
        content: replyContent.trim(),
        parent_comment_id: comment.id,
      })
      setReplies([...replies, reply])
      setReplyContent("")
      setShowReplyInput(false)
      setShowReplies(true)
      toast({
        title: "Reply posted",
      })
    } catch {
      toast({
        title: "Error",
        description: "Failed to post reply",
        variant: "destructive",
      })
    } finally {
      setIsReplying(false)
    }
  }

  const isOwner = currentUserId === comment.user_id

  return (
    <div className={depth > 0 ? "ml-12" : ""}>
      <Card className="overflow-hidden">
        <CardContent className="p-4">
          <div className="flex gap-3">
            <Avatar className="h-8 w-8">
              <AvatarImage
                src={comment.user_profile_picture || "/placeholder-user.jpg"}
                alt={comment.username}
              />
              <AvatarFallback className="bg-gradient-to-br from-purple-500 to-pink-500 text-white">
                {comment.username?.charAt(0).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-semibold">{comment.username}</span>
                  <span className="text-muted-foreground ml-2 text-xs">
                    {formatDistanceToNow(new Date(comment.created_at), { addSuffix: true })}
                  </span>
                </div>
                {isOwner && (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => onDelete(comment.id)}
                        className="text-destructive"
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                )}
              </div>
              <p className="text-foreground mt-2 text-sm">{comment.content}</p>
              <div className="mt-2 flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowReplyInput(!showReplyInput)}
                  className="text-muted-foreground hover:text-primary h-auto p-0 text-xs"
                >
                  <Reply className="mr-1 h-3 w-3" />
                  Reply
                </Button>
                {hasReplies && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleToggleReplies}
                    disabled={loadingReplies}
                    className="text-muted-foreground hover:text-primary h-auto p-0 text-xs"
                  >
                    {loadingReplies ? <Loader2 className="mr-1 h-3 w-3 animate-spin" /> : null}
                    {showReplies ? "Hide" : "Show"} {replies.length || replyCount}{" "}
                    {(replies.length || replyCount) === 1 ? "reply" : "replies"}
                  </Button>
                )}
              </div>

              {showReplyInput && (
                <div className="mt-3 space-y-2">
                  <Textarea
                    placeholder="Write a reply..."
                    value={replyContent}
                    onChange={(e) => setReplyContent(e.target.value)}
                    disabled={isReplying}
                    className="min-h-[60px]"
                  />
                  <div className="flex gap-2">
                    <Button
                      onClick={handleReply}
                      disabled={!replyContent.trim() || isReplying}
                      size="sm"
                    >
                      {isReplying ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Replying...
                        </>
                      ) : (
                        "Reply"
                      )}
                    </Button>
                    <Button variant="outline" onClick={() => setShowReplyInput(false)} size="sm">
                      Cancel
                    </Button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {showReplies && replies.length > 0 && (
        <div className="mt-4 space-y-4">
          {replies.map((reply) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              currentUserId={currentUserId}
              onDelete={onDelete}
              postId={postId}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  )
}

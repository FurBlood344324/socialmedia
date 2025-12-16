"use client"

import { useEffect, useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { MessageCircle } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { api } from "@/lib/api"
import type { Conversation } from "@/lib/types"

interface ConversationListProps {
  onSelectConversation: (userId: number, username: string, profilePicture?: string) => void
  selectedUserId?: number
}

export function ConversationList({ onSelectConversation, selectedUserId }: ConversationListProps) {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    void loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const response = await api.getConversations()
      setConversations(response.conversations)
    } catch (error) {
      console.error("Failed to load conversations:", error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">Loading conversations...</div>
      </div>
    )
  }

  if (conversations.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center p-8 text-center">
        <MessageCircle className="text-muted-foreground mb-4 h-12 w-12" />
        <h3 className="text-foreground mb-2 text-lg font-semibold">No messages yet</h3>
        <p className="text-muted-foreground text-sm">Search for users and start a conversation</p>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-border border-b p-4">
        <h2 className="text-lg font-semibold">Messages</h2>
      </div>
      <div className="flex-1 overflow-y-auto">
        {conversations.map((conversation) => (
          <button
            key={conversation.other_user.user_id}
            onClick={() =>
              onSelectConversation(
                conversation.other_user.user_id,
                conversation.other_user.username,
                conversation.other_user.profile_picture_url
              )
            }
            className={`hover:bg-muted w-full border-b p-4 text-left transition-colors ${
              selectedUserId === conversation.other_user.user_id ? "bg-muted" : ""
            }`}
          >
            <div className="flex items-start gap-3">
              <Avatar>
                <AvatarImage
                  src={conversation.other_user.profile_picture_url || "/placeholder.svg"}
                />
                <AvatarFallback>{conversation.other_user.username[0].toUpperCase()}</AvatarFallback>
              </Avatar>
              <div className="min-w-0 flex-1">
                <div className="mb-1 flex items-center justify-between">
                  <span className="font-semibold">{conversation.other_user.username}</span>
                  {conversation.unread_count > 0 && (
                    <Badge variant="default" className="ml-2">
                      {conversation.unread_count}
                    </Badge>
                  )}
                </div>
                <p className="text-muted-foreground truncate text-sm">
                  {conversation.last_message.content}
                </p>
                <p className="text-muted-foreground mt-1 text-xs">
                  {formatDistanceToNow(new Date(conversation.last_message.created_at), {
                    addSuffix: true,
                  })}
                </p>
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

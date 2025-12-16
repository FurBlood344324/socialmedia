"use client"

import type React from "react"
import { useEffect, useRef, useState } from "react"
import { formatDistanceToNow } from "date-fns"
import { Send, X } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { api } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"
import type { Message } from "@/lib/types"

interface MessageViewProps {
  userId: number
  username: string
  profilePicture?: string
  onClose?: () => void
}

export function MessageView({ userId, username, profilePicture, onClose }: MessageViewProps) {
  const { user } = useAuth()
  const { toast } = useToast()
  const [messages, setMessages] = useState<Message[]>([])
  const [newMessage, setNewMessage] = useState("")
  const [isSending, setIsSending] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const loadMessages = async () => {
      try {
        const response = await api.getConversationMessages(userId)
        setMessages(response.messages.reverse()) // Reverse to show oldest first
      } catch (error) {
        console.error("Failed to load messages:", error)
      } finally {
        setIsLoading(false)
      }
    }

    void loadMessages()
    const interval = setInterval(() => {
      void loadMessages()
    }, 5000) // Poll every 5 seconds
    return () => clearInterval(interval)
  }, [userId])

  const prevMessagesLength = useRef(0)

  useEffect(() => {
    // Only scroll to bottom if new messages were added
    if (messages.length > prevMessagesLength.current) {
      scrollToBottom()
    }
    prevMessagesLength.current = messages.length
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSendMessage = async () => {
    if (!newMessage.trim() || isSending) return

    setIsSending(true)
    try {
      const message = await api.sendMessage({
        receiver_id: userId,
        content: newMessage.trim(),
      })
      setMessages((prev) => [...prev, message])
      setNewMessage("")
    } catch {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      void handleSendMessage()
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-muted-foreground text-sm">Loading messages...</div>
      </div>
    )
  }

  return (
    <div className="flex h-full flex-col">
      {/* Header */}
      <div className="border-border flex items-center gap-3 border-b p-4">
        <Avatar>
          <AvatarImage src={profilePicture || "/placeholder.svg"} />
          <AvatarFallback>{username[0].toUpperCase()}</AvatarFallback>
        </Avatar>
        <div>
          <h2 className="font-semibold">{username}</h2>
        </div>
        {onClose && (
          <Button variant="ghost" size="icon" className="ml-auto" onClick={onClose}>
            <X className="h-4 w-4" />
            <span className="sr-only">Close conversation</span>
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="text-muted-foreground flex h-full items-center justify-center text-center">
            <p>No messages yet. Start the conversation!</p>
          </div>
        ) : (
          messages.map((message) => {
            const isOwnMessage = message.sender_id === user?.user_id
            return (
              <div
                key={message.message_id}
                className={`flex ${isOwnMessage ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg p-3 ${
                    isOwnMessage ? "bg-primary text-primary-foreground" : "bg-muted"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.content}</p>
                  <p
                    className={`mt-1 text-xs ${isOwnMessage ? "text-primary-foreground/70" : "text-muted-foreground"}`}
                  >
                    {formatDistanceToNow(new Date(message.created_at), { addSuffix: true })}
                  </p>
                </div>
              </div>
            )
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-border border-t p-4">
        <div className="flex gap-2">
          <Textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            className="min-h-[60px] resize-none"
            disabled={isSending}
          />
          <Button onClick={handleSendMessage} disabled={!newMessage.trim() || isSending}>
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

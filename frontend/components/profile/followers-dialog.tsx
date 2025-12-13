"use client"

import type React from "react"
import { useState } from "react"
import { UserMinus, UserPlus } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { ScrollArea } from "@/components/ui/scroll-area"
import type { FollowUser } from "@/lib/types"

interface FollowersDialogProps {
  trigger: React.ReactNode
  title: string
  users: FollowUser[]
  onFollowToggle?: (userId: number) => void
  isLoading?: boolean
}

export function FollowersDialog({
  trigger,
  title,
  users,
  onFollowToggle,
  isLoading,
}: FollowersDialogProps) {
  const [open, setOpen] = useState(false)

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh]">
          {users.length === 0 ? (
            <div className="text-muted-foreground py-8 text-center">No users to show</div>
          ) : (
            <div className="space-y-3 pr-4">
              {users.map((user) => (
                <div key={user.user_id} className="flex items-center gap-3 py-2">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={user.profile_picture_url || "/placeholder.svg"} />
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      {user.username.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>

                  <div className="min-w-0 flex-1">
                    <p className="truncate font-semibold">{user.username}</p>
                    {user.bio && (
                      <p className="text-muted-foreground truncate text-sm">{user.bio}</p>
                    )}
                  </div>

                  {onFollowToggle && (
                    <Button
                      size="sm"
                      variant={user.is_following ? "outline" : "default"}
                      onClick={() => onFollowToggle(user.user_id)}
                      disabled={isLoading}
                    >
                      {user.is_following ? (
                        <>
                          <UserMinus className="mr-1 h-4 w-4" />
                          Unfollow
                        </>
                      ) : (
                        <>
                          <UserPlus className="mr-1 h-4 w-4" />
                          Follow
                        </>
                      )}
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </DialogContent>
    </Dialog>
  )
}

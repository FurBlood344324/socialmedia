"use client"

import Link from "next/link"
import { Calendar, LinkIcon, Settings, UserMinus, UserPlus } from "lucide-react"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import type { ProfileData } from "@/lib/types"

interface ProfileHeaderProps {
  profile: ProfileData
  onFollowToggle: () => void
  isLoading?: boolean
}

export function ProfileHeader({ profile, onFollowToggle, isLoading }: ProfileHeaderProps) {
  const getInitials = (username: string) => {
    return username.slice(0, 2).toUpperCase()
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
    })
  }

  return (
    <Card className="p-6">
      <div className="flex flex-col gap-6 md:flex-row">
        <Avatar className="h-24 w-24 md:h-32 md:w-32">
          <AvatarImage
            src={profile.profile_picture_url || "/placeholder.svg"}
            alt={profile.username}
          />
          <AvatarFallback className="bg-primary text-primary-foreground text-2xl md:text-3xl">
            {getInitials(profile.username)}
          </AvatarFallback>
        </Avatar>

        <div className="flex-1 space-y-4">
          <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <h1 className="text-2xl font-bold md:text-3xl">{profile.username}</h1>
              <p className="text-muted-foreground">@{profile.username}</p>
            </div>

            {profile.is_own_profile ? (
              <Button asChild variant="outline" className="w-full bg-transparent sm:w-auto">
                <Link href="/profile/edit">
                  <Settings className="mr-2 h-4 w-4" />
                  Edit Profile
                </Link>
              </Button>
            ) : (
              <Button
                onClick={onFollowToggle}
                disabled={isLoading}
                variant={profile.is_following ? "outline" : "default"}
                className="w-full sm:w-auto"
              >
                {profile.is_following ? (
                  <>
                    <UserMinus className="mr-2 h-4 w-4" />
                    Unfollow
                  </>
                ) : (
                  <>
                    <UserPlus className="mr-2 h-4 w-4" />
                    Follow
                  </>
                )}
              </Button>
            )}
          </div>

          <div className="flex gap-4 text-sm md:gap-6">
            <div>
              <span className="font-bold">{profile.stats.posts_count}</span>{" "}
              <span className="text-muted-foreground">Posts</span>
            </div>
            <button className="hover:underline">
              <span className="font-bold">{profile.stats.followers_count}</span>{" "}
              <span className="text-muted-foreground">Followers</span>
            </button>
            <button className="hover:underline">
              <span className="font-bold">{profile.stats.following_count}</span>{" "}
              <span className="text-muted-foreground">Following</span>
            </button>
          </div>

          {profile.bio && <p className="text-foreground leading-relaxed">{profile.bio}</p>}

          <div className="text-muted-foreground flex flex-wrap gap-3 text-sm">
            <div className="flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              <span>Joined {formatDate(profile.created_at)}</span>
            </div>
            {profile.is_private && (
              <div className="flex items-center gap-1">
                <LinkIcon className="h-4 w-4" />
                <span className="text-primary">Private Account</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}

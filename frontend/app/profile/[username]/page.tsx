"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"
import { FollowersDialog } from "@/components/profile/followers-dialog"
import { ProfileHeader } from "@/components/profile/profile-header"
import { ProfilePosts } from "@/components/profile/profile-posts"
import { Button } from "@/components/ui/button"
import { api } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"
import type { FollowUser, Post, ProfileData } from "@/lib/types"

export default function ProfilePage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const username = params.username as string

  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [followers, setFollowers] = useState<FollowUser[]>([])
  const [following, setFollowing] = useState<FollowUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isFollowLoading, setIsFollowLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const loadProfile = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const profileData = await api.getUserProfile(username)

        // Backend might not return stats, so we initialize them
        const profileWithStats = {
          ...profileData,
          is_own_profile: user?.username === username, // Calculate ownership on client side
          stats: profileData.stats || {
            posts_count: 0,
            followers_count: 0,
            following_count: 0,
          },
        }

        setProfile(profileWithStats)

        // Only fetch specific data if profile exists and we have access
        if (profileData) {
          const [userPosts, followersList, followingList] = await Promise.all([
            api.getUserPosts(profileData.user_id),
            api.getFollowers(profileData.user_id),
            api.getFollowing(profileData.user_id),
          ])

          setPosts(userPosts)
          setFollowers(followersList)
          setFollowing(followingList)

          // Update stats with actual counts from fetched data
          setProfile((prev) =>
            prev
              ? {
                  ...prev,
                  stats: {
                    posts_count: userPosts.length,
                    followers_count: followersList.length,
                    following_count: followingList.length,
                  },
                }
              : null
          )
        }
      } catch (err) {
        console.error("Error loading profile:", err)
        setError(err instanceof Error ? err.message : "Failed to load profile")
      } finally {
        setIsLoading(false)
      }
    }

    void loadProfile()
  }, [username, user?.username])

  const handleFollowToggle = async () => {
    if (!profile) return

    try {
      setIsFollowLoading(true)
      if (profile.is_following) {
        await api.unfollowUser(profile.user_id)
      } else {
        await api.followUser(profile.user_id)
      }
      setProfile({
        ...profile,
        is_following: !profile.is_following,
        stats: {
          ...profile.stats,
          followers_count: profile.is_following
            ? profile.stats.followers_count - 1
            : profile.stats.followers_count + 1,
        },
      })
    } catch (err) {
      console.error("Failed to toggle follow:", err)
    } finally {
      setIsFollowLoading(false)
    }
  }

  const handleUserFollowToggle = async (userId: number) => {
    // Optimistic update
    const userToToggle = followers.find((u) => u.user_id === userId)
    if (!userToToggle) return

    const originalFollowers = [...followers]
    const updatedFollowers = followers.map((user) =>
      user.user_id === userId ? { ...user, is_following: !user.is_following } : user
    )
    setFollowers(updatedFollowers)

    try {
      if (userToToggle.is_following) {
        await api.unfollowUser(userId)
      } else {
        await api.followUser(userId)
      }
    } catch (err) {
      console.error("Failed to toggle follow:", err)
      // Revert on error
      setFollowers(originalFollowers)
    }
  }

  if (isLoading) {
    return (
      <div className="bg-background flex min-h-screen items-center justify-center">
        <Loader2 className="text-primary h-8 w-8 animate-spin" />
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="bg-background flex min-h-screen items-center justify-center">
        <div className="space-y-4 text-center">
          <h2 className="text-2xl font-bold">Profile Not Found</h2>
          <p className="text-muted-foreground">{error || "This user doesn't exist"}</p>
          <Button onClick={() => router.push("/dashboard")}>Go to Dashboard</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-background min-h-screen">
      <div className="mx-auto max-w-4xl space-y-6 px-4 py-8 sm:px-6 lg:px-8">
        <ProfileHeader
          profile={profile}
          onFollowToggle={handleFollowToggle}
          isLoading={isFollowLoading}
        />

        <div className="flex gap-2">
          <FollowersDialog
            trigger={
              <Button variant="outline" size="sm">
                {profile.stats.followers_count} Followers
              </Button>
            }
            title="Followers"
            users={followers}
            onFollowToggle={handleUserFollowToggle}
          />
          <FollowersDialog
            trigger={
              <Button variant="outline" size="sm">
                {profile.stats.following_count} Following
              </Button>
            }
            title="Following"
            users={following}
            onFollowToggle={handleUserFollowToggle}
          />
        </div>

        <ProfilePosts
          posts={posts}
          isPrivateAndNotFollowing={
            profile.is_private && !profile.is_own_profile && !profile.is_following
          }
        />
      </div>
    </div>
  )
}

"use client"

import { useEffect, useState } from "react"
import { useParams, useRouter } from "next/navigation"
import { Grid3X3, Image as ImageIcon, Loader2, MessageSquare } from "lucide-react"
import { FollowersDialog } from "@/components/profile/followers-dialog"
import { ProfileHeader } from "@/components/profile/profile-header"
import { ProfilePosts } from "@/components/profile/profile-posts"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { api } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"
import type { FollowUser, Post, ProfileData, UserCommentWithPost } from "@/lib/types"

export default function ProfilePage() {
  const params = useParams()
  const router = useRouter()
  const { user } = useAuth()
  const username = params.username as string

  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [posts, setPosts] = useState<Post[]>([])
  const [userComments, setUserComments] = useState<UserCommentWithPost[]>([])
  const [followers, setFollowers] = useState<FollowUser[]>([])
  const [following, setFollowing] = useState<FollowUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isFollowLoading, setIsFollowLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState("posts")

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
          const [userPosts, followersList, followingList, commentsWithPosts] = await Promise.all([
            api.getUserPosts(profileData.user_id).catch(() => []),
            api.getFollowers(profileData.user_id).catch(() => []),
            api.getFollowing(profileData.user_id).catch(() => []),
            api.getUserCommentsWithPosts(profileData.user_id).catch(() => []),
          ])

          setPosts(userPosts)
          setFollowers(followersList)
          setFollowing(followingList)
          setUserComments(commentsWithPosts)

          // Update stats with actual counts from fetched data only if we have full access
          setProfile((prev) => {
            if (!prev) return null

            // If we can't see the profile details (private), don't overwrite stats with 0s from empty lists
            if (
              profileData.is_private &&
              !profileData.is_own_profile &&
              !profileData.is_following
            ) {
              return prev
            }

            return {
              ...prev,
              stats: {
                posts_count: userPosts.length,
                followers_count: followersList.length,
                following_count: followingList.length,
              },
            }
          })
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

      if (profile.has_pending_request) {
        // Cancel pending request
        await api.unfollowUser(profile.user_id)
        setProfile({
          ...profile,
          has_pending_request: false,
        })
      } else if (profile.is_following) {
        // Unfollow user
        await api.unfollowUser(profile.user_id)
        setProfile({
          ...profile,
          is_following: false,
          stats: {
            ...profile.stats,
            followers_count: profile.stats.followers_count - 1,
          },
        })
      } else {
        // Follow user
        await api.followUser(profile.user_id)

        if (profile.is_private) {
          // If private, set as pending
          setProfile({
            ...profile,
            has_pending_request: true,
          })
        } else {
          // If public, set as following
          setProfile({
            ...profile,
            is_following: true,
            stats: {
              ...profile.stats,
              followers_count: profile.stats.followers_count + 1,
            },
          })
        }
      }
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
          {profile.is_private && !profile.is_own_profile && !profile.is_following ? (
            <>
              <Button variant="outline" size="sm" disabled>
                Followers
              </Button>
              <Button variant="outline" size="sm" disabled>
                Following
              </Button>
            </>
          ) : (
            <>
              <FollowersDialog
                trigger={
                  <Button variant="outline" size="sm">
                    {profile.stats.followers_count} Followers
                  </Button>
                }
                title="Followers"
                users={followers}
                onFollowToggle={handleUserFollowToggle}
                currentUserId={user?.user_id}
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
                currentUserId={user?.user_id}
              />
            </>
          )}
        </div>

        {profile.is_private && !profile.is_own_profile && !profile.is_following ? (
          <ProfilePosts posts={[]} isPrivateAndNotFollowing={true} />
        ) : (
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="posts" className="flex items-center gap-2">
                <Grid3X3 className="h-4 w-4" />
                Posts
              </TabsTrigger>
              <TabsTrigger value="comments" className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                Comments
              </TabsTrigger>
              <TabsTrigger value="media" className="flex items-center gap-2">
                <ImageIcon className="h-4 w-4" />
                Media
              </TabsTrigger>
            </TabsList>

            <TabsContent value="posts" className="mt-6">
              <ProfilePosts posts={posts} />
            </TabsContent>

            <TabsContent value="comments" className="mt-6">
              {userComments.length === 0 ? (
                <div className="rounded-lg border p-12 text-center">
                  <MessageSquare className="text-muted-foreground mx-auto mb-4 h-12 w-12" />
                  <h3 className="text-lg font-semibold">No Comments Yet</h3>
                  <p className="text-muted-foreground">Comments made on posts will appear here</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {userComments.map((item) => (
                    <div key={item.comment_id} className="rounded-lg border p-4">
                      {/* Original Post */}
                      <div className="bg-muted/50 mb-3 rounded-lg p-3">
                        <div className="mb-2 flex items-center gap-2">
                          <div className="bg-primary/20 h-6 w-6 rounded-full" />
                          <span className="text-sm font-medium">{item.post_author_username}</span>
                        </div>
                        <p className="text-muted-foreground line-clamp-2 text-sm">
                          {item.post_content}
                        </p>
                      </div>
                      {/* User's Comment */}
                      <div className="flex gap-3">
                        <div className="bg-primary/30 h-8 w-8 rounded-full" />
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-medium">{item.commenter_username}</span>
                            <span className="text-muted-foreground text-xs">
                              {new Date(
                                item.comment_created_at.endsWith("Z")
                                  ? item.comment_created_at
                                  : `${item.comment_created_at}Z`
                              ).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="mt-1 text-sm">{item.comment_content}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="media" className="mt-6">
              {posts.filter((p) => p.media_url).length === 0 ? (
                <div className="rounded-lg border p-12 text-center">
                  <ImageIcon className="text-muted-foreground mx-auto mb-4 h-12 w-12" />
                  <h3 className="text-lg font-semibold">No Media Yet</h3>
                  <p className="text-muted-foreground">Posts with images will appear here</p>
                </div>
              ) : (
                <ProfilePosts posts={posts.filter((p) => p.media_url)} />
              )}
            </TabsContent>
          </Tabs>
        )}
      </div>
    </div>
  )
}

import type {
  Comment,
  CommunitiesResponse,
  Community,
  CommunityMembersResponse,
  ConversationsResponse,
  CreateCommentData,
  CreateCommunityData,
  CreatePostData,
  FeedResponse,
  FollowRequestsResponse,
  FollowUser,
  LoginResponse,
  Message,
  MessagesResponse,
  Post,
  ProfileData,
  RecommendationResponse,
  RegisterData,
  SendMessageData, // Declare SendMessageData here
  UpdateCommunityData,
  UpdateProfileData,
  User,
  UserCommentWithPost,
  UserSearchResponse,
} from "./types"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000"

class ApiClient {
  private getAuthHeaders(): HeadersInit {
    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    }
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "An error occurred" }))
      throw new Error(error.message || `HTTP error! status: ${response.status}`)
    }
    return response.json()
  }

  // Auth endpoints
  async login(username: string, password: string): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    })
    return this.handleResponse<LoginResponse>(response)
  }

  async register(data: RegisterData): Promise<LoginResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return this.handleResponse<LoginResponse>(response)
  }

  async getCurrentUser(): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ user: User }>(response)
    return data.user
  }

  // Profile-related API methods
  async getUserProfile(username: string): Promise<ProfileData> {
    const response = await fetch(`${API_BASE_URL}/api/auth/users/username/${username}`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ user: ProfileData }>(response)
    return data.user // The backend wraps user in "user" key for this endpoint too (Line 205 of user_controller)
  }

  async updateProfile(data: UpdateProfileData): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ user: User }>(response)
    return responseData.user
  }

  async deleteAccount(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async followUser(userId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/follow`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async unfollowUser(userId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/follow`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async getFollowers(userId: number): Promise<FollowUser[]> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/followers`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ followers: FollowUser[] }>(response)
    return data.followers || []
  }

  async getFollowing(userId: number): Promise<FollowUser[]> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/following`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ following: FollowUser[] }>(response)
    return data.following || []
  }

  async getUserPosts(userId: number): Promise<Post[]> {
    const response = await fetch(`${API_BASE_URL}/api/posts/user/${userId}`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ posts: Post[] }>(response)
    // The backend might return posts in "posts" key or similar, checking safely.
    return data.posts || []
  }

  async getUserCommentsWithPosts(
    userId: number,
    limit = 50,
    offset = 0
  ): Promise<UserCommentWithPost[]> {
    const response = await fetch(
      `${API_BASE_URL}/api/users/${userId}/comments?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    const data = await this.handleResponse<{ comments: UserCommentWithPost[] }>(response)
    return data.comments || []
  }

  // Posts API
  async getFeed(limit = 50, offset = 0): Promise<FeedResponse> {
    const response = await fetch(`${API_BASE_URL}/api/posts/feed?limit=${limit}&offset=${offset}`, {
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<FeedResponse>(response)
  }

  async getDiscoverPosts(limit = 50, offset = 0): Promise<FeedResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/posts/discover?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<FeedResponse>(response)
  }

  async getTrendingHashtags(
    limit = 5
  ): Promise<{ hashtags: { hashtag: string; count: number }[] }> {
    const response = await fetch(`${API_BASE_URL}/api/posts/trending?limit=${limit}`, {
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<{ hashtags: { hashtag: string; count: number }[] }>(response)
  }

  async searchPosts(query: string, limit = 50, offset = 0): Promise<FeedResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/posts/search?q=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<FeedResponse>(response)
  }

  async searchCommunities(query: string, limit = 50, offset = 0): Promise<CommunitiesResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/communities/search?q=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<CommunitiesResponse>(response)
  }

  async likePost(postId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/like`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async unlikePost(postId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/like`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async createPost(data: CreatePostData): Promise<Post> {
    const response = await fetch(`${API_BASE_URL}/api/posts`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ post: Post }>(response)
    return responseData.post
  }

  async updatePost(postId: number, data: { content: string }): Promise<Post> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ post: Post }>(response)
    return responseData.post
  }

  async deletePost(postId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async createCommunity(data: CreateCommunityData): Promise<Community> {
    const response = await fetch(`${API_BASE_URL}/api/communities`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ community: Community }>(response)
    return responseData.community
  }

  async getCommunities(limit = 50, offset = 0): Promise<CommunitiesResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/communities?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<CommunitiesResponse>(response)
  }

  async getMyCommunities(): Promise<CommunitiesResponse> {
    const response = await fetch(`${API_BASE_URL}/api/communities/me/communities`, {
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<CommunitiesResponse>(response)
  }

  async getCommunityDetails(communityId: number): Promise<Community> {
    const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}`, {
      headers: this.getAuthHeaders(),
    })
    const responseData = await this.handleResponse<{ community: Community }>(response)
    return responseData.community
  }

  async updateCommunity(communityId: number, data: UpdateCommunityData): Promise<Community> {
    const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ community: Community }>(response)
    return responseData.community
  }

  async deleteCommunity(communityId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async joinCommunity(communityId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}/join`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async leaveCommunity(communityId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/communities/${communityId}/leave`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  // Comment API
  async getPostComments(postId: number): Promise<Comment[]> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comments`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ comments: Comment[] }>(response)
    return data.comments || []
  }

  async createComment(postId: number, data: CreateCommentData): Promise<Comment> {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/comments`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ comment: Comment }>(response)
    return responseData.comment
  }

  async updateComment(commentId: number, content: string): Promise<Comment> {
    const response = await fetch(`${API_BASE_URL}/api/comments/${commentId}`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
      body: JSON.stringify({ content }),
    })
    const responseData = await this.handleResponse<{ comment: Comment }>(response)
    return responseData.comment
  }

  async deleteComment(commentId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/comments/${commentId}`, {
      method: "DELETE",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async getCommentReplies(commentId: number): Promise<Comment[]> {
    const response = await fetch(`${API_BASE_URL}/api/comments/${commentId}/replies`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ replies: Comment[] }>(response)
    return data.replies || []
  }

  // Community members API methods
  async getCommunityMembers(
    communityId: number,
    limit = 50,
    offset = 0
  ): Promise<CommunityMembersResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/communities/${communityId}/members?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<CommunityMembersResponse>(response)
  }

  async removeCommunityMember(communityId: number, userId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/communities/${communityId}/members/${userId}`,
      {
        method: "DELETE",
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<void>(response)
  }

  async changeMemberRole(communityId: number, userId: number, roleId: number): Promise<void> {
    const response = await fetch(
      `${API_BASE_URL}/api/communities/${communityId}/members/${userId}/role`,
      {
        method: "PUT",
        headers: this.getAuthHeaders(),
        body: JSON.stringify({ role_id: roleId }),
      }
    )
    return this.handleResponse<void>(response)
  }

  // Community posts API method
  async getCommunityPosts(communityId: number, limit = 50, offset = 0): Promise<FeedResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/posts/community/${communityId}?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<FeedResponse>(response)
  }

  // User API
  async getRecommendations(limit = 5): Promise<RecommendationResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/users/recommendations?limit=${limit}`, {
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<RecommendationResponse>(response)
  }

  // File Upload
  async uploadFile(file: File): Promise<string> {
    const formData = new FormData()
    formData.append("file", file)

    const response = await fetch(`${API_BASE_URL}/api/upload/`, {
      method: "POST",
      body: formData,
    })

    // Handle specific error for upload
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: "An error occurred" }))
      throw new Error(error.message || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data.url
  }

  async generateAvatar(username: string): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/api/upload/generate-avatar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username }),
    })

    const data = await this.handleResponse<{ url: string }>(response)
    return data.url
  }

  // Direct Messages API methods
  async getConversations(limit = 50, offset = 0): Promise<ConversationsResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/messages/conversations?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<ConversationsResponse>(response)
  }

  async getConversationMessages(
    otherUserId: number,
    limit = 50,
    offset = 0
  ): Promise<MessagesResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/messages/conversations/${otherUserId}?limit=${limit}&offset=${offset}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<MessagesResponse>(response)
  }

  async sendMessage(data: SendMessageData): Promise<Message> {
    const response = await fetch(`${API_BASE_URL}/api/messages`, {
      method: "POST",
      headers: this.getAuthHeaders(),
      body: JSON.stringify(data),
    })
    const responseData = await this.handleResponse<{ success: boolean; message: Message }>(response)
    return responseData.message
  }

  async markMessageAsRead(messageId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/messages/${messageId}/read`, {
      method: "PUT",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async getUnreadMessageCount(): Promise<number> {
    const response = await fetch(`${API_BASE_URL}/api/messages/unread-count`, {
      headers: this.getAuthHeaders(),
    })
    const data = await this.handleResponse<{ unread_count: number }>(response)
    return data.unread_count || 0
  }

  // User Search API method
  async searchUsers(query: string, limit = 20, followingOnly = false): Promise<UserSearchResponse> {
    const response = await fetch(
      `${API_BASE_URL}/api/auth/users/search?q=${encodeURIComponent(query)}&limit=${limit}&following_only=${followingOnly}`,
      {
        headers: this.getAuthHeaders(),
      }
    )
    return this.handleResponse<UserSearchResponse>(response)
  }

  // Follow Requests API methods
  async getFollowRequests(): Promise<FollowRequestsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/me/follow-requests`, {
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<FollowRequestsResponse>(response)
  }

  async acceptFollowRequest(followerId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/me/follow-requests/${followerId}/accept`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async rejectFollowRequest(followerId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/me/follow-requests/${followerId}/reject`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }
}

export const api = new ApiClient()

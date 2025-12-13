import type {
  FollowUser,
  LoginResponse,
  Post,
  ProfileData,
  RegisterData,
  UpdateProfileData,
  User,
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

  async followUser(userId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/follow`, {
      method: "POST",
      headers: this.getAuthHeaders(),
    })
    return this.handleResponse<void>(response)
  }

  async unfollowUser(userId: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/api/users/${userId}/unfollow`, {
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

  // TODO: Phase 2 - Posts API
  // async getPosts(): Promise<Post[]> { }
  // async createPost(content: string, image?: string): Promise<Post> { }
  // async likePost(postId: number): Promise<void> { }

  // TODO: Phase 2 - Comments API
  // async getComments(postId: number): Promise<Comment[]> { }
  // async createComment(postId: number, content: string): Promise<Comment> { }

  // TODO: Phase 3 - Communities API
  // async getCommunities(): Promise<Community[]> { }
  // async joinCommunity(communityId: number): Promise<void> { }
}

export const api = new ApiClient()

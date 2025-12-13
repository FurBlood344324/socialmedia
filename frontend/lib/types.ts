// User and Authentication Types
export interface User {
  user_id: number
  username: string
  email: string
  bio?: string
  profile_picture_url?: string
  is_private: boolean
  created_at: string
}

export interface RegisterData {
  username: string
  email: string
  password: string
  bio?: string
  profile_picture_url?: string
  is_private?: boolean
}

export interface LoginResponse {
  token: string
  user: User
}

export interface ApiError {
  message: string
  status?: number
}

// TODO: Phase 2 - Add Post types
export interface Post {
  post_id: number
  user_id: number
  content: string
  image_url?: string
  created_at: string
  likes_count: number
  comments_count: number
  user?: User
}

// TODO: Phase 2 - Add Comment types
export interface Comment {
  comment_id: number
  post_id: number
  user_id: number
  content: string
  created_at: string
}

export interface FollowStats {
  followers_count: number
  following_count: number
  posts_count: number
}

export interface FollowUser {
  user_id: number
  username: string
  profile_picture_url?: string
  bio?: string
  is_following?: boolean
}

export interface ProfileData extends User {
  stats: FollowStats
  is_following?: boolean
  is_own_profile: boolean
}

export interface UpdateProfileData {
  username?: string
  email?: string
  bio?: string
  profile_picture_url?: string
  is_private?: boolean
}

// TODO: Phase 3 - Add Community types
export interface Community {
  community_id: number
  name: string
  description: string
  created_by: number
  member_count: number
  created_at: string
}

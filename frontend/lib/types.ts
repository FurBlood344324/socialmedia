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
  username?: string
  user_profile_picture?: string
  content: string
  media_url?: string
  community_id?: number
  community_name?: string
  created_at: string
  updated_at: string
  like_count: number
  comment_count: number
  liked_by_user: boolean
  engagement_score?: number
  user?: User
}

export interface FeedResponse {
  success: boolean
  posts: Post[]
  limit: number
  offset: number
}

export interface CreatePostData {
  content: string
  media_url?: string
  community_id?: number
}

// TODO: Phase 2 - Add Comment types
export interface Comment {
  id: number
  post_id: number
  user_id: number
  username?: string
  user_profile_picture?: string
  content: string
  parent_comment_id?: number
  created_at: string
  updated_at?: string
  replies?: Comment[]
  reply_count?: number
}

// User comment with associated post data for profile tabs
export interface UserCommentWithPost {
  comment_id: number
  comment_content: string
  comment_created_at: string
  post_id: number
  post_content: string
  media_url?: string
  post_created_at: string
  post_author_id: number
  post_author_username: string
  post_author_profile_picture?: string
  commenter_username: string
  commenter_profile_picture?: string
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
  has_pending_request?: boolean
}

export interface ProfileData extends User {
  stats: FollowStats
  is_following?: boolean
  has_pending_request?: boolean
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
  id: number
  name: string
  description: string
  privacy_id: number // 1=Public, 2=Private
  created_by?: number
  member_count?: number
  created_at: string
  is_member?: boolean
  role_id?: number // 1=Admin, 2=Moderator, 3=Member
}

export interface CreateCommunityData {
  name: string
  description: string
  privacy_id: number
}

export interface CommunitiesResponse {
  communities: Community[]
}

export interface RecommendationResponse {
  success: boolean
  recommendations: Recommendation[]
  count: number
}

export interface Recommendation {
  user_id: number
  suggested_username: string
  mutual_count: number
  post_count: number
  follower_count: number
  recommendation_score: number
}

export interface CreateCommentData {
  content: string
  parent_comment_id?: number
}

export interface CommentsResponse {
  success: boolean
  comments: Comment[]
}

export interface CommunityMember {
  user_id: number
  username: string
  profile_picture_url?: string
  role_id: number // 1=Admin, 2=Moderator, 3=Member
  joined_at: string
}

export interface CommunityMembersResponse {
  members: CommunityMember[]
  total: number
}

export interface UpdateCommunityData {
  name?: string
  description?: string
  privacy_id?: number
}

export interface Message {
  message_id: number
  sender_id: number
  receiver_id: number
  content: string
  media_url?: string
  created_at: string
  is_read?: boolean
}

export interface Conversation {
  other_user: {
    user_id: number
    username: string
    profile_picture_url?: string
  }
  last_message: {
    content: string
    created_at: string
  }
  unread_count: number
}

export interface ConversationsResponse {
  conversations: Conversation[]
  count: number
}

export interface MessagesResponse {
  messages: Message[]
  success: boolean
}

export interface SendMessageData {
  receiver_id: number
  content: string
  media_url?: string
}

export interface FollowRequest {
  follower_id: number
  following_id: number
  status_id: number
  created_at: string
  user_id: number // This comes from the joined User table (the follower)
  username: string
  profile_picture_url?: string
  bio?: string
}

export interface FollowRequestsResponse {
  requests: FollowRequest[]
}

export interface UserSearchResult {
  user_id: number
  username: string
  profile_picture_url?: string
  bio?: string
  is_private: boolean
}

export interface UserSearchResponse {
  users: UserSearchResult[]
  count: number
}

-- ============================================
-- 9. INDEXES
-- ============================================

-- Standard performance indexes
CREATE INDEX idx_users_username ON Users(username);
CREATE INDEX idx_users_email ON Users(email);
CREATE INDEX idx_posts_user_id ON Posts(user_id);
CREATE INDEX idx_posts_community_id ON Posts(community_id);
CREATE INDEX idx_posts_created_at ON Posts(created_at DESC);
CREATE INDEX idx_comments_post_id ON Comments(post_id);
CREATE INDEX idx_comments_user_id ON Comments(user_id);
CREATE INDEX idx_postlikes_post_id ON PostLikes(post_id);
CREATE INDEX idx_follows_follower_id ON Follows(follower_id);
CREATE INDEX idx_follows_following_id ON Follows(following_id);
CREATE INDEX IF NOT EXISTS idx_follows_follower_status ON Follows(follower_id, status_id);
CREATE INDEX IF NOT EXISTS idx_follows_following_status ON Follows(following_id, status_id);
CREATE INDEX idx_messages_sender_id ON Messages(sender_id);
CREATE INDEX idx_messages_receiver_id ON Messages(receiver_id);
CREATE INDEX idx_messages_unread ON Messages(receiver_id) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_posts_user_created ON Posts(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_postlikes_user_id ON PostLikes(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_parent_post ON Comments(parent_comment_id, post_id);
CREATE INDEX IF NOT EXISTS idx_follows_status ON Follows(status_id, following_id);

-- Soft delete indexes (Merged from migrations)
CREATE INDEX IF NOT EXISTS idx_messages_sender_deleted ON Messages(sender_id) WHERE sender_deleted = FALSE;
CREATE INDEX IF NOT EXISTS idx_messages_receiver_deleted ON Messages(receiver_id) WHERE receiver_deleted = FALSE;

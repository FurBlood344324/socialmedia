-- Social Media Database Initialization Script

-- ============================================
-- 1. DROP EXISTING TABLES
-- ============================================
DROP VIEW IF EXISTS advanced_friend_recommendations CASCADE;
DROP VIEW IF EXISTS community_statistics_view CASCADE;
DROP VIEW IF EXISTS active_users_view CASCADE;
DROP VIEW IF EXISTS popular_posts_view CASCADE;
DROP TABLE IF EXISTS Messages CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS PostLikes CASCADE;
DROP TABLE IF EXISTS Posts CASCADE;
DROP TABLE IF EXISTS CommunityMembers CASCADE;
DROP TABLE IF EXISTS Communities CASCADE;
DROP TABLE IF EXISTS Follows CASCADE;
DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS FollowStatus CASCADE;
DROP TABLE IF EXISTS PrivacyTypes CASCADE;
DROP TABLE IF EXISTS Roles CASCADE;

-- ============================================
-- 2. CREATE LOOKUP/REFERENCE TABLES
-- ============================================

CREATE TABLE Roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE PrivacyTypes (
    privacy_id SERIAL PRIMARY KEY,
    privacy_name VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE FollowStatus (
    status_id SERIAL PRIMARY KEY,
    status_name VARCHAR(20) UNIQUE NOT NULL
);

-- ============================================
-- 3. CREATE MAIN ENTITY TABLES
-- ============================================

CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    bio TEXT,
    profile_picture_url TEXT,
    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

CREATE TABLE Communities (
    community_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    creator_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    privacy_id INT REFERENCES PrivacyTypes(privacy_id),
    member_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. CREATE RELATIONSHIP/JUNCTION TABLES
-- ============================================

CREATE TABLE CommunityMembers (
    community_id INT REFERENCES Communities(community_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    role_id INT REFERENCES Roles(role_id),
    joined_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (community_id, user_id)
);

CREATE TABLE Follows (
    follower_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    following_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    status_id INT REFERENCES FollowStatus(status_id),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (follower_id, following_id)
);

-- ============================================
-- 5. CREATE CONTENT TABLES
-- ============================================

CREATE TABLE Posts (
    post_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    community_id INT REFERENCES Communities(community_id) ON DELETE CASCADE ON UPDATE CASCADE,
    content TEXT,
    media_url TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_posts_content_or_media CHECK ((content IS NOT NULL AND content != '') OR (media_url IS NOT NULL AND media_url != ''))
);

CREATE TABLE Comments (
    comment_id SERIAL PRIMARY KEY,
    post_id INT REFERENCES Posts(post_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    content TEXT NOT NULL,
    parent_comment_id INT REFERENCES Comments(comment_id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_comments_min_length CHECK (LENGTH(TRIM(content)) >= 1)
);

CREATE TABLE PostLikes (
    post_id INT REFERENCES Posts(post_id) ON DELETE CASCADE,
    user_id INT REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (post_id, user_id)
);

CREATE TABLE Messages (
    message_id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    receiver_id INT REFERENCES Users(user_id) ON DELETE SET NULL ON UPDATE CASCADE,
    content TEXT,
    media_url TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    sender_deleted BOOLEAN DEFAULT FALSE,
    receiver_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_messages_different_users CHECK (sender_id != receiver_id)
);

-- ============================================
-- 6. FUNCTIONS
-- ============================================

-- Generic function for updating updated_at column
-- Used by: BEFORE UPDATE ON Posts, Users, Comments
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Member Count Update Trigger Function
-- Used by: POST /api/communities/<id>/join, POST /api/communities/<id>/leave
CREATE OR REPLACE FUNCTION update_community_member_count()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE Communities
        SET member_count = member_count + 1
        WHERE community_id = NEW.community_id;
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE Communities
        SET member_count = member_count - 1
        WHERE community_id = OLD.community_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Function: Get friend-of-friend recommendations
-- Used by: GET /api/features/users/advanced-recommendations (Alternative)
CREATE OR REPLACE FUNCTION get_friend_of_friend_recommendations(target_user_id INTEGER)
RETURNS TABLE (
    recommended_user INTEGER,
    username VARCHAR,
    mutual_friends INTEGER,
    connection_strength NUMERIC
) AS $$
DECLARE
    v_accepted_id INT;
BEGIN
    SELECT status_id INTO v_accepted_id FROM FollowStatus WHERE status_name = 'accepted';

    RETURN QUERY
    WITH 
    my_friends AS (
        SELECT following_id AS friend_id
        FROM Follows
        WHERE follower_id = target_user_id
          AND status_id = v_accepted_id
    ),
    friends_of_friends AS (
        SELECT DISTINCT
            f.following_id AS potential_friend,
            mf.friend_id AS mutual_friend
        FROM my_friends mf
        INNER JOIN Follows f ON f.follower_id = mf.friend_id
        WHERE f.status_id = v_accepted_id
          AND f.following_id != target_user_id
          AND f.following_id NOT IN (SELECT friend_id FROM my_friends)
    ),
    mutual_counts AS (
        SELECT 
            potential_friend,
            COUNT(DISTINCT mutual_friend) AS mutual_count
        FROM friends_of_friends
        GROUP BY potential_friend
    ),
    scored_recommendations AS (
        SELECT 
            mc.potential_friend,
            u.username,
            mc.mutual_count,
            (
                mc.mutual_count * 10.0 +
                COALESCE((SELECT COUNT(*) FROM Posts WHERE user_id = mc.potential_friend), 0) * 0.5 +
                COALESCE((SELECT COUNT(*) FROM Follows WHERE following_id = mc.potential_friend AND status_id = v_accepted_id), 0) * 0.1
            ) AS strength
        FROM mutual_counts mc
        INNER JOIN Users u ON u.user_id = mc.potential_friend
    )
    SELECT 
        potential_friend,
        username,
        mutual_count,
        ROUND(strength, 2) AS connection_strength
    FROM scored_recommendations
    ORDER BY strength DESC, mutual_count DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- Message Soft Delete Functions
CREATE OR REPLACE FUNCTION messages_sender_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL THEN
        NEW.sender_deleted := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION messages_receiver_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL THEN
        NEW.receiver_deleted := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- 7. TRIGGERS
-- ============================================

-- Updated At Triggers
CREATE TRIGGER update_users_modtime BEFORE UPDATE ON Users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_posts_modtime BEFORE UPDATE ON Posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_comments_modtime BEFORE UPDATE ON Comments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Community Member Count Trigger
CREATE TRIGGER update_member_count AFTER INSERT OR DELETE ON CommunityMembers FOR EACH ROW EXECUTE FUNCTION update_community_member_count();

-- Message Soft Delete Triggers
-- Used by: DELETE /api/messages/<id> (Note: Requires repository to perform UPDATE instead of DELETE)
CREATE TRIGGER messages_sender_soft_delete_trigger
BEFORE UPDATE OF sender_id ON Messages
FOR EACH ROW
WHEN (NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL)
EXECUTE FUNCTION messages_sender_soft_delete();

CREATE TRIGGER messages_receiver_soft_delete_trigger
BEFORE UPDATE OF receiver_id ON Messages
FOR EACH ROW
WHEN (NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL)
EXECUTE FUNCTION messages_receiver_soft_delete();

-- ============================================
-- 8. VIEWS
-- ============================================

-- Popular Posts View
-- Used by: GET /api/features/posts/popular
CREATE OR REPLACE VIEW popular_posts_view AS
SELECT 
    p.post_id, p.user_id, u.username, u.profile_picture_url,
    p.content, p.media_url, p.community_id, c.name AS community_name,
    p.created_at, p.updated_at,
    COALESCE(like_counts.like_count, 0) AS like_count,
    COALESCE(comment_counts.comment_count, 0) AS comment_count,
    (COALESCE(like_counts.like_count, 0) + (COALESCE(comment_counts.comment_count, 0) * 2)) AS engagement_score,
    (p.created_at > NOW() - INTERVAL '7 days') AS is_recent
FROM Posts p
JOIN Users u ON p.user_id = u.user_id
LEFT JOIN Communities c ON p.community_id = c.community_id
LEFT JOIN (SELECT post_id, COUNT(*) AS like_count FROM PostLikes GROUP BY post_id) like_counts ON p.post_id = like_counts.post_id
LEFT JOIN (SELECT post_id, COUNT(*) AS comment_count FROM Comments GROUP BY post_id) comment_counts ON p.post_id = comment_counts.post_id
ORDER BY engagement_score DESC, p.created_at DESC;

-- Active Users View
-- Used by: GET /api/features/users/active
CREATE OR REPLACE VIEW active_users_view AS
SELECT 
    u.user_id, u.username, u.email, u.profile_picture_url, u.bio, u.created_at AS joined_at,
    COALESCE(post_counts.post_count, 0) AS posts_last_7_days,
    COALESCE(like_counts.like_count, 0) AS likes_last_7_days,
    COALESCE(comment_counts.comment_count, 0) AS comments_last_7_days,
    (COALESCE(post_counts.post_count, 0) + COALESCE(like_counts.like_count, 0) + COALESCE(comment_counts.comment_count, 0)) AS total_activity,
    GREATEST(COALESCE(post_counts.last_post, '1970-01-01'::timestamptz), COALESCE(like_counts.last_like, '1970-01-01'::timestamptz), COALESCE(comment_counts.last_comment, '1970-01-01'::timestamptz)) AS last_activity_at
FROM Users u
LEFT JOIN (SELECT user_id, COUNT(*) AS post_count, MAX(created_at) AS last_post FROM Posts WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY user_id) post_counts ON u.user_id = post_counts.user_id
LEFT JOIN (SELECT user_id, COUNT(*) AS like_count, MAX(created_at) AS last_like FROM PostLikes WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY user_id) like_counts ON u.user_id = like_counts.user_id
LEFT JOIN (SELECT user_id, COUNT(*) AS comment_count, MAX(created_at) AS last_comment FROM Comments WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY user_id) comment_counts ON u.user_id = comment_counts.user_id
WHERE post_counts.post_count > 0 OR like_counts.like_count > 0 OR comment_counts.comment_count > 0
ORDER BY total_activity DESC, last_activity_at DESC;

-- Community Statistics View
-- Used by: GET /api/features/communities/<id>/stats
CREATE OR REPLACE VIEW community_statistics_view AS
SELECT 
    c.community_id, c.name AS community_name, c.description, c.creator_id, creator.username AS creator_username, c.created_at,
    COALESCE(member_counts.total_members, 0) AS total_members,
    COALESCE(member_counts.admin_count, 0) AS admin_count,
    COALESCE(member_counts.moderator_count, 0) AS moderator_count,
    COALESCE(member_counts.regular_member_count, 0) AS regular_member_count,
    COALESCE(post_counts.total_posts, 0) AS total_posts,
    COALESCE(post_counts.posts_last_7_days, 0) AS posts_last_7_days,
    COALESCE(engagement.total_likes, 0) AS total_likes,
    COALESCE(engagement.total_comments, 0) AS total_comments,
    CASE WHEN post_counts.posts_last_7_days > 0 THEN 'active' ELSE 'inactive' END AS activity_level
FROM Communities c
JOIN Users creator ON c.creator_id = creator.user_id
LEFT JOIN (SELECT cm.community_id, COUNT(*) AS total_members, COUNT(*) FILTER (WHERE r.role_name = 'admin') AS admin_count, COUNT(*) FILTER (WHERE r.role_name = 'moderator') AS moderator_count, COUNT(*) FILTER (WHERE r.role_name = 'member') AS regular_member_count FROM CommunityMembers cm LEFT JOIN Roles r ON cm.role_id = r.role_id GROUP BY cm.community_id) member_counts ON c.community_id = member_counts.community_id
LEFT JOIN (SELECT community_id, COUNT(*) AS total_posts, COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '7 days') AS posts_last_7_days FROM Posts GROUP BY community_id) post_counts ON c.community_id = post_counts.community_id
LEFT JOIN (SELECT p.community_id, COUNT(pl.*) AS total_likes, COUNT(DISTINCT co.comment_id) AS total_comments FROM Posts p LEFT JOIN PostLikes pl ON p.post_id = pl.post_id LEFT JOIN Comments co ON p.post_id = co.post_id WHERE p.community_id IS NOT NULL GROUP BY p.community_id) engagement ON c.community_id = engagement.community_id
ORDER BY total_members DESC;

-- View: Advanced friend recommendations
-- Used by: GET /api/features/users/advanced-recommendations
CREATE OR REPLACE VIEW advanced_friend_recommendations AS
WITH user_friends AS (
    SELECT 
        f.follower_id AS user_id,
        f.following_id AS friend_id
    FROM Follows f
    WHERE f.status_id = (SELECT status_id FROM FollowStatus WHERE status_name = 'accepted')
),
friend_suggestions AS (
    SELECT DISTINCT
        uf1.user_id,
        uf2.friend_id AS suggested_friend,
        COUNT(DISTINCT uf1.friend_id) AS mutual_count
    FROM user_friends uf1
    INNER JOIN user_friends uf2 ON uf1.friend_id = uf2.user_id
    WHERE uf2.friend_id != uf1.user_id
      AND NOT EXISTS (
          SELECT 1 FROM user_friends uf3
          WHERE uf3.user_id = uf1.user_id
            AND uf3.friend_id = uf2.friend_id
      )
    GROUP BY uf1.user_id, uf2.friend_id
)
SELECT 
    fs.user_id,
    u.username AS suggested_username,
    fs.mutual_count,
    COALESCE((SELECT COUNT(*) FROM Posts WHERE user_id = fs.suggested_friend), 0) AS post_count,
    COALESCE((SELECT COUNT(*) FROM Follows WHERE following_id = fs.suggested_friend AND status_id = (SELECT status_id FROM FollowStatus WHERE status_name = 'accepted')), 0) AS follower_count,
    (
        fs.mutual_count * 10.0 +
        COALESCE((SELECT COUNT(*) FROM Posts WHERE user_id = fs.suggested_friend), 0) * 0.5 +
        COALESCE((SELECT COUNT(*) FROM Follows WHERE following_id = fs.suggested_friend AND status_id = (SELECT status_id FROM FollowStatus WHERE status_name = 'accepted')), 0) * 0.1
    ) AS recommendation_score
FROM friend_suggestions fs
INNER JOIN Users u ON u.user_id = fs.suggested_friend
ORDER BY fs.user_id, recommendation_score DESC;

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

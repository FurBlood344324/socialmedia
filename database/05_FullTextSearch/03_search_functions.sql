-- Search Functions for Posts and Users
-- These functions provide full-text search with ranking and relevance scoring

\echo 'Creating search functions...'

-- =====================================================
-- Function: search_posts
-- Searches posts by content with relevance ranking
-- =====================================================

CREATE OR REPLACE FUNCTION search_posts(
    search_query TEXT,
    search_language regconfig DEFAULT 'english',
    max_results INT DEFAULT 50
)
RETURNS TABLE (
    post_id INT,
    user_id INT,
    username VARCHAR(50),
    content TEXT,
    media_url TEXT,
    community_id INT,
    community_name VARCHAR(100),
    created_at TIMESTAMP,
    like_count BIGINT,
    comment_count BIGINT,
    relevance_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.post_id,
        p.user_id,
        u.username,
        p.content,
        p.media_url,
        p.community_id,
        c.name AS community_name,
        p.created_at,
        COALESCE(lc.like_count, 0) AS like_count,
        COALESCE(cc.comment_count, 0) AS comment_count,
        ts_rank(p.search_vector, to_tsquery(search_language, search_query)) AS relevance_rank
    FROM Posts p
    JOIN Users u ON p.user_id = u.user_id
    LEFT JOIN Communities c ON p.community_id = c.community_id
    LEFT JOIN (
        SELECT pl.post_id, COUNT(*) AS like_count
        FROM PostLikes pl
        GROUP BY pl.post_id
    ) lc ON p.post_id = lc.post_id
    LEFT JOIN (
        SELECT cm.post_id, COUNT(*) AS comment_count
        FROM Comments cm
        GROUP BY cm.post_id
    ) cc ON p.post_id = cc.post_id
    WHERE p.search_vector @@ to_tsquery(search_language, search_query)
    ORDER BY relevance_rank DESC, p.created_at DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

\echo '✓ search_posts() function created'

-- =====================================================
-- Function: search_posts_simple
-- Simplified version using plainto_tsquery for easier queries
-- =====================================================

CREATE OR REPLACE FUNCTION search_posts_simple(
    search_query TEXT,
    search_language regconfig DEFAULT 'english',
    max_results INT DEFAULT 50
)
RETURNS TABLE (
    post_id INT,
    user_id INT,
    username VARCHAR(50),
    content TEXT,
    media_url TEXT,
    community_id INT,
    community_name VARCHAR(100),
    created_at TIMESTAMP,
    like_count BIGINT,
    comment_count BIGINT,
    relevance_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.post_id,
        p.user_id,
        u.username,
        p.content,
        p.media_url,
        p.community_id,
        c.name AS community_name,
        p.created_at,
        COALESCE(lc.like_count, 0) AS like_count,
        COALESCE(cc.comment_count, 0) AS comment_count,
        ts_rank(p.search_vector, plainto_tsquery(search_language, search_query)) AS relevance_rank
    FROM Posts p
    JOIN Users u ON p.user_id = u.user_id
    LEFT JOIN Communities c ON p.community_id = c.community_id
    LEFT JOIN (
        SELECT pl.post_id, COUNT(*) AS like_count
        FROM PostLikes pl
        GROUP BY pl.post_id
    ) lc ON p.post_id = lc.post_id
    LEFT JOIN (
        SELECT cm.post_id, COUNT(*) AS comment_count
        FROM Comments cm
        GROUP BY cm.post_id
    ) cc ON p.post_id = cc.post_id
    WHERE p.search_vector @@ plainto_tsquery(search_language, search_query)
    ORDER BY relevance_rank DESC, p.created_at DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

\echo '✓ search_posts_simple() function created'

-- =====================================================
-- Function: search_users
-- Searches users by username and bio
-- =====================================================

CREATE OR REPLACE FUNCTION search_users(
    search_query TEXT,
    search_language regconfig DEFAULT 'english',
    max_results INT DEFAULT 50
)
RETURNS TABLE (
    user_id INT,
    username VARCHAR(50),
    email VARCHAR(100),
    bio TEXT,
    profile_picture_url TEXT,
    is_private BOOLEAN,
    created_at TIMESTAMP,
    follower_count BIGINT,
    following_count BIGINT,
    post_count BIGINT,
    relevance_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        u.user_id,
        u.username,
        u.email,
        u.bio,
        u.profile_picture_url,
        u.is_private,
        u.created_at,
        COALESCE(followers.count, 0) AS follower_count,
        COALESCE(following.count, 0) AS following_count,
        COALESCE(posts.count, 0) AS post_count,
        ts_rank(u.search_vector, plainto_tsquery(search_language, search_query)) AS relevance_rank
    FROM Users u
    LEFT JOIN (
        SELECT f.following_id, COUNT(*) AS count
        FROM Follows f
        WHERE f.status_id = (SELECT status_id FROM FollowStatus WHERE status_name = 'accepted')
        GROUP BY f.following_id
    ) followers ON u.user_id = followers.following_id
    LEFT JOIN (
        SELECT f.follower_id, COUNT(*) AS count
        FROM Follows f
        WHERE f.status_id = (SELECT status_id FROM FollowStatus WHERE status_name = 'accepted')
        GROUP BY f.follower_id
    ) following ON u.user_id = following.follower_id
    LEFT JOIN (
        SELECT p.user_id, COUNT(*) AS count
        FROM Posts p
        GROUP BY p.user_id
    ) posts ON u.user_id = posts.user_id
    WHERE u.search_vector @@ plainto_tsquery(search_language, search_query)
    ORDER BY relevance_rank DESC, u.username ASC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

\echo '✓ search_users() function created'

-- =====================================================
-- Function: search_all
-- Combined search across posts and users
-- =====================================================

CREATE OR REPLACE FUNCTION search_all(
    search_query TEXT,
    search_language regconfig DEFAULT 'english'
)
RETURNS TABLE (
    result_type TEXT,
    id INT,
    title TEXT,
    description TEXT,
    created_at TIMESTAMP,
    relevance_rank REAL
) AS $$
BEGIN
    RETURN QUERY
    -- Search posts
    SELECT 
        'post'::TEXT AS result_type,
        p.post_id AS id,
        u.username::TEXT AS title,
        LEFT(p.content, 200) AS description,
        p.created_at,
        ts_rank(p.search_vector, plainto_tsquery(search_language, search_query)) AS relevance_rank
    FROM Posts p
    JOIN Users u ON p.user_id = u.user_id
    WHERE p.search_vector @@ plainto_tsquery(search_language, search_query)
    
    UNION ALL
    
    -- Search users
    SELECT 
        'user'::TEXT AS result_type,
        u.user_id AS id,
        u.username::TEXT AS title,
        COALESCE(u.bio, 'No bio') AS description,
        u.created_at,
        ts_rank(u.search_vector, plainto_tsquery(search_language, search_query)) AS relevance_rank
    FROM Users u
    WHERE u.search_vector @@ plainto_tsquery(search_language, search_query)
    
    ORDER BY relevance_rank DESC, created_at DESC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;

\echo '✓ search_all() function created'

\echo ''
\echo 'Search functions created successfully!'
\echo ''
\echo 'Available functions:'
\echo '  - search_posts(query, language, limit)'
\echo '  - search_posts_simple(query, language, limit)'
\echo '  - search_users(query, language, limit)'
\echo '  - search_all(query, language)'

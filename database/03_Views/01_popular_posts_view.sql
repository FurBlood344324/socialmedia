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

-- Active Users View
-- Used by: GET /api/features/users/active
CREATE OR REPLACE VIEW active_users_view AS
SELECT 
    u.user_id, u.username, u.email, u.profile_picture_url, u.bio, u.created_at AS joined_at,
    COALESCE(post_counts.post_count, 0) AS posts_last_7_days,
    COALESCE(like_counts.like_count, 0) AS likes_last_7_days,
    COALESCE(comment_counts.comment_count, 0) AS comments_last_7_days,
    (COALESCE(post_counts.post_count, 0) + COALESCE(like_counts.like_count, 0) + COALESCE(comment_counts.comment_count, 0)) AS total_activity,
    GREATEST(COALESCE(post_counts.last_post, '1970-01-01'::timestamp), COALESCE(like_counts.last_like, '1970-01-01'::timestamp), COALESCE(comment_counts.last_comment, '1970-01-01'::timestamp)) AS last_activity_at
FROM Users u
LEFT JOIN (SELECT user_id, COUNT(*) AS post_count, MAX(created_at) AS last_post FROM Posts WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY user_id) post_counts ON u.user_id = post_counts.user_id
LEFT JOIN (SELECT user_id, COUNT(*) AS like_count, MAX(created_at) AS last_like FROM PostLikes WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY user_id) like_counts ON u.user_id = like_counts.user_id
LEFT JOIN (SELECT user_id, COUNT(*) AS comment_count, MAX(created_at) AS last_comment FROM Comments WHERE created_at > NOW() - INTERVAL '7 days' GROUP BY user_id) comment_counts ON u.user_id = comment_counts.user_id
WHERE post_counts.post_count > 0 OR like_counts.like_count > 0 OR comment_counts.comment_count > 0
ORDER BY total_activity DESC, last_activity_at DESC;

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

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

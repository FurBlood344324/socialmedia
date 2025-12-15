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

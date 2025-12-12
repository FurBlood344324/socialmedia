# Database Views Documentation

This document describes the database views implemented for frequently used complex queries in the Social Media application.

## Overview

The application uses PostgreSQL views to simplify and optimize:

1. **User feeds** - Personalized post feeds from followed users
2. **Popular content** - Trending posts based on engagement
3. **User activity** - Track active users and their engagement
4. **Community statistics** - Comprehensive community analytics

## Views Overview

### 1. user_feed_view

**Purpose**: Get personalized feed of posts from users that the viewing user follows.

**Key Features**:

- Shows posts only from accepted follows
- Includes engagement metrics (like count, comment count)
- Pre-joined with user and community data
- Optimized with indexes on Follows table

**Columns**:

- `post_id` - Post identifier
- `user_id` - Post author ID
- `username` - Post author username
- `profile_picture_url` - Author's profile picture
- `content` - Post content
- `media_url` - Attached media URL
- `community_id` - Community ID (if posted in community)
- `community_name` - Community name
- `created_at` - Post creation timestamp
- `updated_at` - Last update timestamp
- `like_count` - Number of likes
- `comment_count` - Number of comments
- `viewing_user_id` - The user whose feed this is (follower_id)

**Example Usage**:

```sql
-- Get feed for user with ID 1
SELECT * FROM user_feed_view
WHERE viewing_user_id = 1
ORDER BY created_at DESC
LIMIT 20;

-- Get feed with posts that have comments
SELECT * FROM user_feed_view
WHERE viewing_user_id = 1 AND comment_count > 0
ORDER BY created_at DESC;
```

**Performance Notes**:

- Indexes created on `Follows(follower_id, status_id)` and `Follows(following_id, status_id)`
- Pre-aggregated like and comment counts
- Use `LIMIT` to restrict results for pagination

---

### 2. popular_posts_view

**Purpose**: Show trending/popular posts ordered by engagement score.

**Key Features**:

- Weighted engagement score (likes + comments × 2)
- Recency indicator for posts from last 7 days
- Includes all engagement metrics
- Useful for "Discover" or "Trending" pages

**Columns**:

- `post_id` - Post identifier
- `user_id` - Post author ID
- `username` - Post author username
- `profile_picture_url` - Author's profile picture
- `content` - Post content
- `media_url` - Attached media URL
- `community_id` - Community ID
- `community_name` - Community name
- `created_at` - Post creation timestamp
- `updated_at` - Last update timestamp
- `like_count` - Number of likes
- `comment_count` - Number of comments
- `engagement_score` - Calculated: likes + (comments × 2)
- `is_recent` - Boolean: post from last 7 days

**Example Usage**:

```sql
-- Get top 20 most popular posts
SELECT * FROM popular_posts_view
LIMIT 20;

-- Get popular recent posts only
SELECT * FROM popular_posts_view
WHERE is_recent = true
LIMIT 20;

-- Get highly engaged posts (10+ likes OR 5+ comments)
SELECT * FROM popular_posts_view
WHERE like_count >= 10 OR comment_count >= 5
ORDER BY engagement_score DESC
LIMIT 20;

-- Get popular posts from a specific community
SELECT * FROM popular_posts_view
WHERE community_id = 5
LIMIT 20;
```

**Engagement Score Formula**:

```
engagement_score = like_count + (comment_count × 2)
```

Comments are weighted 2x because they represent deeper engagement.

---

### 3. active_users_view

**Purpose**: Track users who have been active in the last 7 days.

**Key Features**:

- Activity includes: posts, likes, comments
- Separate counters for each activity type
- Total activity score
- Last activity timestamp
- Only shows users with activity > 0

**Columns**:

- `user_id` - User identifier
- `username` - Username
- `email` - User email
- `profile_picture_url` - Profile picture URL
- `bio` - User bio
- `joined_at` - Account creation date
- `posts_last_7_days` - Posts created in last 7 days
- `likes_last_7_days` - Likes given in last 7 days
- `comments_last_7_days` - Comments made in last 7 days
- `total_activity` - Sum of all activity types
- `last_activity_at` - Most recent activity timestamp

**Example Usage**:

```sql
-- Get all active users
SELECT * FROM active_users_view
ORDER BY total_activity DESC;

-- Get top 10 most active users
SELECT * FROM active_users_view
LIMIT 10;

-- Get users who posted at least 5 times
SELECT * FROM active_users_view
WHERE posts_last_7_days >= 5;

-- Get users active today
SELECT * FROM active_users_view
WHERE last_activity_at > CURRENT_DATE;

-- Get posting-focused users
SELECT * FROM active_users_view
WHERE posts_last_7_days > likes_last_7_days
ORDER BY posts_last_7_days DESC;
```

**Activity Score Calculation**:

```
total_activity = posts_last_7_days + likes_last_7_days + comments_last_7_days
```

---

### 4. community_statistics_view

**Purpose**: Comprehensive analytics for all communities.

**Key Features**:

- Member counts by role (admin, moderator, member)
- Post counts (total, last 7 days, last 30 days)
- Engagement metrics (likes, comments, averages)
- Activity level classification
- Last post timestamp

**Columns**:

- `community_id` - Community identifier
- `community_name` - Community name
- `description` - Community description
- `creator_id` - Creator user ID
- `creator_username` - Creator username
- `created_at` - Community creation date
- `total_members` - Total member count
- `admin_count` - Number of admins
- `moderator_count` - Number of moderators
- `regular_member_count` - Number of regular members
- `total_posts` - All-time post count
- `posts_last_7_days` - Posts in last 7 days
- `posts_last_30_days` - Posts in last 30 days
- `total_likes` - Total likes on all posts
- `total_comments` - Total comments on all posts
- `avg_likes_per_post` - Average likes per post
- `avg_comments_per_post` - Average comments per post
- `activity_level` - 'active' | 'moderate' | 'inactive'
- `last_post_at` - Timestamp of most recent post

**Activity Level Classification**:

- **active**: Has posts in last 7 days
- **moderate**: Has posts in last 30 days (but not last 7)
- **inactive**: No posts in last 30 days

**Example Usage**:

```sql
-- Get all community statistics
SELECT * FROM community_statistics_view;

-- Get top 10 communities by members
SELECT * FROM community_statistics_view
ORDER BY total_members DESC
LIMIT 10;

-- Get only active communities
SELECT * FROM community_statistics_view
WHERE activity_level = 'active'
ORDER BY posts_last_7_days DESC;

-- Get communities with high engagement
SELECT * FROM community_statistics_view
WHERE avg_likes_per_post > 10
ORDER BY avg_likes_per_post DESC;

-- Get growing communities (many recent posts)
SELECT * FROM community_statistics_view
WHERE posts_last_7_days > 5
ORDER BY posts_last_7_days DESC;

-- Community health report
SELECT
    community_name,
    total_members,
    posts_last_7_days,
    activity_level,
    ROUND((posts_last_7_days::numeric / NULLIF(total_members, 0) * 100), 2) AS engagement_rate
FROM community_statistics_view
WHERE total_members > 10
ORDER BY engagement_rate DESC;
```

## Installation

### Using the Setup Script

```bash
# From the database directory
psql -U your_user -d your_database -f setup_views.sql
```

### Manual Installation

```bash
# Create views individually
psql -U your_user -d your_database -f 04_Views/01_user_feed_view.sql
psql -U your_user -d your_database -f 04_Views/02_popular_posts_view.sql
psql -U your_user -d your_database -f 04_Views/03_active_users_view.sql
psql -U your_user -d your_database -f 04_Views/04_community_statistics_view.sql
```

## Testing

```bash
# Run all view tests
psql -U your_user -d your_database -f test_views.sql
```

## Performance Considerations

### Indexes Created

- `idx_follows_follower_status` on Follows(follower_id, status_id)
- `idx_follows_following_status` on Follows(following_id, status_id)

### Optimization Tips

1. **Use LIMIT for pagination**:

```sql
SELECT * FROM popular_posts_view LIMIT 20 OFFSET 0;
```

2. **Filter early in queries**:

```sql
-- Good: Filter on indexed columns first
SELECT * FROM user_feed_view WHERE viewing_user_id = 1 LIMIT 20;

-- Avoid: Scanning entire view then filtering
SELECT * FROM user_feed_view WHERE content LIKE '%search%';
```

3. **Materialized Views for Heavy Queries**:
   If `community_statistics_view` becomes slow with many communities:

```sql
CREATE MATERIALIZED VIEW community_statistics_materialized AS
SELECT * FROM community_statistics_view;

-- Refresh periodically
REFRESH MATERIALIZED VIEW community_statistics_materialized;
```

4. **Add WHERE clauses before ordering**:

```sql
-- More efficient
SELECT * FROM popular_posts_view
WHERE is_recent = true
ORDER BY engagement_score DESC
LIMIT 10;
```

## Maintenance

### Refreshing Views

Regular views automatically reflect current data. No refresh needed.

### Dropping Views

```sql
-- Drop a specific view
DROP VIEW IF EXISTS user_feed_view;

-- Drop all views
DROP VIEW IF EXISTS user_feed_view CASCADE;
DROP VIEW IF EXISTS popular_posts_view CASCADE;
DROP VIEW IF EXISTS active_users_view CASCADE;
DROP VIEW IF EXISTS community_statistics_view CASCADE;
```

### Checking View Definitions

```sql
-- List all views
SELECT table_name
FROM information_schema.views
WHERE table_schema = 'public';

-- Get view definition
\d+ user_feed_view
```

## Application Integration

### Python/Flask Example

```python
from sqlalchemy import text
from api.extensions import db

# Get user feed
def get_user_feed(user_id, limit=20, offset=0):
    query = text("""
        SELECT * FROM user_feed_view
        WHERE viewing_user_id = :user_id
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = db.session.execute(query, {
        "user_id": user_id,
        "limit": limit,
        "offset": offset
    })
    return [dict(row) for row in result]

# Get popular posts
def get_popular_posts(limit=20):
    query = text("""
        SELECT * FROM popular_posts_view
        WHERE is_recent = true
        LIMIT :limit
    """)
    result = db.session.execute(query, {"limit": limit})
    return [dict(row) for row in result]

# Get active users
def get_active_users(limit=10):
    query = text("SELECT * FROM active_users_view LIMIT :limit")
    result = db.session.execute(query, {"limit": limit})
    return [dict(row) for row in result]

# Get community stats
def get_community_statistics(community_id=None):
    if community_id:
        query = text("""
            SELECT * FROM community_statistics_view
            WHERE community_id = :community_id
        """)
        result = db.session.execute(query, {"community_id": community_id})
        return dict(result.fetchone())
    else:
        query = text("SELECT * FROM community_statistics_view")
        result = db.session.execute(query)
        return [dict(row) for row in result]
```

## Troubleshooting

### Issue: View returns no data

```sql
-- Check if underlying tables have data
SELECT COUNT(*) FROM Follows WHERE status_id = (
    SELECT status_id FROM FollowStatus WHERE status_name = 'accepted'
);
SELECT COUNT(*) FROM Posts;
SELECT COUNT(*) FROM Users;
```

### Issue: Slow query performance

```sql
-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM user_feed_view WHERE viewing_user_id = 1 LIMIT 20;

-- Check if indexes exist
\di idx_follows_follower_status
\di idx_follows_following_status
```

### Issue: View definition errors

```sql
-- Check view status
SELECT * FROM pg_views WHERE viewname = 'user_feed_view';

-- Recreate view
DROP VIEW user_feed_view CASCADE;
\i 04_Views/01_user_feed_view.sql
```

## Best Practices

1. **Always use LIMIT** when querying views to avoid loading excessive data
2. **Filter by indexed columns** (user_id, community_id) when possible
3. **Use views in application code** instead of complex JOIN queries
4. **Monitor query performance** with EXPLAIN ANALYZE
5. **Consider materialized views** for expensive aggregations
6. **Update views** when underlying schema changes

## Future Enhancements

Potential additions:

- [ ] Materialized view for community_statistics_view
- [ ] View for user recommendations based on interests
- [ ] View for trending hashtags/topics
- [ ] View for user engagement history
- [ ] View for content moderation queue
- [ ] View for notification aggregations

## References

- [PostgreSQL Views Documentation](https://www.postgresql.org/docs/current/sql-createview.html)
- [Materialized Views](https://www.postgresql.org/docs/current/sql-creatematerializedview.html)
- [View Performance Optimization](https://www.postgresql.org/docs/current/rules-views.html)

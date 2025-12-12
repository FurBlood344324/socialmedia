-- Create GIN Indexes for Full-Text Search
-- GIN (Generalized Inverted Index) provides optimal performance for full-text search

\echo 'Creating GIN indexes for full-text search...'

-- =====================================================
-- Create GIN index on Posts.search_vector
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_posts_search_vector 
ON Posts USING GIN(search_vector);

\echo '✓ GIN index created on Posts.search_vector'

-- =====================================================
-- Create GIN index on Users.search_vector
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_users_search_vector 
ON Users USING GIN(search_vector);

\echo '✓ GIN index created on Users.search_vector'

-- =====================================================
-- Create additional indexes for hybrid searches
-- =====================================================

-- Index for searching posts by user
CREATE INDEX IF NOT EXISTS idx_posts_user_id_created 
ON Posts(user_id, created_at DESC);

-- Index for searching posts by community
CREATE INDEX IF NOT EXISTS idx_posts_community_id_created 
ON Posts(community_id, created_at DESC);

\echo '✓ Additional supporting indexes created'

-- =====================================================
-- Analyze tables for query optimization
-- =====================================================

ANALYZE Posts;
ANALYZE Users;

\echo ''
\echo 'GIN indexes created successfully!'
\echo 'Search queries will now be significantly faster'

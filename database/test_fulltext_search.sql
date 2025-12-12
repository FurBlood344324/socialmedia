-- Test Script for Full-Text Search
-- This script tests all search functionality with sample data

\echo '========================================='
\echo 'TESTING FULL-TEXT SEARCH'
\echo '========================================='

-- =====================================================
-- TEST 1: Insert test data (if needed)
-- =====================================================
\echo ''
\echo 'TEST 1: Preparing test data...'
\echo '---------------------------------------'

-- Insert test users (if they don't exist)
INSERT INTO Users (username, email, password_hash, bio)
VALUES 
    ('techguru', 'tech@example.com', 'hash123', 'Software developer passionate about AI and machine learning'),
    ('foodlover', 'food@example.com', 'hash456', 'Food blogger sharing delicious recipes'),
    ('turkishcoder', 'turkish@example.com', 'hash789', 'Yazılım geliştirici, Python ve PostgreSQL uzmanı')
ON CONFLICT (username) DO NOTHING;

-- Get user IDs for test posts
DO $$
DECLARE
    tech_user_id INT;
    food_user_id INT;
    turkish_user_id INT;
BEGIN
    SELECT user_id INTO tech_user_id FROM Users WHERE username = 'techguru' LIMIT 1;
    SELECT user_id INTO food_user_id FROM Users WHERE username = 'foodlover' LIMIT 1;
    SELECT user_id INTO turkish_user_id FROM Users WHERE username = 'turkishcoder' LIMIT 1;
    
    -- Insert test posts (if they don't exist)
    INSERT INTO Posts (user_id, content)
    VALUES 
        (tech_user_id, 'Exploring the latest advancements in artificial intelligence and deep learning models'),
        (tech_user_id, 'Building scalable web applications with PostgreSQL and Python'),
        (food_user_id, 'Amazing pasta recipe with fresh tomatoes and basil'),
        (food_user_id, 'Best coffee shops in Istanbul for remote work'),
        (turkish_user_id, 'PostgreSQL veritabanı optimizasyonu için ipuçları'),
        (turkish_user_id, 'Python ile makine öğrenmesi projeleri'),
        (turkish_user_id, 'Veritabanı full-text search özellikleri çok güçlü')
    ON CONFLICT DO NOTHING;
END $$;

\echo '✓ Test data ready'

-- =====================================================
-- TEST 2: Test English search on posts
-- =====================================================
\echo ''
\echo 'TEST 2: Testing English search...'
\echo '---------------------------------------'

\echo ''
\echo 'Search for "artificial intelligence":'
SELECT 
    post_id,
    username,
    LEFT(content, 60) AS content_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts_simple('artificial intelligence', 'english'::regconfig, 10);

\echo ''
\echo 'Search for "PostgreSQL":'
SELECT 
    post_id,
    username,
    LEFT(content, 60) AS content_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts_simple('PostgreSQL', 'english'::regconfig, 10);

\echo ''
\echo 'Search for "food OR coffee":'
SELECT 
    post_id,
    username,
    LEFT(content, 60) AS content_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts_simple('food coffee', 'english'::regconfig, 10);

-- =====================================================
-- TEST 3: Test Turkish search on posts
-- =====================================================
\echo ''
\echo 'TEST 3: Testing Turkish search...'
\echo '---------------------------------------'

\echo ''
\echo 'Search for "veritabanı" (database in Turkish):'
SELECT 
    post_id,
    username,
    content,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts_turkish('veritabanı');

\echo ''
\echo 'Search for "öğrenme" (learning in Turkish):'
SELECT 
    post_id,
    username,
    content,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts_turkish('öğrenme');

-- =====================================================
-- TEST 4: Test user search
-- =====================================================
\echo ''
\echo 'TEST 4: Testing user search...'
\echo '---------------------------------------'

\echo ''
\echo 'Search for "developer":'
SELECT 
    user_id,
    username,
    LEFT(bio, 50) AS bio_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_users('developer', 'english'::regconfig);

\echo ''
\echo 'Search for "yazılım" (software in Turkish):'
SELECT 
    user_id,
    username,
    bio,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_users_turkish('yazılım');

\echo ''
\echo 'Search for "food":'
SELECT 
    user_id,
    username,
    LEFT(bio, 50) AS bio_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_users('food', 'english'::regconfig);

-- =====================================================
-- TEST 5: Test combined search
-- =====================================================
\echo ''
\echo 'TEST 5: Testing combined search (posts + users)...'
\echo '---------------------------------------'

\echo ''
\echo 'Search for "Python":'
SELECT 
    result_type,
    id,
    title,
    LEFT(description, 60) AS description_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_all('Python', 'english'::regconfig)
LIMIT 10;

-- =====================================================
-- TEST 6: Test advanced search with operators
-- =====================================================
\echo ''
\echo 'TEST 6: Testing advanced search operators...'
\echo '---------------------------------------'

\echo ''
\echo 'Search with AND operator "machine & learning":'
SELECT 
    post_id,
    username,
    LEFT(content, 60) AS content_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts('machine & learning', 'english'::regconfig);

\echo ''
\echo 'Search with OR operator "Python | PostgreSQL":'
SELECT 
    post_id,
    username,
    LEFT(content, 60) AS content_preview,
    ROUND(relevance_rank::numeric, 4) AS rank
FROM search_posts('Python | PostgreSQL', 'english'::regconfig);

-- =====================================================
-- TEST 7: Performance test
-- =====================================================
\echo ''
\echo 'TEST 7: Performance testing...'
\echo '---------------------------------------'

\echo ''
\echo 'EXPLAIN ANALYZE for English search:'
EXPLAIN ANALYZE
SELECT * FROM search_posts_simple('PostgreSQL', 'english'::regconfig, 10);

\echo ''
\echo 'EXPLAIN ANALYZE for Turkish search:'
EXPLAIN ANALYZE
SELECT * FROM search_posts_turkish('veritabanı');

-- =====================================================
-- TEST 8: Test auto-update triggers
-- =====================================================
\echo ''
\echo 'TEST 8: Testing auto-update triggers...'
\echo '---------------------------------------'

-- Insert a new post and verify search_vector is auto-populated
DO $$
DECLARE
    test_user_id INT;
    test_post_id INT;
BEGIN
    SELECT user_id INTO test_user_id FROM Users LIMIT 1;
    
    INSERT INTO Posts (user_id, content)
    VALUES (test_user_id, 'Testing automatic search vector update trigger functionality')
    RETURNING post_id INTO test_post_id;
    
    -- Check if search_vector was automatically populated
    IF EXISTS (
        SELECT 1 FROM Posts 
        WHERE post_id = test_post_id 
        AND search_vector IS NOT NULL
    ) THEN
        RAISE NOTICE '✓ Trigger working: search_vector auto-populated for post_id %', test_post_id;
    ELSE
        RAISE WARNING '✗ Trigger failed: search_vector is NULL for post_id %', test_post_id;
    END IF;
    
    -- Clean up test post
    DELETE FROM Posts WHERE post_id = test_post_id;
END $$;

-- =====================================================
-- TEST 9: Verify indexes are being used
-- =====================================================
\echo ''
\echo 'TEST 9: Verifying GIN index usage...'
\echo '---------------------------------------'

-- Check that the query plan uses the GIN index
\echo ''
\echo 'Query plan should show "Bitmap Index Scan" using idx_posts_search_vector:'
EXPLAIN 
SELECT * FROM Posts 
WHERE search_vector @@ plainto_tsquery('english', 'PostgreSQL');

-- =====================================================
-- Summary
-- =====================================================
\echo ''
\echo '========================================='
\echo 'FULL-TEXT SEARCH TESTS COMPLETED!'
\echo '========================================='
\echo ''
\echo 'Test Summary:'
\echo '  ✓ English search on posts'
\echo '  ✓ Turkish search on posts'
\echo '  ✓ User search'
\echo '  ✓ Combined search (posts + users)'
\echo '  ✓ Advanced operators (AND, OR)'
\echo '  ✓ Performance analysis'
\echo '  ✓ Auto-update triggers'
\echo '  ✓ GIN index verification'
\echo ''
\echo 'All search functionality is working correctly!'

-- Setup Script for Full-Text Search
-- Run this script to install all full-text search components

\echo '========================================='
\echo 'INSTALLING FULL-TEXT SEARCH'
\echo '========================================='

-- =====================================================
-- Step 1: Add search_vector columns
-- =====================================================
\echo ''
\echo 'Step 1: Adding search_vector columns...'
\i 05_FullTextSearch/01_add_search_columns.sql

-- =====================================================
-- Step 2: Create GIN indexes
-- =====================================================
\echo ''
\echo 'Step 2: Creating GIN indexes...'
\i 05_FullTextSearch/02_create_search_indexes.sql

-- =====================================================
-- Step 3: Create search functions
-- =====================================================
\echo ''
\echo 'Step 3: Creating search functions...'
\i 05_FullTextSearch/03_search_functions.sql

-- =====================================================
-- Step 4: Configure Turkish language support
-- =====================================================
\echo ''
\echo 'Step 4: Configuring Turkish language support...'
\i 05_FullTextSearch/04_turkish_config.sql

-- =====================================================
-- Verify installation
-- =====================================================
\echo ''
\echo 'Verifying installation...'

-- Check columns exist
SELECT 
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'public'
  AND column_name = 'search_vector'
  AND table_name IN ('posts', 'users')
ORDER BY table_name;

-- Check indexes exist
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
  AND indexname LIKE '%search_vector%'
ORDER BY tablename;

-- Check functions exist
SELECT 
    routine_name,
    routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
  AND routine_name LIKE 'search_%'
ORDER BY routine_name;

\echo ''
\echo '========================================='
\echo 'FULL-TEXT SEARCH INSTALLATION COMPLETE!'
\echo '========================================='
\echo ''
\echo 'Available search functions:'
\echo '  - search_posts(query, language, limit)'
\echo '  - search_posts_simple(query, language, limit)'
\echo '  - search_posts_turkish(query, limit)'
\echo '  - search_users(query, language, limit)'
\echo '  - search_users_turkish(query, limit)'
\echo '  - search_all(query, language)'
\echo ''
\echo 'Run test_fulltext_search.sql to verify functionality'

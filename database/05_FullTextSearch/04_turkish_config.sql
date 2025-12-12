-- Turkish Language Configuration for Full-Text Search
-- Configures Turkish stemming, stop-words, and language-specific search

\echo 'Setting up Turkish language configuration...'

-- =====================================================
-- Install Turkish text search configuration
-- Note: PostgreSQL comes with basic 'turkish' config
-- =====================================================

-- Check if turkish configuration exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_ts_config WHERE cfgname = 'turkish'
    ) THEN
        RAISE NOTICE 'Turkish configuration not found. Using simple configuration.';
        
        -- Create a simple Turkish configuration based on simple
        CREATE TEXT SEARCH CONFIGURATION turkish_simple ( COPY = simple );
    ELSE
        RAISE NOTICE 'Turkish configuration already exists.';
    END IF;
END $$;

\echo '✓ Turkish configuration verified'

-- =====================================================
-- Create custom Turkish stop-words dictionary
-- =====================================================

-- Check if turkish_stopwords dictionary exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_ts_dict WHERE dictname = 'turkish_stopwords'
    ) THEN
        CREATE TEXT SEARCH DICTIONARY turkish_stopwords (
            TEMPLATE = simple,
            STOPWORDS = turkish
        );
        RAISE NOTICE 'Turkish stop-words dictionary created';
    ELSE
        RAISE NOTICE 'Turkish stop-words dictionary already exists';
    END IF;
END $$;

\echo '✓ Turkish stop-words dictionary configured'

-- =====================================================
-- Create bilingual (Turkish + English) configuration
-- Useful for mixed-language content
-- =====================================================

-- Check if bilingual config exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_ts_config WHERE cfgname = 'bilingual_tr_en'
    ) THEN
        CREATE TEXT SEARCH CONFIGURATION bilingual_tr_en ( COPY = english );
        
        -- Add Turkish stemming to bilingual config
        ALTER TEXT SEARCH CONFIGURATION bilingual_tr_en
            ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
            WITH turkish_stem, english_stem;
            
        RAISE NOTICE 'Bilingual (Turkish + English) configuration created';
    ELSE
        RAISE NOTICE 'Bilingual configuration already exists';
    END IF;
END $$;

\echo '✓ Bilingual (Turkish + English) configuration ready'

-- =====================================================
-- Update trigger functions to support Turkish
-- =====================================================

-- Update Posts search_vector function to support Turkish
CREATE OR REPLACE FUNCTION posts_search_vector_update_turkish()
RETURNS TRIGGER AS $$
BEGIN
    -- Use bilingual config for better Turkish + English support
    NEW.search_vector := 
        setweight(to_tsvector('bilingual_tr_en', COALESCE(NEW.content, '')), 'A');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Update Users search_vector function to support Turkish
CREATE OR REPLACE FUNCTION users_search_vector_update_turkish()
RETURNS TRIGGER AS $$
BEGIN
    -- Use bilingual config for better Turkish + English support
    NEW.search_vector := 
        setweight(to_tsvector('bilingual_tr_en', COALESCE(NEW.username, '')), 'A') ||
        setweight(to_tsvector('bilingual_tr_en', COALESCE(NEW.bio, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

\echo '✓ Turkish-aware trigger functions created'

-- =====================================================
-- Create Turkish-specific search functions
-- =====================================================

-- Search posts in Turkish
CREATE OR REPLACE FUNCTION search_posts_turkish(
    search_query TEXT,
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
    -- Use 'turkish' configuration for better Turkish stemming
    RETURN QUERY
    SELECT * FROM search_posts_simple(search_query, 'turkish'::regconfig, max_results);
END;
$$ LANGUAGE plpgsql;

-- Search users in Turkish
CREATE OR REPLACE FUNCTION search_users_turkish(
    search_query TEXT,
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
    -- Use 'turkish' configuration for better Turkish stemming
    RETURN QUERY
    SELECT * FROM search_users(search_query, 'turkish'::regconfig, max_results);
END;
$$ LANGUAGE plpgsql;

\echo '✓ Turkish-specific search functions created'

-- =====================================================
-- Optional: Switch existing data to use Turkish config
-- Uncomment these lines to update all existing records
-- =====================================================

-- Update all Posts to use bilingual config
-- UPDATE Posts 
-- SET search_vector = to_tsvector('bilingual_tr_en', COALESCE(content, ''));

-- Update all Users to use bilingual config
-- UPDATE Users 
-- SET search_vector = 
--     setweight(to_tsvector('bilingual_tr_en', COALESCE(username, '')), 'A') ||
--     setweight(to_tsvector('bilingual_tr_en', COALESCE(bio, '')), 'B');

\echo ''
\echo 'Turkish language configuration completed!'
\echo ''
\echo 'Available configurations:'
\echo '  - turkish: Pure Turkish configuration'
\echo '  - bilingual_tr_en: Turkish + English hybrid'
\echo ''
\echo 'Turkish-specific functions:'
\echo '  - search_posts_turkish(query, limit)'
\echo '  - search_users_turkish(query, limit)'
\echo ''
\echo 'Usage examples:'
\echo "  SELECT * FROM search_posts_turkish('güzel');"
\echo "  SELECT * FROM search_posts_simple('beautiful', 'english'::regconfig);"
\echo "  SELECT * FROM search_posts_simple('yazılım', 'turkish'::regconfig);"

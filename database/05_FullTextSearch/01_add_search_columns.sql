-- Add Full-Text Search Columns
-- This script adds tsvector columns to Posts and Users tables for full-text search

\echo 'Adding search_vector columns...'

-- =====================================================
-- Add search_vector column to Posts table
-- =====================================================

-- Add the tsvector column
ALTER TABLE Posts 
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Create function to update Posts search_vector
CREATE OR REPLACE FUNCTION posts_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'A');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update search_vector on INSERT or UPDATE
DROP TRIGGER IF EXISTS posts_search_vector_trigger ON Posts;
CREATE TRIGGER posts_search_vector_trigger
    BEFORE INSERT OR UPDATE OF content
    ON Posts
    FOR EACH ROW
    EXECUTE FUNCTION posts_search_vector_update();

-- Update existing Posts records
UPDATE Posts 
SET search_vector = to_tsvector('english', COALESCE(content, ''))
WHERE search_vector IS NULL;

\echo '✓ Posts search_vector column added'

-- =====================================================
-- Add search_vector column to Users table
-- =====================================================

-- Add the tsvector column
ALTER TABLE Users 
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Create function to update Users search_vector
CREATE OR REPLACE FUNCTION users_search_vector_update()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.username, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.bio, '')), 'B');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update search_vector on INSERT or UPDATE
DROP TRIGGER IF EXISTS users_search_vector_trigger ON Users;
CREATE TRIGGER users_search_vector_trigger
    BEFORE INSERT OR UPDATE OF username, bio
    ON Users
    FOR EACH ROW
    EXECUTE FUNCTION users_search_vector_update();

-- Update existing Users records
UPDATE Users 
SET search_vector = 
    setweight(to_tsvector('english', COALESCE(username, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(bio, '')), 'B')
WHERE search_vector IS NULL;

\echo '✓ Users search_vector column added'

\echo ''
\echo 'Search columns added successfully!'
\echo 'Next step: Create GIN indexes for optimal performance'

# Full-Text Search Documentation

Complete guide to using PostgreSQL full-text search in the Social Media application.

## Overview

Full-text search allows users to search for posts and users using natural language queries. The system supports:
- **English search** with stemming and stop-words
- **Turkish search** with language-specific processing
- **Bilingual support** for mixed Turkish/English content
- **Relevance ranking** for better search results
- **Auto-updating** search indexes via triggers

## Features

### Search Capabilities
- Search posts by content
- Search users by username and bio
- Combined search across posts and users
- Advanced operators (AND, OR, NOT)
- Phrase search
- Relevance scoring
- Language-specific stemming

### Performance
- GIN (Generalized Inverted Index) for fast lookups
- Automatic index updates via triggers
- Sub-millisecond search times
- Optimized for large datasets

## Database Schema

### Added Columns

**Posts table:**
```sql
search_vector tsvector  -- Auto-populated from content
```

**Users table:**
```sql
search_vector tsvector  -- Auto-populated from username and bio
```

### Indexes

```sql
-- GIN indexes for fast full-text search
idx_posts_search_vector ON Posts USING GIN(search_vector)
idx_users_search_vector ON Users USING GIN(search_vector)

-- Supporting indexes
idx_posts_user_id_created ON Posts(user_id, created_at DESC)
idx_posts_community_id_created ON Posts(community_id, created_at DESC)
```

### Automatic Updates

Triggers automatically update `search_vector` when data changes:
- **posts_search_vector_trigger**: Updates when post content changes
- **users_search_vector_trigger**: Updates when username or bio changes

## Search Functions

### 1. search_posts_simple()

Search posts using plain text query (recommended for most cases).

**Signature:**
```sql
search_posts_simple(
    search_query TEXT,
    search_language regconfig DEFAULT 'english',
    max_results INT DEFAULT 50
)
```

**Returns:**
- post_id, user_id, username, content, media_url
- community_id, community_name, created_at
- like_count, comment_count
- relevance_rank (0.0 to 1.0)

**Examples:**
```sql
-- Search for "artificial intelligence"
SELECT * FROM search_posts_simple('artificial intelligence');

-- Search with language specified
SELECT * FROM search_posts_simple('PostgreSQL', 'english'::regconfig, 20);

-- Search multiple words (OR logic)
SELECT * FROM search_posts_simple('machine learning AI');
```

### 2. search_posts()

Advanced search with operator support (AND, OR, NOT).

**Signature:**
```sql
search_posts(
    search_query TEXT,
    search_language regconfig DEFAULT 'english',
    max_results INT DEFAULT 50
)
```

**Examples:**
```sql
-- AND operator: both words must exist
SELECT * FROM search_posts('machine & learning');

-- OR operator: either word can exist
SELECT * FROM search_posts('Python | PostgreSQL');

-- NOT operator: exclude words
SELECT * FROM search_posts('database & !MongoDB');

-- Phrase search
SELECT * FROM search_posts('machine <-> learning');  -- adjacent words
```

### 3. search_posts_turkish()

Search posts in Turkish with proper stemming.

**Signature:**
```sql
search_posts_turkish(
    search_query TEXT,
    max_results INT DEFAULT 50
)
```

**Examples:**
```sql
-- Turkish word search
SELECT * FROM search_posts_turkish('veritabanı');

-- Multiple Turkish words
SELECT * FROM search_posts_turkish('yazılım geliştirme');
```

### 4. search_users()

Search users by username and bio.

**Signature:**
```sql
search_users(
    search_query TEXT,
    search_language regconfig DEFAULT 'english',
    max_results INT DEFAULT 50
)
```

**Returns:**
- user_id, username, email, bio
- profile_picture_url, is_private, created_at
- follower_count, following_count, post_count
- relevance_rank

**Examples:**
```sql
-- Find developers
SELECT * FROM search_users('developer');

-- Find food bloggers
SELECT * FROM search_users('food blogger');

-- Turkish search
SELECT * FROM search_users('yazılımcı', 'turkish'::regconfig);
```

### 5. search_users_turkish()

Turkish-specific user search.

**Examples:**
```sql
SELECT * FROM search_users_turkish('yazılım');
SELECT * FROM search_users_turkish('yemek blogger');
```

### 6. search_all()

Combined search across both posts and users.

**Signature:**
```sql
search_all(
    search_query TEXT,
    search_language regconfig DEFAULT 'english'
)
```

**Returns:**
- result_type ('post' or 'user')
- id (post_id or user_id)
- title (username)
- description (content preview or bio)
- created_at, relevance_rank

**Examples:**
```sql
-- Search everything
SELECT * FROM search_all('Python programming');

-- Filter by type
SELECT * FROM search_all('developer') WHERE result_type = 'user';
```

## Language Support

### English Configuration

Default language with:
- English stemming (running → run, computers → computer)
- Stop-word removal (the, is, at, etc.)
- Case-insensitive search

**Usage:**
```sql
SELECT * FROM search_posts_simple('query', 'english'::regconfig);
```

### Turkish Configuration

Turkish-specific features:
- Turkish stemming (çalışıyor → çalış)
- Turkish stop-words (ve, veya, için, etc.)
- Turkish character support (ı, ğ, ş, ç, ö, ü)

**Usage:**
```sql
SELECT * FROM search_posts_turkish('veritabanı');
-- or
SELECT * FROM search_posts_simple('veritabanı', 'turkish'::regconfig);
```

### Bilingual Support

For mixed Turkish/English content:
```sql
-- Uses bilingual_tr_en configuration
-- Applies both Turkish and English stemming
```

## Application Integration

### Python/Flask Example

```python
from sqlalchemy import text
from api.extensions import db

def search_posts_api(query, language='english', limit=20):
    """Search posts with full-text search."""
    sql = text("""
        SELECT * FROM search_posts_simple(:query, :language::regconfig, :limit)
    """)
    result = db.session.execute(sql, {
        'query': query,
        'language': language,
        'limit': limit
    })
    return [dict(row) for row in result]

def search_users_api(query, language='english', limit=20):
    """Search users with full-text search."""
    sql = text("""
        SELECT * FROM search_users(:query, :language::regconfig, :limit)
    """)
    result = db.session.execute(sql, {
        'query': query,
        'language': language,
        'limit': limit
    })
    return [dict(row) for row in result]

def search_all_api(query, language='english'):
    """Combined search across posts and users."""
    sql = text("""
        SELECT * FROM search_all(:query, :language::regconfig)
    """)
    result = db.session.execute(sql, {
        'query': query,
        'language': language
    })
    return [dict(row) for row in result]
```

### REST API Endpoints

```python
from flask import Blueprint, request, jsonify

search_bp = Blueprint('search', __name__, url_prefix='/api/search')

@search_bp.route('/posts', methods=['GET'])
def search_posts_endpoint():
    query = request.args.get('q', '')
    language = request.args.get('lang', 'english')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = search_posts_api(query, language, limit)
    return jsonify({'results': results, 'count': len(results)})

@search_bp.route('/users', methods=['GET'])
def search_users_endpoint():
    query = request.args.get('q', '')
    language = request.args.get('lang', 'english')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = search_users_api(query, language, limit)
    return jsonify({'results': results, 'count': len(results)})

@search_bp.route('/all', methods=['GET'])
def search_all_endpoint():
    query = request.args.get('q', '')
    language = request.args.get('lang', 'english')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = search_all_api(query, language)
    
    # Group by type
    posts = [r for r in results if r['result_type'] == 'post']
    users = [r for r in results if r['result_type'] == 'user']
    
    return jsonify({
        'posts': posts,
        'users': users,
        'total': len(results)
    })
```

## Usage Examples

### Simple Searches

```sql
-- Find posts about AI
SELECT post_id, username, content, relevance_rank 
FROM search_posts_simple('artificial intelligence')
LIMIT 10;

-- Find food bloggers
SELECT username, bio, follower_count
FROM search_users('food blogger')
WHERE is_private = false;

-- Turkish post search
SELECT * FROM search_posts_turkish('makine öğrenmesi');
```

### Advanced Searches

```sql
-- Posts with Python OR PostgreSQL
SELECT * FROM search_posts('Python | PostgreSQL');

-- Posts with Python AND database (both required)
SELECT * FROM search_posts('Python & database');

-- Posts about Python but NOT Django
SELECT * FROM search_posts('Python & !Django');

-- Exact phrase search
SELECT * FROM search_posts('machine <-> learning');
```

### Filtered Searches

```sql
-- Search posts from a specific user
SELECT p.* FROM search_posts_simple('PostgreSQL') p
WHERE p.user_id = 5;

-- Search posts in a specific community
SELECT p.* FROM search_posts_simple('tutorial') p
WHERE p.community_id = 10;

-- Search recent posts only
SELECT p.* FROM search_posts_simple('news') p
WHERE p.created_at > NOW() - INTERVAL '7 days';

-- Search popular posts
SELECT p.* FROM search_posts_simple('technology') p
WHERE p.like_count > 10
ORDER BY p.like_count DESC;
```

### Combined Searches

```sql
-- Search everything for "Python"
SELECT 
    result_type,
    title,
    description,
    relevance_rank
FROM search_all('Python programming')
ORDER BY relevance_rank DESC
LIMIT 20;
```

## Performance Optimization

### Query Performance

```sql
-- Check query execution plan
EXPLAIN ANALYZE
SELECT * FROM search_posts_simple('PostgreSQL');

-- Should show "Bitmap Index Scan" using GIN index
-- Typical execution time: < 1ms for small datasets
```

### Index Maintenance

```sql
-- Rebuild indexes if needed
REINDEX INDEX idx_posts_search_vector;
REINDEX INDEX idx_users_search_vector;

-- Update statistics
ANALYZE Posts;
ANALYZE Users;

-- Check index size
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_indexes
WHERE indexname LIKE '%search_vector%';
```

### Best Practices

1. **Use LIMIT**: Always limit results to prevent large result sets
   ```sql
   SELECT * FROM search_posts_simple('query') LIMIT 20;
   ```

2. **Cache frequently searched terms**: Store popular searches in application cache

3. **Add filters early**: Filter by user_id, community_id, date before searching
   ```sql
   -- Good: Filter after search function
   SELECT * FROM search_posts_simple('query') 
   WHERE created_at > NOW() - INTERVAL '30 days';
   ```

4. **Monitor slow queries**: Use PostgreSQL logging to track performance
   ```sql
   SET log_min_duration_statement = 100;  -- Log queries > 100ms
   ```

## Troubleshooting

### No Results Found

```sql
-- Check if search_vector is populated
SELECT post_id, search_vector FROM Posts LIMIT 5;

-- Manually update if needed
UPDATE Posts SET content = content;  -- Triggers update
```

### Slow Queries

```sql
-- Check if GIN index is being used
EXPLAIN SELECT * FROM Posts 
WHERE search_vector @@ plainto_tsquery('english', 'test');

-- Should show "Bitmap Index Scan" not "Seq Scan"
```

### Turkish Characters Not Working

```sql
-- Verify Turkish configuration exists
SELECT cfgname FROM pg_ts_config WHERE cfgname = 'turkish';

-- Use Turkish-specific functions
SELECT * FROM search_posts_turkish('içerik');
```

### Trigger Not Firing

```sql
-- Check if triggers exist
SELECT tgname, tgenabled FROM pg_trigger 
WHERE tgrelid = 'Posts'::regclass;

-- Recreate triggers if needed
\i 05_FullTextSearch/01_add_search_columns.sql
```

## Advanced Topics

### Custom Stop Words

```sql
-- Add custom stop words
ALTER TEXT SEARCH DICTIONARY turkish_stopwords 
    STOPWORDS = '/path/to/custom_stopwords.txt';
```

### Weighting

Search vectors use weights (A, B, C, D) for importance:
- **A (highest)**: Post content, username
- **B**: User bio
- **C, D**: Less important fields

```sql
-- Example: Username is weighted higher than bio
setweight(to_tsvector('english', username), 'A') ||
setweight(to_tsvector('english', bio), 'B')
```

### Highlighting Results

```sql
-- Highlight matching words in results
SELECT 
    post_id,
    ts_headline('english', content, plainto_tsquery('english', 'PostgreSQL'),
        'MaxWords=50, MinWords=20') AS highlighted_content
FROM Posts
WHERE search_vector @@ plainto_tsquery('english', 'PostgreSQL');
```

## Maintenance

### Regular Tasks

```bash
# Rebuild indexes monthly
psql -d socialmedia -c "REINDEX INDEX CONCURRENTLY idx_posts_search_vector;"
psql -d socialmedia -c "REINDEX INDEX CONCURRENTLY idx_users_search_vector;"

# Update statistics weekly
psql -d socialmedia -c "ANALYZE Posts;"
psql -d socialmedia -c "ANALYZE Users;"
```

### Monitoring

```sql
-- Check search performance
SELECT 
    COUNT(*) as search_count,
    AVG(execution_time) as avg_time
FROM pg_stat_statements
WHERE query LIKE '%search_posts%';

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as times_used,
    idx_tup_read as tuples_read
FROM pg_stat_user_indexes
WHERE indexname LIKE '%search_vector%';
```

## References

- [PostgreSQL Full-Text Search Documentation](https://www.postgresql.org/docs/current/textsearch.html)
- [GIN Indexes](https://www.postgresql.org/docs/current/gin.html)
- [Text Search Functions](https://www.postgresql.org/docs/current/functions-textsearch.html)
- [Turkish Text Search](https://www.postgresql.org/docs/current/textsearch-dictionaries.html)

## Files Structure

```
database/
├── 05_FullTextSearch/
│   ├── 01_add_search_columns.sql      # Add tsvector columns and triggers
│   ├── 02_create_search_indexes.sql   # Create GIN indexes
│   ├── 03_search_functions.sql        # Search function definitions
│   └── 04_turkish_config.sql          # Turkish language configuration
├── setup_fulltext_search.sql          # Complete installation script
├── test_fulltext_search.sql           # Test suite
└── FULLTEXT_SEARCH_README.md          # This file
```

## Installation

```bash
# Install all components
cd database
psql -U postgres -d social_media_db -f setup_fulltext_search.sql

# Run tests
psql -U postgres -d social_media_db -f test_fulltext_search.sql
```

## Summary

Full-text search is now fully operational with:
- ✅ English and Turkish language support
- ✅ Auto-updating search indexes
- ✅ Sub-millisecond search performance
- ✅ 6 search functions for different use cases
- ✅ Complete API integration examples
- ✅ Comprehensive test suite

Search is ready for production use!

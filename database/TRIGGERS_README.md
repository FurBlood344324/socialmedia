# Database Triggers Documentation

This document describes the database triggers implemented for automatic operations in the Social Media application.

## Overview

The application uses PostgreSQL triggers to automate:

1. **Timestamp management** - Auto-update `updated_at` columns
2. **Audit logging** - Track user deletions for compliance
3. **Cascade cleanup** - Clean up related data when posts are deleted

## Trigger Categories

### 1. Updated_at Triggers

**Purpose**: Automatically update the `updated_at` timestamp whenever a record is modified.

**Tables Affected**:

- `Users`
- `Posts`
- `Comments`

**Trigger Function**:

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Triggers**:

- `update_users_updated_at` - BEFORE UPDATE on Users
- `update_posts_updated_at` - BEFORE UPDATE on Posts
- `update_comments_updated_at` - BEFORE UPDATE on Comments

**Example**:

```sql
-- Update a user
UPDATE Users SET bio = 'New bio' WHERE user_id = 1;
-- updated_at is automatically set to CURRENT_TIMESTAMP
```

### 2. Audit Log Triggers

**Purpose**: Log deletions for compliance, auditing, and potential data recovery.

**Audit Log Table Structure**:

```sql
CREATE TABLE AuditLog (
    audit_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    user_id INT,
    username VARCHAR(50),
    email VARCHAR(100),
    record_data JSONB,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_by INT,
    reason TEXT
);
```

**Trigger Function**:

```sql
CREATE OR REPLACE FUNCTION log_user_deletion()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO AuditLog (
        table_name,
        operation,
        user_id,
        username,
        email,
        record_data,
        deleted_at
    ) VALUES (
        'Users',
        'DELETE',
        OLD.user_id,
        OLD.username,
        OLD.email,
        jsonb_build_object(
            'user_id', OLD.user_id,
            'username', OLD.username,
            'email', OLD.email,
            'bio', OLD.bio,
            -- ... all user fields
        ),
        CURRENT_TIMESTAMP
    );
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
```

**Triggers**:

- `audit_user_deletion` - BEFORE DELETE on Users

**Example**:

```sql
-- Delete a user
DELETE FROM Users WHERE user_id = 123;
-- Automatically creates an audit log entry with full user data
```

**Querying Audit Logs**:

```sql
-- View all user deletions
SELECT * FROM AuditLog WHERE table_name = 'Users' ORDER BY deleted_at DESC;

-- View specific user's deletion record
SELECT * FROM AuditLog WHERE user_id = 123;

-- Extract data from JSONB
SELECT
    username,
    record_data->>'email' AS email,
    record_data->>'bio' AS bio,
    deleted_at
FROM AuditLog
WHERE table_name = 'Users';
```

### 3. Cascade Cleanup Triggers

**Purpose**: Automatically clean up related data (likes, comments) when posts are deleted.

**Note**: While PostgreSQL's `ON DELETE CASCADE` handles foreign key relationships, these triggers provide additional control and logging.

**Trigger Functions**:

```sql
-- Cleanup post likes
CREATE OR REPLACE FUNCTION cleanup_post_likes()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM PostLikes WHERE post_id = OLD.post_id;
    RAISE NOTICE 'Cleaned up likes for post_id: %', OLD.post_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Cleanup post comments
CREATE OR REPLACE FUNCTION cleanup_post_comments()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM Comments WHERE post_id = OLD.post_id;
    RAISE NOTICE 'Cleaned up comments for post_id: %', OLD.post_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
```

**Triggers**:

- `cleanup_likes_on_post_delete` - BEFORE DELETE on Posts
- `cleanup_comments_on_post_delete` - BEFORE DELETE on Posts

**Example**:

```sql
-- Delete a post
DELETE FROM Posts WHERE post_id = 456;
-- Automatically deletes:
-- - All likes (PostLikes) for this post
-- - All comments (Comments) for this post
```

## Installation

### Option 1: Using the Setup Script

```bash
# From the database directory
psql -U your_user -d your_database -f setup_triggers.sql
```

### Option 2: Manual Installation

```bash
# Step 1: Add updated_at columns
psql -U your_user -d your_database -f 02_Migrations/01_add_updated_at_columns.sql

# Step 2: Create audit log table
psql -U your_user -d your_database -f 02_Migrations/02_create_audit_log_table.sql

# Step 3: Create updated_at triggers
psql -U your_user -d your_database -f 03_Triggers/01_updated_at_triggers.sql

# Step 4: Create audit log triggers
psql -U your_user -d your_database -f 03_Triggers/02_audit_log_triggers.sql

# Step 5: Create cascade cleanup triggers
psql -U your_user -d your_database -f 03_Triggers/03_cascade_cleanup_triggers.sql
```

## Testing

### Database-level Testing

```bash
# Run SQL tests
psql -U your_user -d your_database -f test_triggers.sql
```

### Application-level Testing

```bash
# Run Python tests
cd backend
python -m pytest tests/test_triggers.py -v
```

## Verifying Triggers

```sql
-- List all triggers in the database
SELECT
    trigger_name,
    event_object_table AS table_name,
    action_timing AS timing,
    event_manipulation AS event
FROM information_schema.triggers
WHERE trigger_schema = 'public'
ORDER BY event_object_table, trigger_name;
```

Expected output:

```
       trigger_name        | table_name |  timing  | event
---------------------------+------------+----------+--------
 cleanup_comments_on_...   | posts      | BEFORE   | DELETE
 cleanup_likes_on_post...  | posts      | BEFORE   | DELETE
 update_posts_updated_at   | posts      | BEFORE   | UPDATE
 update_comments_updated.. | comments   | BEFORE   | UPDATE
 audit_user_deletion       | users      | BEFORE   | DELETE
 update_users_updated_at   | users      | BEFORE   | UPDATE
```

## Trigger Execution Order

When multiple triggers exist on the same table and event:

1. Triggers execute in **alphabetical order by name**
2. BEFORE triggers execute before the operation
3. AFTER triggers execute after the operation

Example for DELETE on Posts:

1. `cleanup_comments_on_post_delete` (BEFORE DELETE)
2. `cleanup_likes_on_post_delete` (BEFORE DELETE)
3. Actual DELETE operation
4. Foreign key cascades (if any)

## Performance Considerations

1. **Updated_at triggers**: Minimal overhead (~0.1ms per update)
2. **Audit log triggers**: Small overhead for INSERT operation (~1ms)
3. **Cascade cleanup triggers**: Can be expensive for posts with many likes/comments

**Optimization tips**:

- Ensure indexes exist on foreign keys (`post_id`, `user_id`)
- Consider batch operations for bulk deletions
- Monitor audit log table size and archive old records

## Maintenance

### Disabling Triggers Temporarily

```sql
-- Disable a specific trigger
ALTER TABLE Users DISABLE TRIGGER update_users_updated_at;

-- Re-enable
ALTER TABLE Users ENABLE TRIGGER update_users_updated_at;

-- Disable all triggers on a table
ALTER TABLE Users DISABLE TRIGGER ALL;
```

### Dropping Triggers

```sql
-- Drop a specific trigger
DROP TRIGGER IF EXISTS update_users_updated_at ON Users;

-- Drop the function (will cascade to all triggers using it)
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
```

### Audit Log Maintenance

```sql
-- Archive old audit logs (older than 1 year)
DELETE FROM AuditLog WHERE deleted_at < NOW() - INTERVAL '1 year';

-- Or move to archive table
INSERT INTO AuditLog_Archive
SELECT * FROM AuditLog WHERE deleted_at < NOW() - INTERVAL '1 year';

DELETE FROM AuditLog WHERE deleted_at < NOW() - INTERVAL '1 year';
```

## Learning Notes

### Key Concepts Demonstrated

1. **BEFORE vs AFTER Triggers**

   - BEFORE: Can modify NEW values, prevent operation
   - AFTER: Cannot modify values, used for logging

2. **NEW and OLD Keywords**

   - NEW: Contains new values (INSERT, UPDATE)
   - OLD: Contains old values (UPDATE, DELETE)

3. **Trigger Functions**

   - Must return a trigger type
   - Can access TG_OP, TG_TABLE_NAME
   - Use RETURN NEW/OLD/NULL

4. **JSONB for Flexible Logging**
   - Store complete record snapshots
   - Query with -> and ->> operators

## Troubleshooting

### Issue: Trigger not firing

```sql
-- Check if trigger exists
SELECT * FROM pg_trigger WHERE tgname = 'update_users_updated_at';

-- Check trigger status
SELECT tgname, tgenabled FROM pg_trigger WHERE tgname = 'update_users_updated_at';
-- tgenabled: 'O' = enabled, 'D' = disabled
```

### Issue: Performance degradation

```sql
-- Check execution time
EXPLAIN ANALYZE DELETE FROM Posts WHERE post_id = 123;

-- Monitor trigger execution
SET log_statement = 'all';
SET log_duration = on;
```

### Issue: Audit log growing too large

```sql
-- Check table size
SELECT pg_size_pretty(pg_total_relation_size('AuditLog'));

-- Implement partitioning or regular archiving
```

## Future Enhancements

Potential additions:

- [ ] Denormalized counters with triggers (like_count, comment_count in Posts table)
- [ ] Audit logging for Posts and Comments
- [ ] Soft delete triggers (mark as deleted instead of actual deletion)
- [ ] Notification triggers (trigger events for real-time notifications)
- [ ] Data validation triggers (enforce business rules at database level)

## References

- [PostgreSQL Trigger Documentation](https://www.postgresql.org/docs/current/triggers.html)
- [PL/pgSQL Functions](https://www.postgresql.org/docs/current/plpgsql.html)
- [JSONB Operations](https://www.postgresql.org/docs/current/functions-json.html)

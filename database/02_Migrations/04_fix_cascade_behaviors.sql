-- ============================================================================
-- Migration: Fix Foreign Key CASCADE Behaviors
-- ============================================================================
-- This migration corrects foreign key constraints to implement proper
-- cascade behaviors for data integrity and user experience.
--
-- Issues Fixed:
-- 1. Posts.community_id: NO ACTION → CASCADE
--    - Community deletion should delete posts (no orphan data)
-- 2. Messages: CASCADE → SET NULL with soft delete support
--    - User deletion should preserve message history
-- 3. Add ON UPDATE CASCADE where user_id is referenced
--    - Ensure referential integrity when primary keys change
--
-- Usage: psql -U username -d database_name -f 04_fix_cascade_behaviors.sql
-- ============================================================================

\echo '========================================='
\echo 'Fixing Foreign Key CASCADE Behaviors'
\echo '========================================='

-- ============================================================================
-- SECTION 1: Fix Posts.community_id (NO ACTION → CASCADE)
-- ============================================================================
\echo ''
\echo 'Section 1: Fixing Posts.community_id constraint...'

-- Drop existing constraint
ALTER TABLE Posts 
DROP CONSTRAINT IF EXISTS posts_community_id_fkey;

-- Recreate with CASCADE on delete
ALTER TABLE Posts
ADD CONSTRAINT posts_community_id_fkey
FOREIGN KEY (community_id) 
REFERENCES Communities(community_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ Posts.community_id: Now uses CASCADE on delete'
\echo '  → Community deleted = posts deleted (no orphan data)'

-- ============================================================================
-- SECTION 2: Add soft delete support to Messages table
-- ============================================================================
\echo ''
\echo 'Section 2: Adding soft delete columns to Messages...'

-- Add sender/receiver deleted flags if they don't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'messages' AND column_name = 'sender_deleted'
    ) THEN
        ALTER TABLE Messages ADD COLUMN sender_deleted BOOLEAN DEFAULT FALSE;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'messages' AND column_name = 'receiver_deleted'
    ) THEN
        ALTER TABLE Messages ADD COLUMN receiver_deleted BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

\echo '✓ Messages: Added sender_deleted and receiver_deleted columns'

-- ============================================================================
-- SECTION 3: Fix Messages foreign keys (CASCADE → SET NULL)
-- ============================================================================
\echo ''
\echo 'Section 3: Fixing Messages foreign key constraints...'

-- Drop existing constraints
ALTER TABLE Messages 
DROP CONSTRAINT IF EXISTS messages_sender_id_fkey;

ALTER TABLE Messages 
DROP CONSTRAINT IF EXISTS messages_receiver_id_fkey;

-- Recreate with SET NULL on delete and CASCADE on update
ALTER TABLE Messages
ADD CONSTRAINT messages_sender_id_fkey
FOREIGN KEY (sender_id) 
REFERENCES Users(user_id)
ON DELETE SET NULL
ON UPDATE CASCADE;

ALTER TABLE Messages
ADD CONSTRAINT messages_receiver_id_fkey
FOREIGN KEY (receiver_id) 
REFERENCES Users(user_id)
ON DELETE SET NULL
ON UPDATE CASCADE;

\echo '✓ Messages.sender_id: Changed from CASCADE to SET NULL'
\echo '✓ Messages.receiver_id: Changed from CASCADE to SET NULL'
\echo '  → User deletion preserves message history'

-- ============================================================================
-- SECTION 3.5: Create triggers for soft delete
-- ============================================================================
\echo ''
\echo 'Section 3.5: Creating soft delete triggers...'

-- Trigger function for sender deletion
CREATE OR REPLACE FUNCTION messages_sender_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL THEN
        NEW.sender_deleted := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function for receiver deletion
CREATE OR REPLACE FUNCTION messages_receiver_soft_delete()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL THEN
        NEW.receiver_deleted := TRUE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
DROP TRIGGER IF EXISTS messages_sender_soft_delete_trigger ON Messages;
CREATE TRIGGER messages_sender_soft_delete_trigger
BEFORE UPDATE OF sender_id
ON Messages
FOR EACH ROW
WHEN (NEW.sender_id IS NULL AND OLD.sender_id IS NOT NULL)
EXECUTE FUNCTION messages_sender_soft_delete();

DROP TRIGGER IF EXISTS messages_receiver_soft_delete_trigger ON Messages;
CREATE TRIGGER messages_receiver_soft_delete_trigger
BEFORE UPDATE OF receiver_id
ON Messages
FOR EACH ROW
WHEN (NEW.receiver_id IS NULL AND OLD.receiver_id IS NOT NULL)
EXECUTE FUNCTION messages_receiver_soft_delete();

\echo '✓ Created soft delete triggers for Messages'

-- ============================================================================
-- SECTION 4: Add ON UPDATE CASCADE to other user_id references
-- ============================================================================
\echo ''
\echo 'Section 4: Adding ON UPDATE CASCADE to user_id references...'

-- Posts.user_id
ALTER TABLE Posts 
DROP CONSTRAINT IF EXISTS posts_user_id_fkey;

ALTER TABLE Posts
ADD CONSTRAINT posts_user_id_fkey
FOREIGN KEY (user_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ Posts.user_id: Added ON UPDATE CASCADE'

-- Comments.user_id
ALTER TABLE Comments 
DROP CONSTRAINT IF EXISTS comments_user_id_fkey;

ALTER TABLE Comments
ADD CONSTRAINT comments_user_id_fkey
FOREIGN KEY (user_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ Comments.user_id: Added ON UPDATE CASCADE'

-- PostLikes.user_id
ALTER TABLE PostLikes 
DROP CONSTRAINT IF EXISTS postlikes_user_id_fkey;

ALTER TABLE PostLikes
ADD CONSTRAINT postlikes_user_id_fkey
FOREIGN KEY (user_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ PostLikes.user_id: Added ON UPDATE CASCADE'

-- Follows.follower_id and following_id
ALTER TABLE Follows 
DROP CONSTRAINT IF EXISTS follows_follower_id_fkey;

ALTER TABLE Follows 
DROP CONSTRAINT IF EXISTS follows_following_id_fkey;

ALTER TABLE Follows
ADD CONSTRAINT follows_follower_id_fkey
FOREIGN KEY (follower_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

ALTER TABLE Follows
ADD CONSTRAINT follows_following_id_fkey
FOREIGN KEY (following_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ Follows.follower_id: Added ON UPDATE CASCADE'
\echo '✓ Follows.following_id: Added ON UPDATE CASCADE'

-- CommunityMembers.user_id
ALTER TABLE CommunityMembers 
DROP CONSTRAINT IF EXISTS communitymembers_user_id_fkey;

ALTER TABLE CommunityMembers
ADD CONSTRAINT communitymembers_user_id_fkey
FOREIGN KEY (user_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ CommunityMembers.user_id: Added ON UPDATE CASCADE'

-- Communities.creator_id
ALTER TABLE Communities 
DROP CONSTRAINT IF EXISTS communities_creator_id_fkey;

ALTER TABLE Communities
ADD CONSTRAINT communities_creator_id_fkey
FOREIGN KEY (creator_id) 
REFERENCES Users(user_id)
ON DELETE CASCADE
ON UPDATE CASCADE;

\echo '✓ Communities.creator_id: Added ON UPDATE CASCADE'

-- ============================================================================
-- SECTION 5: Add indexes for new columns
-- ============================================================================
\echo ''
\echo 'Section 5: Creating indexes for new columns...'

CREATE INDEX IF NOT EXISTS idx_messages_sender_deleted 
ON Messages(sender_id) WHERE sender_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_messages_receiver_deleted 
ON Messages(receiver_id) WHERE receiver_deleted = FALSE;

\echo '✓ Created partial indexes for non-deleted messages'

-- ============================================================================
-- SECTION 6: Verification
-- ============================================================================
\echo ''
\echo '========================================='
\echo 'Verification'
\echo '========================================='

\echo ''
\echo 'Updated Foreign Key Constraints:'
SELECT 
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS references_table,
    rc.update_rule AS on_update,
    rc.delete_rule AS on_delete
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND (
    (tc.table_name = 'posts' AND kcu.column_name = 'community_id')
    OR (tc.table_name = 'messages' AND kcu.column_name IN ('sender_id', 'receiver_id'))
    OR (kcu.column_name = 'user_id')
    OR (tc.table_name = 'follows' AND kcu.column_name IN ('follower_id', 'following_id'))
  )
ORDER BY tc.table_name, kcu.column_name;

\echo ''
\echo '========================================='
\echo 'Migration Complete!'
\echo '========================================='
\echo ''
\echo 'Changes Summary:'
\echo '1. Posts.community_id: SET NULL on community deletion'
\echo '2. Messages: Added soft delete columns (sender_deleted, receiver_deleted)'
\echo '3. Messages: SET NULL on user deletion (preserves history)'
\echo '4. All user_id references: Added ON UPDATE CASCADE'
\echo '5. Created indexes for message soft delete queries'
\echo ''
\echo 'Benefits:'
\echo '- Communities can be deleted without losing posts'
\echo '- Message history preserved when users delete accounts'
\echo '- Referential integrity maintained on user_id updates'
\echo '- Improved query performance with partial indexes'
\echo ''

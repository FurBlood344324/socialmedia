-- ============================================================================
-- Test Suite: Foreign Key CASCADE Behaviors
-- ============================================================================
-- Tests to verify all foreign key cascade behaviors work correctly
-- ============================================================================

\echo '========================================='
\echo 'Testing Foreign Key CASCADE Behaviors'
\echo '========================================='

-- ============================================================================
-- TEST 1: Posts.community_id CASCADE behavior
-- ============================================================================
\echo ''
\echo 'TEST 1: Posts deleted when community deleted (CASCADE)'

DO $$
DECLARE
    test_user_id INTEGER;
    test_community_id INTEGER;
    test_post_id INTEGER;
    post_count INTEGER;
BEGIN
    -- Setup: Create test data
    INSERT INTO Users (username, email, password_hash)
    VALUES ('cascade_test_user', 'cascade@test.com', 'hash')
    RETURNING user_id INTO test_user_id;
    
    INSERT INTO Communities (name, description, creator_id)
    VALUES ('Test Community CASCADE', 'Will be deleted', test_user_id)
    RETURNING community_id INTO test_community_id;
    
    INSERT INTO Posts (user_id, community_id, content)
    VALUES (test_user_id, test_community_id, 'Post in community')
    RETURNING post_id INTO test_post_id;
    
    -- Verify post exists
    SELECT COUNT(*) INTO post_count FROM Posts WHERE post_id = test_post_id;
    IF post_count != 1 THEN
        RAISE EXCEPTION 'Setup failed: Post not created';
    END IF;
    
    -- Execute: Delete community
    DELETE FROM Communities WHERE community_id = test_community_id;
    
    -- Verify: Post should be deleted (CASCADE)
    SELECT COUNT(*) INTO post_count FROM Posts WHERE post_id = test_post_id;
    
    IF post_count = 0 THEN
        RAISE NOTICE '✓ TEST 1 PASSED: Post deleted with community (CASCADE)';
    ELSE
        RAISE EXCEPTION '✗ TEST 1 FAILED: Post still exists after community deletion';
    END IF;
    
    -- Cleanup
    DELETE FROM Users WHERE user_id = test_user_id;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '✗ TEST 1 FAILED: %', SQLERRM;
        ROLLBACK;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TEST 2: Messages soft delete when user deleted (sender)
-- ============================================================================
\echo ''
\echo 'TEST 2: Messages preserved when sender deleted (SET NULL + soft delete)'

DO $$
DECLARE
    sender_id INTEGER;
    receiver_id INTEGER;
    test_message_id INTEGER;
    msg_sender_id INTEGER;
    msg_deleted_sender BOOLEAN;
BEGIN
    -- Setup: Create test users and message
    INSERT INTO Users (username, email, password_hash)
    VALUES ('sender_user', 'sender@test.com', 'hash')
    RETURNING user_id INTO sender_id;
    
    INSERT INTO Users (username, email, password_hash)
    VALUES ('receiver_user', 'receiver@test.com', 'hash')
    RETURNING user_id INTO receiver_id;
    
    INSERT INTO Messages (sender_id, receiver_id, content)
    VALUES (sender_id, receiver_id, 'Test message')
    RETURNING message_id INTO test_message_id;
    
    -- Execute: Delete sender
    DELETE FROM Users WHERE user_id = sender_id;
    
    -- Verify: Message should exist with NULL sender_id and sender_deleted = true
    SELECT m.sender_id, m.sender_deleted INTO msg_sender_id, msg_deleted_sender
    FROM Messages m WHERE m.message_id = test_message_id;
    
    IF msg_sender_id IS NULL AND msg_deleted_sender = true THEN
        RAISE NOTICE '✓ TEST 2 PASSED: Message preserved with soft delete flag';
    ELSE
        RAISE EXCEPTION '✗ TEST 2 FAILED: sender_id=%, sender_deleted=%', msg_sender_id, msg_deleted_sender;
    END IF;
    
    -- Cleanup
    DELETE FROM Messages WHERE message_id = test_message_id;
    DELETE FROM Users WHERE user_id = receiver_id;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '✗ TEST 2 FAILED: %', SQLERRM;
        ROLLBACK;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TEST 3: Messages soft delete when user deleted (receiver)
-- ============================================================================
\echo ''
\echo 'TEST 3: Messages preserved when receiver deleted (SET NULL + soft delete)'

DO $$
DECLARE
    sender_id INTEGER;
    receiver_id INTEGER;
    test_message_id INTEGER;
    msg_receiver_id INTEGER;
    msg_deleted_receiver BOOLEAN;
BEGIN
    -- Setup: Create test users and message
    INSERT INTO Users (username, email, password_hash)
    VALUES ('sender_user2', 'sender2@test.com', 'hash')
    RETURNING user_id INTO sender_id;
    
    INSERT INTO Users (username, email, password_hash)
    VALUES ('receiver_user2', 'receiver2@test.com', 'hash')
    RETURNING user_id INTO receiver_id;
    
    INSERT INTO Messages (sender_id, receiver_id, content)
    VALUES (sender_id, receiver_id, 'Test message 2')
    RETURNING message_id INTO test_message_id;
    
    -- Execute: Delete receiver
    DELETE FROM Users WHERE user_id = receiver_id;
    
    -- Verify: Message should exist with NULL receiver_id and receiver_deleted = true
    SELECT m.receiver_id, m.receiver_deleted INTO msg_receiver_id, msg_deleted_receiver
    FROM Messages m WHERE m.message_id = test_message_id;
    
    IF msg_receiver_id IS NULL AND msg_deleted_receiver = true THEN
        RAISE NOTICE '✓ TEST 3 PASSED: Message preserved with soft delete flag';
    ELSE
        RAISE EXCEPTION '✗ TEST 3 FAILED: receiver_id=%, receiver_deleted=%', msg_receiver_id, msg_deleted_receiver;
    END IF;
    
    -- Cleanup
    DELETE FROM Messages WHERE message_id = test_message_id;
    DELETE FROM Users WHERE user_id = sender_id;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '✗ TEST 3 FAILED: %', SQLERRM;
        ROLLBACK;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TEST 4: ON UPDATE CASCADE for user_id changes
-- ============================================================================
\echo ''
\echo 'TEST 4: Foreign keys updated when user_id changes (ON UPDATE CASCADE)'

DO $$
DECLARE
    old_user_id INTEGER;
    new_user_id INTEGER := 999999;
    test_post_id INTEGER;
    updated_post_user_id INTEGER;
BEGIN
    -- Setup: Create test user and post
    INSERT INTO Users (username, email, password_hash)
    VALUES ('update_test_user', 'update@test.com', 'hash')
    RETURNING user_id INTO old_user_id;
    
    INSERT INTO Posts (user_id, content)
    VALUES (old_user_id, 'Test post for UPDATE CASCADE')
    RETURNING post_id INTO test_post_id;
    
    -- Execute: Update user_id (if supported by database)
    -- Note: This may fail if user_id is SERIAL and not updatable
    BEGIN
        UPDATE Users SET user_id = new_user_id WHERE user_id = old_user_id;
        
        -- Verify: Post user_id should be updated
        SELECT user_id INTO updated_post_user_id FROM Posts WHERE post_id = test_post_id;
        
        IF updated_post_user_id = new_user_id THEN
            RAISE NOTICE '✓ TEST 4 PASSED: Foreign key updated with ON UPDATE CASCADE';
        ELSE
            RAISE EXCEPTION '✗ TEST 4 FAILED: Post user_id not updated (expected %, got %)', new_user_id, updated_post_user_id;
        END IF;
        
        -- Cleanup
        DELETE FROM Posts WHERE post_id = test_post_id;
        DELETE FROM Users WHERE user_id = new_user_id;
        
    EXCEPTION
        WHEN OTHERS THEN
            -- If UPDATE on primary key fails, that's expected for SERIAL columns
            IF SQLERRM LIKE '%cannot update%' OR SQLERRM LIKE '%serial%' THEN
                RAISE NOTICE '⚠ TEST 4 SKIPPED: Primary key update not supported (SERIAL column)';
                -- Cleanup
                DELETE FROM Posts WHERE post_id = test_post_id;
                DELETE FROM Users WHERE user_id = old_user_id;
            ELSE
                RAISE;
            END IF;
    END;
    
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE '✗ TEST 4 FAILED: %', SQLERRM;
        ROLLBACK;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TEST 5: Verify soft delete columns exist
-- ============================================================================
\echo ''
\echo 'TEST 5: Verify Messages table has soft delete columns'

DO $$
DECLARE
    column_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO column_count
    FROM information_schema.columns
    WHERE table_name = 'messages'
    AND column_name IN ('sender_deleted', 'receiver_deleted');
    
    IF column_count = 2 THEN
        RAISE NOTICE '✓ TEST 5 PASSED: Soft delete columns exist';
    ELSE
        RAISE EXCEPTION '✗ TEST 5 FAILED: Only % soft delete columns found (expected 2)', column_count;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TEST 6: Verify trigger functions exist
-- ============================================================================
\echo ''
\echo 'TEST 6: Verify soft delete triggers exist'

DO $$
DECLARE
    trigger_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO trigger_count
    FROM pg_trigger
    WHERE tgname IN ('messages_sender_soft_delete_trigger', 'messages_receiver_soft_delete_trigger');
    
    IF trigger_count = 2 THEN
        RAISE NOTICE '✓ TEST 6 PASSED: Soft delete triggers exist';
    ELSE
        RAISE EXCEPTION '✗ TEST 6 FAILED: Only % triggers found (expected 2)', trigger_count;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Summary
-- ============================================================================
\echo ''
\echo '========================================='
\echo 'Test Summary'
\echo '========================================='
\echo 'All CASCADE behavior tests completed!'
\echo 'Check output above for results.'
\echo '========================================='

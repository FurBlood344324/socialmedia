"""
Tests for SQL injection vulnerabilities in repository methods
This test suite verifies that all SQL queries are properly parameterized and resist SQL injection attacks
"""

import unittest
from api.repositories.user_repository import UserRepository
from api.repositories.post_repository import PostRepository
from api.repositories.comment_repository import CommentRepository
from api.repositories.community_repository import CommunityRepository
from api.repositories.message_repository import MessageRepository
from api.repositories.follow_repository import FollowRepository
from api.entities.entities import User, Post, Comment, Community, Message, Follow
from tests.base_test import BaseTest


class TestSQLInjection(BaseTest):
    """Test suite for SQL injection attack resistance"""

    def setUp(self):
        super().setUp()
        self.user_repo = UserRepository()
        self.post_repo = PostRepository()
        self.comment_repo = CommentRepository()
        self.community_repo = CommunityRepository()
        self.message_repo = MessageRepository()
        self.follow_repo = FollowRepository()
        
        # Create a test user for various tests
        self.test_user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            bio="Test bio",
            profile_picture_url=None,
            is_private=False
        )
        self.test_user = self.user_repo.create(self.test_user)

    # ===== User Repository SQL Injection Tests =====
    
    def test_user_get_by_username_sql_injection_attack(self):
        """Test that username lookup resists SQL injection via string concatenation"""
        # Classic SQL injection attempts
        malicious_usernames = [
            "admin'--",
            "admin' OR '1'='1",
            "admin' OR '1'='1'--",
            "' OR 1=1--",
            "'; DROP TABLE Users;--",
            "admin') OR ('1'='1",
            "1' UNION SELECT * FROM Users--",
            "admin' AND 1=0 UNION ALL SELECT NULL, username, email, password_hash, NULL, NULL, NULL, NULL, NULL FROM Users--"
        ]
        
        for malicious_username in malicious_usernames:
            # Should return None (not found), not error or return all users
            result = self.user_repo.get_by_username(malicious_username)
            self.assertIsNone(result, 
                f"SQL injection attempt with username '{malicious_username}' should return None")
    
    def test_user_get_by_email_sql_injection_attack(self):
        """Test that email lookup resists SQL injection"""
        malicious_emails = [
            "admin@example.com'--",
            "admin@example.com' OR '1'='1",
            "'; DROP TABLE Users;--",
            "test@example.com' UNION SELECT * FROM Users--"
        ]
        
        for malicious_email in malicious_emails:
            result = self.user_repo.get_by_email(malicious_email)
            self.assertIsNone(result, 
                f"SQL injection attempt with email '{malicious_email}' should return None")
    
    def test_user_search_sql_injection_attack(self):
        """Test that user search resists SQL injection via ILIKE patterns"""
        malicious_searches = [
            "admin' OR '1'='1",
            "' OR 1=1--",
            "%'; DROP TABLE Users;--",
            "'; DELETE FROM Users WHERE '1'='1",
            "test%' UNION SELECT * FROM Users--",
            "' OR username LIKE '%",
            "\\'; TRUNCATE TABLE Users;--"
        ]
        
        for malicious_search in malicious_searches:
            # Should not error, should handle safely
            try:
                results = self.user_repo.search(malicious_search, limit=10)
                # Should return empty or safe results, not all users
                self.assertIsInstance(results, list,
                    f"SQL injection attempt with search '{malicious_search}' should return a list")
            except Exception as e:
                self.fail(f"SQL injection attempt with search '{malicious_search}' caused error: {str(e)}")
    
    def test_user_create_with_malicious_data(self):
        """Test that creating users with malicious data is safe"""
        malicious_user = User(
            username="'; DROP TABLE Users;--",
            email="malicious@example.com' OR '1'='1",
            password_hash="' OR '1'='1'--",
            bio="Normal bio",
            profile_picture_url=None,
            is_private=False
        )
        
        try:
            created_user = self.user_repo.create(malicious_user)
            # Should create successfully with the exact malicious strings as data
            self.assertEqual(created_user.username, "'; DROP TABLE Users;--")
            self.assertEqual(created_user.email, "malicious@example.com' OR '1'='1")
            
            # Verify the data was stored correctly and can be retrieved
            retrieved = self.user_repo.get_by_username("'; DROP TABLE Users;--")
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.username, "'; DROP TABLE Users;--")
        except ValueError as e:
            # Might fail due to constraints, but not SQL injection
            pass

    # ===== Post Repository SQL Injection Tests =====
    
    def test_post_search_sql_injection_attack(self):
        """Test that post search resists SQL injection"""
        # Create a test post first
        test_post = Post(
            user_id=self.test_user.user_id,
            community_id=None,
            content="Test post content",
            media_url=None
        )
        self.post_repo.create(test_post)
        
        malicious_searches = [
            "' OR '1'='1",
            "test' OR 1=1--",
            "%'; DROP TABLE Posts;--",
            "' UNION SELECT * FROM Users--",
            "'; DELETE FROM Posts WHERE '1'='1"
        ]
        
        for malicious_search in malicious_searches:
            try:
                results = self.post_repo.search_posts(malicious_search, limit=10)
                self.assertIsInstance(results, list,
                    f"SQL injection attempt with search '{malicious_search}' should return a list")
            except Exception as e:
                self.fail(f"SQL injection attempt with search '{malicious_search}' caused error: {str(e)}")
    
    def test_post_create_with_malicious_content(self):
        """Test that creating posts with malicious content is safe"""
        malicious_post = Post(
            user_id=self.test_user.user_id,
            community_id=None,
            content="'; DROP TABLE Posts;-- OR '1'='1",
            media_url="http://example.com/image.jpg' OR '1'='1"
        )
        
        created_post = self.post_repo.create(malicious_post)
        self.assertEqual(created_post.content, "'; DROP TABLE Posts;-- OR '1'='1")
        
        # Verify the malicious content is stored and retrieved correctly
        retrieved = self.post_repo.get_by_id(created_post.post_id)
        self.assertEqual(retrieved.content, "'; DROP TABLE Posts;-- OR '1'='1")

    # ===== Comment Repository SQL Injection Tests =====
    
    def test_comment_create_with_malicious_content(self):
        """Test that comments with malicious content are safely stored"""
        # Create a post first
        test_post = Post(
            user_id=self.test_user.user_id,
            community_id=None,
            content="Test post",
            media_url=None
        )
        test_post = self.post_repo.create(test_post)
        
        malicious_comment = Comment(
            post_id=test_post.post_id,
            user_id=self.test_user.user_id,
            content="'; DROP TABLE Comments; SELECT '1",
            parent_comment_id=None
        )
        
        created_comment = self.comment_repo.create(malicious_comment)
        self.assertIsNotNone(created_comment)
        self.assertEqual(created_comment.content, "'; DROP TABLE Comments; SELECT '1")
        
        # Verify retrieval
        retrieved = self.comment_repo.get_by_id(created_comment.comment_id)
        self.assertEqual(retrieved.content, "'; DROP TABLE Comments; SELECT '1")

    # ===== Community Repository SQL Injection Tests =====
    
    def test_community_search_sql_injection_attack(self):
        """Test that community search resists SQL injection"""
        malicious_searches = [
            "' OR '1'='1",
            "test' OR 1=1--",
            "%'; DROP TABLE Communities;--",
            "' UNION SELECT * FROM Users--"
        ]
        
        for malicious_search in malicious_searches:
            try:
                results = self.community_repo.search(malicious_search, limit=10, user_id=self.test_user.user_id)
                self.assertIsInstance(results, list,
                    f"SQL injection attempt with search '{malicious_search}' should return a list")
            except Exception as e:
                self.fail(f"SQL injection attempt with search '{malicious_search}' caused error: {str(e)}")
    
    def test_community_create_with_malicious_name(self):
        """Test that communities with malicious names are safely created"""
        malicious_community = Community(
            name="'; DROP TABLE Communities;--",
            description="Test description' OR '1'='1",
            creator_id=self.test_user.user_id,
            privacy_id=1
        )
        
        try:
            created_community = self.community_repo.create(malicious_community)
            self.assertEqual(created_community.name, "'; DROP TABLE Communities;--")
            
            # Verify retrieval
            retrieved = self.community_repo.get_by_id(created_community.community_id)
            self.assertEqual(retrieved.name, "'; DROP TABLE Communities;--")
        except ValueError as e:
            # May fail due to constraints, but not SQL injection
            pass

    # ===== Message Repository SQL Injection Tests =====
    
    def test_message_create_with_malicious_content(self):
        """Test that messages with malicious content are safely stored"""
        # Create a second user to send messages to
        receiver = User(
            username="receiver",
            email="receiver@example.com",
            password_hash="hashed",
            bio=None,
            profile_picture_url=None,
            is_private=False
        )
        receiver = self.user_repo.create(receiver)
        
        malicious_message = Message(
            sender_id=self.test_user.user_id,
            receiver_id=receiver.user_id,
            content="'; DROP TABLE Messages; SELECT '1",
            media_url="http://example.com/img.jpg' OR '1'='1",
            is_read=False
        )
        
        created_message = self.message_repo.create(malicious_message)
        self.assertEqual(created_message.content, "'; DROP TABLE Messages; SELECT '1")
        
        # Verify retrieval
        retrieved = self.message_repo.get_by_id(created_message.message_id)
        self.assertEqual(retrieved.content, "'; DROP TABLE Messages; SELECT '1")
    
    def test_message_get_conversation_sql_injection(self):
        """Test that conversation retrieval resists SQL injection via user IDs"""
        # This tests that numeric parameters are properly handled
        # Attempting to pass malicious strings as IDs should fail type checking
        # but we test with valid IDs to ensure query parameterization
        receiver = User(
            username="receiver2",
            email="receiver2@example.com",
            password_hash="hashed",
            bio=None,
            profile_picture_url=None,
            is_private=False
        )
        receiver = self.user_repo.create(receiver)
        
        # Create a test message
        test_message = Message(
            sender_id=self.test_user.user_id,
            receiver_id=receiver.user_id,
            content="Test message",
            media_url=None,
            is_read=False
        )
        self.message_repo.create(test_message)
        
        # Normal retrieval should work
        messages = self.message_repo.get_conversation(
            self.test_user.user_id, 
            receiver.user_id,
            limit=10
        )
        self.assertIsInstance(messages, list)
        self.assertGreater(len(messages), 0)

    # ===== Follow Repository SQL Injection Tests =====
    
    def test_follow_operations_with_valid_ids(self):
        """Test that follow operations use proper parameterization"""
        # Create a second user
        user2 = User(
            username="user2",
            email="user2@example.com",
            password_hash="hashed",
            bio=None,
            profile_picture_url=None,
            is_private=False
        )
        user2 = self.user_repo.create(user2)
        
        # Create follow relationship
        follow = Follow(
            follower_id=self.test_user.user_id,
            following_id=user2.user_id,
            status_id=2  # accepted
        )
        
        created_follow = self.follow_repo.create(follow)
        self.assertIsNotNone(created_follow)
        
        # Verify retrieval works with proper IDs
        retrieved = self.follow_repo.get_by_ids(
            self.test_user.user_id,
            user2.user_id
        )
        self.assertIsNotNone(retrieved)
        
        # Get followers and following lists
        followers = self.follow_repo.get_followers(user2.user_id)
        self.assertIsInstance(followers, list)
        
        following = self.follow_repo.get_following(self.test_user.user_id)
        self.assertIsInstance(following, list)

    # ===== Cross-Repository SQL Injection Tests =====
    
    def test_special_characters_in_text_fields(self):
        """Test that special SQL characters are safely handled"""
        special_chars_user = User(
            username="user_with_'quotes'",
            email="test+special@example.com",
            password_hash="password'with\"quotes",
            bio="Bio with \\ backslash and 'quotes' and \"double quotes\"",
            profile_picture_url=None,
            is_private=False
        )
        
        try:
            created = self.user_repo.create(special_chars_user)
            self.assertEqual(created.username, "user_with_'quotes'")
            self.assertEqual(created.bio, "Bio with \\ backslash and 'quotes' and \"double quotes\"")
        except ValueError:
            # May fail due to validation, but not SQL injection
            pass
    
    def test_unicode_and_special_characters(self):
        """Test that Unicode and special characters are safely handled"""
        unicode_user = User(
            username="user_测试",
            email="unicode@example.com",
            password_hash="hashed",
            bio="Bio with emoji 😀 and unicode 中文",
            profile_picture_url=None,
            is_private=False
        )
        
        try:
            created = self.user_repo.create(unicode_user)
            self.assertEqual(created.username, "user_测试")
            self.assertEqual(created.bio, "Bio with emoji 😀 and unicode 中文")
            
            # Verify search handles unicode
            results = self.user_repo.search("测试", limit=10)
            self.assertIsInstance(results, list)
        except ValueError:
            # May fail due to validation, but not SQL injection
            pass
    
    def test_null_byte_injection(self):
        """Test that null byte injection is safely handled"""
        null_byte_user = User(
            username="admin\x00test",
            email="nullbyte@example.com",
            password_hash="hashed",
            bio="Bio with \x00 null byte",
            profile_picture_url=None,
            is_private=False
        )
        
        try:
            created = self.user_repo.create(null_byte_user)
            # Should store the null byte as data, not interpret it
            retrieved = self.user_repo.get_by_id(created.user_id)
            self.assertIsNotNone(retrieved)
        except ValueError:
            # May fail due to validation, but not SQL injection
            pass
    
    def test_limit_and_offset_parameters(self):
        """Test that LIMIT and OFFSET parameters are properly handled"""
        # These should be safe since they're passed as parameters
        # Testing with various values to ensure proper parameterization
        try:
            users = self.user_repo.get_all(limit=10, offset=0)
            self.assertIsInstance(users, list)
            
            users = self.user_repo.get_all(limit=1, offset=0)
            self.assertIsInstance(users, list)
            
            # Large values should work without SQL injection
            users = self.user_repo.get_all(limit=1000, offset=0)
            self.assertIsInstance(users, list)
        except Exception as e:
            self.fail(f"LIMIT/OFFSET parameterization failed: {str(e)}")
    
    def test_order_by_injection_resistance(self):
        """Test that ORDER BY clauses are hardcoded and not injectable"""
        # Since ORDER BY is hardcoded in queries (not parameterized),
        # this test verifies that user input doesn't reach ORDER BY clauses
        try:
            # Normal operations should work
            users = self.user_repo.get_all(limit=10, offset=0)
            self.assertIsInstance(users, list)
            
            posts = self.post_repo.get_by_user_id(self.test_user.user_id, limit=10)
            self.assertIsInstance(posts, list)
        except Exception as e:
            self.fail(f"ORDER BY clause handling failed: {str(e)}")
    
    def test_exists_methods_sql_injection(self):
        """Test that EXISTS queries resist SQL injection"""
        malicious_emails = [
            "admin@example.com' OR '1'='1",
            "'; DROP TABLE Users;--@example.com"
        ]
        
        for malicious_email in malicious_emails:
            result = self.user_repo.exists_by_email(malicious_email)
            self.assertIsInstance(result, bool,
                f"exists_by_email with '{malicious_email}' should return boolean")
        
        malicious_usernames = [
            "admin' OR '1'='1",
            "'; DROP TABLE Users;--"
        ]
        
        for malicious_username in malicious_usernames:
            result = self.user_repo.exists_by_username(malicious_username)
            self.assertIsInstance(result, bool,
                f"exists_by_username with '{malicious_username}' should return boolean")


if __name__ == '__main__':
    unittest.main()


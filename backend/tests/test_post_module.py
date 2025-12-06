"""Tests for PostRepository and PostService"""

import sys
import os

# Add parent directory (backend/) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from api.entities.entities import Post
from api.repositories.post_repository import PostRepository
from api.services.post_service import PostService


class TestPostRepository(unittest.TestCase):
    """Test cases for PostRepository"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.repo = PostRepository()
        self.repo.db = self.mock_db

    def test_create_post(self):
        """Test creating a new post"""
        # Arrange
        post = Post(
            user_id=1,
            content="Test post content",
            media_url="http://example.com/image.jpg",
            community_id=None
        )
        
        mock_row = MagicMock()
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Test post content"
        mock_row.media_url = "http://example.com/image.jpg"
        mock_row.community_id = None
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.create(post)
        
        # Assert
        self.assertEqual(result.content, "Test post content")
        self.assertEqual(result.user_id, 1)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_create_post passed")

    def test_get_by_id(self):
        """Test getting post by ID"""
        # Arrange
        mock_row = MagicMock()
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Test content"
        mock_row.media_url = None
        mock_row.community_id = None
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.get_by_id(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.post_id, 1)
        print("✅ test_get_by_id passed")

    def test_get_by_user_id(self):
        """Test getting posts by user ID"""
        # Arrange
        mock_row = MagicMock()
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "User post"
        mock_row.media_url = None
        mock_row.community_id = None
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchall.return_value = [mock_row]
        
        # Act
        result = self.repo.get_by_user_id(1)
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].user_id, 1)
        print("✅ test_get_by_user_id passed")

    def test_update_post(self):
        """Test updating a post"""
        # Arrange
        post = Post(
            post_id=1,
            user_id=1,
            content="Updated content",
            media_url=None,
            community_id=None
        )
        
        mock_row = MagicMock()
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Updated content"
        mock_row.media_url = None
        mock_row.community_id = None
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.update(post)
        
        # Assert
        self.assertEqual(result.content, "Updated content")
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_update_post passed")

    def test_delete_post(self):
        """Test deleting a post"""
        # Arrange
        mock_row = MagicMock()
        mock_row.post_id = 1
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.delete(1)
        
        # Assert
        self.assertTrue(result)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_delete_post passed")


class TestPostService(unittest.TestCase):
    """Test cases for PostService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = PostService()
        self.mock_repo = MagicMock()
        self.service.post_repository = self.mock_repo

    def test_create_post_success(self):
        """Test successful post creation"""
        # Arrange
        self.mock_repo.create.return_value = Post(
            post_id=1,
            user_id=1,
            content="Test post",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.create_post(user_id=1, content="Test post")
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['post']['content'], "Test post")
        print("✅ test_create_post_success passed")

    def test_create_post_validation_error(self):
        """Test post creation with validation error"""
        # Act - no content and no media
        result = self.service.create_post(user_id=1)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
        print("✅ test_create_post_validation_error passed")

    def test_get_post_found(self):
        """Test getting existing post"""
        # Arrange
        self.mock_repo.get_by_id.return_value = Post(
            post_id=1,
            user_id=1,
            content="Test post",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.get_post(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['post_id'], 1)
        print("✅ test_get_post_found passed")

    def test_get_post_not_found(self):
        """Test getting non-existent post"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.get_post(999)
        
        # Assert
        self.assertIsNone(result)
        print("✅ test_get_post_not_found passed")

    def test_update_post_success(self):
        """Test successful post update by owner"""
        # Arrange
        existing_post = Post(
            post_id=1,
            user_id=1,
            content="Old content",
            created_at=datetime.now()
        )
        self.mock_repo.get_by_id.return_value = existing_post
        self.mock_repo.update.return_value = Post(
            post_id=1,
            user_id=1,
            content="New content",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.update_post(1, 1, {"content": "New content"})
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['post']['content'], "New content")
        print("✅ test_update_post_success passed")

    def test_update_post_not_owner(self):
        """Test post update by non-owner (should fail)"""
        # Arrange
        existing_post = Post(post_id=1, user_id=1, content="Content")
        self.mock_repo.get_by_id.return_value = existing_post
        
        # Act - user 2 trying to update user 1's post
        result = self.service.update_post(1, 2, {"content": "Hacked"})
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("only edit your own", result['error'])
        print("✅ test_update_post_not_owner passed")

    def test_delete_post_success(self):
        """Test successful post deletion by owner"""
        # Arrange
        self.mock_repo.get_by_id.return_value = Post(post_id=1, user_id=1)
        self.mock_repo.delete.return_value = True
        
        # Act
        result = self.service.delete_post(1, 1)
        
        # Assert
        self.assertTrue(result['success'])
        print("✅ test_delete_post_success passed")

    def test_delete_post_not_owner(self):
        """Test post deletion by non-owner (should fail)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = Post(post_id=1, user_id=1)
        
        # Act - user 2 trying to delete user 1's post
        result = self.service.delete_post(1, 2)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("only delete your own", result['error'])
        print("✅ test_delete_post_not_owner passed")

    def test_get_user_posts(self):
        """Test getting user's posts"""
        # Arrange
        mock_post = Post(
            post_id=1,
            user_id=1,
            content="User post",
            created_at=datetime.now()
        )
        self.mock_repo.get_by_user_id.return_value = [mock_post]
        self.mock_repo.count.return_value = 1
        
        # Act
        result = self.service.get_user_posts(1)
        
        # Assert
        self.assertEqual(len(result['posts']), 1)
        self.assertEqual(result['total'], 1)
        print("✅ test_get_user_posts passed")

    def test_get_feed(self):
        """Test getting user's feed"""
        # Arrange
        mock_posts = [
            Post(post_id=1, user_id=2, content="Friend post 1", created_at=datetime.now()),
            Post(post_id=2, user_id=3, content="Friend post 2", created_at=datetime.now())
        ]
        self.mock_repo.get_feed.return_value = mock_posts
        
        # Act
        result = self.service.get_feed(1)
        
        # Assert
        self.assertEqual(len(result['posts']), 2)
        print("✅ test_get_feed passed")


class TestPostValidation(unittest.TestCase):
    """Test cases for Post entity validation"""

    def test_valid_post_with_content(self):
        """Test validation passes with content"""
        post = Post(user_id=1, content="Valid content")
        errors = post.validate()
        self.assertEqual(len(errors), 0)
        print("✅ test_valid_post_with_content passed")

    def test_valid_post_with_media(self):
        """Test validation passes with media URL"""
        post = Post(user_id=1, media_url="http://example.com/image.jpg")
        errors = post.validate()
        self.assertEqual(len(errors), 0)
        print("✅ test_valid_post_with_media passed")

    def test_invalid_post_no_content_no_media(self):
        """Test validation fails without content or media"""
        post = Post(user_id=1)
        errors = post.validate()
        self.assertGreater(len(errors), 0)
        self.assertIn("content or media", errors[0].lower())
        print("✅ test_invalid_post_no_content_no_media passed")

    def test_invalid_post_content_too_long(self):
        """Test validation fails with content too long"""
        post = Post(user_id=1, content="a" * 5001)
        errors = post.validate()
        self.assertGreater(len(errors), 0)
        print("✅ test_invalid_post_content_too_long passed")


if __name__ == "__main__":
    print("\n🧪 Testing Post Module...\n")
    print("=" * 50)
    print("PostRepository Tests")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)

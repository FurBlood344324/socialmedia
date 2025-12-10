"""Tests for Post Like functionality - PostRepository, PostService, and PostController"""

import sys
import os

# Add parent directory (backend/) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from api.entities.entities import Post, PostLike
from api.repositories.post_repository import PostRepository
from api.services.post_service import PostService


class TestPostLikeRepository(unittest.TestCase):
    """Test cases for PostRepository like methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.repo = PostRepository()
        self.repo.db = self.mock_db

    def test_like_post_success(self):
        """Test successfully liking a post"""
        # Arrange
        self.mock_db.session.execute.return_value = MagicMock()
        
        # Act
        result = self.repo.like_post(post_id=1, user_id=2)
        
        # Assert
        self.assertTrue(result)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_like_post_success passed")

    def test_like_post_duplicate(self):
        """Test liking a post that's already liked (duplicate)"""
        # Arrange - simulate database constraint violation
        self.mock_db.session.execute.side_effect = Exception("Duplicate key")
        
        # Act
        result = self.repo.like_post(post_id=1, user_id=2)
        
        # Assert
        self.assertFalse(result)
        self.mock_db.session.rollback.assert_called_once()
        print("✅ test_like_post_duplicate passed")

    def test_unlike_post_success(self):
        """Test successfully unliking a post"""
        # Arrange
        mock_result = MagicMock()
        mock_row = MagicMock()
        mock_row.post_id = 1
        mock_result.fetchone.return_value = mock_row
        self.mock_db.session.execute.return_value = mock_result
        
        # Act
        result = self.repo.unlike_post(post_id=1, user_id=2)
        
        # Assert
        self.assertTrue(result)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_unlike_post_success passed")

    def test_unlike_post_not_found(self):
        """Test unliking a post that wasn't liked"""
        # Arrange
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        self.mock_db.session.execute.return_value = mock_result
        
        # Act
        result = self.repo.unlike_post(post_id=1, user_id=2)
        
        # Assert
        self.assertFalse(result)
        print("✅ test_unlike_post_not_found passed")

    def test_get_post_likes(self):
        """Test getting all users who liked a post"""
        # Arrange
        mock_row1 = MagicMock()
        mock_row1.post_id = 1
        mock_row1.user_id = 2
        mock_row1.created_at = datetime.now()
        
        mock_row2 = MagicMock()
        mock_row2.post_id = 1
        mock_row2.user_id = 3
        mock_row2.created_at = datetime.now()
        
        mock_result = MagicMock()
        mock_result.fetchall.return_value = [mock_row1, mock_row2]
        self.mock_db.session.execute.return_value = mock_result
        
        # Act
        result = self.repo.get_post_likes(post_id=1)
        
        # Assert
        self.assertEqual(len(result), 2)
        self.assertIsInstance(result[0], PostLike)
        self.assertEqual(result[0].user_id, 2)
        print("✅ test_get_post_likes passed")

    def test_count_likes(self):
        """Test counting likes on a post"""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        self.mock_db.session.execute.return_value = mock_result
        
        # Act
        result = self.repo.count_likes(post_id=1)
        
        # Assert
        self.assertEqual(result, 5)
        print("✅ test_count_likes passed")

    def test_has_user_liked_true(self):
        """Test checking if user liked a post (returns True)"""
        # Arrange
        mock_result = MagicMock()
        mock_result.fetchone.return_value = MagicMock()
        self.mock_db.session.execute.return_value = mock_result
        
        # Act
        result = self.repo.has_user_liked(post_id=1, user_id=2)
        
        # Assert
        self.assertTrue(result)
        print("✅ test_has_user_liked_true passed")

    def test_has_user_liked_false(self):
        """Test checking if user liked a post (returns False)"""
        # Arrange
        mock_result = MagicMock()
        mock_result.fetchone.return_value = None
        self.mock_db.session.execute.return_value = mock_result
        
        # Act
        result = self.repo.has_user_liked(post_id=1, user_id=2)
        
        # Assert
        self.assertFalse(result)
        print("✅ test_has_user_liked_false passed")


class TestPostLikeService(unittest.TestCase):
    """Test cases for PostService like methods"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = PostService()
        self.service.post_repository = MagicMock()

    def test_like_post_success(self):
        """Test successfully liking a post through service"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        self.service.post_repository.get_by_id.return_value = mock_post
        self.service.post_repository.has_user_liked.return_value = False
        self.service.post_repository.like_post.return_value = True
        self.service.post_repository.count_likes.return_value = 1
        
        # Act
        result = self.service.like_post(post_id=1, user_id=2)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['like_count'], 1)
        print("✅ test_like_post_success (service) passed")

    def test_like_post_own_post(self):
        """Test that users cannot like their own posts"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        self.service.post_repository.get_by_id.return_value = mock_post
        
        # Act
        result = self.service.like_post(post_id=1, user_id=1)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("cannot like your own", result['error'])
        print("✅ test_like_post_own_post passed")

    def test_like_post_already_liked(self):
        """Test liking a post that's already liked"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        self.service.post_repository.get_by_id.return_value = mock_post
        self.service.post_repository.has_user_liked.return_value = True
        
        # Act
        result = self.service.like_post(post_id=1, user_id=2)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("already liked", result['error'])
        print("✅ test_like_post_already_liked passed")

    def test_like_post_not_found(self):
        """Test liking a non-existent post"""
        # Arrange
        self.service.post_repository.get_by_id.return_value = None
        
        # Act
        result = self.service.like_post(post_id=999, user_id=2)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("not found", result['error'])
        print("✅ test_like_post_not_found passed")

    def test_unlike_post_success(self):
        """Test successfully unliking a post through service"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        self.service.post_repository.get_by_id.return_value = mock_post
        self.service.post_repository.has_user_liked.return_value = True
        self.service.post_repository.unlike_post.return_value = True
        self.service.post_repository.count_likes.return_value = 0
        
        # Act
        result = self.service.unlike_post(post_id=1, user_id=2)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['like_count'], 0)
        print("✅ test_unlike_post_success (service) passed")

    def test_unlike_post_not_liked(self):
        """Test unliking a post that wasn't liked"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        self.service.post_repository.get_by_id.return_value = mock_post
        self.service.post_repository.has_user_liked.return_value = False
        
        # Act
        result = self.service.unlike_post(post_id=1, user_id=2)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("not liked", result['error'])
        print("✅ test_unlike_post_not_liked passed")

    def test_get_like_count_success(self):
        """Test getting like count for a post"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        self.service.post_repository.get_by_id.return_value = mock_post
        self.service.post_repository.count_likes.return_value = 5
        
        # Act
        result = self.service.get_like_count(post_id=1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['like_count'], 5)
        print("✅ test_get_like_count_success passed")

    def test_get_post_likes_success(self):
        """Test getting users who liked a post"""
        # Arrange
        mock_post = Post(post_id=1, user_id=1, content="Test post")
        mock_like1 = PostLike(post_id=1, user_id=2, created_at=datetime.now())
        mock_like2 = PostLike(post_id=1, user_id=3, created_at=datetime.now())
        
        self.service.post_repository.get_by_id.return_value = mock_post
        self.service.post_repository.get_post_likes.return_value = [mock_like1, mock_like2]
        
        # Act
        result = self.service.get_post_likes(post_id=1)
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        self.assertEqual(len(result['likes']), 2)
        print("✅ test_get_post_likes_success passed")


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running Post Like Functionality Tests")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPostLikeRepository))
    suite.addTests(loader.loadTestsFromTestCase(TestPostLikeService))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

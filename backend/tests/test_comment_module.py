"""Tests for CommentRepository and CommentService"""

import sys
import os

# Add parent directory (backend/) to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock
from datetime import datetime

from api.entities.entities import Comment
from api.repositories.comment_repository import CommentRepository
from api.services.comment_service import CommentService


class TestCommentRepository(unittest.TestCase):
    """Test cases for CommentRepository"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.repo = CommentRepository()
        self.repo.db = self.mock_db

    def test_create_comment(self):
        """Test creating a new comment"""
        # Arrange
        comment = Comment(
            post_id=1,
            user_id=1,
            content="Test comment"
        )
        
        mock_row = MagicMock()
        mock_row.comment_id = 1
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Test comment"
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.create(comment)
        
        # Assert
        self.assertEqual(result.content, "Test comment")
        self.assertEqual(result.post_id, 1)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_create_comment passed")

    def test_get_by_id(self):
        """Test getting comment by ID"""
        # Arrange
        mock_row = MagicMock()
        mock_row.comment_id = 1
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Test comment"
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.get_by_id(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.comment_id, 1)
        print("✅ test_get_by_id passed")

    def test_get_by_post_id(self):
        """Test getting comments by post ID"""
        # Arrange
        mock_row = MagicMock()
        mock_row.comment_id = 1
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Post comment"
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchall.return_value = [mock_row]
        
        # Act
        result = self.repo.get_by_post_id(1)
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].post_id, 1)
        print("✅ test_get_by_post_id passed")

    def test_get_by_user_id(self):
        """Test getting comments by user ID"""
        # Arrange
        mock_row = MagicMock()
        mock_row.comment_id = 1
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "User comment"
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchall.return_value = [mock_row]
        
        # Act
        result = self.repo.get_by_user_id(1)
        
        # Assert
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].user_id, 1)
        print("✅ test_get_by_user_id passed")

    def test_update_comment(self):
        """Test updating a comment"""
        # Arrange
        comment = Comment(
            comment_id=1,
            post_id=1,
            user_id=1,
            content="Updated comment"
        )
        
        mock_row = MagicMock()
        mock_row.comment_id = 1
        mock_row.post_id = 1
        mock_row.user_id = 1
        mock_row.content = "Updated comment"
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.update(comment)
        
        # Assert
        self.assertEqual(result.content, "Updated comment")
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_update_comment passed")

    def test_delete_comment(self):
        """Test deleting a comment"""
        # Arrange
        mock_row = MagicMock()
        mock_row.comment_id = 1
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.delete(1)
        
        # Assert
        self.assertTrue(result)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_delete_comment passed")

    def test_count_by_post_id(self):
        """Test counting comments for a post"""
        # Arrange
        self.mock_db.session.execute.return_value.scalar.return_value = 5
        
        # Act
        result = self.repo.count_by_post_id(1)
        
        # Assert
        self.assertEqual(result, 5)
        print("✅ test_count_by_post_id passed")


class TestCommentService(unittest.TestCase):
    """Test cases for CommentService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = CommentService()
        self.mock_repo = MagicMock()
        self.service.comment_repository = self.mock_repo

    def test_create_comment_success(self):
        """Test successful comment creation"""
        # Arrange
        self.mock_repo.create.return_value = Comment(
            comment_id=1,
            post_id=1,
            user_id=1,
            content="Test comment",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.create_comment(
            post_id=1,
            user_id=1,
            content="Test comment"
        )
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['comment']['content'], "Test comment")
        print("✅ test_create_comment_success passed")

    def test_create_comment_empty_content(self):
        """Test comment creation with empty content"""
        # Act
        result = self.service.create_comment(post_id=1, user_id=1, content="")
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
        print("✅ test_create_comment_empty_content passed")

    def test_create_comment_too_long(self):
        """Test comment creation with content too long"""
        # Act
        result = self.service.create_comment(
            post_id=1,
            user_id=1,
            content="a" * 2001
        )
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn('errors', result)
        print("✅ test_create_comment_too_long passed")

    def test_get_comment_found(self):
        """Test getting existing comment"""
        # Arrange
        self.mock_repo.get_by_id.return_value = Comment(
            comment_id=1,
            post_id=1,
            user_id=1,
            content="Test comment",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.get_comment(1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result['comment_id'], 1)
        print("✅ test_get_comment_found passed")

    def test_get_comment_not_found(self):
        """Test getting non-existent comment"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.get_comment(999)
        
        # Assert
        self.assertIsNone(result)
        print("✅ test_get_comment_not_found passed")

    def test_get_post_comments(self):
        """Test getting post's comments"""
        # Arrange
        mock_comments = [
            Comment(comment_id=1, post_id=1, user_id=1, content="Comment 1", created_at=datetime.now()),
            Comment(comment_id=2, post_id=1, user_id=2, content="Comment 2", created_at=datetime.now())
        ]
        self.mock_repo.get_by_post_id.return_value = mock_comments
        self.mock_repo.count_by_post_id.return_value = 2
        
        # Act
        result = self.service.get_post_comments(1)
        
        # Assert
        self.assertEqual(len(result['comments']), 2)
        self.assertEqual(result['total'], 2)
        print("✅ test_get_post_comments passed")

    def test_update_comment_success(self):
        """Test successful comment update by owner"""
        # Arrange
        existing_comment = Comment(
            comment_id=1,
            post_id=1,
            user_id=1,
            content="Old content",
            created_at=datetime.now()
        )
        self.mock_repo.get_by_id.return_value = existing_comment
        self.mock_repo.update.return_value = Comment(
            comment_id=1,
            post_id=1,
            user_id=1,
            content="New content",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.update_comment(1, 1, "New content")
        
        # Assert
        self.assertTrue(result['success'])
        self.assertEqual(result['comment']['content'], "New content")
        print("✅ test_update_comment_success passed")

    def test_update_comment_not_owner(self):
        """Test comment update by non-owner (should fail)"""
        # Arrange
        existing_comment = Comment(comment_id=1, post_id=1, user_id=1, content="Content")
        self.mock_repo.get_by_id.return_value = existing_comment
        
        # Act - user 2 trying to update user 1's comment
        result = self.service.update_comment(1, 2, "Hacked")
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("only edit your own", result['error'])
        print("✅ test_update_comment_not_owner passed")

    def test_delete_comment_success(self):
        """Test successful comment deletion by owner"""
        # Arrange
        self.mock_repo.get_by_id.return_value = Comment(
            comment_id=1, post_id=1, user_id=1, content="Test"
        )
        self.mock_repo.delete.return_value = True
        
        # Act
        result = self.service.delete_comment(1, 1)
        
        # Assert
        self.assertTrue(result['success'])
        print("✅ test_delete_comment_success passed")

    def test_delete_comment_not_owner(self):
        """Test comment deletion by non-owner (should fail)"""
        # Arrange
        self.mock_repo.get_by_id.return_value = Comment(
            comment_id=1, post_id=1, user_id=1, content="Test"
        )
        
        # Act - user 2 trying to delete user 1's comment
        result = self.service.delete_comment(1, 2)
        
        # Assert
        self.assertFalse(result['success'])
        self.assertIn("only delete your own", result['error'])
        print("✅ test_delete_comment_not_owner passed")


class TestCommentValidation(unittest.TestCase):
    """Test cases for Comment entity validation"""

    def test_valid_comment(self):
        """Test validation passes with valid content"""
        comment = Comment(post_id=1, user_id=1, content="Valid comment")
        errors = comment.validate()
        self.assertEqual(len(errors), 0)
        print("✅ test_valid_comment passed")

    def test_invalid_comment_empty(self):
        """Test validation fails with empty content"""
        comment = Comment(post_id=1, user_id=1, content="")
        errors = comment.validate()
        self.assertGreater(len(errors), 0)
        print("✅ test_invalid_comment_empty passed")

    def test_invalid_comment_whitespace_only(self):
        """Test validation fails with whitespace only"""
        comment = Comment(post_id=1, user_id=1, content="   ")
        errors = comment.validate()
        self.assertGreater(len(errors), 0)
        print("✅ test_invalid_comment_whitespace_only passed")

    def test_invalid_comment_too_long(self):
        """Test validation fails with content too long"""
        comment = Comment(post_id=1, user_id=1, content="a" * 2001)
        errors = comment.validate()
        self.assertGreater(len(errors), 0)
        print("✅ test_invalid_comment_too_long passed")


if __name__ == "__main__":
    print("\n🧪 Testing Comment Module...\n")
    print("=" * 50)
    print("CommentRepository Tests")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)

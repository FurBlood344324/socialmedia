"""Tests for Repository layer (UserRepository)"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock
from datetime import datetime

from api.entities.entities import User
from api.repositories.user_repository import UserRepository


class TestUserRepository(unittest.TestCase):
    """Test cases for UserRepository"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.repo = UserRepository()
        self.repo.db = self.mock_db

    def _create_mock_row(self, user_id=1, username="testuser", email="test@example.com",
                         password_hash="hashed", bio=None, profile_picture_url=None,
                         is_private=False, created_at=None):
        """Helper to create a mock database row"""
        mock_row = MagicMock()
        mock_row.user_id = user_id
        mock_row.username = username
        mock_row.email = email
        mock_row.password_hash = password_hash
        mock_row.bio = bio
        mock_row.profile_picture_url = profile_picture_url
        mock_row.is_private = is_private
        mock_row.created_at = created_at or datetime.now()
        return mock_row

    def test_create_user(self):
        """Test creating a new user"""
        # Arrange
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            bio="Test bio",
            is_private=False
        )

        mock_row = self._create_mock_row(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            bio="Test bio"
        )
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.create(user)

        # Assert
        self.assertEqual(result.username, "testuser")
        self.assertEqual(result.email, "test@example.com")
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_create_user passed")

    def test_create_user_with_all_fields(self):
        """Test creating a user with all optional fields"""
        # Arrange
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            bio="Hello world",
            profile_picture_url="http://example.com/pic.jpg",
            is_private=True
        )

        mock_row = self._create_mock_row(
            username="testuser",
            email="test@example.com",
            bio="Hello world",
            profile_picture_url="http://example.com/pic.jpg",
            is_private=True
        )
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.create(user)

        # Assert
        self.assertEqual(result.bio, "Hello world")
        self.assertEqual(result.profile_picture_url, "http://example.com/pic.jpg")
        self.assertTrue(result.is_private)
        print("✅ test_create_user_with_all_fields passed")

    def test_get_by_id_found(self):
        """Test getting user by ID when user exists"""
        # Arrange
        mock_row = self._create_mock_row(user_id=1, username="testuser")
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.get_by_id(1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, 1)
        print("✅ test_get_by_id_found passed")

    def test_get_by_id_not_found(self):
        """Test getting user by ID when user doesn't exist"""
        # Arrange
        self.mock_db.session.execute.return_value.fetchone.return_value = None

        # Act
        result = self.repo.get_by_id(999)

        # Assert
        self.assertIsNone(result)
        print("✅ test_get_by_id_not_found passed")

    def test_get_by_email(self):
        """Test getting user by email"""
        # Arrange
        mock_row = self._create_mock_row(email="test@example.com")
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.get_by_email("test@example.com")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.email, "test@example.com")
        print("✅ test_get_by_email passed")

    def test_get_by_email_not_found(self):
        """Test getting user by email when not found"""
        # Arrange
        self.mock_db.session.execute.return_value.fetchone.return_value = None

        # Act
        result = self.repo.get_by_email("notfound@example.com")

        # Assert
        self.assertIsNone(result)
        print("✅ test_get_by_email_not_found passed")

    def test_get_by_username(self):
        """Test getting user by username"""
        # Arrange
        mock_row = self._create_mock_row(username="testuser")
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.get_by_username("testuser")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")
        print("✅ test_get_by_username passed")

    def test_get_by_username_not_found(self):
        """Test getting user by username when not found"""
        # Arrange
        self.mock_db.session.execute.return_value.fetchone.return_value = None

        # Act
        result = self.repo.get_by_username("notfound")

        # Assert
        self.assertIsNone(result)
        print("✅ test_get_by_username_not_found passed")

    def test_update_user(self):
        """Test updating a user"""
        # Arrange
        user = User(
            user_id=1,
            username="updateduser",
            email="updated@example.com",
            password_hash="newhash",
            bio="Updated bio",
            is_private=True
        )

        mock_row = self._create_mock_row(
            user_id=1,
            username="updateduser",
            email="updated@example.com",
            password_hash="newhash",
            bio="Updated bio",
            is_private=True
        )
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.update(user)

        # Assert
        self.assertEqual(result.username, "updateduser")
        self.assertEqual(result.bio, "Updated bio")
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_update_user passed")

    def test_delete_user_success(self):
        """Test deleting a user successfully"""
        # Arrange
        mock_row = MagicMock()
        mock_row.user_id = 1
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row

        # Act
        result = self.repo.delete(1)

        # Assert
        self.assertTrue(result)
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_delete_user_success passed")

    def test_delete_user_not_found(self):
        """Test deleting a user that doesn't exist"""
        # Arrange
        self.mock_db.session.execute.return_value.fetchone.return_value = None

        # Act
        result = self.repo.delete(999)

        # Assert
        self.assertFalse(result)
        print("✅ test_delete_user_not_found passed")

    def test_get_all_users(self):
        """Test getting all users with pagination"""
        # Arrange
        mock_rows = [
            self._create_mock_row(user_id=1, username="user1"),
            self._create_mock_row(user_id=2, username="user2")
        ]
        self.mock_db.session.execute.return_value.fetchall.return_value = mock_rows

        # Act
        result = self.repo.get_all(limit=100, offset=0)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].username, "user1")
        self.assertEqual(result[1].username, "user2")
        print("✅ test_get_all_users passed")

    def test_get_all_users_empty(self):
        """Test getting all users when no users exist"""
        # Arrange
        self.mock_db.session.execute.return_value.fetchall.return_value = []

        # Act
        result = self.repo.get_all()

        # Assert
        self.assertEqual(len(result), 0)
        print("✅ test_get_all_users_empty passed")

    def test_search_users(self):
        """Test searching users by username"""
        # Arrange
        mock_rows = [
            self._create_mock_row(user_id=1, username="john"),
            self._create_mock_row(user_id=2, username="johnny")
        ]
        self.mock_db.session.execute.return_value.fetchall.return_value = mock_rows

        # Act
        result = self.repo.search("john")

        # Assert
        self.assertEqual(len(result), 2)
        print("✅ test_search_users passed")

    def test_search_users_no_results(self):
        """Test searching users with no results"""
        # Arrange
        self.mock_db.session.execute.return_value.fetchall.return_value = []

        # Act
        result = self.repo.search("nonexistent")

        # Assert
        self.assertEqual(len(result), 0)
        print("✅ test_search_users_no_results passed")

    def test_count_users(self):
        """Test counting total users"""
        # Arrange
        self.mock_db.session.execute.return_value.scalar.return_value = 42

        # Act
        result = self.repo.count()

        # Assert
        self.assertEqual(result, 42)
        print("✅ test_count_users passed")

    def test_exists_by_email_true(self):
        """Test exists_by_email returns True when email exists"""
        # Arrange
        self.mock_db.session.execute.return_value.scalar.return_value = True

        # Act
        result = self.repo.exists_by_email("test@example.com")

        # Assert
        self.assertTrue(result)
        print("✅ test_exists_by_email_true passed")

    def test_exists_by_email_false(self):
        """Test exists_by_email returns False when email doesn't exist"""
        # Arrange
        self.mock_db.session.execute.return_value.scalar.return_value = False

        # Act
        result = self.repo.exists_by_email("notfound@example.com")

        # Assert
        self.assertFalse(result)
        print("✅ test_exists_by_email_false passed")

    def test_exists_by_username_true(self):
        """Test exists_by_username returns True when username exists"""
        # Arrange
        self.mock_db.session.execute.return_value.scalar.return_value = True

        # Act
        result = self.repo.exists_by_username("testuser")

        # Assert
        self.assertTrue(result)
        print("✅ test_exists_by_username_true passed")

    def test_exists_by_username_false(self):
        """Test exists_by_username returns False when username doesn't exist"""
        # Arrange
        self.mock_db.session.execute.return_value.scalar.return_value = False

        # Act
        result = self.repo.exists_by_username("notfound")

        # Assert
        self.assertFalse(result)
        print("✅ test_exists_by_username_false passed")


if __name__ == "__main__":
    print("\n🧪 Testing Repository Layer (UserRepository)...\n")
    print("=" * 60)
    unittest.main(verbosity=2, exit=False)

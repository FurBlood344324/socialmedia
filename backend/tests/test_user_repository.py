"""Tests for UserRepository and UserService"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from api.entities.entities import User
from api.repositories.user_repository import UserRepository
from api.services.user_service import UserService


class TestUserRepository(unittest.TestCase):
    """Test cases for UserRepository"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_db = MagicMock()
        self.repo = UserRepository()
        self.repo.db = self.mock_db

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
        
        mock_row = MagicMock()
        mock_row.user_id = 1
        mock_row.username = "testuser"
        mock_row.email = "test@example.com"
        mock_row.password_hash = "hashed_password"
        mock_row.bio = "Test bio"
        mock_row.profile_picture_url = None
        mock_row.is_private = False
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.create(user)
        
        # Assert
        self.assertEqual(result.username, "testuser")
        self.assertEqual(result.email, "test@example.com")
        self.mock_db.session.commit.assert_called_once()
        print("✅ test_create_user passed")

    def test_get_by_id_found(self):
        """Test getting user by ID when user exists"""
        # Arrange
        mock_row = MagicMock()
        mock_row.user_id = 1
        mock_row.username = "testuser"
        mock_row.email = "test@example.com"
        mock_row.password_hash = "hashed"
        mock_row.bio = None
        mock_row.profile_picture_url = None
        mock_row.is_private = False
        mock_row.created_at = datetime.now()
        
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
        mock_row = MagicMock()
        mock_row.user_id = 1
        mock_row.username = "testuser"
        mock_row.email = "test@example.com"
        mock_row.password_hash = "hashed"
        mock_row.bio = None
        mock_row.profile_picture_url = None
        mock_row.is_private = False
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.get_by_email("test@example.com")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.email, "test@example.com")
        print("✅ test_get_by_email passed")

    def test_get_by_username(self):
        """Test getting user by username"""
        # Arrange
        mock_row = MagicMock()
        mock_row.user_id = 1
        mock_row.username = "testuser"
        mock_row.email = "test@example.com"
        mock_row.password_hash = "hashed"
        mock_row.bio = None
        mock_row.profile_picture_url = None
        mock_row.is_private = False
        mock_row.created_at = datetime.now()
        
        self.mock_db.session.execute.return_value.fetchone.return_value = mock_row
        
        # Act
        result = self.repo.get_by_username("testuser")
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result.username, "testuser")
        print("✅ test_get_by_username passed")

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
        
        mock_row = MagicMock()
        mock_row.user_id = 1
        mock_row.username = "updateduser"
        mock_row.email = "updated@example.com"
        mock_row.password_hash = "newhash"
        mock_row.bio = "Updated bio"
        mock_row.profile_picture_url = None
        mock_row.is_private = True
        mock_row.created_at = datetime.now()
        
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


class TestUserService(unittest.TestCase):
    """Test cases for UserService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = UserService()
        self.mock_repo = MagicMock()
        self.service.user_repository = self.mock_repo

    def test_register_success(self):
        """Test successful user registration"""
        # Arrange
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.get_by_email.return_value = None
        self.mock_repo.create.return_value = User(
            user_id=1,
            username="newuser",
            email="new@example.com",
            password_hash="hashed",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.register("newuser", "new@example.com", "password123")
        
        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["user"]["username"], "newuser")
        print("✅ test_register_success passed")

    def test_register_username_exists(self):
        """Test registration with existing username"""
        # Arrange
        self.mock_repo.get_by_username.return_value = User(username="existinguser")
        
        # Act
        result = self.service.register("existinguser", "new@example.com", "password")
        
        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Username already exists")
        print("✅ test_register_username_exists passed")

    def test_register_email_exists(self):
        """Test registration with existing email"""
        # Arrange
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.get_by_email.return_value = User(email="existing@example.com")
        
        # Act
        result = self.service.register("newuser", "existing@example.com", "password")
        
        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Email already exists")
        print("✅ test_register_email_exists passed")

    def test_get_user_by_id(self):
        """Test getting user by ID"""
        # Arrange
        self.mock_repo.get_by_id.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.get_user(user_id=1)
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["user_id"], 1)
        print("✅ test_get_user_by_id passed")

    def test_get_user_not_found(self):
        """Test getting user that doesn't exist"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.get_user(user_id=999)
        
        # Assert
        self.assertIsNone(result)
        print("✅ test_get_user_not_found passed")

    def test_update_profile_success(self):
        """Test successful profile update"""
        # Arrange
        existing_user = User(
            user_id=1,
            username="olduser",
            email="old@example.com",
            password_hash="oldhash",
            bio="Old bio",
            created_at=datetime.now()
        )
        self.mock_repo.get_by_id.return_value = existing_user
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.update.return_value = User(
            user_id=1,
            username="newuser",
            email="old@example.com",
            password_hash="oldhash",
            bio="New bio",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.update_profile(1, {"username": "newuser", "bio": "New bio"})
        
        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["user"]["username"], "newuser")
        print("✅ test_update_profile_success passed")

    def test_update_profile_user_not_found(self):
        """Test updating profile for non-existent user"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.update_profile(999, {"bio": "New bio"})
        
        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "User not found")
        print("✅ test_update_profile_user_not_found passed")

    def test_delete_account_success(self):
        """Test successful account deletion"""
        # Arrange
        self.mock_repo.get_by_id.return_value = User(user_id=1)
        self.mock_repo.delete.return_value = True
        
        # Act
        result = self.service.delete_account(1)
        
        # Assert
        self.assertTrue(result["success"])
        print("✅ test_delete_account_success passed")

    def test_delete_account_not_found(self):
        """Test deleting non-existent account"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None
        
        # Act
        result = self.service.delete_account(999)
        
        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "User not found")
        print("✅ test_delete_account_not_found passed")

    @patch('api.services.user_service.check_password_hash')
    def test_authenticate_success(self, mock_check_hash):
        """Test successful authentication"""
        # Arrange
        mock_check_hash.return_value = True
        self.mock_repo.get_by_email.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            created_at=datetime.now()
        )
        
        # Act
        result = self.service.authenticate("test@example.com", "password")
        
        # Assert
        self.assertTrue(result["success"])
        print("✅ test_authenticate_success passed")

    @patch('api.services.user_service.check_password_hash')
    def test_authenticate_wrong_password(self, mock_check_hash):
        """Test authentication with wrong password"""
        # Arrange
        mock_check_hash.return_value = False
        self.mock_repo.get_by_email.return_value = User(
            user_id=1,
            email="test@example.com",
            password_hash="hashed"
        )
        
        # Act
        result = self.service.authenticate("test@example.com", "wrongpassword")
        
        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid email or password")
        print("✅ test_authenticate_wrong_password passed")

    def test_authenticate_user_not_found(self):
        """Test authentication with non-existent email"""
        # Arrange
        self.mock_repo.get_by_email.return_value = None
        
        # Act
        result = self.service.authenticate("notfound@example.com", "password")
        
        # Assert
        self.assertFalse(result["success"])
        print("✅ test_authenticate_user_not_found passed")


if __name__ == "__main__":
    print("\n🧪 Testing UserRepository and UserService...\n")
    print("=" * 50)
    print("UserRepository Tests")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)

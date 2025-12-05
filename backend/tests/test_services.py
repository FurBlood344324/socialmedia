"""Tests for Service layer (AuthService and UserService)"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime

from api.entities.entities import User
from api.services.auth_service import AuthService
from api.services.user_service import UserService


class TestAuthService(unittest.TestCase):
    """Test cases for AuthService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = AuthService()
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
        self.mock_repo.get_by_username.return_value = User(
            username="existinguser",
            email="existing@example.com",
            password_hash="hash"
        )

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
        self.mock_repo.get_by_email.return_value = User(
            username="someuser",
            email="existing@example.com",
            password_hash="hash"
        )

        # Act
        result = self.service.register("newuser", "existing@example.com", "password")

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Email already exists")
        print("✅ test_register_email_exists passed")

    def test_register_with_optional_fields(self):
        """Test registration with bio and profile picture"""
        # Arrange
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.get_by_email.return_value = None
        self.mock_repo.create.return_value = User(
            user_id=1,
            username="newuser",
            email="new@example.com",
            password_hash="hashed",
            bio="Hello world",
            profile_picture_url="http://example.com/pic.jpg",
            is_private=True,
            created_at=datetime.now()
        )

        # Act
        result = self.service.register(
            username="newuser",
            email="new@example.com",
            password="password123",
            bio="Hello world",
            profile_picture_url="http://example.com/pic.jpg",
            is_private=True
        )

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["user"]["bio"], "Hello world")
        self.assertTrue(result["user"]["is_private"])
        print("✅ test_register_with_optional_fields passed")

    def test_register_create_fails(self):
        """Test registration when user creation fails"""
        # Arrange
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.get_by_email.return_value = None
        self.mock_repo.create.return_value = None

        # Act
        result = self.service.register("newuser", "new@example.com", "password")

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Failed to create user")
        print("✅ test_register_create_fails passed")

    @patch('api.services.auth_service.check_password_hash')
    @patch('api.services.auth_service.generate_token')
    def test_login_success(self, mock_generate_token, mock_check_hash):
        """Test successful login"""
        # Arrange
        mock_check_hash.return_value = True
        mock_generate_token.return_value = "test_jwt_token"
        self.mock_repo.get_by_username.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed",
            created_at=datetime.now()
        )

        # Act
        result = self.service.login("testuser", "password")

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["token"], "test_jwt_token")
        self.assertEqual(result["user"]["username"], "testuser")
        print("✅ test_login_success passed")

    @patch('api.services.auth_service.check_password_hash')
    def test_login_wrong_password(self, mock_check_hash):
        """Test login with wrong password"""
        # Arrange
        mock_check_hash.return_value = False
        self.mock_repo.get_by_username.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed"
        )

        # Act
        result = self.service.login("testuser", "wrongpassword")

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid username or password")
        print("✅ test_login_wrong_password passed")

    def test_login_user_not_found(self):
        """Test login with non-existent username"""
        # Arrange
        self.mock_repo.get_by_username.return_value = None

        # Act
        result = self.service.login("notfound", "password")

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Invalid username or password")
        print("✅ test_login_user_not_found passed")

    def test_get_user_by_id_success(self):
        """Test getting user by ID"""
        # Arrange
        self.mock_repo.get_by_id.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now()
        )

        # Act
        result = self.service.get_user_by_id(1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["user_id"], 1)
        self.assertEqual(result["username"], "testuser")
        print("✅ test_get_user_by_id_success passed")

    def test_get_user_by_id_not_found(self):
        """Test getting user by ID when not found"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None

        # Act
        result = self.service.get_user_by_id(999)

        # Assert
        self.assertIsNone(result)
        print("✅ test_get_user_by_id_not_found passed")


class TestUserService(unittest.TestCase):
    """Test cases for UserService"""

    def setUp(self):
        """Set up test fixtures"""
        self.service = UserService()
        self.mock_repo = MagicMock()
        self.service.user_repository = self.mock_repo

    def test_get_user_by_id(self):
        """Test getting user by ID"""
        # Arrange
        self.mock_repo.get_by_id.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now()
        )

        # Act
        result = self.service.get_user(user_id=1)

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["user_id"], 1)
        print("✅ test_get_user_by_id passed")

    def test_get_user_by_username(self):
        """Test getting user by username"""
        # Arrange
        self.mock_repo.get_by_username.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now()
        )

        # Act
        result = self.service.get_user(username="testuser")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["username"], "testuser")
        print("✅ test_get_user_by_username passed")

    def test_get_user_by_email(self):
        """Test getting user by email"""
        # Arrange
        self.mock_repo.get_by_email.return_value = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            created_at=datetime.now()
        )

        # Act
        result = self.service.get_user(email="test@example.com")

        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(result["email"], "test@example.com")
        print("✅ test_get_user_by_email passed")

    def test_get_user_not_found(self):
        """Test getting user that doesn't exist"""
        # Arrange
        self.mock_repo.get_by_id.return_value = None

        # Act
        result = self.service.get_user(user_id=999)

        # Assert
        self.assertIsNone(result)
        print("✅ test_get_user_not_found passed")

    def test_get_user_entity(self):
        """Test getting user entity by ID"""
        # Arrange
        expected_user = User(
            user_id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hash"
        )
        self.mock_repo.get_by_id.return_value = expected_user

        # Act
        result = self.service.get_user_entity(1)

        # Assert
        self.assertIsNotNone(result)
        self.assertIsInstance(result, User)
        self.assertEqual(result.user_id, 1)
        print("✅ test_get_user_entity passed")

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
        updated_user = User(
            user_id=1,
            username="newuser",
            email="old@example.com",
            password_hash="oldhash",
            bio="New bio",
            created_at=datetime.now()
        )
        self.mock_repo.get_by_id.return_value = existing_user
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.update.return_value = updated_user

        # Act
        result = self.service.update_profile(1, {"username": "newuser", "bio": "New bio"})

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["user"]["username"], "newuser")
        self.assertEqual(result["user"]["bio"], "New bio")
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

    def test_update_profile_username_exists(self):
        """Test updating profile with username that already exists"""
        # Arrange
        existing_user = User(
            user_id=1,
            username="olduser",
            email="old@example.com",
            password_hash="hash"
        )
        other_user = User(
            user_id=2,
            username="takenuser",
            email="taken@example.com",
            password_hash="hash"
        )
        self.mock_repo.get_by_id.return_value = existing_user
        self.mock_repo.get_by_username.return_value = other_user

        # Act
        result = self.service.update_profile(1, {"username": "takenuser"})

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Username already exists")
        print("✅ test_update_profile_username_exists passed")

    def test_update_profile_email_exists(self):
        """Test updating profile with email that already exists"""
        # Arrange
        existing_user = User(
            user_id=1,
            username="user1",
            email="old@example.com",
            password_hash="hash"
        )
        other_user = User(
            user_id=2,
            username="user2",
            email="taken@example.com",
            password_hash="hash"
        )
        self.mock_repo.get_by_id.return_value = existing_user
        self.mock_repo.get_by_username.return_value = None
        self.mock_repo.get_by_email.return_value = other_user

        # Act
        result = self.service.update_profile(1, {"email": "taken@example.com"})

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Email already exists")
        print("✅ test_update_profile_email_exists passed")

    def test_update_profile_password(self):
        """Test updating password"""
        # Arrange
        existing_user = User(
            user_id=1,
            username="user1",
            email="user@example.com",
            password_hash="oldhash",
            created_at=datetime.now()
        )
        updated_user = User(
            user_id=1,
            username="user1",
            email="user@example.com",
            password_hash="newhash",
            created_at=datetime.now()
        )
        self.mock_repo.get_by_id.return_value = existing_user
        self.mock_repo.update.return_value = updated_user

        # Act
        result = self.service.update_profile(1, {"password": "newpassword"})

        # Assert
        self.assertTrue(result["success"])
        self.mock_repo.update.assert_called_once()
        print("✅ test_update_profile_password passed")

    def test_update_profile_privacy(self):
        """Test updating is_private field"""
        # Arrange
        existing_user = User(
            user_id=1,
            username="user1",
            email="user@example.com",
            password_hash="hash",
            is_private=False,
            created_at=datetime.now()
        )
        updated_user = User(
            user_id=1,
            username="user1",
            email="user@example.com",
            password_hash="hash",
            is_private=True,
            created_at=datetime.now()
        )
        self.mock_repo.get_by_id.return_value = existing_user
        self.mock_repo.update.return_value = updated_user

        # Act
        result = self.service.update_profile(1, {"is_private": True})

        # Assert
        self.assertTrue(result["success"])
        self.assertTrue(result["user"]["is_private"])
        print("✅ test_update_profile_privacy passed")

    def test_delete_account_success(self):
        """Test successful account deletion"""
        # Arrange
        self.mock_repo.get_by_id.return_value = User(user_id=1, username="user", email="u@e.com", password_hash="h")
        self.mock_repo.delete.return_value = True

        # Act
        result = self.service.delete_account(1)

        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "Account deleted successfully")
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

    def test_delete_account_fails(self):
        """Test when account deletion fails"""
        # Arrange
        self.mock_repo.get_by_id.return_value = User(user_id=1, username="user", email="u@e.com", password_hash="h")
        self.mock_repo.delete.return_value = False

        # Act
        result = self.service.delete_account(1)

        # Assert
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Failed to delete account")
        print("✅ test_delete_account_fails passed")

    def test_search_users(self):
        """Test searching users"""
        # Arrange
        users = [
            User(user_id=1, username="john", email="john@example.com", password_hash="h", created_at=datetime.now()),
            User(user_id=2, username="johnny", email="johnny@example.com", password_hash="h", created_at=datetime.now())
        ]
        self.mock_repo.search.return_value = users

        # Act
        result = self.service.search_users("john", limit=20)

        # Assert
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["username"], "john")
        self.assertEqual(result[1]["username"], "johnny")
        print("✅ test_search_users passed")

    def test_search_users_empty(self):
        """Test searching users with no results"""
        # Arrange
        self.mock_repo.search.return_value = []

        # Act
        result = self.service.search_users("nonexistent")

        # Assert
        self.assertEqual(len(result), 0)
        print("✅ test_search_users_empty passed")

    def test_get_all_users(self):
        """Test getting all users with pagination"""
        # Arrange
        users = [
            User(user_id=1, username="user1", email="u1@example.com", password_hash="h", created_at=datetime.now()),
            User(user_id=2, username="user2", email="u2@example.com", password_hash="h", created_at=datetime.now())
        ]
        self.mock_repo.get_all.return_value = users

        # Act
        result = self.service.get_all_users(limit=100, offset=0)

        # Assert
        self.assertEqual(len(result), 2)
        print("✅ test_get_all_users passed")


if __name__ == "__main__":
    print("\n🧪 Testing Service Layer (AuthService and UserService)...\n")
    print("=" * 60)
    unittest.main(verbosity=2, exit=False)

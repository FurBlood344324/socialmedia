"""Tests for Middleware layer (JWT and Authorization)"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import jwt

from api.middleware.jwt import (
    encode_token, decode_token, decode_auth_token, generate_token, SECRET_KEY
)


class TestJWT(unittest.TestCase):
    """Test cases for JWT functions"""

    def test_encode_token(self):
        """Test encoding a payload to JWT token"""
        # Arrange
        payload = {
            "user_id": 1,
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }

        # Act
        token = encode_token(payload)

        # Assert
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)
        print("✅ test_encode_token passed")

    def test_decode_token_valid(self):
        """Test decoding a valid JWT token"""
        # Arrange
        payload = {
            "user_id": 1,
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = encode_token(payload)

        # Act
        decoded = decode_token(token)

        # Assert
        self.assertIsNotNone(decoded)
        self.assertEqual(decoded["user_id"], 1)
        self.assertEqual(decoded["username"], "testuser")
        print("✅ test_decode_token_valid passed")

    def test_decode_token_expired(self):
        """Test decoding an expired JWT token"""
        # Arrange
        payload = {
            "user_id": 1,
            "username": "testuser",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        # Act
        decoded = decode_token(token)

        # Assert
        self.assertIsNone(decoded)
        print("✅ test_decode_token_expired passed")

    def test_decode_token_invalid(self):
        """Test decoding an invalid JWT token"""
        # Arrange
        invalid_token = "invalid.token.here"

        # Act
        decoded = decode_token(invalid_token)

        # Assert
        self.assertIsNone(decoded)
        print("✅ test_decode_token_invalid passed")

    def test_decode_token_wrong_secret(self):
        """Test decoding a token signed with wrong secret"""
        # Arrange
        payload = {
            "user_id": 1,
            "username": "testuser",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, "wrong_secret", algorithm="HS256")

        # Act
        decoded = decode_token(token)

        # Assert
        self.assertIsNone(decoded)
        print("✅ test_decode_token_wrong_secret passed")

    def test_generate_token(self):
        """Test generating a token for a user"""
        # Act
        token = generate_token(user_id=1, username="testuser")

        # Assert
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

        # Verify token contents
        decoded = decode_token(token)
        self.assertEqual(decoded["user_id"], 1)
        self.assertEqual(decoded["username"], "testuser")
        self.assertIn("exp", decoded)
        self.assertIn("iat", decoded)
        print("✅ test_generate_token passed")

    def test_generate_token_no_role(self):
        """Test that generated token does not contain role"""
        # Act
        token = generate_token(user_id=1, username="testuser")

        # Assert
        decoded = decode_token(token)
        self.assertNotIn("role", decoded)
        print("✅ test_generate_token_no_role passed")


class TestDecodeAuthToken(unittest.TestCase):
    """Test cases for decode_auth_token that require Flask app context"""

    def setUp(self):
        """Set up Flask test app"""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

    def test_decode_auth_token_valid(self):
        """Test extracting and decoding token from Authorization header"""
        # Arrange
        token = generate_token(user_id=1, username="testuser")

        with self.app.test_request_context(headers={"Authorization": f"Bearer {token}"}):
            # Act
            payload = decode_auth_token()

            # Assert
            self.assertIsNotNone(payload)
            self.assertEqual(payload["user_id"], 1)
            self.assertEqual(payload["username"], "testuser")
        print("✅ test_decode_auth_token_valid passed")

    def test_decode_auth_token_no_header(self):
        """Test decode_auth_token with no Authorization header"""
        with self.app.test_request_context():
            # Act
            payload = decode_auth_token()

            # Assert
            self.assertIsNone(payload)
        print("✅ test_decode_auth_token_no_header passed")

    def test_decode_auth_token_no_bearer(self):
        """Test decode_auth_token without Bearer prefix"""
        # Arrange
        token = generate_token(user_id=1, username="testuser")

        with self.app.test_request_context(headers={"Authorization": token}):
            # Act
            payload = decode_auth_token()

            # Assert
            self.assertIsNone(payload)
        print("✅ test_decode_auth_token_no_bearer passed")

    def test_decode_auth_token_invalid_token(self):
        """Test decode_auth_token with invalid token"""
        with self.app.test_request_context(headers={"Authorization": "Bearer invalid.token.here"}):
            # Act
            payload = decode_auth_token()

            # Assert
            self.assertIsNone(payload)
        print("✅ test_decode_auth_token_invalid_token passed")


class TestAuthorization(unittest.TestCase):
    """Test cases for Authorization decorators"""

    def setUp(self):
        """Set up Flask test app"""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    @patch('api.middleware.authorization.decode_auth_token')
    def test_token_required_valid(self, mock_decode):
        """Test token_required decorator with valid token"""
        from api.middleware.authorization import token_required

        mock_decode.return_value = {"user_id": 1, "username": "testuser"}

        @self.app.route('/test')
        @token_required
        def test_route():
            from flask import g, jsonify
            return jsonify({"user_id": g.current_user_id, "username": g.current_username})

        # Act
        with self.app.test_client() as client:
            response = client.get('/test')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["user_id"], 1)
        self.assertEqual(data["username"], "testuser")
        print("✅ test_token_required_valid passed")

    @patch('api.middleware.authorization.decode_auth_token')
    def test_token_required_no_token(self, mock_decode):
        """Test token_required decorator without token"""
        from api.middleware.authorization import token_required

        mock_decode.return_value = None

        @self.app.route('/test2')
        @token_required
        def test_route():
            from flask import jsonify
            return jsonify({"message": "success"})

        # Act
        with self.app.test_client() as client:
            response = client.get('/test2')

        # Assert
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["error"], "Unauthorized")
        print("✅ test_token_required_no_token passed")

    @patch('api.middleware.authorization.decode_auth_token')
    def test_token_required_no_user_id(self, mock_decode):
        """Test token_required decorator with token but no user_id"""
        from api.middleware.authorization import token_required

        mock_decode.return_value = {"username": "testuser"}  # No user_id

        @self.app.route('/test3')
        @token_required
        def test_route():
            from flask import jsonify
            return jsonify({"message": "success"})

        # Act
        with self.app.test_client() as client:
            response = client.get('/test3')

        # Assert
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["error"], "Unauthorized")
        print("✅ test_token_required_no_user_id passed")

    @patch('api.middleware.authorization.decode_auth_token')
    def test_get_user_id_valid(self, mock_decode):
        """Test get_user_id decorator with valid token"""
        from api.middleware.authorization import get_user_id

        mock_decode.return_value = {"user_id": 42, "username": "testuser"}

        @self.app.route('/getuserid')
        @get_user_id()
        def test_route():
            from flask import jsonify
            return jsonify({"error": "Should not reach here"})

        # Act
        with self.app.test_client() as client:
            response = client.get('/getuserid')

        # Assert
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["user_id"], 42)
        print("✅ test_get_user_id_valid passed")

    @patch('api.middleware.authorization.decode_auth_token')
    def test_get_user_id_no_token(self, mock_decode):
        """Test get_user_id decorator without token"""
        from api.middleware.authorization import get_user_id

        mock_decode.return_value = None

        @self.app.route('/getuserid2')
        @get_user_id()
        def test_route():
            from flask import jsonify
            return jsonify({"error": "Should not reach here"})

        # Act
        with self.app.test_client() as client:
            response = client.get('/getuserid2')

        # Assert
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data["error"], "Unauthorized")
        print("✅ test_get_user_id_no_token passed")


class TestCommunityPermissions(unittest.TestCase):
    """Test cases for Community Permissions"""

    def test_has_community_permission_admin(self):
        """Test admin has all community permissions"""
        from api.permissions.permissions import has_community_permission

        # Assert
        self.assertTrue(has_community_permission("admin", "can_delete_posts"))
        self.assertTrue(has_community_permission("admin", "can_delete_comments"))
        self.assertTrue(has_community_permission("admin", "can_remove_members"))
        self.assertTrue(has_community_permission("admin", "can_edit_community"))
        self.assertTrue(has_community_permission("admin", "can_manage_roles"))
        print("✅ test_has_community_permission_admin passed")

    def test_has_community_permission_moderator(self):
        """Test moderator has limited community permissions"""
        from api.permissions.permissions import has_community_permission

        # Assert
        self.assertTrue(has_community_permission("moderator", "can_delete_posts"))
        self.assertTrue(has_community_permission("moderator", "can_delete_comments"))
        self.assertTrue(has_community_permission("moderator", "can_remove_members"))
        self.assertFalse(has_community_permission("moderator", "can_edit_community"))
        self.assertFalse(has_community_permission("moderator", "can_manage_roles"))
        print("✅ test_has_community_permission_moderator passed")

    def test_has_community_permission_member(self):
        """Test member has no special community permissions"""
        from api.permissions.permissions import has_community_permission

        # Assert
        self.assertFalse(has_community_permission("member", "can_delete_posts"))
        self.assertFalse(has_community_permission("member", "can_delete_comments"))
        self.assertFalse(has_community_permission("member", "can_remove_members"))
        self.assertFalse(has_community_permission("member", "can_edit_community"))
        self.assertFalse(has_community_permission("member", "can_manage_roles"))
        print("✅ test_has_community_permission_member passed")

    def test_has_community_permission_invalid_role(self):
        """Test invalid role returns False"""
        from api.permissions.permissions import has_community_permission

        # Assert
        self.assertFalse(has_community_permission("invalid_role", "can_delete_posts"))
        self.assertFalse(has_community_permission("", "can_delete_posts"))
        print("✅ test_has_community_permission_invalid_role passed")

    def test_has_community_permission_invalid_permission(self):
        """Test invalid permission returns False"""
        from api.permissions.permissions import has_community_permission

        # Assert
        self.assertFalse(has_community_permission("admin", "invalid_permission"))
        self.assertFalse(has_community_permission("admin", ""))
        print("✅ test_has_community_permission_invalid_permission passed")


if __name__ == "__main__":
    print("\n🧪 Testing Middleware Layer (JWT and Authorization)...\n")
    print("=" * 60)
    unittest.main(verbosity=2, exit=False)

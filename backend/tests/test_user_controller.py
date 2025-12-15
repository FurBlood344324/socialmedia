from tests.base_test import BaseTest

class TestUserController(BaseTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()

    def test_register_endpoint(self):
        resp = self.client.post('/api/auth/register', json={
            "username": "apitest",
            "email": "api@test.com",
            "password": "password123",
            "bio": "API user"
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["success"] is True
        assert data["user"]["username"] == "apitest"

    def test_login_endpoint(self):
        # Create user first
        self.client.post('/api/auth/register', json={
            "username": "logintest",
            "email": "login@test.com",
            "password": "password123"
        })
        
        # Login
        resp = self.client.post('/api/auth/login', json={
            "username": "logintest",
            "password": "password123"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data
        return data["token"]

    def test_get_me_protected_route(self):
        token = self.test_login_endpoint()
        
        # Access /api/auth/me
        resp = self.client.get('/api/auth/me', headers={
            "Authorization": f"Bearer {token}"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["user"]["username"] == "logintest"

    def test_update_profile(self):
        token = self.test_login_endpoint()
        
        # Update Profile
        resp = self.client.put('/api/auth/me', 
            headers={"Authorization": f"Bearer {token}"},
            json={"bio": "Updated Bio", "is_private": True}
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["success"] is True
        
        # Verify changes
        resp = self.client.get('/api/auth/me', headers={"Authorization": f"Bearer {token}"})
        assert resp.get_json()["user"]["bio"] == "Updated Bio"
        assert resp.get_json()["user"]["is_private"] is True

    def test_user_search_and_discovery(self):
        token = self.test_login_endpoint()
        
        # Search for self
        resp = self.client.get('/api/auth/users/search?q=login', 
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["users"]) >= 1
        assert data["users"][0]["username"] == "logintest"
        
        # Get recommendations
        resp = self.client.get('/api/auth/users/recommendations',
             headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert "recommendations" in resp.get_json()

    def test_get_other_user_profile(self):
        token = self.test_login_endpoint() # Logged in as logintest
        
        # Create another user 'other'
        self.client.post('/api/auth/register', json={
            "username": "other",
            "email": "other@test.com",
            "password": "password"
        })
        
        # Get by username
        resp = self.client.get('/api/auth/users/username/other',
            headers={"Authorization": f"Bearer {token}"}
        )
        assert resp.status_code == 200
        assert resp.get_json()["user"]["username"] == "other"


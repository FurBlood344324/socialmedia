from tests.base_test import BaseTest

class TestFollowController(BaseTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()
        
        # U1 Token
        self.client.post('/api/auth/register', json={"username": "u1", "email": "u1@e.com", "password": "p"})
        r = self.client.post('/api/auth/login', json={"username": "u1", "password": "p"})
        self.token1 = r.get_json()['token']
        self.id1 = r.get_json()['user']['user_id']
        
        # U2 Token
        self.client.post('/api/auth/register', json={"username": "u2", "email": "u2@e.com", "password": "p"})
        r = self.client.post('/api/auth/login', json={"username": "u2", "password": "p"})
        self.token2 = r.get_json()['token']
        self.id2 = r.get_json()['user']['user_id']

    def test_follow_api(self):
        # U1 follows U2 (LinkedIn-style: goes to pending)
        resp = self.client.post(f'/api/users/{self.id2}/follow',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 201
        
        # Check Following list of U1 (should be empty - request is pending)
        resp = self.client.get(f'/api/users/{self.id1}/following',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 200
        following = resp.get_json()['following']
        assert len(following) == 0  # Pending requests don't show in following list
        
        # U2 accepts the request
        resp = self.client.post(f'/api/me/follow-requests/{self.id1}/accept',
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        assert resp.status_code == 200
        
        # Now check both users are following each other (mutual connection)
        resp = self.client.get(f'/api/users/{self.id1}/following',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        following = resp.get_json()['following']
        assert len(following) == 1
        assert following[0]['user_id'] == self.id2
        
        resp = self.client.get(f'/api/users/{self.id2}/following',
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        following = resp.get_json()['following']
        assert len(following) == 1
        assert following[0]['user_id'] == self.id1
        
        # Unfollow (should break mutual connection)
        resp = self.client.delete(f'/api/users/{self.id2}/follow',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 200
        
        # Both should have empty following lists
        resp = self.client.get(f'/api/users/{self.id1}/following',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert len(resp.get_json()['following']) == 0
        
        resp = self.client.get(f'/api/users/{self.id2}/following',
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        assert len(resp.get_json()['following']) == 0

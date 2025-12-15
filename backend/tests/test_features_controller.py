from tests.base_test import BaseTest

class TestFeaturesController(BaseTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()

    def test_popular_posts_endpoint(self):
        resp = self.client.get('/api/features/posts/popular')
        assert resp.status_code == 200
        assert 'posts' in resp.get_json()

    def test_active_users_endpoint(self):
        resp = self.client.get('/api/features/users/active')
        assert resp.status_code == 200
        assert 'users' in resp.get_json()

    def test_community_stats_endpoint(self):
        # Create community first
        self.client.post('/api/auth/register', json={"username": "f_user", "email": "f@t.com", "password": "p"})
        token = self.client.post('/api/auth/login', json={"username": "f_user", "password": "p"}).get_json()['token']
        
        resp = self.client.post('/api/communities',
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Stats Comm", "description": "Desc"}
        )
        cid = resp.get_json()['community']['id']
        
        # Get stats
        resp = self.client.get(f'/api/features/communities/{cid}/stats')
        assert resp.status_code == 200
        assert resp.get_json()['community_name'] == "Stats Comm"

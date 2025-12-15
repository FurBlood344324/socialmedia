from tests.base_test import BaseTest

class TestCommunityController(BaseTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()
        
        # User 1 (Creator)
        self.client.post('/api/auth/register', json={"username": "c1", "email": "c1@t.com", "password": "p"})
        r = self.client.post('/api/auth/login', json={"username": "c1", "password": "p"})
        self.token1 = r.get_json()['token']
        
        # User 2 (Joiner)
        self.client.post('/api/auth/register', json={"username": "c2", "email": "c2@t.com", "password": "p"})
        r = self.client.post('/api/auth/login', json={"username": "c2", "password": "p"})
        self.token2 = r.get_json()['token']

    def test_community_api_lifecycle(self):
        # 1. Create
        resp = self.client.post('/api/communities',
            headers={"Authorization": f"Bearer {self.token1}"},
            json={"name": "API Comm", "description": "Desc"}
        )
        assert resp.status_code == 201
        cid = resp.get_json()['community']['id']
        
        # 2. Join (U2)
        resp = self.client.post(f'/api/communities/{cid}/join',
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        assert resp.status_code == 201
        
        # 3. Get Members
        resp = self.client.get(f'/api/communities/{cid}/members',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 200
        assert resp.status_code == 200
        assert len(resp.get_json()['members']) == 2

    def test_community_search(self):
        # Create communities
        resp = self.client.post('/api/communities',
            headers={"Authorization": f"Bearer {self.token1}"},
            json={"name": "Python Devs", "description": "Python developers group"}
        )
        assert resp.status_code == 201
        
        # Search exact
        resp = self.client.get('/api/communities/search?q=Python',
             headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 200
        assert len(resp.get_json()['communities']) >= 1
        assert resp.get_json()['communities'][0]['name'] == 'Python Devs'

    def test_community_admin_actions(self):
        # Create community
        resp = self.client.post('/api/communities',
            headers={"Authorization": f"Bearer {self.token1}"},
            json={"name": "To Delete", "description": "Desc"}
        )
        cid = resp.get_json()['community']['id']
        
        # Update (Creator/Admin)
        resp = self.client.put(f'/api/communities/{cid}',
            headers={"Authorization": f"Bearer {self.token1}"},
            json={"name": "Updated Name", "description": "New Desc"}
        )
        assert resp.status_code == 200
        assert resp.get_json()['community']['name'] == "Updated Name"
        
        # Update (Non-admin - should fail)
        resp = self.client.put(f'/api/communities/{cid}',
            headers={"Authorization": f"Bearer {self.token2}"},
            json={"name": "Hacked"}
        )
        assert resp.status_code == 403
        
        # Delete (Creator/Admin)
        resp = self.client.delete(f'/api/communities/{cid}',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 200
        
        # Verify deletion
        resp = self.client.get(f'/api/communities/{cid}',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 404

    def test_role_management(self):
        # Create community
        resp = self.client.post('/api/communities',
            headers={"Authorization": f"Bearer {self.token1}"},
            json={"name": "Role Test", "description": "Desc"}
        )
        cid = resp.get_json()['community']['id']
        
        # User 2 joins
        self.client.post(f'/api/communities/{cid}/join',
            headers={"Authorization": f"Bearer {self.token2}"}
        )
        
        # Get U2 ID (from member list or login response)
        # Login response had user_id? Not stored in setUp.
        # But U2 joined, so we can find user_id from members list
        resp = self.client.get(f'/api/communities/{cid}/members', 
             headers={"Authorization": f"Bearer {self.token1}"}
        )
        members = resp.get_json()['members']
        u2_id = next(m['user_id'] for m in members if m['username'] == 'c2')
        
        # Promote U2 to Moderator (role_id=2)
        resp = self.client.put(f'/api/communities/{cid}/members/{u2_id}/role',
            headers={"Authorization": f"Bearer {self.token1}"},
            json={"role_id": 2}
        )
        assert resp.status_code == 200
        
        # Verify role
        resp = self.client.get(f'/api/communities/{cid}/members', 
             headers={"Authorization": f"Bearer {self.token1}"}
        )
        members = resp.get_json()['members']
        u2_member = next(m for m in members if m['user_id'] == u2_id)
        assert u2_member['role_id'] == 2
        
        # Kick U2
        resp = self.client.delete(f'/api/communities/{cid}/members/{u2_id}',
            headers={"Authorization": f"Bearer {self.token1}"}
        )
        assert resp.status_code == 200
        
        # Verify kicked
        resp = self.client.get(f'/api/communities/{cid}/members', 
             headers={"Authorization": f"Bearer {self.token1}"}
        )
        members = resp.get_json()['members']
        assert not any(m['user_id'] == u2_id for m in members)

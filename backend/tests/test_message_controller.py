from tests.base_test import BaseTest

class TestMessageController(BaseTest):
    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()
        
        # U1
        self.client.post('/api/auth/register', json={"username": "m1", "email": "m1@e.com", "password": "p"})
        r = self.client.post('/api/auth/login', json={"username": "m1", "password": "p"})
        self.t1 = r.get_json()['token']
        self.id1 = r.get_json()['user']['user_id']
        
        # U2
        self.client.post('/api/auth/register', json={"username": "m2", "email": "m2@e.com", "password": "p"})
        r = self.client.post('/api/auth/login', json={"username": "m2", "password": "p"})
        self.t2 = r.get_json()['token']
        self.id2 = r.get_json()['user']['user_id']
        
        # U1 follows U2 (required for messaging)
        self.client.post(f'/api/users/{self.id2}/follow',
            headers={"Authorization": f"Bearer {self.t1}"}
        )

    def test_message_flow(self):
        # 1. Send (U1 -> U2)
        resp = self.client.post('/api/messages',
            headers={"Authorization": f"Bearer {self.t1}"},
            json={"receiver_id": self.id2, "content": "API Msg"}
        )
        assert resp.status_code == 201
        mid = resp.get_json()['message']['message_id']
        
        # 2. Check Inbox (U2)
        resp = self.client.get('/api/messages/conversations',
            headers={"Authorization": f"Bearer {self.t2}"}
        )
        assert resp.status_code == 200
        convs = resp.get_json()['conversations']
        assert len(convs) >= 1
        
        # 3. Read (U2)
        resp = self.client.put(f'/api/messages/{mid}/read',
            headers={"Authorization": f"Bearer {self.t2}"}
        )
        assert resp.status_code == 200


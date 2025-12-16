from tests.base_test import BaseTest
from api.services.follow_service import FollowService
from api.services.auth_service import AuthService

class TestFollowService(BaseTest):
    def setUp(self):
        super().setUp()
        self.follow_service = FollowService()
        self.auth_service = AuthService()
        
        # Public user
        r1 = self.auth_service.register("pub", "pub@e.com", "p")
        self.pub_id = r1['user']['user_id']
        
        # Private user
        r2 = self.auth_service.register("priv", "priv@e.com", "p", is_private=True)
        self.priv_id = r2['user']['user_id']
        
        # Follower
        r3 = self.auth_service.register("follower", "f@e.com", "p")
        self.follower_id = r3['user']['user_id']

    def test_follow_public_now_pending(self):
        # LinkedIn-style: all follow requests go to pending
        res = self.follow_service.follow_user(self.follower_id, self.pub_id)
        assert res['success'] is True
        assert res['status'] == "pending"

    def test_follow_private_pending(self):
        res = self.follow_service.follow_user(self.follower_id, self.priv_id)
        assert res['success'] is True
        assert res['status'] == "pending"
        
        # Accept flow
        acc_res = self.follow_service.accept_follow_request(self.follower_id, self.priv_id) # Args: follower_id, following_id (me)
        assert acc_res['success'] is True
        assert acc_res['follow']['status_id'] == 2

    def test_unfollow(self):
        self.follow_service.follow_user(self.follower_id, self.pub_id)
        res = self.follow_service.unfollow_user(self.follower_id, self.pub_id)
        assert res['success'] is True

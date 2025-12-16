from tests.base_test import BaseTest
from api.services.follow_service import FollowService
from api.services.auth_service import AuthService

class TestMutualFollow(BaseTest):
    def setUp(self):
        super().setUp()
        self.follow_service = FollowService()
        self.auth_service = AuthService()
        
        # Create two users
        r1 = self.auth_service.register("user1", "user1@e.com", "p")
        self.user1_id = r1['user']['user_id']
        
        r2 = self.auth_service.register("user2", "user2@e.com", "p")
        self.user2_id = r2['user']['user_id']

    def test_accept_creates_mutual_follow(self):
        """Test that accepting a follow request creates mutual connection"""
        # User1 follows User2
        res = self.follow_service.follow_user(self.user1_id, self.user2_id)
        assert res['success'] is True
        assert res['status'] == "pending"
        
        # User2 accepts the request
        acc_res = self.follow_service.accept_follow_request(self.user1_id, self.user2_id)
        assert acc_res['success'] is True
        
        # Check that both users are now following each other
        user1_following = self.follow_service.get_following(self.user1_id)
        user2_following = self.follow_service.get_following(self.user2_id)
        
        # User1 should be following User2
        assert len(user1_following) == 1
        assert user1_following[0]['user_id'] == self.user2_id
        
        # User2 should be following User1 (mutual)
        assert len(user2_following) == 1
        assert user2_following[0]['user_id'] == self.user1_id

    def test_unfollow_breaks_mutual_connection(self):
        """Test that unfollowing breaks the mutual connection"""
        # Create mutual connection
        self.follow_service.follow_user(self.user1_id, self.user2_id)
        self.follow_service.accept_follow_request(self.user1_id, self.user2_id)
        
        # User1 unfollows User2
        unfollow_res = self.follow_service.unfollow_user(self.user1_id, self.user2_id)
        assert unfollow_res['success'] is True
        
        # Check that both users are no longer following each other
        user1_following = self.follow_service.get_following(self.user1_id)
        user2_following = self.follow_service.get_following(self.user2_id)
        
        # Neither should be following the other
        assert len(user1_following) == 0
        assert len(user2_following) == 0

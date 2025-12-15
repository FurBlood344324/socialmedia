from tests.base_test import BaseTest
from api.services.post_service import PostService
from api.services.auth_service import AuthService

class TestPostService(BaseTest):
    def setUp(self):
        super().setUp()
        self.post_service = PostService()
        self.auth_service = AuthService()
        
        # Register main user
        res = self.auth_service.register("poster", "p@s.com", "pass")
        self.user_id = res['user']['user_id']

    def test_create_validate_post(self):
        # Empty content should fail
        res = self.post_service.create_post(self.user_id, content="")
        assert res['success'] is False
        
        # Valid post
        res = self.post_service.create_post(self.user_id, content="Valid Content")
        assert res['success'] is True
        assert res['post']['content'] == "Valid Content"

    def test_delete_ownership(self):
        # User 1 creates post
        res = self.post_service.create_post(self.user_id, content="To Delete")
        post_id = res['post']['post_id']
        
        # User 2 tries to delete
        res2 = self.auth_service.register("hacker", "h@s.com", "pass")
        hacker_id = res2['user']['user_id']
        
        del_res = self.post_service.delete_post(post_id, hacker_id)
        assert del_res['success'] is False
        assert "own posts" in del_res['error'].lower()
        
        # User 1 deletes
        del_res = self.post_service.delete_post(post_id, self.user_id)
        assert del_res['success'] is True


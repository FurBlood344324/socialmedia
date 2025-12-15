from tests.base_test import BaseTest
from api.services.message_service import MessageService
from api.services.auth_service import AuthService
from api.services.follow_service import FollowService

class TestMessageService(BaseTest):
    def setUp(self):
        super().setUp()
        self.msg_service = MessageService()
        self.auth_service = AuthService()
        self.follow_service = FollowService()
        
        r1 = self.auth_service.register("s_svc", "s@s.com", "p")
        self.sid = r1['user']['user_id']
        r2 = self.auth_service.register("r_svc", "r@s.com", "p")
        self.rid = r2['user']['user_id']
        
        # Create follow relationship (sender follows receiver)
        self.follow_service.follow_user(self.sid, self.rid)

    def test_send_and_read(self):
        # Send
        res = self.msg_service.send_message(self.sid, self.rid, "Hello Service")
        assert res['success'] is True
        mid = res['message']['message_id']
        
        # Unread count
        count_res = self.msg_service.get_unread_count(self.rid)
        assert count_res['unread_count'] == 1
        
        # Mark read
        read_res = self.msg_service.mark_as_read(mid, self.rid)
        assert read_res['success'] is True
        assert read_res['message']['is_read'] is True

    def test_delete_ownership(self):
        res = self.msg_service.send_message(self.sid, self.rid, "To Delete")
        mid = res['message']['message_id']
        
        # Receiver cannot delete (in this implementation usually only sender or both? Service says 'Only sender can delete')
        del_res = self.msg_service.delete_message(mid, self.rid)
        assert del_res['success'] is False
        
        # Sender can delete
        del_res = self.msg_service.delete_message(mid, self.sid)
        assert del_res['success'] is True


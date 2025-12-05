"""Test file for entity models validation"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from api.entities.entities import (
    Role, PrivacyType, FollowStatus, User, Post, 
    Comment, Community, CommunityMember, Follow, Message
)


def test_role():
    role = Role(role_id=1, role_name="admin")
    assert role.role_id == 1
    assert role.role_name == "admin"
    print("✅ Role model OK")


def test_privacy_type():
    privacy = PrivacyType(privacy_id=1, privacy_name="public")
    assert privacy.privacy_id == 1
    assert privacy.privacy_name == "public"
    print("✅ PrivacyType model OK")


def test_follow_status():
    status = FollowStatus(status_id=1, status_name="pending")
    assert status.status_id == 1
    assert status.status_name == "pending"
    print("✅ FollowStatus model OK")


def test_user():
    user = User(
        user_id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        bio="Hello world",
        profile_picture_url="http://example.com/pic.jpg",
        is_private=False,
        created_at=datetime.now()
    )
    assert user.user_id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_private == False
    print("✅ User model OK")


def test_post():
    post = Post(
        post_id=1,
        user_id=1,
        community_id=None,
        content="Test post content",
        media_url=None,
        created_at=datetime.now()
    )
    assert post.post_id == 1
    assert post.user_id == 1
    assert post.content == "Test post content"
    print("✅ Post model OK")


def test_comment():
    comment = Comment(
        comment_id=1,
        post_id=1,
        user_id=1,
        content="Test comment",
        created_at=datetime.now()
    )
    assert comment.comment_id == 1
    assert comment.post_id == 1
    assert comment.user_id == 1
    print("✅ Comment model OK")


def test_community():
    community = Community(
        community_id=1,
        name="Test Community",
        description="A test community",
        creator_id=1,
        privacy_id=1,
        created_at=datetime.now()
    )
    assert community.community_id == 1
    assert community.name == "Test Community"
    assert community.creator_id == 1
    print("✅ Community model OK")


def test_community_member():
    member = CommunityMember(
        community_id=1,
        user_id=1,
        role_id=1,
        joined_at=datetime.now()
    )
    assert member.community_id == 1
    assert member.user_id == 1
    assert member.role_id == 1
    print("✅ CommunityMember model OK")


def test_follow():
    follow = Follow(
        follower_id=1,
        following_id=2,
        status_id=1,
        created_at=datetime.now()
    )
    assert follow.follower_id == 1
    assert follow.following_id == 2
    assert follow.status_id == 1
    print("✅ Follow model OK")


def test_message():
    message = Message(
        message_id=1,
        sender_id=1,
        receiver_id=2,
        content="Hello!",
        media_url=None,
        is_read=False,
        created_at=datetime.now()
    )
    assert message.message_id == 1
    assert message.sender_id == 1
    assert message.receiver_id == 2
    assert message.is_read == False
    print("✅ Message model OK")


def test_default_values():
    """Test that default values work correctly"""
    user = User()
    assert user.is_private == False
    
    message = Message()
    assert message.is_read == False
    
    print("✅ Default values OK")


if __name__ == "__main__":
    print("\n🧪 Testing Entity Models...\n")
    
    test_role()
    test_privacy_type()
    test_follow_status()
    test_user()
    test_post()
    test_comment()
    test_community()
    test_community_member()
    test_follow()
    test_message()
    test_default_values()
    
    print("\n✅ All entity tests passed!\n")
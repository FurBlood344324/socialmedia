# Entity classes for the Social Media application
# Based on database tables: users, posts, comments, communities, 
# community_members, follow, follow_status, messages, privacy_types, roles

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Role:
    """Role model for community member roles (admin, moderator, member, etc.)"""
    role_id: Optional[int] = None
    role_name: Optional[str] = None


@dataclass
class PrivacyType:
    """PrivacyType model for community privacy settings"""
    privacy_id: Optional[int] = None
    privacy_name: Optional[str] = None


@dataclass
class FollowStatus:
    """FollowStatus model for follow request states (pending, accepted, rejected)"""
    status_id: Optional[int] = None
    status_name: Optional[str] = None


@dataclass
class User:
    """User model representing application users"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    is_private: bool = False
    created_at: Optional[datetime] = None


@dataclass
class Post:
    """Post model for user posts"""
    post_id: Optional[int] = None
    user_id: Optional[int] = None
    community_id: Optional[int] = None
    content: Optional[str] = None
    media_url: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Comment:
    """Comment model for post comments"""
    comment_id: Optional[int] = None
    post_id: Optional[int] = None
    user_id: Optional[int] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None


@dataclass
class Community:
    """Community model for user communities/groups"""
    community_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[int] = None
    privacy_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class CommunityMember:
    """CommunityMember model for community membership with roles"""
    community_id: Optional[int] = None
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    joined_at: Optional[datetime] = None


@dataclass
class Follow:
    """Follow model for user follow relationships"""
    follower_id: Optional[int] = None
    following_id: Optional[int] = None
    status_id: Optional[int] = None
    created_at: Optional[datetime] = None


@dataclass
class Message:
    """Message model for direct messages between users"""
    message_id: Optional[int] = None
    sender_id: Optional[int] = None
    receiver_id: Optional[int] = None
    content: Optional[str] = None
    media_url: Optional[str] = None
    is_read: bool = False
    created_at: Optional[datetime] = None

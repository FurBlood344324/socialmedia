# Entity classes for the Social Media application

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class Role:
    """Role model for community member roles (admin, moderator, member, etc.)"""
    role_id: Optional[int] = None
    role_name: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> Optional['Role']:
        if row is None:
            return None
        return cls(role_id=row.role_id, role_name=row.role_name)

    def to_dict(self) -> Dict[str, Any]:
        return {"role_id": self.role_id, "role_name": self.role_name}


@dataclass
class PrivacyType:
    """PrivacyType model for community privacy settings"""
    privacy_id: Optional[int] = None
    privacy_name: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> Optional['PrivacyType']:
        if row is None:
            return None
        return cls(privacy_id=row.privacy_id, privacy_name=row.privacy_name)

    def to_dict(self) -> Dict[str, Any]:
        return {"privacy_id": self.privacy_id, "privacy_name": self.privacy_name}


@dataclass
class FollowStatus:
    """FollowStatus model for follow request states (pending, accepted, rejected)"""
    status_id: Optional[int] = None
    status_name: Optional[str] = None

    @classmethod
    def from_row(cls, row) -> Optional['FollowStatus']:
        if row is None:
            return None
        return cls(status_id=row.status_id, status_name=row.status_name)

    def to_dict(self) -> Dict[str, Any]:
        return {"status_id": self.status_id, "status_name": self.status_name}


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

    @classmethod
    def from_row(cls, row) -> Optional['User']:
        if row is None:
            return None
        return cls(
            user_id=row.user_id,
            username=row.username,
            email=row.email,
            password_hash=row.password_hash,
            bio=row.bio,
            profile_picture_url=row.profile_picture_url,
            is_private=row.is_private,
            created_at=row.created_at
        )

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert to dict. Set include_sensitive=True to include password_hash."""
        data = {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "bio": self.bio,
            "profile_picture_url": self.profile_picture_url,
            "is_private": self.is_private,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data["password_hash"] = self.password_hash
        return data

    def validate(self) -> List[str]:
        """Returns list of validation errors, empty if valid."""
        errors = []
        if not self.username or len(self.username) < 3:
            errors.append("Username must be at least 3 characters")
        if self.username and len(self.username) > 50:
            errors.append("Username must be at most 50 characters")
        if not self.email or '@' not in self.email:
            errors.append("Invalid email format")
        return errors


@dataclass
class Post:
    """Post model for user posts"""
    post_id: Optional[int] = None
    user_id: Optional[int] = None
    community_id: Optional[int] = None
    content: Optional[str] = None
    media_url: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional['Post']:
        if row is None:
            return None
        return cls(
            post_id=row.post_id,
            user_id=row.user_id,
            community_id=row.community_id,
            content=row.content,
            media_url=row.media_url,
            created_at=row.created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "community_id": self.community_id,
            "content": self.content,
            "media_url": self.media_url,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def validate(self) -> List[str]:
        errors = []
        if not self.content and not self.media_url:
            errors.append("Post must have content or media")
        if self.content and len(self.content) > 5000:
            errors.append("Content must be at most 5000 characters")
        return errors


@dataclass
class PostLike:
    """PostLike model for post likes"""
    post_id: Optional[int] = None
    user_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional['PostLike']:
        if row is None:
            return None
        return cls(
            post_id=row.post_id,
            user_id=row.user_id,
            created_at=row.created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "post_id": self.post_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


@dataclass
class Comment:
    """Comment model for post comments"""
    comment_id: Optional[int] = None
    post_id: Optional[int] = None
    user_id: Optional[int] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional['Comment']:
        if row is None:
            return None
        return cls(
            comment_id=row.comment_id,
            post_id=row.post_id,
            user_id=row.user_id,
            content=row.content,
            created_at=row.created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "comment_id": self.comment_id,
            "post_id": self.post_id,
            "user_id": self.user_id,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def validate(self) -> List[str]:
        errors = []
        if not self.content or len(self.content.strip()) == 0:
            errors.append("Comment content is required")
        if self.content and len(self.content) > 2000:
            errors.append("Comment must be at most 2000 characters")
        return errors


@dataclass
class Community:
    """Community model for user communities/groups"""
    community_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    creator_id: Optional[int] = None
    privacy_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional['Community']:
        if row is None:
            return None
        return cls(
            community_id=row.community_id,
            name=row.name,
            description=row.description,
            creator_id=row.creator_id,
            privacy_id=row.privacy_id,
            created_at=row.created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "community_id": self.community_id,
            "name": self.name,
            "description": self.description,
            "creator_id": self.creator_id,
            "privacy_id": self.privacy_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def validate(self) -> List[str]:
        errors = []
        if not self.name or len(self.name) < 3:
            errors.append("Community name must be at least 3 characters")
        if self.name and len(self.name) > 100:
            errors.append("Community name must be at most 100 characters")
        return errors


@dataclass
class CommunityMember:
    """CommunityMember model for community membership with roles"""
    community_id: Optional[int] = None
    user_id: Optional[int] = None
    role_id: Optional[int] = None
    joined_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional['CommunityMember']:
        if row is None:
            return None
        return cls(
            community_id=row.community_id,
            user_id=row.user_id,
            role_id=row.role_id,
            joined_at=row.joined_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "community_id": self.community_id,
            "user_id": self.user_id,
            "role_id": self.role_id,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None
        }


@dataclass
class Follow:
    """Follow model for user follow relationships"""
    follower_id: Optional[int] = None
    following_id: Optional[int] = None
    status_id: Optional[int] = None
    created_at: Optional[datetime] = None

    @classmethod
    def from_row(cls, row) -> Optional['Follow']:
        if row is None:
            return None
        return cls(
            follower_id=row.follower_id,
            following_id=row.following_id,
            status_id=row.status_id,
            created_at=row.created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "follower_id": self.follower_id,
            "following_id": self.following_id,
            "status_id": self.status_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


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

    @classmethod
    def from_row(cls, row) -> Optional['Message']:
        if row is None:
            return None
        return cls(
            message_id=row.message_id,
            sender_id=row.sender_id,
            receiver_id=row.receiver_id,
            content=row.content,
            media_url=row.media_url,
            is_read=row.is_read,
            created_at=row.created_at
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "content": self.content,
            "media_url": self.media_url,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def validate(self) -> List[str]:
        errors = []
        if not self.content and not self.media_url:
            errors.append("Message must have content or media")
        if self.content and len(self.content) > 5000:
            errors.append("Message must be at most 5000 characters")
        return errors

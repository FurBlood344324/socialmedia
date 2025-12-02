from sqlalchemy import text
from api.extensions import db
from api.entities.entities import User
from typing import Optional, List


class UserRepository:
    def __init__(self):
        self.db = db

    def create(self, user: User) -> User:
        """Create a new user in the database"""
        query = text("""
            INSERT INTO users (username, email, password_hash, bio, profile_picture_url, is_private)
            VALUES (:username, :email, :password_hash, :bio, :profile_picture_url, :is_private)
            RETURNING user_id, username, email, password_hash, bio, profile_picture_url, is_private, created_at
        """)
        
        result = self.db.session.execute(query, {
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "bio": user.bio,
            "profile_picture_url": user.profile_picture_url,
            "is_private": user.is_private
        })
        self.db.session.commit()
        
        row = result.fetchone()
        return self._row_to_user(row)

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        query = text("SELECT * FROM users WHERE user_id = :user_id")
        result = self.db.session.execute(query, {"user_id": user_id})
        row = result.fetchone()
        
        if row:
            return self._row_to_user(row)
        return None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        query = text("SELECT * FROM users WHERE email = :email")
        result = self.db.session.execute(query, {"email": email})
        row = result.fetchone()
        
        if row:
            return self._row_to_user(row)
        return None

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        query = text("SELECT * FROM users WHERE username = :username")
        result = self.db.session.execute(query, {"username": username})
        row = result.fetchone()
        
        if row:
            return self._row_to_user(row)
        return None

    def update(self, user: User) -> Optional[User]:
        """Update an existing user"""
        query = text("""
            UPDATE users 
            SET username = :username,
                email = :email,
                password_hash = :password_hash,
                bio = :bio,
                profile_picture_url = :profile_picture_url,
                is_private = :is_private
            WHERE user_id = :user_id
            RETURNING user_id, username, email, password_hash, bio, profile_picture_url, is_private, created_at
        """)
        
        result = self.db.session.execute(query, {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "password_hash": user.password_hash,
            "bio": user.bio,
            "profile_picture_url": user.profile_picture_url,
            "is_private": user.is_private
        })
        self.db.session.commit()
        
        row = result.fetchone()
        if row:
            return self._row_to_user(row)
        return None

    def delete(self, user_id: int) -> bool:
        """Delete a user by ID"""
        query = text("DELETE FROM users WHERE user_id = :user_id RETURNING user_id")
        result = self.db.session.execute(query, {"user_id": user_id})
        self.db.session.commit()
        
        return result.fetchone() is not None

    def get_all(self, limit: int = 100, offset: int = 0) -> List[User]:
        """Get all users with pagination"""
        query = text("""
            SELECT * FROM users 
            ORDER BY created_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {"limit": limit, "offset": offset})
        
        return [self._row_to_user(row) for row in result.fetchall()]

    def _row_to_user(self, row) -> User:
        """Convert database row to User entity"""
        return User(
            user_id=row.user_id,
            username=row.username,
            email=row.email,
            password_hash=row.password_hash,
            bio=row.bio,
            profile_picture_url=row.profile_picture_url,
            is_private=row.is_private,
            created_at=row.created_at
        )

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from api.extensions import db
from api.entities.entities import Follow
from typing import Optional, List


class FollowRepository:
    def __init__(self):
        self.db = db
    
    def create(self, follow: Follow) -> Follow:
        """Create a new follow relationship"""
        try:
            query = text("""
                INSERT INTO Follows (follower_id, following_id, status_id)
                VALUES (:follower_id, :following_id, :status_id)
                RETURNING follower_id, following_id, status_id, created_at
            """)
            
            result = self.db.session.execute(query, {
                "follower_id": follow.follower_id,
                "following_id": follow.following_id,
                "status_id": follow.status_id
            })
            self.db.session.commit()
            return Follow.from_row(result.fetchone())
        except IntegrityError:
            self.db.session.rollback()
            raise ValueError("Follow relationship already exists")
        except SQLAlchemyError:
            self.db.session.rollback()
            raise

    def get_by_ids(self, follower_id: int, following_id: int) -> Optional[Follow]:
        """Get follow relationship by follower and following IDs"""
        query = text("""
            SELECT * FROM Follows 
            WHERE follower_id = :follower_id AND following_id = :following_id
        """)
        result = self.db.session.execute(query, {
            "follower_id": follower_id,
            "following_id": following_id
        })
        return Follow.from_row(result.fetchone())

    def update_status(self, follower_id: int, following_id: int, status_id: int) -> Optional[Follow]:
        """Update follow status (pending, accepted, rejected)"""
        try:
            query = text("""
                UPDATE Follows 
                SET status_id = :status_id
                WHERE follower_id = :follower_id AND following_id = :following_id
                RETURNING follower_id, following_id, status_id, created_at
            """)
            
            result = self.db.session.execute(query, {
                "follower_id": follower_id,
                "following_id": following_id,
                "status_id": status_id
            })
            self.db.session.commit()
            return Follow.from_row(result.fetchone())
        except SQLAlchemyError:
            self.db.session.rollback()
            raise

    def delete(self, follower_id: int, following_id: int) -> bool:
        """Delete a follow relationship"""
        query = text("""
            DELETE FROM Follows 
            WHERE follower_id = :follower_id AND following_id = :following_id
            RETURNING follower_id
        """)
        result = self.db.session.execute(query, {
            "follower_id": follower_id,
            "following_id": following_id
        })
        self.db.session.commit()
        return result.fetchone() is not None

    def get_followers(self, user_id: int, current_user_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all followers of a user (only accepted follows)"""
        query = text("""
            SELECT 
                f.*, u.user_id, u.username, u.profile_picture_url, u.bio,
                CASE 
                    WHEN :current_user_id IS NOT NULL THEN 
                        EXISTS(
                            SELECT 1 FROM Follows f2 
                            WHERE f2.follower_id = :current_user_id 
                            AND f2.following_id = u.user_id 
                            AND f2.status_id = 2
                        )
                    ELSE FALSE 
                END as is_following
            FROM Follows f
            JOIN Users u ON f.follower_id = u.user_id
            WHERE f.following_id = :user_id AND f.status_id = 2
            ORDER BY f.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "user_id": user_id,
            "current_user_id": current_user_id,
            "limit": limit,
            "offset": offset
        })
        return [dict(row._mapping) for row in result.fetchall()]

    def get_following(self, user_id: int, current_user_id: Optional[int] = None, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get all users that a user is following (only accepted follows)"""
        query = text("""
            SELECT 
                f.*, u.user_id, u.username, u.profile_picture_url, u.bio,
                CASE 
                    WHEN :current_user_id IS NOT NULL THEN 
                        EXISTS(
                            SELECT 1 FROM Follows f2 
                            WHERE f2.follower_id = :current_user_id 
                            AND f2.following_id = u.user_id 
                            AND f2.status_id = 2
                        )
                    ELSE FALSE 
                END as is_following
            FROM Follows f
            JOIN Users u ON f.following_id = u.user_id
            WHERE f.follower_id = :user_id AND f.status_id = 2
            ORDER BY f.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "user_id": user_id,
            "current_user_id": current_user_id,
            "limit": limit,
            "offset": offset
        })
        return [dict(row._mapping) for row in result.fetchall()]

    def get_pending_requests(self, user_id: int, limit: int = 100, offset: int = 0) -> List[dict]:
        """Get pending follow requests for a user"""
        query = text("""
            SELECT f.*, u.user_id, u.username, u.profile_picture_url, u.bio
            FROM Follows f
            JOIN Users u ON f.follower_id = u.user_id
            WHERE f.following_id = :user_id AND f.status_id = 1
            ORDER BY f.created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })
        rows = [dict(row._mapping) for row in result.fetchall()]
        # Convert datetime to isoformat for JSON serialization
        for row in rows:
            if row.get('created_at'):
                row['created_at'] = row['created_at'].isoformat()
        return rows

    def count_followers(self, user_id: int) -> int:
        """Count accepted followers of a user"""
        query = text("""
            SELECT COUNT(*) as count 
            FROM Follows 
            WHERE following_id = :user_id AND status_id = 2
        """)
        result = self.db.session.execute(query, {"user_id": user_id})
        row = result.fetchone()
        return row.count if row else 0

    def count_following(self, user_id: int) -> int:
        """Count users that a user is following (accepted)"""
        query = text("""
            SELECT COUNT(*) as count 
            FROM Follows 
            WHERE follower_id = :user_id AND status_id = 2
        """)
        result = self.db.session.execute(query, {"user_id": user_id})
        row = result.fetchone()
        return row.count if row else 0

    def is_following(self, follower_id: int, following_id: int) -> bool:
        """Check if follower is following another user (accepted status)"""
        query = text("""
            SELECT COUNT(*) as count 
            FROM Follows 
            WHERE follower_id = :follower_id 
            AND following_id = :following_id 
            AND status_id = 2
        """)
        result = self.db.session.execute(query, {
            "follower_id": follower_id,
            "following_id": following_id
        })
        row = result.fetchone()
        return row.count > 0 if row else False

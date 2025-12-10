from sqlalchemy import text
from api.extensions import db
from api.entities.entities import Post, PostLike
from typing import Optional, List


class PostRepository:
    def __init__(self):
        self.db = db

    def create(self, post: Post) -> Post:
        """Create a new post in the database"""
        query = text("""
            INSERT INTO Posts (user_id, community_id, content, media_url)
            VALUES (:user_id, :community_id, :content, :media_url)
            RETURNING post_id, user_id, community_id, content, media_url, created_at
        """)
        
        result = self.db.session.execute(query, {
            "user_id": post.user_id,
            "community_id": post.community_id,
            "content": post.content,
            "media_url": post.media_url
        })
        self.db.session.commit()
        
        row = result.fetchone()
        return Post.from_row(row)

    def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID"""
        query = text("SELECT * FROM Posts WHERE post_id = :post_id")
        result = self.db.session.execute(query, {"post_id": post_id})
        row = result.fetchone()
        return Post.from_row(row)

    def get_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Post]:
        """Get all posts by a specific user"""
        query = text("""
            SELECT * FROM Posts 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })
        return [Post.from_row(row) for row in result.fetchall()]

    def get_by_community_id(self, community_id: int, limit: int = 50, offset: int = 0) -> List[Post]:
        """Get all posts in a specific community"""
        query = text("""
            SELECT * FROM Posts 
            WHERE community_id = :community_id 
            ORDER BY created_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "community_id": community_id,
            "limit": limit,
            "offset": offset
        })
        return [Post.from_row(row) for row in result.fetchall()]

    def update(self, post: Post) -> Optional[Post]:
        """Update an existing post"""
        query = text("""
            UPDATE Posts 
            SET content = :content,
                media_url = :media_url,
                community_id = :community_id
            WHERE post_id = :post_id
            RETURNING post_id, user_id, community_id, content, media_url, created_at
        """)
        
        result = self.db.session.execute(query, {
            "post_id": post.post_id,
            "content": post.content,
            "media_url": post.media_url,
            "community_id": post.community_id
        })
        self.db.session.commit()
        
        row = result.fetchone()
        return Post.from_row(row)

    def delete(self, post_id: int) -> bool:
        """Delete a post by ID"""
        query = text("DELETE FROM Posts WHERE post_id = :post_id RETURNING post_id")
        result = self.db.session.execute(query, {"post_id": post_id})
        self.db.session.commit()
        return result.fetchone() is not None

    def get_feed(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Post]:
        """Get posts from users that the given user follows (accepted follows only)"""
        query = text("""
            SELECT DISTINCT p.* 
            FROM Posts p
            INNER JOIN Follows f ON p.user_id = f.following_id
            WHERE f.follower_id = :user_id 
                AND f.status_id = (SELECT status_id FROM FollowStatus WHERE status_name = 'accepted')
            ORDER BY p.created_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })
        return [Post.from_row(row) for row in result.fetchall()]

    def count(self, user_id: Optional[int] = None, community_id: Optional[int] = None) -> int:
        """Count posts (optionally filtered by user or community)"""
        if user_id:
            query = text("SELECT COUNT(*) FROM Posts WHERE user_id = :user_id")
            result = self.db.session.execute(query, {"user_id": user_id})
        elif community_id:
            query = text("SELECT COUNT(*) FROM Posts WHERE community_id = :community_id")
            result = self.db.session.execute(query, {"community_id": community_id})
        else:
            query = text("SELECT COUNT(*) FROM Posts")
            result = self.db.session.execute(query)
        
        return result.scalar()

    def like_post(self, post_id: int, user_id: int) -> bool:
        """Add a like to a post"""
        try:
            query = text("""
                INSERT INTO PostLikes (post_id, user_id)
                VALUES (:post_id, :user_id)
            """)
            self.db.session.execute(query, {"post_id": post_id, "user_id": user_id})
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            return False

    def unlike_post(self, post_id: int, user_id: int) -> bool:
        """Remove a like from a post"""
        query = text("""
            DELETE FROM PostLikes 
            WHERE post_id = :post_id AND user_id = :user_id
            RETURNING post_id
        """)
        result = self.db.session.execute(query, {"post_id": post_id, "user_id": user_id})
        self.db.session.commit()
        return result.fetchone() is not None

    def get_post_likes(self, post_id: int) -> List[PostLike]:
        """Get all users who liked a post"""
        query = text("""
            SELECT post_id, user_id, created_at 
            FROM PostLikes 
            WHERE post_id = :post_id
            ORDER BY created_at DESC
        """)
        result = self.db.session.execute(query, {"post_id": post_id})
        return [PostLike.from_row(row) for row in result.fetchall()]

    def count_likes(self, post_id: int) -> int:
        """Count the number of likes on a post"""
        query = text("SELECT COUNT(*) FROM PostLikes WHERE post_id = :post_id")
        result = self.db.session.execute(query, {"post_id": post_id})
        return result.scalar()

    def has_user_liked(self, post_id: int, user_id: int) -> bool:
        """Check if a user has liked a post"""
        query = text("""
            SELECT 1 FROM PostLikes 
            WHERE post_id = :post_id AND user_id = :user_id
        """)
        result = self.db.session.execute(query, {"post_id": post_id, "user_id": user_id})
        return result.fetchone() is not None

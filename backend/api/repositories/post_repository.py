from sqlalchemy import text
from api.extensions import db
from api.entities.entities import Post
from typing import Optional, List


class PostRepository:
    def __init__(self):
        self.db = db

    def create(self, post: Post) -> Post:
        """Create a new post in the database"""
        query = text("""
            INSERT INTO posts (user_id, community_id, content, media_url)
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
        query = text("SELECT * FROM posts WHERE post_id = :post_id")
        result = self.db.session.execute(query, {"post_id": post_id})
        row = result.fetchone()
        return Post.from_row(row)

    def get_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Post]:
        """Get all posts by a specific user"""
        query = text("""
            SELECT * FROM posts 
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
            SELECT * FROM posts 
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
            UPDATE posts 
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
        query = text("DELETE FROM posts WHERE post_id = :post_id RETURNING post_id")
        result = self.db.session.execute(query, {"post_id": post_id})
        self.db.session.commit()
        return result.fetchone() is not None

    def get_feed(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Post]:
        """Get posts from users that the given user follows (accepted follows only)"""
        query = text("""
            SELECT DISTINCT p.* 
            FROM posts p
            INNER JOIN follows f ON p.user_id = f.following_id
            WHERE f.follower_id = :user_id 
                AND f.status_id = (SELECT status_id FROM followstatus WHERE status_name = 'accepted')
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
            query = text("SELECT COUNT(*) FROM posts WHERE user_id = :user_id")
            result = self.db.session.execute(query, {"user_id": user_id})
        elif community_id:
            query = text("SELECT COUNT(*) FROM posts WHERE community_id = :community_id")
            result = self.db.session.execute(query, {"community_id": community_id})
        else:
            query = text("SELECT COUNT(*) FROM posts")
            result = self.db.session.execute(query)
        
        return result.scalar()

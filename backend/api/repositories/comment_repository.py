from sqlalchemy import text
from api.extensions import db
from api.entities.entities import Comment
from typing import Optional, List


class CommentRepository:
    def __init__(self):
        self.db = db

    def create(self, comment: Comment) -> Comment:
        """Create a new comment in the database"""
        query = text("""
            INSERT INTO Comments (post_id, user_id, content, parent_comment_id)
            VALUES (:post_id, :user_id, :content, :parent_comment_id)
            RETURNING comment_id
        """)
        
        result = self.db.session.execute(query, {
            "post_id": comment.post_id,
            "user_id": comment.user_id,
            "content": comment.content,
            "parent_comment_id": comment.parent_comment_id
        })
        self.db.session.commit()
        
        row = result.fetchone()
        if row:
            return self.get_by_id(row.comment_id)
        return None

    def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID"""
        query = text("""
            SELECT c.*, u.username, u.profile_picture_url
            FROM Comments c
            JOIN Users u ON c.user_id = u.user_id
            WHERE c.comment_id = :comment_id
        """)
        result = self.db.session.execute(query, {"comment_id": comment_id})
        row = result.fetchone()
        return Comment.from_row(row)

    def get_by_post_id(self, post_id: int, limit: int = 100, offset: int = 0) -> List[Comment]:
        """Get all top-level comments for a specific post (no parent)"""
        query = text("""
            SELECT c.*, u.username, u.profile_picture_url
            FROM Comments c
            JOIN Users u ON c.user_id = u.user_id
            WHERE c.post_id = :post_id AND c.parent_comment_id IS NULL
            ORDER BY c.created_at ASC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "post_id": post_id,
            "limit": limit,
            "offset": offset
        })
        return [Comment.from_row(row) for row in result.fetchall()]

    def get_by_user_id(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Comment]:
        """Get all comments by a specific user"""
        query = text("""
            SELECT c.*, u.username, u.profile_picture_url
            FROM Comments c
            JOIN Users u ON c.user_id = u.user_id
            WHERE c.user_id = :user_id 
            ORDER BY c.created_at DESC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "user_id": user_id,
            "limit": limit,
            "offset": offset
        })
        return [Comment.from_row(row) for row in result.fetchall()]

    def update(self, comment: Comment) -> Optional[Comment]:
        """Update an existing comment"""
        query = text("""
            UPDATE Comments 
            SET content = :content
            WHERE comment_id = :comment_id
            RETURNING comment_id
        """)
        
        result = self.db.session.execute(query, {
            "comment_id": comment.comment_id,
            "content": comment.content
        })
        self.db.session.commit()
        
        row = result.fetchone()
        if row:
            return self.get_by_id(row.comment_id)
        return None

    def delete(self, comment_id: int) -> bool:
        """Delete a comment by ID"""
        query = text("DELETE FROM Comments WHERE comment_id = :comment_id RETURNING comment_id")
        result = self.db.session.execute(query, {"comment_id": comment_id})
        self.db.session.commit()
        return result.fetchone() is not None

    def count_by_post_id(self, post_id: int) -> int:
        """Count top-level comments for a specific post"""
        query = text("SELECT COUNT(*) FROM Comments WHERE post_id = :post_id AND parent_comment_id IS NULL")
        result = self.db.session.execute(query, {"post_id": post_id})
        return result.scalar()

    def get_replies(self, comment_id: int, limit: int = 100, offset: int = 0) -> List[Comment]:
        """Get all replies to a specific comment"""
        query = text("""
            SELECT c.*, u.username, u.profile_picture_url
            FROM Comments c
            JOIN Users u ON c.user_id = u.user_id
            WHERE c.parent_comment_id = :comment_id 
            ORDER BY c.created_at ASC 
            LIMIT :limit OFFSET :offset
        """)
        result = self.db.session.execute(query, {
            "comment_id": comment_id,
            "limit": limit,
            "offset": offset
        })
        return [Comment.from_row(row) for row in result.fetchall()]

    def count_replies(self, comment_id: int) -> int:
        """Count replies to a specific comment"""
        query = text("SELECT COUNT(*) FROM Comments WHERE parent_comment_id = :comment_id")
        result = self.db.session.execute(query, {"comment_id": comment_id})
        return result.scalar()

    def get_by_user_id_with_posts(self, user_id: int, limit: int = 50, offset: int = 0) -> List[dict]:
        """Get all comments by a user with their associated post data"""
        query = text("""
            SELECT 
                c.comment_id, c.content as comment_content, c.created_at as comment_created_at,
                p.post_id, p.content as post_content, p.media_url, p.created_at as post_created_at,
                post_author.user_id as post_author_id, post_author.username as post_author_username,
                post_author.profile_picture_url as post_author_profile_picture,
                commenter.username as commenter_username, commenter.profile_picture_url as commenter_profile_picture
            FROM Comments c
            JOIN Posts p ON c.post_id = p.post_id
            JOIN Users post_author ON p.user_id = post_author.user_id
            JOIN Users commenter ON c.user_id = commenter.user_id
            WHERE c.user_id = :user_id
            ORDER BY c.created_at DESC
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
            if row.get('comment_created_at'):
                row['comment_created_at'] = row['comment_created_at'].isoformat()
            if row.get('post_created_at'):
                row['post_created_at'] = row['post_created_at'].isoformat()
        return rows

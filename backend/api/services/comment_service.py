from api.repositories.comment_repository import CommentRepository
from api.entities.entities import Comment
from typing import Optional, Dict, Any, List


class CommentService:
    def __init__(self):
        self.comment_repository = CommentRepository()

    def create_comment(self, post_id: int, user_id: int, content: str) -> Dict[str, Any]:
        """Create a new comment with validation"""
        # Create comment entity
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content
        )
        
        # Validate content
        errors = comment.validate()
        if errors:
            return {"success": False, "errors": errors}
        
        # Save to database
        created_comment = self.comment_repository.create(comment)
        
        return {
            "success": True,
            "comment": created_comment.to_dict()
        }

    def get_comment(self, comment_id: int) -> Optional[Dict[str, Any]]:
        """Get comment by ID"""
        comment = self.comment_repository.get_by_id(comment_id)
        if comment:
            return comment.to_dict()
        return None

    def get_post_comments(self, post_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all comments for a specific post"""
        comments = self.comment_repository.get_by_post_id(post_id, limit, offset)
        total = self.comment_repository.count_by_post_id(post_id)
        
        return {
            "comments": [comment.to_dict() for comment in comments],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def get_user_comments(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get all comments by a specific user"""
        comments = self.comment_repository.get_by_user_id(user_id, limit, offset)
        
        return {
            "comments": [comment.to_dict() for comment in comments],
            "limit": limit,
            "offset": offset
        }

    def update_comment(self, comment_id: int, user_id: int, content: str) -> Dict[str, Any]:
        """Update a comment with ownership validation"""
        # Get existing comment
        comment = self.comment_repository.get_by_id(comment_id)
        if not comment:
            return {"success": False, "error": "Comment not found"}
        
        # Ownership validation
        if comment.user_id != user_id:
            return {"success": False, "error": "You can only edit your own comments"}
        
        # Update content
        comment.content = content
        
        # Validate updated comment
        errors = comment.validate()
        if errors:
            return {"success": False, "errors": errors}
        
        # Save updates
        updated_comment = self.comment_repository.update(comment)
        
        return {
            "success": True,
            "comment": updated_comment.to_dict()
        }

    def delete_comment(self, comment_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a comment with ownership validation"""
        # Get existing comment
        comment = self.comment_repository.get_by_id(comment_id)
        if not comment:
            return {"success": False, "error": "Comment not found"}
        
        # Ownership validation
        if comment.user_id != user_id:
            return {"success": False, "error": "You can only delete your own comments"}
        
        # Delete comment
        deleted = self.comment_repository.delete(comment_id)
        
        if deleted:
            return {"success": True, "message": "Comment deleted successfully"}
        return {"success": False, "error": "Failed to delete comment"}

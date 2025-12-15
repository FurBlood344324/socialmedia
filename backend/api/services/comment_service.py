from api.repositories.comment_repository import CommentRepository
from api.entities.entities import Comment
from typing import Optional, Dict, Any, List


class CommentService:
    def __init__(self):
        self.comment_repository = CommentRepository()

    def create_comment(self, post_id: int, user_id: int, content: str, parent_comment_id: int = None) -> Dict[str, Any]:
        """Create a new comment with validation"""
        # Validate parent comment exists if provided
        if parent_comment_id:
            parent_comment = self.comment_repository.get_by_id(parent_comment_id)
            if not parent_comment:
                return {"success": False, "error": "Parent comment not found"}
            # Ensure parent comment belongs to the same post
            if parent_comment.post_id != post_id:
                return {"success": False, "error": "Parent comment does not belong to this post"}
        
        # Create comment entity
        comment = Comment(
            post_id=post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id
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
        """Get all top-level comments for a specific post with reply counts"""
        comments = self.comment_repository.get_by_post_id(post_id, limit, offset)
        total = self.comment_repository.count_by_post_id(post_id)
        
        # Add reply count to each comment
        comments_with_replies = []
        for comment in comments:
            comment_dict = comment.to_dict()
            comment_dict['reply_count'] = self.comment_repository.count_replies(comment.comment_id)
            comments_with_replies.append(comment_dict)
        
        return {
            "comments": comments_with_replies,
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

    def get_user_comments_with_posts(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get all comments by a user with their associated post data"""
        comments_with_posts = self.comment_repository.get_by_user_id_with_posts(user_id, limit, offset)
        
        return {
            "comments": comments_with_posts,
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

    def reply_to_comment(self, comment_id: int, user_id: int, content: str) -> Dict[str, Any]:
        """Create a reply to a comment with validation"""
        # Get parent comment
        parent_comment = self.comment_repository.get_by_id(comment_id)
        if not parent_comment:
            return {"success": False, "error": "Parent comment not found"}
        
        # Create reply using create_comment with parent_comment_id
        return self.create_comment(
            post_id=parent_comment.post_id,
            user_id=user_id,
            content=content,
            parent_comment_id=comment_id
        )

    def get_comment_replies(self, comment_id: int, limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Get all replies to a specific comment"""
        # Validate comment exists
        comment = self.comment_repository.get_by_id(comment_id)
        if not comment:
            return {"success": False, "error": "Comment not found"}
        
        replies = self.comment_repository.get_replies(comment_id, limit, offset)
        total = self.comment_repository.count_replies(comment_id)
        
        # Add reply count to each reply (for nested replies)
        replies_with_counts = []
        for reply in replies:
            reply_dict = reply.to_dict()
            reply_dict['reply_count'] = self.comment_repository.count_replies(reply.comment_id)
            replies_with_counts.append(reply_dict)
        
        return {
            "success": True,
            "replies": replies_with_counts,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def get_comment_with_replies(self, comment_id: int) -> Dict[str, Any]:
        """Get a comment with all its replies (comment tree)"""
        comment = self.comment_repository.get_by_id(comment_id)
        if not comment:
            return {"success": False, "error": "Comment not found"}
        
        comment_dict = comment.to_dict()
        
        # Get all replies
        replies_result = self.get_comment_replies(comment_id)
        comment_dict['replies'] = replies_result.get('replies', [])
        comment_dict['reply_count'] = replies_result.get('total', 0)
        
        return {
            "success": True,
            "comment": comment_dict
        }

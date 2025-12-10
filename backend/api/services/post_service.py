from api.repositories.post_repository import PostRepository
from api.entities.entities import Post
from typing import Optional, Dict, Any, List


class PostService:
    def __init__(self):
        self.post_repository = PostRepository()

    def create_post(self, user_id: int, content: str = None, 
                    media_url: str = None, community_id: int = None) -> Dict[str, Any]:
        """Create a new post with validation"""
        # Create post entity
        post = Post(
            user_id=user_id,
            content=content,
            media_url=media_url,
            community_id=community_id
        )
        
        # Validate content
        errors = post.validate()
        if errors:
            return {"success": False, "errors": errors}
        
        # Save to database
        created_post = self.post_repository.create(post)
        
        return {
            "success": True,
            "post": created_post.to_dict()
        }

    def get_post(self, post_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get post by ID with like count and user's like status"""
        post = self.post_repository.get_by_id(post_id)
        if post:
            post_dict = post.to_dict()
            post_dict['like_count'] = self.post_repository.count_likes(post_id)
            if user_id:
                post_dict['liked_by_user'] = self.post_repository.has_user_liked(post_id, user_id)
            return post_dict
        return None

    def get_user_posts(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get all posts by a specific user"""
        posts = self.post_repository.get_by_user_id(user_id, limit, offset)
        total = self.post_repository.count(user_id=user_id)
        
        return {
            "posts": [post.to_dict() for post in posts],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def get_community_posts(self, community_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get all posts in a specific community"""
        posts = self.post_repository.get_by_community_id(community_id, limit, offset)
        total = self.post_repository.count(community_id=community_id)
        
        return {
            "posts": [post.to_dict() for post in posts],
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def update_post(self, post_id: int, user_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a post with ownership validation"""
        # Get existing post
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        # Ownership validation
        if post.user_id != user_id:
            return {"success": False, "error": "You can only edit your own posts"}
        
        # Apply updates
        if "content" in updates:
            post.content = updates["content"]
        if "media_url" in updates:
            post.media_url = updates["media_url"]
        if "community_id" in updates:
            post.community_id = updates["community_id"]
        
        # Validate updated post
        errors = post.validate()
        if errors:
            return {"success": False, "errors": errors}
        
        # Save updates
        updated_post = self.post_repository.update(post)
        
        return {
            "success": True,
            "post": updated_post.to_dict()
        }

    def delete_post(self, post_id: int, user_id: int) -> Dict[str, Any]:
        """Delete a post with ownership validation"""
        # Get existing post
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        # Ownership validation
        if post.user_id != user_id:
            return {"success": False, "error": "You can only delete your own posts"}
        
        # Delete post
        deleted = self.post_repository.delete(post_id)
        
        if deleted:
            return {"success": True, "message": "Post deleted successfully"}
        return {"success": False, "error": "Failed to delete post"}

    def get_feed(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get authenticated user's feed (posts from followed users)"""
        posts = self.post_repository.get_feed(user_id, limit, offset)
        
        return {
            "posts": [post.to_dict() for post in posts],
            "limit": limit,
            "offset": offset
        }

    def like_post(self, post_id: int, user_id: int) -> Dict[str, Any]:
        """Like a post with validation"""
        # Get post
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        # Prevent liking own posts
        if post.user_id == user_id:
            return {"success": False, "error": "You cannot like your own posts"}
        
        # Check if already liked
        if self.post_repository.has_user_liked(post_id, user_id):
            return {"success": False, "error": "You have already liked this post"}
        
        # Add like
        success = self.post_repository.like_post(post_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "Post liked successfully",
                "like_count": self.post_repository.count_likes(post_id)
            }
        return {"success": False, "error": "Failed to like post"}

    def unlike_post(self, post_id: int, user_id: int) -> Dict[str, Any]:
        """Unlike a post"""
        # Get post
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        # Check if liked
        if not self.post_repository.has_user_liked(post_id, user_id):
            return {"success": False, "error": "You have not liked this post"}
        
        # Remove like
        success = self.post_repository.unlike_post(post_id, user_id)
        
        if success:
            return {
                "success": True,
                "message": "Post unliked successfully",
                "like_count": self.post_repository.count_likes(post_id)
            }
        return {"success": False, "error": "Failed to unlike post"}

    def get_like_count(self, post_id: int) -> Dict[str, Any]:
        """Get like count for a post"""
        # Verify post exists
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        count = self.post_repository.count_likes(post_id)
        return {"success": True, "like_count": count}

    def get_post_likes(self, post_id: int) -> Dict[str, Any]:
        """Get users who liked a post"""
        # Verify post exists
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        likes = self.post_repository.get_post_likes(post_id)
        return {
            "success": True,
            "likes": [like.to_dict() for like in likes],
            "count": len(likes)
        }

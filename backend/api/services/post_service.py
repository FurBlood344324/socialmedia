from api.repositories.post_repository import PostRepository
from api.repositories.user_repository import UserRepository
from api.repositories.follow_repository import FollowRepository
from api.entities.entities import Post
from typing import Optional, Dict, Any, List


class PostService:
    def __init__(self):
        self.post_repository = PostRepository()
        self.user_repository = UserRepository()
        self.follow_repository = FollowRepository()

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
        
        # Get post with engagement metrics (will be 0 for new posts)
        post_with_stats = self.post_repository.get_with_stats(created_post.post_id, user_id)
        
        return {
            "success": True,
            "post": post_with_stats
        }

    def get_post(self, post_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get post by ID with engagement metrics and user's interaction status (with privacy check)"""
        # Use the new get_with_stats method
        post_dict = self.post_repository.get_with_stats(post_id, user_id)
        
        if post_dict:
            # Get the basic post to check privacy
            post = self.post_repository.get_by_id(post_id)
            
            # Check if user can view this post
            if user_id and not self.can_view_post(post, user_id):
                return None
            
            return post_dict
        return None

    def get_user_posts(self, user_id: int, current_user_id: int = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get all posts by a specific user with engagement metrics (filtered by privacy)"""
        # Check if current user can view this user's posts
        if current_user_id and current_user_id != user_id:
            post_author = self.user_repository.get_by_id(user_id)
            if post_author and post_author.is_private:
                # Check if current user is an accepted follower
                follow = self.follow_repository.get_by_ids(current_user_id, user_id)
                if not follow or follow.status_id != 2:
                    return {
                        "posts": [],
                        "total": 0,
                        "limit": limit,
                        "offset": offset,
                        "message": "This account is private"
                    }
        
        # Use the new method with stats
        posts = self.post_repository.get_by_user_id_with_stats(user_id, current_user_id, limit, offset)
        total = self.post_repository.count(user_id=user_id)
        
        return {
            "posts": posts,
            "total": total,
            "limit": limit,
            "offset": offset
        }

    def get_community_posts(self, community_id: int, current_user_id: int = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get all posts in a specific community with engagement metrics"""
        posts = self.post_repository.get_by_community_id_with_stats(community_id, current_user_id, limit, offset)
        total = self.post_repository.count(community_id=community_id)
        
        return {
            "posts": posts,
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
        
        # Get post with engagement metrics
        post_with_stats = self.post_repository.get_with_stats(post_id, user_id)
        
        return {
            "success": True,
            "post": post_with_stats
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
        """Get authenticated user's feed with engagement metrics (posts from accepted follows only)
        
        OPTIMIZED: No N+1 queries
        - User info fetched in single query with JOIN
        - Privacy filtering done in single pass (no additional queries)
        """
        # Use the optimized feed method - includes user info in single query
        posts = self.post_repository.get_feed_with_stats(user_id, limit, offset)
        
        # Filter posts based on privacy (already have user info, no extra queries)
        filtered_posts = []
        for post_dict in posts:
            # User info already fetched with JOIN - no additional query
            is_private = post_dict.get('is_private', False)
            post_user_id = post_dict['user_id']
            
            # Include if: own post, public user, or accepted follow (already verified in query)
            if post_user_id == user_id or not is_private:
                # Accepted follow already verified by query JOIN condition
                filtered_posts.append(post_dict)
        
        return {
            "posts": filtered_posts,
            "limit": limit,
            "offset": offset
        }
    
    def get_discover_feed(self, user_id: int, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get popular posts for discovery"""
        posts = self.post_repository.get_popular(user_id, limit, offset)
        
        return {
            "posts": posts,
            "limit": limit,
            "offset": offset
        }

    def get_trending_hashtags(self, limit: int = 5) -> Dict[str, Any]:
        """Get trending hashtags"""
        hashtags = self.post_repository.get_trending_hashtags(limit)
        return {"success": True, "hashtags": hashtags}

    def search_posts(self, query: str, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Search posts"""
        posts = self.post_repository.search_posts(query, limit, offset)
        return {
            "success": True,
            "posts": posts,
            "limit": limit,
            "offset": offset
        }

    def like_post(self, post_id: int, user_id: int) -> Dict[str, Any]:
        """Like a post with validation"""
        # Get post
        post = self.post_repository.get_by_id(post_id)
        if not post:
            return {"success": False, "error": "Post not found"}
        
        # Check if already liked
        if self.post_repository.has_user_liked(post_id, user_id):
            return {"success": False, "error": "You have already liked this post"}
        
        # Add like
        success = self.post_repository.like_post(post_id, user_id)
        
        if success:
            # Get updated stats
            post_with_stats = self.post_repository.get_with_stats(post_id, user_id)
            return {
                "success": True,
                "message": "Post liked successfully",
                "like_count": post_with_stats['like_count'],
                "comment_count": post_with_stats['comment_count'],
                "liked_by_user": post_with_stats['liked_by_user']
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
            # Get updated stats
            post_with_stats = self.post_repository.get_with_stats(post_id, user_id)
            return {
                "success": True,
                "message": "Post unliked successfully",
                "like_count": post_with_stats['like_count'],
                "comment_count": post_with_stats['comment_count'],
                "liked_by_user": post_with_stats['liked_by_user']
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

    def can_view_post(self, post: Post, current_user_id: int) -> bool:
        """Check if current user can view a post based on privacy settings"""
        # User can always view their own posts
        if post.user_id == current_user_id:
            return True
        
        # Get post author
        post_author = self.user_repository.get_by_id(post.user_id)
        if not post_author:
            return False
        
        # If author is public, everyone can view
        if not post_author.is_private:
            return True
        
        # If author is private, check if current user is an accepted follower
        return self._is_accepted_follower(current_user_id, post.user_id)

    def _is_accepted_follower(self, follower_id: int, following_id: int) -> bool:
        """Helper method to check if user is an accepted follower"""
        follow = self.follow_repository.get_by_ids(follower_id, following_id)
        return follow is not None and follow.status_id == 2

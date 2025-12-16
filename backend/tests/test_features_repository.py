from tests.base_test import BaseTest
from api.repositories.features_repository import FeaturesRepository
from api.repositories.user_repository import UserRepository
from api.repositories.post_repository import PostRepository
from api.repositories.community_repository import CommunityRepository
from api.entities.entities import User, Post, Community


class TestFeaturesRepository(BaseTest):
    def setUp(self):
        super().setUp()
        self.features_repo = FeaturesRepository()
        self.user_repo = UserRepository()
        self.post_repo = PostRepository()
        self.community_repo = CommunityRepository()
        
        # Create test users
        self.user1 = self.user_repo.create(User(
            username="features_user1", 
            email="fu1@test.com", 
            password_hash="hash123"
        ))
        self.user2 = self.user_repo.create(User(
            username="features_user2", 
            email="fu2@test.com", 
            password_hash="hash123"
        ))

    def test_get_popular_posts_returns_list(self):
        """Test that get_popular_posts returns a list"""
        # Create some posts first
        self.post_repo.create(Post(user_id=self.user1.user_id, content="Popular post 1"))
        self.post_repo.create(Post(user_id=self.user2.user_id, content="Popular post 2"))
        
        posts = self.features_repo.get_popular_posts(limit=10)
        
        assert isinstance(posts, list)

    def test_get_popular_posts_limit(self):
        """Test that limit parameter works correctly"""
        # Create multiple posts
        for i in range(5):
            self.post_repo.create(Post(user_id=self.user1.user_id, content=f"Post {i}"))
        
        posts = self.features_repo.get_popular_posts(limit=3)
        
        assert len(posts) <= 3

    def test_get_active_users_returns_list(self):
        """Test that get_active_users returns a list"""
        users = self.features_repo.get_active_users(limit=10)
        
        assert isinstance(users, list)

    def test_get_active_users_limit(self):
        """Test that limit parameter works for active users"""
        users = self.features_repo.get_active_users(limit=5)
        
        assert len(users) <= 5

    def test_get_community_stats_existing_community(self):
        """Test getting stats for an existing community"""
        # Create a community
        community = self.community_repo.create(Community(
            name="Test Stats Community",
            description="A community for testing stats",
            creator_id=self.user1.user_id
        ))
        
        stats = self.features_repo.get_community_stats(community.community_id)
        
        assert stats is not None
        assert stats['community_name'] == "Test Stats Community"
        assert 'total_members' in stats
        assert 'total_posts' in stats
        assert 'roles' in stats
        assert 'engagement' in stats

    def test_get_community_stats_nonexistent_community(self):
        """Test getting stats for a non-existent community returns None"""
        stats = self.features_repo.get_community_stats(99999)
        
        assert stats is None

    def test_get_advanced_friend_recommendations_returns_list(self):
        """Test that get_advanced_friend_recommendations returns a list"""
        recommendations = self.features_repo.get_advanced_friend_recommendations(
            user_id=self.user1.user_id,
            limit=10
        )
        
        assert isinstance(recommendations, list)

    def test_get_advanced_friend_recommendations_limit(self):
        """Test that limit parameter works for recommendations"""
        recommendations = self.features_repo.get_advanced_friend_recommendations(
            user_id=self.user1.user_id,
            limit=5
        )
        
        assert len(recommendations) <= 5

    def test_popular_posts_structure(self):
        """Test that popular posts have correct structure"""
        # Create a post
        self.post_repo.create(Post(user_id=self.user1.user_id, content="Structure test post"))
        
        posts = self.features_repo.get_popular_posts(limit=1)
        
        if len(posts) > 0:
            post = posts[0]
            # Check expected keys exist
            expected_keys = ['post_id', 'author_id', 'author_username', 'content', 
                           'like_count', 'comment_count', 'engagement_score']
            for key in expected_keys:
                assert key in post, f"Missing key: {key}"

    def test_active_users_structure(self):
        """Test that active users have correct structure"""
        users = self.features_repo.get_active_users(limit=10)
        
        if len(users) > 0:
            user = users[0]
            expected_keys = ['user_id', 'username', 'profile_picture_url', 
                           'posts_last_7_days', 'total_activity']
            for key in expected_keys:
                assert key in user, f"Missing key: {key}"

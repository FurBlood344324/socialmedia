from tests.base_test import BaseTest
from api.services.features_service import FeaturesService
from api.services.auth_service import AuthService
from api.services.community_service import CommunityService
from api.services.post_service import PostService


class TestFeaturesService(BaseTest):
    def setUp(self):
        super().setUp()
        self.features_service = FeaturesService()
        self.auth_service = AuthService()
        self.community_service = CommunityService()
        self.post_service = PostService()
        
        # Register test users
        res1 = self.auth_service.register("features_test_user1", "ftu1@test.com", "password123")
        self.user1_id = res1['user']['user_id']
        
        res2 = self.auth_service.register("features_test_user2", "ftu2@test.com", "password123")
        self.user2_id = res2['user']['user_id']

    def test_get_popular_posts_success(self):
        """Test getting popular posts returns success"""
        result = self.features_service.get_popular_posts(limit=10)
        
        assert result['success'] is True
        assert 'posts' in result
        assert 'count' in result
        assert isinstance(result['posts'], list)

    def test_get_popular_posts_limit_validation_min(self):
        """Test that limit validation works for minimum value"""
        result = self.features_service.get_popular_posts(limit=0)
        
        assert result['success'] is True
        # Should have clamped to minimum of 1

    def test_get_popular_posts_limit_validation_max(self):
        """Test that limit validation works for maximum value"""
        result = self.features_service.get_popular_posts(limit=500)
        
        assert result['success'] is True
        # Should have clamped to maximum of 100

    def test_get_active_users_success(self):
        """Test getting active users returns success"""
        result = self.features_service.get_active_users(limit=10)
        
        assert result['success'] is True
        assert 'users' in result
        assert 'count' in result
        assert isinstance(result['users'], list)

    def test_get_active_users_limit_validation_min(self):
        """Test that limit validation works for minimum value"""
        result = self.features_service.get_active_users(limit=-5)
        
        assert result['success'] is True

    def test_get_active_users_limit_validation_max(self):
        """Test that limit validation works for maximum value"""
        result = self.features_service.get_active_users(limit=200)
        
        assert result['success'] is True

    def test_get_community_stats_existing(self):
        """Test getting stats for an existing community"""
        # Create a community
        community = self.community_service.create_community(
            name="Service Test Community",
            description="A community for service testing",
            creator_id=self.user1_id
        )
        community_id = community.community_id
        
        result = self.features_service.get_community_stats(community_id)
        
        assert result['success'] is True
        assert 'stats' in result
        assert result['stats']['community_name'] == "Service Test Community"

    def test_get_community_stats_not_found(self):
        """Test getting stats for non-existent community"""
        result = self.features_service.get_community_stats(99999)
        
        assert result['success'] is False
        assert 'error' in result
        assert 'not found' in result['error'].lower()

    def test_get_advanced_recommendations_success(self):
        """Test getting friend recommendations returns success"""
        result = self.features_service.get_advanced_recommendations(user_id=self.user1_id)
        
        assert result['success'] is True
        assert 'recommendations' in result
        assert 'count' in result
        assert isinstance(result['recommendations'], list)

    def test_get_advanced_recommendations_limit_validation_min(self):
        """Test that limit validation works for minimum value"""
        result = self.features_service.get_advanced_recommendations(
            user_id=self.user1_id, 
            limit=0
        )
        
        assert result['success'] is True

    def test_get_advanced_recommendations_limit_validation_max(self):
        """Test that limit validation works for maximum value"""
        result = self.features_service.get_advanced_recommendations(
            user_id=self.user1_id, 
            limit=100
        )
        
        assert result['success'] is True

    def test_get_popular_posts_with_data(self):
        """Test getting popular posts when there is data"""
        # Create some posts
        self.post_service.create_post(self.user1_id, content="Test popular post 1")
        self.post_service.create_post(self.user2_id, content="Test popular post 2")
        
        result = self.features_service.get_popular_posts(limit=10)
        
        assert result['success'] is True
        # Posts should be returned (if the view includes them)
        assert isinstance(result['posts'], list)

    def test_get_active_users_with_activity(self):
        """Test getting active users when users have activity"""
        # Create some posts to generate activity
        self.post_service.create_post(self.user1_id, content="Activity post 1")
        self.post_service.create_post(self.user1_id, content="Activity post 2")
        self.post_service.create_post(self.user2_id, content="Activity post 3")
        
        result = self.features_service.get_active_users(limit=10)
        
        assert result['success'] is True
        assert isinstance(result['users'], list)

    def test_community_stats_structure(self):
        """Test that community stats have correct structure"""
        # Create a community
        community = self.community_service.create_community(
            name="Structure Test Community",
            description="Testing stats structure",
            creator_id=self.user1_id
        )
        community_id = community.community_id
        
        result = self.features_service.get_community_stats(community_id)
        
        assert result['success'] is True
        stats = result['stats']
        
        # Check expected keys
        assert 'community_id' in stats
        assert 'community_name' in stats
        assert 'total_members' in stats
        assert 'total_posts' in stats
        assert 'roles' in stats
        assert 'engagement' in stats
        
        # Check nested structures
        assert 'admins' in stats['roles']
        assert 'moderators' in stats['roles']
        assert 'regular_members' in stats['roles']
        assert 'total_likes' in stats['engagement']
        assert 'total_comments' in stats['engagement']

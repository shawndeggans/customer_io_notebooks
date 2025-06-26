"""
Comprehensive tests for Customer.IO People Manager.

Tests cover:
- Data model validation (UserTraits, UserIdentification, UserDeletionRequest)
- PeopleManager operations (identify, delete, suppress, batch operations)
- Error handling and validation
- Integration with API client
- Enum validation and type safety
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from pydantic import ValidationError

from utils.people_manager import (
    UserLifecycleStage,
    UserPlan,
    UserTraits,
    UserIdentification,
    UserDeletionRequest,
    PeopleManager
)
from utils.error_handlers import CustomerIOError


class TestUserLifecycleStage:
    """Test UserLifecycleStage enum."""
    
    def test_lifecycle_stage_values(self):
        """Test all lifecycle stage values."""
        assert UserLifecycleStage.REGISTERED == "registered"
        assert UserLifecycleStage.ONBOARDED == "onboarded"
        assert UserLifecycleStage.ACTIVE == "active"
        assert UserLifecycleStage.DORMANT == "dormant"
        assert UserLifecycleStage.CHURNED == "churned"
        assert UserLifecycleStage.SUPPRESSED == "suppressed"
    
    def test_lifecycle_stage_membership(self):
        """Test lifecycle stage membership."""
        valid_stages = [stage.value for stage in UserLifecycleStage]
        assert "registered" in valid_stages
        assert "invalid_stage" not in valid_stages


class TestUserPlan:
    """Test UserPlan enum."""
    
    def test_user_plan_values(self):
        """Test all user plan values."""
        assert UserPlan.FREE == "free"
        assert UserPlan.BASIC == "basic"
        assert UserPlan.PREMIUM == "premium"
        assert UserPlan.ENTERPRISE == "enterprise"
    
    def test_user_plan_membership(self):
        """Test user plan membership."""
        valid_plans = [plan.value for plan in UserPlan]
        assert "free" in valid_plans
        assert "invalid_plan" not in valid_plans


class TestUserTraits:
    """Test UserTraits data model."""
    
    def test_valid_user_traits(self):
        """Test valid user traits creation."""
        traits = UserTraits(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            plan=UserPlan.PREMIUM,
            lifecycle_stage=UserLifecycleStage.ACTIVE,
            total_spent=199.99,
            login_count=15
        )
        
        assert traits.email == "test@example.com"
        assert traits.first_name == "John"
        assert traits.last_name == "Doe"
        assert traits.plan == "premium"  # Should be converted to string
        assert traits.lifecycle_stage == "active"
        assert traits.total_spent == 199.99
        assert traits.login_count == 15
    
    def test_required_email_field(self):
        """Test that email field is required."""
        with pytest.raises(ValidationError, match="field required"):
            UserTraits()
    
    def test_email_validation_valid_formats(self):
        """Test email validation with valid formats."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.org",
            "user+tag@example.co.uk",
            "123@example.com"
        ]
        
        for email in valid_emails:
            traits = UserTraits(email=email)
            assert traits.email == email.lower()
    
    def test_email_validation_invalid_formats(self):
        """Test email validation with invalid formats."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@@example.com",
            "user name@example.com"
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValidationError, match="Invalid email format"):
                UserTraits(email=email)
    
    def test_email_normalization(self):
        """Test email normalization."""
        traits = UserTraits(email="  TEST@EXAMPLE.COM  ")
        assert traits.email == "test@example.com"
    
    def test_negative_total_spent_validation(self):
        """Test validation of negative total_spent."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            UserTraits(email="test@example.com", total_spent=-10.0)
    
    def test_negative_login_count_validation(self):
        """Test validation of negative login_count."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            UserTraits(email="test@example.com", login_count=-1)
    
    def test_enum_value_conversion(self):
        """Test that enum values are converted to strings."""
        traits = UserTraits(
            email="test@example.com",
            plan=UserPlan.ENTERPRISE,
            lifecycle_stage=UserLifecycleStage.CHURNED
        )
        
        assert isinstance(traits.plan, str)
        assert isinstance(traits.lifecycle_stage, str)
        assert traits.plan == "enterprise"
        assert traits.lifecycle_stage == "churned"
    
    def test_optional_fields(self):
        """Test that optional fields can be None."""
        traits = UserTraits(email="test@example.com")
        
        assert traits.first_name is None
        assert traits.last_name is None
        assert traits.plan is None
        assert traits.lifecycle_stage is None
        assert traits.created_at is None
        assert traits.last_login is None
        assert traits.total_spent is None
        assert traits.login_count is None


class TestUserIdentification:
    """Test UserIdentification data model."""
    
    def test_user_identification_with_user_id(self):
        """Test user identification with user ID."""
        traits = UserTraits(email="test@example.com")
        user = UserIdentification(user_id="user_123", traits=traits)
        
        assert user.user_id == "user_123"
        assert user.anonymous_id is None
        assert user.traits.email == "test@example.com"
        assert isinstance(user.timestamp, datetime)
    
    def test_user_identification_with_anonymous_id(self):
        """Test user identification with anonymous ID."""
        traits = UserTraits(email="test@example.com")
        user = UserIdentification(anonymous_id="anon_456", traits=traits)
        
        assert user.anonymous_id == "anon_456"
        assert user.user_id is None
        assert user.traits.email == "test@example.com"
    
    def test_user_identification_with_both_ids(self):
        """Test user identification with both IDs."""
        traits = UserTraits(email="test@example.com")
        user = UserIdentification(
            user_id="user_123",
            anonymous_id="anon_456",
            traits=traits
        )
        
        assert user.user_id == "user_123"
        assert user.anonymous_id == "anon_456"
    
    def test_required_traits_field(self):
        """Test that traits field is required."""
        with pytest.raises(ValidationError, match="field required"):
            UserIdentification(user_id="user_123")
    
    def test_user_id_validation_empty(self):
        """Test user ID validation with empty string."""
        traits = UserTraits(email="test@example.com")
        
        with pytest.raises(ValidationError, match="User ID cannot be empty"):
            UserIdentification(user_id="", traits=traits)
    
    def test_user_id_validation_too_long(self):
        """Test user ID validation with string too long."""
        traits = UserTraits(email="test@example.com")
        long_id = "x" * 256
        
        with pytest.raises(ValidationError, match="User ID cannot exceed 255 characters"):
            UserIdentification(user_id=long_id, traits=traits)
    
    def test_user_id_normalization(self):
        """Test user ID whitespace normalization."""
        traits = UserTraits(email="test@example.com")
        user = UserIdentification(user_id="  user_123  ", traits=traits)
        
        assert user.user_id == "user_123"
    
    def test_automatic_timestamp(self):
        """Test automatic timestamp setting."""
        traits = UserTraits(email="test@example.com")
        
        with patch('utils.people_manager.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            user = UserIdentification(user_id="user_123", traits=traits)
            
            assert user.timestamp == mock_now
    
    def test_custom_timestamp(self):
        """Test setting custom timestamp."""
        traits = UserTraits(email="test@example.com")
        custom_time = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        
        user = UserIdentification(
            user_id="user_123",
            traits=traits,
            timestamp=custom_time
        )
        
        assert user.timestamp == custom_time


class TestUserDeletionRequest:
    """Test UserDeletionRequest data model."""
    
    def test_user_deletion_request_basic(self):
        """Test basic user deletion request."""
        request = UserDeletionRequest(user_id="user_123")
        
        assert request.user_id == "user_123"
        assert request.reason == "user_request"  # Default value
        assert isinstance(request.timestamp, datetime)
    
    def test_user_deletion_request_with_reason(self):
        """Test user deletion request with custom reason."""
        request = UserDeletionRequest(
            user_id="user_123",
            reason="gdpr_erasure"
        )
        
        assert request.user_id == "user_123"
        assert request.reason == "gdpr_erasure"
    
    def test_required_user_id_field(self):
        """Test that user_id field is required."""
        with pytest.raises(ValidationError, match="field required"):
            UserDeletionRequest()
    
    def test_automatic_timestamp(self):
        """Test automatic timestamp setting."""
        with patch('utils.people_manager.datetime') as mock_datetime:
            mock_now = datetime(2024, 1, 15, 12, 30, 0, tzinfo=timezone.utc)
            mock_datetime.now.return_value = mock_now
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            request = UserDeletionRequest(user_id="user_123")
            
            assert request.timestamp == mock_now


class TestPeopleManager:
    """Test PeopleManager class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock CustomerIOClient."""
        return Mock()
    
    @pytest.fixture
    def people_manager(self, mock_client):
        """Create PeopleManager with mock client."""
        return PeopleManager(mock_client)
    
    @pytest.fixture
    def sample_user_traits(self):
        """Create sample user traits."""
        return UserTraits(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            plan=UserPlan.PREMIUM
        )
    
    @pytest.fixture
    def sample_user_identification(self, sample_user_traits):
        """Create sample user identification."""
        return UserIdentification(
            user_id="user_123",
            traits=sample_user_traits
        )
    
    def test_people_manager_initialization(self, mock_client):
        """Test PeopleManager initialization."""
        manager = PeopleManager(mock_client)
        
        assert manager.client == mock_client
        assert manager.logger is not None
    
    @patch('utils.people_manager.validate_request_size', return_value=True)
    def test_identify_user_success(self, mock_validate, people_manager, sample_user_identification):
        """Test successful user identification."""
        # Mock API response
        people_manager.client.identify.return_value = {"status": "success"}
        
        result = people_manager.identify_user(sample_user_identification)
        
        assert result == {"status": "success"}
        people_manager.client.identify.assert_called_once()
        
        # Check call arguments
        call_args = people_manager.client.identify.call_args[1]
        assert "userId" in call_args
        assert "traits" in call_args
        assert "timestamp" in call_args
        assert call_args["userId"] == "user_123"
    
    @patch('utils.people_manager.validate_request_size', return_value=False)
    def test_identify_user_request_too_large(self, mock_validate, people_manager, sample_user_identification):
        """Test user identification with request too large."""
        with pytest.raises(Exception, match="Request size exceeds 32KB limit"):
            people_manager.identify_user(sample_user_identification)
    
    def test_identify_user_with_anonymous_id(self, people_manager, sample_user_traits):
        """Test user identification with anonymous ID."""
        user = UserIdentification(anonymous_id="anon_456", traits=sample_user_traits)
        people_manager.client.identify.return_value = {"status": "success"}
        
        result = people_manager.identify_user(user)
        
        call_args = people_manager.client.identify.call_args[1]
        assert "anonymousId" in call_args
        assert call_args["anonymousId"] == "anon_456"
        assert "userId" not in call_args
    
    def test_identify_user_api_error(self, people_manager, sample_user_identification):
        """Test user identification with API error."""
        people_manager.client.identify.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            people_manager.identify_user(sample_user_identification)
    
    def test_delete_user_success(self, people_manager):
        """Test successful user deletion."""
        deletion_request = UserDeletionRequest(
            user_id="user_123",
            reason="user_request"
        )
        people_manager.client.track.return_value = {"status": "success"}
        
        result = people_manager.delete_user(deletion_request)
        
        assert result == {"status": "success"}
        people_manager.client.track.assert_called_once()
        
        # Check call arguments
        call_args = people_manager.client.track.call_args[1]
        assert call_args["user_id"] == "user_123"
        assert call_args["event"] == "User Deleted"
        assert "reason" in call_args["properties"]
        assert "deleted_at" in call_args["properties"]
    
    def test_suppress_user_success(self, people_manager):
        """Test successful user suppression."""
        people_manager.client.track.return_value = {"status": "success"}
        
        result = people_manager.suppress_user("user_123", "gdpr_request")
        
        assert result == {"status": "success"}
        
        call_args = people_manager.client.track.call_args[1]
        assert call_args["user_id"] == "user_123"
        assert call_args["event"] == "User Suppressed"
        assert call_args["properties"]["reason"] == "gdpr_request"
    
    def test_suppress_user_default_reason(self, people_manager):
        """Test user suppression with default reason."""
        people_manager.client.track.return_value = {"status": "success"}
        
        people_manager.suppress_user("user_123")
        
        call_args = people_manager.client.track.call_args[1]
        assert call_args["properties"]["reason"] == "gdpr_request"
    
    def test_unsuppress_user_success(self, people_manager):
        """Test successful user unsuppression."""
        people_manager.client.track.return_value = {"status": "success"}
        
        result = people_manager.unsuppress_user("user_123", "user_return")
        
        assert result == {"status": "success"}
        
        call_args = people_manager.client.track.call_args[1]
        assert call_args["user_id"] == "user_123"
        assert call_args["event"] == "User Unsuppressed"
        assert call_args["properties"]["reason"] == "user_return"
    
    def test_unsuppress_user_default_reason(self, people_manager):
        """Test user unsuppression with default reason."""
        people_manager.client.track.return_value = {"status": "success"}
        
        people_manager.unsuppress_user("user_123")
        
        call_args = people_manager.client.track.call_args[1]
        assert call_args["properties"]["reason"] == "user_request"
    
    @patch('utils.people_manager.BatchTransformer.optimize_batch_sizes')
    def test_batch_identify_users_success(self, mock_optimize, people_manager, sample_user_traits):
        """Test successful batch user identification."""
        # Create test users
        users = [
            UserIdentification(user_id=f"user_{i}", traits=sample_user_traits)
            for i in range(3)
        ]
        
        # Mock batch optimization
        mock_optimize.return_value = [
            [{"type": "identify", "userId": "user_0"}],
            [{"type": "identify", "userId": "user_1"}, {"type": "identify", "userId": "user_2"}]
        ]
        
        # Mock API responses
        people_manager.client.batch.return_value = {"status": "success"}
        
        results = people_manager.batch_identify_users(users)
        
        assert len(results) == 2  # Two batches
        assert all(result["status"] == "success" for result in results)
        assert people_manager.client.batch.call_count == 2
    
    @patch('utils.people_manager.BatchTransformer.optimize_batch_sizes')
    def test_batch_identify_users_partial_failure(self, mock_optimize, people_manager, sample_user_traits):
        """Test batch identification with partial failures."""
        users = [
            UserIdentification(user_id=f"user_{i}", traits=sample_user_traits)
            for i in range(2)
        ]
        
        mock_optimize.return_value = [
            [{"type": "identify", "userId": "user_0"}],
            [{"type": "identify", "userId": "user_1"}]
        ]
        
        # First call succeeds, second fails
        people_manager.client.batch.side_effect = [
            {"status": "success"},
            CustomerIOError("API error")
        ]
        
        results = people_manager.batch_identify_users(users)
        
        assert len(results) == 2
        assert results[0]["status"] == "success"
        assert results[1]["status"] == "failed"
        assert "error" in results[1]
    
    def test_update_user_lifecycle(self, people_manager):
        """Test updating user lifecycle stage."""
        people_manager.client.track.return_value = {"status": "success"}
        
        result = people_manager.update_user_lifecycle(
            "user_123",
            UserLifecycleStage.ACTIVE,
            {"additional": "property"}
        )
        
        assert result == {"status": "success"}
        
        call_args = people_manager.client.track.call_args[1]
        assert call_args["event"] == "Lifecycle Stage Updated"
        assert call_args["properties"]["lifecycle_stage"] == "active"
        assert call_args["properties"]["additional"] == "property"
    
    def test_update_user_plan(self, people_manager):
        """Test updating user subscription plan."""
        people_manager.client.track.return_value = {"status": "success"}
        
        result = people_manager.update_user_plan(
            "user_123",
            UserPlan.PREMIUM,
            UserPlan.BASIC,
            {"upgrade_reason": "user_request"}
        )
        
        assert result == {"status": "success"}
        
        call_args = people_manager.client.track.call_args[1]
        assert call_args["event"] == "Plan Updated"
        assert call_args["properties"]["plan"] == "premium"
        assert call_args["properties"]["previous_plan"] == "basic"
        assert call_args["properties"]["upgrade_reason"] == "user_request"
    
    def test_update_user_plan_without_previous(self, people_manager):
        """Test updating user plan without previous plan."""
        people_manager.client.track.return_value = {"status": "success"}
        
        people_manager.update_user_plan("user_123", UserPlan.PREMIUM)
        
        call_args = people_manager.client.track.call_args[1]
        assert "previous_plan" not in call_args["properties"]
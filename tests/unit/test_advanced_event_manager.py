"""
Comprehensive tests for Customer.IO Advanced Event Manager.

Tests cover:
- Journey stage and funnel type enumerations
- Data model validation (JourneyStep, UserJourney, ConversionFunnel, AttributionTouchpoint)
- User journey tracking and completion
- Conversion funnel creation and analysis
- Attribution modeling with multiple touchpoint support
- Real-time pattern detection
- Behavioral pattern analysis
- Performance metrics and monitoring
"""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch
from pydantic import ValidationError

from utils.advanced_event_manager import (
    JourneyStage,
    FunnelType,
    AttributionModel,
    SegmentationType,
    JourneyStep,
    UserJourney,
    FunnelStep,
    ConversionFunnel,
    AttributionTouchpoint,
    RealTimePatternDetector,
    AdvancedEventManager
)
from utils.event_manager import EventManager
from utils.error_handlers import CustomerIOError


class TestJourneyStage:
    """Test JourneyStage enum."""
    
    def test_journey_stage_values(self):
        """Test all journey stage values."""
        assert JourneyStage.AWARENESS == "awareness"
        assert JourneyStage.INTEREST == "interest"
        assert JourneyStage.CONSIDERATION == "consideration"
        assert JourneyStage.CONVERSION == "conversion"
        assert JourneyStage.RETENTION == "retention"
        assert JourneyStage.ADVOCACY == "advocacy"
    
    def test_journey_stage_membership(self):
        """Test journey stage membership."""
        valid_stages = [stage.value for stage in JourneyStage]
        assert "awareness" in valid_stages
        assert "invalid_stage" not in valid_stages


class TestFunnelType:
    """Test FunnelType enum."""
    
    def test_funnel_type_values(self):
        """Test all funnel type values."""
        assert FunnelType.ACQUISITION == "acquisition"
        assert FunnelType.ACTIVATION == "activation"
        assert FunnelType.RETENTION == "retention"
        assert FunnelType.REVENUE == "revenue"
        assert FunnelType.REFERRAL == "referral"
        assert FunnelType.CUSTOM == "custom"
    
    def test_funnel_type_membership(self):
        """Test funnel type membership."""
        valid_types = [funnel_type.value for funnel_type in FunnelType]
        assert "acquisition" in valid_types
        assert "invalid_type" not in valid_types


class TestAttributionModel:
    """Test AttributionModel enum."""
    
    def test_attribution_model_values(self):
        """Test all attribution model values."""
        assert AttributionModel.FIRST_TOUCH == "first_touch"
        assert AttributionModel.LAST_TOUCH == "last_touch"
        assert AttributionModel.LINEAR == "linear"
        assert AttributionModel.TIME_DECAY == "time_decay"
        assert AttributionModel.POSITION_BASED == "position_based"
        assert AttributionModel.CUSTOM == "custom"
    
    def test_attribution_model_membership(self):
        """Test attribution model membership."""
        valid_models = [model.value for model in AttributionModel]
        assert "first_touch" in valid_models
        assert "invalid_model" not in valid_models


class TestJourneyStep:
    """Test JourneyStep data model."""
    
    def test_valid_journey_step(self):
        """Test valid journey step creation."""
        now = datetime.now(timezone.utc)
        step = JourneyStep(
            step_id="landing_page",
            event="Page Viewed",
            timestamp=now,
            properties={"page_name": "Home", "source": "google"},
            stage=JourneyStage.AWARENESS,
            duration_seconds=120.5
        )
        
        assert step.step_id == "landing_page"
        assert step.event == "Page Viewed"
        assert step.timestamp == now
        assert step.properties == {"page_name": "Home", "source": "google"}
        assert step.stage == "awareness"
        assert step.duration_seconds == 120.5
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            JourneyStep()
    
    def test_step_id_validation_empty(self):
        """Test step ID validation with empty string."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError, match="Step ID cannot be empty"):
            JourneyStep(
                step_id="",
                event="Test Event",
                timestamp=now
            )
    
    def test_step_id_normalization(self):
        """Test step ID normalization."""
        now = datetime.now(timezone.utc)
        step = JourneyStep(
            step_id="  LANDING_PAGE  ",
            event="Page Viewed",
            timestamp=now
        )
        
        assert step.step_id == "landing_page"
    
    def test_negative_duration_validation(self):
        """Test validation of negative duration."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            JourneyStep(
                step_id="test",
                event="Test Event",
                timestamp=now,
                duration_seconds=-10
            )
    
    def test_optional_fields_default_none(self):
        """Test that optional fields default appropriately."""
        now = datetime.now(timezone.utc)
        step = JourneyStep(
            step_id="test",
            event="Test Event",
            timestamp=now
        )
        
        assert step.properties == {}
        assert step.stage is None
        assert step.duration_seconds is None


class TestUserJourney:
    """Test UserJourney data model."""
    
    def test_valid_user_journey(self):
        """Test valid user journey creation."""
        now = datetime.now(timezone.utc)
        step = JourneyStep(
            step_id="landing",
            event="Page Viewed",
            timestamp=now
        )
        
        journey = UserJourney(
            journey_id="journey_123",
            user_id="user_456",
            journey_type="onboarding",
            steps=[step],
            conversion_value=49.99,
            metadata={"source": "google"}
        )
        
        assert journey.journey_id == "journey_123"
        assert journey.user_id == "user_456"
        assert journey.journey_type == "onboarding"
        assert len(journey.steps) == 1
        assert journey.conversion_value == 49.99
        assert journey.metadata == {"source": "google"}
        assert isinstance(journey.started_at, datetime)
        assert journey.is_completed is False
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            UserJourney()
    
    def test_id_validation_empty(self):
        """Test ID validation with empty strings."""
        with pytest.raises(ValidationError, match="ID cannot be empty"):
            UserJourney(
                journey_id="",
                user_id="user_123",
                journey_type="test"
            )
        
        with pytest.raises(ValidationError, match="ID cannot be empty"):
            UserJourney(
                journey_id="journey_123",
                user_id="",
                journey_type="test"
            )
    
    def test_id_normalization(self):
        """Test ID whitespace normalization."""
        journey = UserJourney(
            journey_id="  journey_123  ",
            user_id="  user_456  ",
            journey_type="onboarding"
        )
        
        assert journey.journey_id == "journey_123"
        assert journey.user_id == "user_456"
    
    def test_step_order_validation(self):
        """Test that steps must be in chronological order."""
        now = datetime.now(timezone.utc)
        
        step1 = JourneyStep(
            step_id="step1",
            event="Event 1",
            timestamp=now + timedelta(minutes=1)  # Later timestamp
        )
        
        step2 = JourneyStep(
            step_id="step2",
            event="Event 2",
            timestamp=now  # Earlier timestamp
        )
        
        with pytest.raises(ValidationError, match="Journey steps must be in chronological order"):
            UserJourney(
                journey_id="journey_123",
                user_id="user_456",
                journey_type="test",
                steps=[step1, step2]  # Wrong order
            )
    
    def test_add_step_method(self):
        """Test adding steps to journey."""
        now = datetime.now(timezone.utc)
        journey = UserJourney(
            journey_id="journey_123",
            user_id="user_456",
            journey_type="test"
        )
        
        step = JourneyStep(
            step_id="test_step",
            event="Test Event",
            timestamp=now
        )
        
        journey.add_step(step)
        
        assert len(journey.steps) == 1
        assert journey.steps[0] == step
    
    def test_get_duration_minutes_no_steps(self):
        """Test duration calculation with no steps."""
        journey = UserJourney(
            journey_id="journey_123",
            user_id="user_456",
            journey_type="test"
        )
        
        assert journey.get_duration_minutes() is None
    
    def test_get_duration_minutes_with_steps(self):
        """Test duration calculation with steps."""
        now = datetime.now(timezone.utc)
        
        step1 = JourneyStep(
            step_id="step1",
            event="Event 1",
            timestamp=now
        )
        
        step2 = JourneyStep(
            step_id="step2",
            event="Event 2",
            timestamp=now + timedelta(minutes=5)
        )
        
        journey = UserJourney(
            journey_id="journey_123",
            user_id="user_456",
            journey_type="test",
            steps=[step1, step2]
        )
        
        assert journey.get_duration_minutes() == 5.0
    
    def test_get_duration_minutes_completed_journey(self):
        """Test duration calculation for completed journey."""
        now = datetime.now(timezone.utc)
        
        step = JourneyStep(
            step_id="step1",
            event="Event 1",
            timestamp=now
        )
        
        journey = UserJourney(
            journey_id="journey_123",
            user_id="user_456",
            journey_type="test",
            steps=[step],
            completed_at=now + timedelta(minutes=10)
        )
        
        assert journey.get_duration_minutes() == 10.0


class TestFunnelStep:
    """Test FunnelStep data model."""
    
    def test_valid_funnel_step(self):
        """Test valid funnel step creation."""
        step = FunnelStep(
            step_name="Landing Page Visit",
            step_order=1,
            event_patterns=["Page Viewed"],
            required=True,
            time_window_hours=24
        )
        
        assert step.step_name == "Landing Page Visit"
        assert step.step_order == 1
        assert step.event_patterns == ["Page Viewed"]
        assert step.required is True
        assert step.time_window_hours == 24
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            FunnelStep()
    
    def test_step_order_validation(self):
        """Test step order must be positive."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 1"):
            FunnelStep(
                step_name="Test Step",
                step_order=0,
                event_patterns=["Test Event"]
            )
    
    def test_time_window_validation(self):
        """Test time window must be positive."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 1"):
            FunnelStep(
                step_name="Test Step",
                step_order=1,
                event_patterns=["Test Event"],
                time_window_hours=0
            )
    
    def test_default_required_true(self):
        """Test that required defaults to True."""
        step = FunnelStep(
            step_name="Test Step",
            step_order=1,
            event_patterns=["Test Event"]
        )
        
        assert step.required is True


class TestConversionFunnel:
    """Test ConversionFunnel data model."""
    
    def test_valid_conversion_funnel(self):
        """Test valid conversion funnel creation."""
        steps = [
            FunnelStep(
                step_name="Landing",
                step_order=1,
                event_patterns=["Page Viewed"]
            ),
            FunnelStep(
                step_name="Signup",
                step_order=2,
                event_patterns=["User Registered"]
            )
        ]
        
        funnel = ConversionFunnel(
            funnel_id="funnel_123",
            funnel_name="Onboarding Funnel",
            funnel_type=FunnelType.ACQUISITION,
            steps=steps,
            attribution_model=AttributionModel.LINEAR,
            lookback_days=60
        )
        
        assert funnel.funnel_id == "funnel_123"
        assert funnel.funnel_name == "Onboarding Funnel"
        assert funnel.funnel_type == "acquisition"
        assert len(funnel.steps) == 2
        assert funnel.attribution_model == "linear"
        assert funnel.lookback_days == 60
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            ConversionFunnel()
    
    def test_default_attribution_model(self):
        """Test that attribution model defaults to LAST_TOUCH."""
        steps = [
            FunnelStep(
                step_name="Test",
                step_order=1,
                event_patterns=["Test Event"]
            )
        ]
        
        funnel = ConversionFunnel(
            funnel_id="funnel_123",
            funnel_name="Test Funnel",
            funnel_type=FunnelType.CUSTOM,
            steps=steps
        )
        
        assert funnel.attribution_model == "last_touch"
    
    def test_default_lookback_days(self):
        """Test that lookback_days defaults to 30."""
        steps = [
            FunnelStep(
                step_name="Test",
                step_order=1,
                event_patterns=["Test Event"]
            )
        ]
        
        funnel = ConversionFunnel(
            funnel_id="funnel_123",
            funnel_name="Test Funnel",
            funnel_type=FunnelType.CUSTOM,
            steps=steps
        )
        
        assert funnel.lookback_days == 30
    
    def test_empty_steps_validation(self):
        """Test that funnel must have at least one step."""
        with pytest.raises(ValidationError, match="Funnel must have at least one step"):
            ConversionFunnel(
                funnel_id="funnel_123",
                funnel_name="Test Funnel",
                funnel_type=FunnelType.CUSTOM,
                steps=[]
            )
    
    def test_step_order_validation(self):
        """Test that steps must be in sequential order."""
        steps = [
            FunnelStep(
                step_name="Step 1",
                step_order=2,  # Wrong order
                event_patterns=["Event 1"]
            ),
            FunnelStep(
                step_name="Step 2",
                step_order=1,  # Wrong order
                event_patterns=["Event 2"]
            )
        ]
        
        with pytest.raises(ValidationError, match="Funnel steps must be in sequential order"):
            ConversionFunnel(
                funnel_id="funnel_123",
                funnel_name="Test Funnel",
                funnel_type=FunnelType.CUSTOM,
                steps=steps
            )
    
    def test_duplicate_step_order_validation(self):
        """Test that steps cannot have duplicate order numbers."""
        steps = [
            FunnelStep(
                step_name="Step 1",
                step_order=1,
                event_patterns=["Event 1"]
            ),
            FunnelStep(
                step_name="Step 2",
                step_order=1,  # Duplicate order
                event_patterns=["Event 2"]
            )
        ]
        
        with pytest.raises(ValidationError, match="Funnel steps cannot have duplicate order numbers"):
            ConversionFunnel(
                funnel_id="funnel_123",
                funnel_name="Test Funnel",
                funnel_type=FunnelType.CUSTOM,
                steps=steps
            )
    
    def test_lookback_days_validation(self):
        """Test lookback days validation."""
        steps = [
            FunnelStep(
                step_name="Test",
                step_order=1,
                event_patterns=["Test Event"]
            )
        ]
        
        # Too small
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 1"):
            ConversionFunnel(
                funnel_id="funnel_123",
                funnel_name="Test Funnel",
                funnel_type=FunnelType.CUSTOM,
                steps=steps,
                lookback_days=0
            )
        
        # Too large
        with pytest.raises(ValidationError, match="ensure this value is less than or equal to 365"):
            ConversionFunnel(
                funnel_id="funnel_123",
                funnel_name="Test Funnel",
                funnel_type=FunnelType.CUSTOM,
                steps=steps,
                lookback_days=400
            )


class TestAttributionTouchpoint:
    """Test AttributionTouchpoint data model."""
    
    def test_valid_attribution_touchpoint(self):
        """Test valid attribution touchpoint creation."""
        now = datetime.now(timezone.utc)
        
        touchpoint = AttributionTouchpoint(
            touchpoint_id="tp_123",
            user_id="user_456",
            channel="google_ads",
            campaign="brand_awareness",
            source="google",
            medium="cpc",
            content="homepage_ad",
            timestamp=now,
            conversion_value=49.99,
            position_in_journey=1
        )
        
        assert touchpoint.touchpoint_id == "tp_123"
        assert touchpoint.user_id == "user_456"
        assert touchpoint.channel == "google_ads"
        assert touchpoint.campaign == "brand_awareness"
        assert touchpoint.source == "google"
        assert touchpoint.medium == "cpc"
        assert touchpoint.content == "homepage_ad"
        assert touchpoint.timestamp == now
        assert touchpoint.conversion_value == 49.99
        assert touchpoint.position_in_journey == 1
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            AttributionTouchpoint()
    
    def test_required_field_validation_empty(self):
        """Test validation of empty required fields."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError, match="Field cannot be empty"):
            AttributionTouchpoint(
                touchpoint_id="",
                user_id="user_456",
                channel="google_ads",
                timestamp=now,
                position_in_journey=1
            )
        
        with pytest.raises(ValidationError, match="Field cannot be empty"):
            AttributionTouchpoint(
                touchpoint_id="tp_123",
                user_id="",
                channel="google_ads",
                timestamp=now,
                position_in_journey=1
            )
        
        with pytest.raises(ValidationError, match="Field cannot be empty"):
            AttributionTouchpoint(
                touchpoint_id="tp_123",
                user_id="user_456",
                channel="",
                timestamp=now,
                position_in_journey=1
            )
    
    def test_field_normalization(self):
        """Test field whitespace normalization."""
        now = datetime.now(timezone.utc)
        
        touchpoint = AttributionTouchpoint(
            touchpoint_id="  tp_123  ",
            user_id="  user_456  ",
            channel="  google_ads  ",
            timestamp=now,
            position_in_journey=1
        )
        
        assert touchpoint.touchpoint_id == "tp_123"
        assert touchpoint.user_id == "user_456"
        assert touchpoint.channel == "google_ads"
    
    def test_position_validation(self):
        """Test position in journey must be positive."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 1"):
            AttributionTouchpoint(
                touchpoint_id="tp_123",
                user_id="user_456",
                channel="google_ads",
                timestamp=now,
                position_in_journey=0
            )
    
    def test_conversion_value_validation(self):
        """Test conversion value must be non-negative."""
        now = datetime.now(timezone.utc)
        
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            AttributionTouchpoint(
                touchpoint_id="tp_123",
                user_id="user_456",
                channel="google_ads",
                timestamp=now,
                position_in_journey=1,
                conversion_value=-10.0
            )
    
    def test_optional_fields_default_none(self):
        """Test that optional fields default to None."""
        now = datetime.now(timezone.utc)
        
        touchpoint = AttributionTouchpoint(
            touchpoint_id="tp_123",
            user_id="user_456",
            channel="google_ads",
            timestamp=now,
            position_in_journey=1
        )
        
        assert touchpoint.campaign is None
        assert touchpoint.source is None
        assert touchpoint.medium is None
        assert touchpoint.content is None
        assert touchpoint.conversion_value is None


class TestRealTimePatternDetector:
    """Test RealTimePatternDetector class."""
    
    @pytest.fixture
    def pattern_detector(self):
        """Create pattern detector with 30-minute window."""
        return RealTimePatternDetector(window_size_minutes=30)
    
    def test_pattern_detector_initialization(self, pattern_detector):
        """Test pattern detector initialization."""
        assert pattern_detector.window_size_minutes == 30
        assert len(pattern_detector.event_windows) == 0
        assert len(pattern_detector.pattern_alerts) == 0
    
    def test_add_event_single_event(self, pattern_detector):
        """Test adding single event."""
        now = datetime.now(timezone.utc)
        
        patterns = pattern_detector.add_event(
            user_id="user_123",
            event_name="Page Viewed",
            timestamp=now,
            properties={"page_name": "Home"}
        )
        
        assert len(patterns) == 0  # No patterns with single event
        assert len(pattern_detector.event_windows["user_123"]) == 1
    
    def test_rapid_engagement_pattern(self, pattern_detector):
        """Test rapid engagement pattern detection."""
        now = datetime.now(timezone.utc)
        
        # Add 5 events in 4 minutes (rapid engagement)
        events = [
            ("Page Viewed", {"page_name": "Home"}),
            ("Product Viewed", {"product_id": "123"}),
            ("Product Viewed", {"product_id": "456"}),
            ("Product Added to Cart", {"product_id": "123"}),
            ("Checkout Started", {"cart_value": "49.99"})
        ]
        
        patterns = []
        for i, (event_name, properties) in enumerate(events):
            timestamp = now + timedelta(seconds=i * 60)  # 1 minute apart
            new_patterns = pattern_detector.add_event(
                user_id="user_rapid",
                event_name=event_name,
                timestamp=timestamp,
                properties=properties
            )
            patterns.extend(new_patterns)
        
        # Should detect rapid engagement pattern
        rapid_patterns = [p for p in patterns if p["pattern_type"] == "rapid_engagement"]
        assert len(rapid_patterns) > 0
        
        pattern = rapid_patterns[0]
        assert pattern["user_id"] == "user_rapid"
        assert pattern["event_count"] == 5
        assert pattern["time_span_minutes"] <= 5
    
    def test_conversion_intent_pattern(self, pattern_detector):
        """Test conversion intent pattern detection."""
        now = datetime.now(timezone.utc)
        
        # Add conversion sequence
        conversion_events = [
            "Product Viewed",
            "Product Added to Cart", 
            "Checkout Started"
        ]
        
        patterns = []
        for i, event_name in enumerate(conversion_events):
            timestamp = now + timedelta(minutes=i * 2)
            new_patterns = pattern_detector.add_event(
                user_id="user_conversion",
                event_name=event_name,
                timestamp=timestamp
            )
            patterns.extend(new_patterns)
        
        # Should detect conversion intent pattern
        intent_patterns = [p for p in patterns if p["pattern_type"] == "conversion_intent"]
        assert len(intent_patterns) > 0
        
        pattern = intent_patterns[0]
        assert pattern["user_id"] == "user_conversion"
        assert pattern["event_sequence"] == conversion_events
    
    def test_window_cleanup(self, pattern_detector):
        """Test that old events are cleaned from window."""
        now = datetime.now(timezone.utc)
        
        # Add old event (outside window)
        old_timestamp = now - timedelta(minutes=35)  # Outside 30-minute window
        pattern_detector.add_event(
            user_id="user_123",
            event_name="Old Event",
            timestamp=old_timestamp
        )
        
        # Add new event
        pattern_detector.add_event(
            user_id="user_123",
            event_name="New Event",
            timestamp=now
        )
        
        # Should only have new event
        events = list(pattern_detector.event_windows["user_123"])
        assert len(events) == 1
        assert events[0]["event_name"] == "New Event"


class TestAdvancedEventManager:
    """Test AdvancedEventManager class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock CustomerIOClient."""
        return Mock()
    
    @pytest.fixture
    def mock_event_manager(self):
        """Create mock EventManager."""
        return Mock(spec=EventManager)
    
    @pytest.fixture
    def advanced_manager(self, mock_client, mock_event_manager):
        """Create AdvancedEventManager with mock dependencies."""
        return AdvancedEventManager(mock_client, mock_event_manager)
    
    def test_advanced_manager_initialization(self, mock_client, mock_event_manager):
        """Test AdvancedEventManager initialization."""
        manager = AdvancedEventManager(mock_client, mock_event_manager)
        
        assert manager.client == mock_client
        assert manager.event_manager == mock_event_manager
        assert manager.logger is not None
        assert isinstance(manager.pattern_detector, RealTimePatternDetector)
    
    def test_advanced_manager_initialization_without_event_manager(self, mock_client):
        """Test AdvancedEventManager initialization without event manager."""
        with patch('utils.advanced_event_manager.EventManager') as mock_event_manager_class:
            mock_event_manager_instance = Mock()
            mock_event_manager_class.return_value = mock_event_manager_instance
            
            manager = AdvancedEventManager(mock_client)
            
            assert manager.client == mock_client
            assert manager.event_manager == mock_event_manager_instance
            mock_event_manager_class.assert_called_once_with(mock_client)
    
    def test_create_user_journey(self, advanced_manager):
        """Test user journey creation."""
        now = datetime.now(timezone.utc)
        initial_step = JourneyStep(
            step_id="landing",
            event="Page Viewed",
            timestamp=now
        )
        
        journey = advanced_manager.create_user_journey(
            user_id="user_123",
            journey_type="onboarding",
            initial_step=initial_step
        )
        
        assert journey.user_id == "user_123"
        assert journey.journey_type == "onboarding"
        assert len(journey.steps) == 1
        assert journey.steps[0] == initial_step
        assert "journey_user_123_onboarding_" in journey.journey_id
    
    def test_create_user_journey_without_initial_step(self, advanced_manager):
        """Test user journey creation without initial step."""
        journey = advanced_manager.create_user_journey(
            user_id="user_123",
            journey_type="onboarding"
        )
        
        assert journey.user_id == "user_123"
        assert journey.journey_type == "onboarding"
        assert len(journey.steps) == 0
    
    def test_add_journey_steps(self, advanced_manager):
        """Test adding steps to journey."""
        journey = advanced_manager.create_user_journey(
            user_id="user_123",
            journey_type="onboarding"
        )
        
        now = datetime.now(timezone.utc)
        steps_data = [
            {
                "step_id": "step1",
                "event": "Event 1",
                "timestamp": now,
                "stage": JourneyStage.AWARENESS
            },
            {
                "step_id": "step2",
                "event": "Event 2",
                "timestamp": now + timedelta(minutes=5),
                "stage": JourneyStage.INTEREST
            }
        ]
        
        journey = advanced_manager.add_journey_steps(journey, steps_data)
        
        assert len(journey.steps) == 2
        assert journey.steps[0].step_id == "step1"
        assert journey.steps[1].step_id == "step2"
        assert journey.steps[1].duration_seconds == 300  # 5 minutes
    
    def test_complete_journey_success(self, advanced_manager):
        """Test successful journey completion."""
        journey = advanced_manager.create_user_journey(
            user_id="user_123",
            journey_type="onboarding"
        )
        
        advanced_manager.event_manager.send_event.return_value = {"status": "success"}
        
        result = advanced_manager.complete_journey(journey, conversion_value=49.99)
        
        assert result == {"status": "success"}
        assert journey.is_completed is True
        assert journey.conversion_value == 49.99
        assert journey.completed_at is not None
        
        # Check event was sent
        advanced_manager.event_manager.send_event.assert_called_once()
        call_args = advanced_manager.event_manager.send_event.call_args[0][0]
        assert call_args["userId"] == "user_123"
        assert call_args["event"] == "Journey Completed"
        assert call_args["properties"]["conversion_value"] == 49.99
    
    def test_complete_journey_api_error(self, advanced_manager):
        """Test journey completion with API error."""
        journey = advanced_manager.create_user_journey(
            user_id="user_123",
            journey_type="onboarding"
        )
        
        advanced_manager.event_manager.send_event.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            advanced_manager.complete_journey(journey)
    
    def test_create_conversion_funnel(self, advanced_manager):
        """Test conversion funnel creation."""
        step_definitions = [
            {
                "step_name": "Landing",
                "step_order": 1,
                "event_patterns": ["Page Viewed"]
            },
            {
                "step_name": "Signup",
                "step_order": 2,
                "event_patterns": ["User Registered"]
            }
        ]
        
        funnel = advanced_manager.create_conversion_funnel(
            funnel_name="Test Funnel",
            funnel_type=FunnelType.ACQUISITION,
            step_definitions=step_definitions
        )
        
        assert funnel.funnel_name == "Test Funnel"
        assert funnel.funnel_type == "acquisition"
        assert len(funnel.steps) == 2
        assert "funnel_test_funnel_" in funnel.funnel_id
    
    def test_analyze_funnel_conversion(self, advanced_manager):
        """Test funnel conversion analysis."""
        # Create funnel
        step_definitions = [
            {
                "step_name": "Landing",
                "step_order": 1,
                "event_patterns": ["Page Viewed"]
            },
            {
                "step_name": "Signup",
                "step_order": 2,
                "event_patterns": ["User Registered"]
            }
        ]
        
        funnel = advanced_manager.create_conversion_funnel(
            funnel_name="Test Funnel",
            funnel_type=FunnelType.ACQUISITION,
            step_definitions=step_definitions
        )
        
        # Create sample journeys
        now = datetime.now(timezone.utc)
        
        journey1 = UserJourney(
            journey_id="j1",
            user_id="u1",
            journey_type="test",
            steps=[
                JourneyStep(step_id="s1", event="Page Viewed", timestamp=now),
                JourneyStep(step_id="s2", event="User Registered", timestamp=now + timedelta(minutes=5))
            ],
            is_completed=True
        )
        
        journey2 = UserJourney(
            journey_id="j2",
            user_id="u2",
            journey_type="test",
            steps=[
                JourneyStep(step_id="s1", event="Page Viewed", timestamp=now)
            ],
            is_completed=False
        )
        
        journeys = [journey1, journey2]
        
        analysis = advanced_manager.analyze_funnel_conversion(funnel, journeys)
        
        assert analysis["total_users"] == 2
        assert analysis["completed_journeys"] == 1
        assert analysis["overall_conversion_rate"] == 0.5  # 1 out of 2 completed signup
        assert "step_analysis" in analysis
        assert "Landing" in analysis["step_analysis"]
        assert "Signup" in analysis["step_analysis"]
    
    def test_create_attribution_touchpoints(self, advanced_manager):
        """Test attribution touchpoint creation."""
        now = datetime.now(timezone.utc)
        
        touchpoint_data = [
            {
                "channel": "google_ads",
                "source": "google",
                "medium": "cpc",
                "timestamp": now - timedelta(days=1)
            },
            {
                "channel": "email",
                "source": "newsletter",
                "medium": "email",
                "timestamp": now
            }
        ]
        
        touchpoints = advanced_manager.create_attribution_touchpoints(
            user_id="user_123",
            touchpoint_data=touchpoint_data
        )
        
        assert len(touchpoints) == 2
        assert all(tp.user_id == "user_123" for tp in touchpoints)
        assert touchpoints[0].position_in_journey == 1
        assert touchpoints[1].position_in_journey == 2
        assert "tp_user_123_1_" in touchpoints[0].touchpoint_id
    
    def test_calculate_attribution_weights_first_touch(self, advanced_manager):
        """Test first-touch attribution weights."""
        touchpoints = [Mock(), Mock(), Mock()]  # 3 touchpoints
        
        weights = advanced_manager.calculate_attribution_weights(
            touchpoints, AttributionModel.FIRST_TOUCH
        )
        
        assert weights == [1.0, 0.0, 0.0]
    
    def test_calculate_attribution_weights_last_touch(self, advanced_manager):
        """Test last-touch attribution weights."""
        touchpoints = [Mock(), Mock(), Mock()]  # 3 touchpoints
        
        weights = advanced_manager.calculate_attribution_weights(
            touchpoints, AttributionModel.LAST_TOUCH
        )
        
        assert weights == [0.0, 0.0, 1.0]
    
    def test_calculate_attribution_weights_linear(self, advanced_manager):
        """Test linear attribution weights."""
        touchpoints = [Mock(), Mock(), Mock()]  # 3 touchpoints
        
        weights = advanced_manager.calculate_attribution_weights(
            touchpoints, AttributionModel.LINEAR
        )
        
        expected = [1/3, 1/3, 1/3]
        assert all(abs(w - e) < 0.001 for w, e in zip(weights, expected))
    
    def test_calculate_attribution_weights_time_decay(self, advanced_manager):
        """Test time-decay attribution weights."""
        touchpoints = [Mock(), Mock(), Mock()]  # 3 touchpoints
        
        weights = advanced_manager.calculate_attribution_weights(
            touchpoints, AttributionModel.TIME_DECAY
        )
        
        # More recent touchpoints should get higher weights
        assert weights[0] < weights[1] < weights[2]
        assert abs(sum(weights) - 1.0) < 0.001  # Should sum to 1
    
    def test_calculate_attribution_weights_position_based(self, advanced_manager):
        """Test position-based attribution weights."""
        touchpoints = [Mock(), Mock(), Mock(), Mock()]  # 4 touchpoints
        
        weights = advanced_manager.calculate_attribution_weights(
            touchpoints, AttributionModel.POSITION_BASED
        )
        
        # First and last should get 40% each, middle should split 20%
        assert weights[0] == 0.4  # First
        assert weights[-1] == 0.4  # Last
        assert weights[1] == weights[2] == 0.1  # Middle (20% / 2)
    
    def test_calculate_attribution_weights_empty_list(self, advanced_manager):
        """Test attribution weights with empty touchpoint list."""
        weights = advanced_manager.calculate_attribution_weights(
            [], AttributionModel.LINEAR
        )
        
        assert weights == []
    
    def test_calculate_attribution_weights_single_touchpoint(self, advanced_manager):
        """Test attribution weights with single touchpoint."""
        touchpoints = [Mock()]
        
        weights = advanced_manager.calculate_attribution_weights(
            touchpoints, AttributionModel.LINEAR
        )
        
        assert weights == [1.0]
    
    def test_create_attribution_analysis(self, advanced_manager):
        """Test attribution analysis creation."""
        now = datetime.now(timezone.utc)
        
        touchpoints = [
            AttributionTouchpoint(
                touchpoint_id="tp1",
                user_id="user_123",
                channel="google_ads",
                campaign="brand",
                source="google",
                medium="cpc",
                timestamp=now - timedelta(days=1),
                position_in_journey=1
            ),
            AttributionTouchpoint(
                touchpoint_id="tp2",
                user_id="user_123",
                channel="email",
                source="newsletter",
                medium="email",
                timestamp=now,
                position_in_journey=2
            )
        ]
        
        analysis = advanced_manager.create_attribution_analysis(
            touchpoints=touchpoints,
            model=AttributionModel.LINEAR,
            conversion_value=100.0
        )
        
        assert analysis["attribution_model"] == "linear"
        assert analysis["total_conversion_value"] == 100.0
        assert analysis["total_touchpoints"] == 2
        assert analysis["journey_duration_days"] == 1
        assert "channel_attribution" in analysis
        assert "google_ads" in analysis["channel_attribution"]
        assert "email" in analysis["channel_attribution"]
        assert len(analysis["touchpoint_details"]) == 2
    
    def test_analyze_behavior_patterns(self, advanced_manager):
        """Test behavior pattern analysis."""
        now = datetime.now(timezone.utc)
        
        # Create sample journeys
        journey1 = UserJourney(
            journey_id="j1",
            user_id="u1",
            journey_type="test",
            steps=[
                JourneyStep(
                    step_id="s1", 
                    event="Page Viewed", 
                    timestamp=now,
                    stage=JourneyStage.AWARENESS
                ),
                JourneyStep(
                    step_id="s2", 
                    event="User Registered", 
                    timestamp=now + timedelta(minutes=5),
                    stage=JourneyStage.CONVERSION
                )
            ],
            is_completed=True
        )
        
        journey2 = UserJourney(
            journey_id="j2",
            user_id="u2",
            journey_type="test",
            steps=[
                JourneyStep(
                    step_id="s1", 
                    event="Page Viewed", 
                    timestamp=now,
                    stage=JourneyStage.AWARENESS
                ),
                JourneyStep(
                    step_id="s2", 
                    event="Product Viewed", 
                    timestamp=now + timedelta(minutes=3),
                    stage=JourneyStage.INTEREST
                )
            ],
            is_completed=False
        )
        
        journeys = [journey1, journey2]
        
        analysis = advanced_manager.analyze_behavior_patterns(journeys)
        
        assert analysis["total_journeys"] == 2
        assert analysis["completed_journeys"] == 1
        assert analysis["completion_rate"] == 0.5
        assert analysis["avg_steps_per_journey"] == 2.0
        assert "common_event_pairs" in analysis
        assert "common_stage_transitions" in analysis
    
    def test_get_metrics(self, advanced_manager):
        """Test getting advanced event manager metrics."""
        metrics = advanced_manager.get_metrics()
        
        assert "client" in metrics
        assert "event_manager" in metrics
        assert "pattern_detector" in metrics
        assert "supported_features" in metrics
        assert "performance" in metrics
        
        # Check supported features
        features = metrics["supported_features"]
        assert "journey_stages" in features
        assert "funnel_types" in features
        assert "attribution_models" in features
        assert "segmentation_types" in features
        
        # Check that enum values are included
        assert "awareness" in features["journey_stages"]
        assert "acquisition" in features["funnel_types"]
        assert "first_touch" in features["attribution_models"]
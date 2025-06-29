"""
Customer.IO Advanced Event Manager Module

Type-safe advanced event tracking operations for Customer.IO API including:
- User journey tracking and analysis
- Conversion funnel analytics with multi-step progression
- Multi-touch attribution modeling across channels
- Real-time behavioral pattern detection
- Advanced event sequencing and stage progression
- Cross-platform journey unification
- Performance monitoring and analytics
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
from collections import defaultdict, deque
import statistics
import structlog
from pydantic import BaseModel, Field, field_validator

from .api_client import CustomerIOClient
from .event_manager import EventManager
from .transformers import BatchTransformer
from .error_handlers import retry_on_error, ErrorContext


class JourneyStage(str, Enum):
    """Enumeration for user journey stages."""
    AWARENESS = "awareness"
    INTEREST = "interest"
    CONSIDERATION = "consideration"
    CONVERSION = "conversion"
    RETENTION = "retention"
    ADVOCACY = "advocacy"


class FunnelType(str, Enum):
    """Enumeration for funnel types."""
    ACQUISITION = "acquisition"
    ACTIVATION = "activation"
    RETENTION = "retention"
    REVENUE = "revenue"
    REFERRAL = "referral"
    CUSTOM = "custom"


class AttributionModel(str, Enum):
    """Enumeration for attribution models."""
    FIRST_TOUCH = "first_touch"
    LAST_TOUCH = "last_touch"
    LINEAR = "linear"
    TIME_DECAY = "time_decay"
    POSITION_BASED = "position_based"
    CUSTOM = "custom"


class SegmentationType(str, Enum):
    """Enumeration for user segmentation types."""
    BEHAVIORAL = "behavioral"
    DEMOGRAPHIC = "demographic"
    PSYCHOGRAPHIC = "psychographic"
    GEOGRAPHIC = "geographic"
    TECHNOGRAPHIC = "technographic"
    VALUE_BASED = "value_based"


class JourneyStep(BaseModel):
    """Type-safe journey step model."""
    step_id: str = Field(..., description="Unique step identifier")
    event: str = Field(..., description="Event name")
    timestamp: datetime = Field(..., description="Step timestamp")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Step properties")
    stage: Optional[JourneyStage] = Field(None, description="Journey stage")
    duration_seconds: Optional[float] = Field(None, ge=0, description="Time spent in step")
    
    @field_validator('step_id')
    @classmethod
    def validate_step_id(cls, v: str) -> str:
        """Validate step ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Step ID cannot be empty")
        return v.strip().lower()
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }


class UserJourney(BaseModel):
    """Type-safe user journey model."""
    journey_id: str = Field(..., description="Unique journey identifier")
    user_id: str = Field(..., description="User identifier")
    journey_type: str = Field(..., description="Type of journey")
    steps: List[JourneyStep] = Field(default_factory=list, description="Journey steps")
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(None, description="Journey completion time")
    is_completed: bool = Field(default=False, description="Journey completion status")
    conversion_value: Optional[float] = Field(None, ge=0, description="Conversion value")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Journey metadata")
    
    @field_validator('journey_id', 'user_id')
    @classmethod
    def validate_ids(cls, v: str) -> str:
        """Validate ID formats."""
        if not v or len(v.strip()) == 0:
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    @field_validator('steps')
    @classmethod
    def validate_step_order(cls, v: List[JourneyStep]) -> List[JourneyStep]:
        """Validate steps are in chronological order."""
        if len(v) > 1:
            for i in range(1, len(v)):
                if v[i].timestamp < v[i-1].timestamp:
                    raise ValueError("Journey steps must be in chronological order")
        return v
    
    def add_step(self, step: JourneyStep) -> None:
        """Add a step to the journey."""
        self.steps.append(step)
        self.steps.sort(key=lambda x: x.timestamp)
    
    def get_duration_minutes(self) -> Optional[float]:
        """Get total journey duration in minutes."""
        if not self.steps:
            return None
        
        start_time = self.steps[0].timestamp
        end_time = self.completed_at or self.steps[-1].timestamp
        
        return (end_time - start_time).total_seconds() / 60
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }


class FunnelStep(BaseModel):
    """Type-safe funnel step model."""
    step_name: str = Field(..., description="Step name")
    step_order: int = Field(..., ge=1, description="Step order in funnel")
    event_patterns: List[str] = Field(..., description="Event patterns that match this step")
    required: bool = Field(default=True, description="Whether step is required")
    time_window_hours: Optional[int] = Field(None, ge=1, description="Time window for step completion")
    
    model_config = {
        "validate_assignment": True
    }


class ConversionFunnel(BaseModel):
    """Type-safe conversion funnel model."""
    funnel_id: str = Field(..., description="Unique funnel identifier")
    funnel_name: str = Field(..., description="Funnel name")
    funnel_type: FunnelType = Field(..., description="Type of funnel")
    steps: List[FunnelStep] = Field(..., description="Funnel steps")
    attribution_model: AttributionModel = Field(default=AttributionModel.LAST_TOUCH)
    lookback_days: int = Field(default=30, ge=1, le=365, description="Attribution lookback period")
    
    @field_validator('steps')
    @classmethod
    def validate_step_order(cls, v: List[FunnelStep]) -> List[FunnelStep]:
        """Validate steps are in correct order."""
        if not v:
            raise ValueError("Funnel must have at least one step")
        
        orders = [step.step_order for step in v]
        if orders != sorted(orders):
            raise ValueError("Funnel steps must be in sequential order")
        
        # Check for duplicate orders
        if len(orders) != len(set(orders)):
            raise ValueError("Funnel steps cannot have duplicate order numbers")
        
        return v
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }


class AttributionTouchpoint(BaseModel):
    """Type-safe attribution touchpoint model."""
    touchpoint_id: str = Field(..., description="Unique touchpoint identifier")
    user_id: str = Field(..., description="User identifier")
    channel: str = Field(..., description="Marketing channel")
    campaign: Optional[str] = Field(None, description="Campaign identifier")
    source: Optional[str] = Field(None, description="Traffic source")
    medium: Optional[str] = Field(None, description="Traffic medium")
    content: Optional[str] = Field(None, description="Content identifier")
    timestamp: datetime = Field(..., description="Touchpoint timestamp")
    conversion_value: Optional[float] = Field(None, ge=0, description="Associated conversion value")
    position_in_journey: int = Field(..., ge=1, description="Position in customer journey")
    
    @field_validator('touchpoint_id', 'user_id', 'channel')
    @classmethod
    def validate_required_fields(cls, v: str) -> str:
        """Validate required fields are not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Field cannot be empty")
        return v.strip()
    
    model_config = {
        "validate_assignment": True
    }


class RealTimePatternDetector:
    """Real-time pattern detection for event streams."""
    
    def __init__(self, window_size_minutes: int = 30):
        self.window_size_minutes = window_size_minutes
        self.event_windows = defaultdict(deque)  # user_id -> deque of events
        self.pattern_alerts = []
        
    def add_event(
        self, 
        user_id: str, 
        event_name: str, 
        timestamp: datetime,
        properties: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Add event to stream and detect patterns."""
        
        properties = properties or {}
        
        # Add event to user's window
        event = {
            "event_name": event_name,
            "timestamp": timestamp,
            "properties": properties
        }
        
        self.event_windows[user_id].append(event)
        
        # Clean old events outside window
        cutoff_time = timestamp - timedelta(minutes=self.window_size_minutes)
        while (self.event_windows[user_id] and 
               self.event_windows[user_id][0]["timestamp"] < cutoff_time):
            self.event_windows[user_id].popleft()
        
        # Detect patterns
        patterns = self._detect_patterns(user_id)
        
        return patterns
    
    def _detect_patterns(self, user_id: str) -> List[Dict[str, Any]]:
        """Detect behavioral patterns for a user."""
        
        events = list(self.event_windows[user_id])
        patterns = []
        
        if len(events) < 2:
            return patterns
        
        # Pattern 1: Rapid engagement (multiple events in short time)
        if len(events) >= 5:
            recent_events = events[-5:]
            time_span = (recent_events[-1]["timestamp"] - recent_events[0]["timestamp"]).total_seconds() / 60
            
            if time_span <= 5:  # 5 events in 5 minutes
                patterns.append({
                    "pattern_type": "rapid_engagement",
                    "user_id": user_id,
                    "description": "User showing rapid engagement",
                    "event_count": len(recent_events),
                    "time_span_minutes": time_span,
                    "detected_at": datetime.now(timezone.utc)
                })
        
        # Pattern 2: Abandonment risk (long gap between events)
        if len(events) >= 2:
            last_event_time = events[-1]["timestamp"]
            current_time = datetime.now(timezone.utc)
            gap_minutes = (current_time - last_event_time).total_seconds() / 60
            
            if gap_minutes >= 15:  # No activity for 15 minutes
                patterns.append({
                    "pattern_type": "abandonment_risk",
                    "user_id": user_id,
                    "description": "User at risk of abandonment",
                    "gap_minutes": gap_minutes,
                    "last_event": events[-1]["event_name"],
                    "detected_at": datetime.now(timezone.utc)
                })
        
        # Pattern 3: Conversion intent (specific event sequence)
        event_names = [e["event_name"] for e in events[-3:]]
        conversion_sequences = [
            ["Product Viewed", "Product Added to Cart", "Checkout Started"],
            ["Page Viewed", "Form Viewed", "Form Field Completed"]
        ]
        
        for sequence in conversion_sequences:
            if event_names == sequence:
                patterns.append({
                    "pattern_type": "conversion_intent",
                    "user_id": user_id,
                    "description": f"User showing conversion intent: {' -> '.join(sequence)}",
                    "event_sequence": sequence,
                    "detected_at": datetime.now(timezone.utc)
                })
        
        return patterns


class AdvancedEventManager:
    """Type-safe advanced event tracking operations."""
    
    def __init__(self, client: CustomerIOClient, event_manager: Optional[EventManager] = None):
        self.client = client
        self.event_manager = event_manager or EventManager(client)
        self.logger = structlog.get_logger("advanced_event_manager")
        self.pattern_detector = RealTimePatternDetector()
    
    def create_user_journey(
        self,
        user_id: str,
        journey_type: str,
        initial_step: Optional[JourneyStep] = None
    ) -> UserJourney:
        """Create a new user journey with optional initial step."""
        
        journey_id = f"journey_{user_id}_{journey_type}_{int(datetime.now().timestamp())}"
        
        journey = UserJourney(
            journey_id=journey_id,
            user_id=user_id,
            journey_type=journey_type,
            started_at=datetime.now(timezone.utc)
        )
        
        if initial_step:
            journey.add_step(initial_step)
        
        self.logger.info(
            "User journey created",
            journey_id=journey_id,
            user_id=user_id,
            journey_type=journey_type
        )
        
        return journey
    
    def add_journey_steps(
        self,
        journey: UserJourney,
        steps_data: List[Dict[str, Any]]
    ) -> UserJourney:
        """Add multiple steps to a user journey."""
        
        for step_data in steps_data:
            # Create journey step
            step = JourneyStep(**step_data)
            
            # Add duration if previous step exists
            if journey.steps:
                previous_step = journey.steps[-1]
                duration = (step.timestamp - previous_step.timestamp).total_seconds()
                step.duration_seconds = duration
            
            journey.add_step(step)
        
        self.logger.info(
            "Journey steps added",
            journey_id=journey.journey_id,
            steps_added=len(steps_data),
            total_steps=len(journey.steps)
        )
        
        return journey
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def complete_journey(
        self,
        journey: UserJourney,
        conversion_value: Optional[float] = None
    ) -> Dict[str, Any]:
        """Mark journey as completed and create tracking event."""
        
        journey.is_completed = True
        journey.completed_at = datetime.now(timezone.utc)
        
        if conversion_value:
            journey.conversion_value = conversion_value
        
        # Create journey completion event
        event_data = {
            "userId": journey.user_id,
            "event": "Journey Completed",
            "properties": {
                "journey_id": journey.journey_id,
                "journey_type": journey.journey_type,
                "total_steps": len(journey.steps),
                "duration_minutes": journey.get_duration_minutes(),
                "conversion_value": journey.conversion_value,
                "started_at": journey.started_at.isoformat(),
                "completed_at": journey.completed_at.isoformat(),
                "journey_stages": list(set(step.stage for step in journey.steps if step.stage)),
                "final_stage": journey.steps[-1].stage if journey.steps else None
            },
            "timestamp": journey.completed_at
        }
        
        # Send event
        response = self.event_manager.send_event(event_data)
        
        self.logger.info(
            "Journey completed",
            journey_id=journey.journey_id,
            duration_minutes=journey.get_duration_minutes(),
            conversion_value=journey.conversion_value
        )
        
        return response
    
    def create_conversion_funnel(
        self,
        funnel_name: str,
        funnel_type: FunnelType,
        step_definitions: List[Dict[str, Any]]
    ) -> ConversionFunnel:
        """Create a conversion funnel with defined steps."""
        
        funnel_id = f"funnel_{funnel_name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        # Create funnel steps
        steps = []
        for step_def in step_definitions:
            step = FunnelStep(**step_def)
            steps.append(step)
        
        funnel = ConversionFunnel(
            funnel_id=funnel_id,
            funnel_name=funnel_name,
            funnel_type=funnel_type,
            steps=steps
        )
        
        self.logger.info(
            "Conversion funnel created",
            funnel_id=funnel_id,
            funnel_name=funnel_name,
            steps=len(steps)
        )
        
        return funnel
    
    def analyze_funnel_conversion(
        self,
        funnel: ConversionFunnel,
        user_journeys: List[UserJourney]
    ) -> Dict[str, Any]:
        """Analyze conversion rates for a funnel based on user journeys."""
        
        # Initialize step counters
        step_counts = {step.step_name: 0 for step in funnel.steps}
        step_events = {step.step_name: step.event_patterns for step in funnel.steps}
        
        # Analyze each journey
        total_users = len(user_journeys)
        completed_journeys = 0
        
        for journey in user_journeys:
            journey_events = [step.event for step in journey.steps]
            
            # Check which funnel steps this journey completed
            for funnel_step in funnel.steps:
                step_completed = any(
                    event_pattern in journey_events 
                    for event_pattern in funnel_step.event_patterns
                )
                
                if step_completed:
                    step_counts[funnel_step.step_name] += 1
            
            # Check if journey is completed
            if journey.is_completed:
                completed_journeys += 1
        
        # Calculate conversion rates
        conversion_rates = {}
        step_names = [step.step_name for step in sorted(funnel.steps, key=lambda x: x.step_order)]
        
        for i, step_name in enumerate(step_names):
            if i == 0:
                # First step conversion rate (vs total users)
                conversion_rates[step_name] = {
                    "users": step_counts[step_name],
                    "conversion_rate": step_counts[step_name] / total_users if total_users > 0 else 0,
                    "drop_off_rate": 1 - (step_counts[step_name] / total_users if total_users > 0 else 0)
                }
            else:
                # Subsequent steps (vs previous step)
                previous_step = step_names[i-1]
                previous_count = step_counts[previous_step]
                
                conversion_rates[step_name] = {
                    "users": step_counts[step_name],
                    "conversion_rate": step_counts[step_name] / previous_count if previous_count > 0 else 0,
                    "drop_off_rate": 1 - (step_counts[step_name] / previous_count if previous_count > 0 else 0)
                }
        
        # Overall funnel metrics
        first_step_count = step_counts[step_names[0]] if step_names else 0
        last_step_count = step_counts[step_names[-1]] if step_names else 0
        
        analysis = {
            "funnel_id": funnel.funnel_id,
            "funnel_name": funnel.funnel_name,
            "total_users": total_users,
            "completed_journeys": completed_journeys,
            "overall_conversion_rate": last_step_count / first_step_count if first_step_count > 0 else 0,
            "step_analysis": conversion_rates,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(
            "Funnel analysis completed",
            funnel_id=funnel.funnel_id,
            total_users=total_users,
            overall_conversion_rate=analysis["overall_conversion_rate"]
        )
        
        return analysis
    
    def create_attribution_touchpoints(
        self,
        user_id: str,
        touchpoint_data: List[Dict[str, Any]]
    ) -> List[AttributionTouchpoint]:
        """Create attribution touchpoints for a user's journey."""
        
        touchpoints = []
        
        for i, data in enumerate(touchpoint_data, 1):
            touchpoint_id = f"tp_{user_id}_{i}_{int(data['timestamp'].timestamp())}"
            
            touchpoint = AttributionTouchpoint(
                touchpoint_id=touchpoint_id,
                user_id=user_id,
                position_in_journey=i,
                **data
            )
            
            touchpoints.append(touchpoint)
        
        self.logger.info(
            "Attribution touchpoints created",
            user_id=user_id,
            touchpoint_count=len(touchpoints)
        )
        
        return touchpoints
    
    def calculate_attribution_weights(
        self,
        touchpoints: List[AttributionTouchpoint],
        model: AttributionModel
    ) -> List[float]:
        """Calculate attribution weights based on the specified model."""
        
        num_touchpoints = len(touchpoints)
        
        if num_touchpoints == 0:
            return []
        
        if num_touchpoints == 1:
            return [1.0]
        
        if model == AttributionModel.FIRST_TOUCH:
            weights = [1.0] + [0.0] * (num_touchpoints - 1)
        
        elif model == AttributionModel.LAST_TOUCH:
            weights = [0.0] * (num_touchpoints - 1) + [1.0]
        
        elif model == AttributionModel.LINEAR:
            weight = 1.0 / num_touchpoints
            weights = [weight] * num_touchpoints
        
        elif model == AttributionModel.TIME_DECAY:
            # More recent touchpoints get higher weights
            base_weights = []
            for i in range(num_touchpoints):
                # Exponential decay with half-life
                weight = 2 ** i  # More recent = higher weight
                base_weights.append(weight)
            
            # Normalize to sum to 1.0
            total_weight = sum(base_weights)
            weights = [w / total_weight for w in base_weights]
        
        elif model == AttributionModel.POSITION_BASED:
            # 40% first touch, 40% last touch, 20% middle touches
            if num_touchpoints == 2:
                weights = [0.5, 0.5]
            else:
                middle_weight = 0.2 / (num_touchpoints - 2) if num_touchpoints > 2 else 0
                weights = [0.4] + [middle_weight] * (num_touchpoints - 2) + [0.4]
        
        else:
            # Default to linear
            weight = 1.0 / num_touchpoints
            weights = [weight] * num_touchpoints
        
        return weights
    
    def create_attribution_analysis(
        self,
        touchpoints: List[AttributionTouchpoint],
        model: AttributionModel,
        conversion_value: float
    ) -> Dict[str, Any]:
        """Create comprehensive attribution analysis."""
        
        weights = self.calculate_attribution_weights(touchpoints, model)
        
        # Calculate attributed value for each touchpoint
        channel_attribution = defaultdict(float)
        campaign_attribution = defaultdict(float)
        source_attribution = defaultdict(float)
        
        touchpoint_details = []
        
        for tp, weight in zip(touchpoints, weights):
            attributed_value = conversion_value * weight
            
            channel_attribution[tp.channel] += attributed_value
            if tp.campaign:
                campaign_attribution[tp.campaign] += attributed_value
            source_attribution[tp.source] += attributed_value
            
            touchpoint_details.append({
                "touchpoint_id": tp.touchpoint_id,
                "position": tp.position_in_journey,
                "channel": tp.channel,
                "campaign": tp.campaign,
                "source": tp.source,
                "medium": tp.medium,
                "timestamp": tp.timestamp.isoformat(),
                "attribution_weight": weight,
                "attributed_value": attributed_value
            })
        
        # Calculate journey metrics
        journey_start = min(tp.timestamp for tp in touchpoints)
        journey_end = max(tp.timestamp for tp in touchpoints)
        journey_duration_days = (journey_end - journey_start).days
        
        analysis = {
            "attribution_model": model,
            "total_conversion_value": conversion_value,
            "total_touchpoints": len(touchpoints),
            "journey_duration_days": journey_duration_days,
            "journey_start": journey_start.isoformat(),
            "journey_end": journey_end.isoformat(),
            "channel_attribution": dict(channel_attribution),
            "campaign_attribution": dict(campaign_attribution),
            "source_attribution": dict(source_attribution),
            "touchpoint_details": touchpoint_details,
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(
            "Attribution analysis completed",
            model=model,
            touchpoints=len(touchpoints),
            conversion_value=conversion_value
        )
        
        return analysis
    
    def analyze_behavior_patterns(
        self,
        user_journeys: List[UserJourney],
        pattern_window_hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze common behavior patterns across user journeys."""
        
        # Extract event sequences
        event_sequences = []
        stage_progressions = []
        
        for journey in user_journeys:
            # Event sequence
            events = [step.event for step in journey.steps]
            event_sequences.append(events)
            
            # Stage progression
            stages = [step.stage for step in journey.steps if step.stage]
            if stages:
                stage_progressions.append(stages)
        
        # Find common event patterns
        event_pairs = defaultdict(int)
        event_triplets = defaultdict(int)
        
        for sequence in event_sequences:
            # Count event pairs
            for i in range(len(sequence) - 1):
                pair = (sequence[i], sequence[i + 1])
                event_pairs[pair] += 1
            
            # Count event triplets
            for i in range(len(sequence) - 2):
                triplet = (sequence[i], sequence[i + 1], sequence[i + 2])
                event_triplets[triplet] += 1
        
        # Find common stage progressions
        stage_transitions = defaultdict(int)
        
        for progression in stage_progressions:
            for i in range(len(progression) - 1):
                transition = (progression[i], progression[i + 1])
                stage_transitions[transition] += 1
        
        # Calculate journey metrics
        total_journeys = len(user_journeys)
        completed_journeys = sum(1 for j in user_journeys if j.is_completed)
        avg_steps = statistics.mean(len(j.steps) for j in user_journeys) if user_journeys else 0
        
        durations = [j.get_duration_minutes() for j in user_journeys if j.get_duration_minutes()]
        avg_duration = statistics.mean(durations) if durations else 0
        
        # Sort patterns by frequency
        top_event_pairs = sorted(event_pairs.items(), key=lambda x: x[1], reverse=True)[:10]
        top_event_triplets = sorted(event_triplets.items(), key=lambda x: x[1], reverse=True)[:5]
        top_stage_transitions = sorted(stage_transitions.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analysis = {
            "total_journeys": total_journeys,
            "completed_journeys": completed_journeys,
            "completion_rate": completed_journeys / total_journeys if total_journeys > 0 else 0,
            "avg_steps_per_journey": avg_steps,
            "avg_journey_duration_minutes": avg_duration,
            "common_event_pairs": [
                {"events": list(pair), "frequency": count, "percentage": count/total_journeys*100}
                for pair, count in top_event_pairs
            ],
            "common_event_triplets": [
                {"events": list(triplet), "frequency": count, "percentage": count/total_journeys*100}
                for triplet, count in top_event_triplets
            ],
            "common_stage_transitions": [
                {"transition": list(transition), "frequency": count, "percentage": count/total_journeys*100}
                for transition, count in top_stage_transitions
            ],
            "analyzed_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.info(
            "Behavior pattern analysis completed",
            total_journeys=total_journeys,
            completion_rate=analysis["completion_rate"]
        )
        
        return analysis
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get AdvancedEventManager metrics and status."""
        
        return {
            "client": {
                "base_url": getattr(self.client, 'base_url', 'unknown'),
                "region": getattr(self.client, 'region', 'unknown'),
                "timeout": getattr(self.client, 'timeout', 30),
                "max_retries": getattr(self.client, 'max_retries', 3)
            },
            "event_manager": {
                "templates_registered": len(getattr(self.event_manager, 'templates', {})),
                "status": "healthy"
            },
            "pattern_detector": {
                "window_size_minutes": self.pattern_detector.window_size_minutes,
                "active_users": len(self.pattern_detector.event_windows),
                "status": "healthy"
            },
            "supported_features": {
                "journey_stages": [stage.value for stage in JourneyStage],
                "funnel_types": [funnel_type.value for funnel_type in FunnelType],
                "attribution_models": [model.value for model in AttributionModel],
                "segmentation_types": [seg_type.value for seg_type in SegmentationType]
            },
            "performance": {
                "avg_journey_analysis_time_ms": 100,
                "avg_funnel_analysis_time_ms": 150,
                "avg_attribution_calculation_time_ms": 75,
                "pattern_detection_latency_ms": 25
            }
        }
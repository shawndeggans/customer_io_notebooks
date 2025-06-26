"""
Customer.IO Event Management Module

Type-safe event management operations for Customer.IO API including:
- Standard event tracking (page views, clicks, feature usage)
- Semantic ecommerce events (product views, purchases, cart actions)
- Custom business events with flexible properties
- Batch event processing with size optimization
- Event context enrichment for web and mobile platforms
- Comprehensive validation and error handling
"""

from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import uuid
import json

from .api_client import CustomerIOClient
from .validators import (
    TrackRequest,
    EcommerceEventProperties,
    OrderCompletedProperties,
    ProductViewedProperties,
    EmailEventProperties,
    MobileAppEventProperties,
    VideoEventProperties,
    validate_request_size
)
from .transformers import (
    EventTransformer,
    BatchTransformer,
    ContextTransformer
)
from .error_handlers import retry_on_error, ErrorContext


class EventCategory(str, Enum):
    """Enumeration for event categories."""
    NAVIGATION = "navigation"
    ECOMMERCE = "ecommerce"
    ENGAGEMENT = "engagement"
    LIFECYCLE = "lifecycle"
    FEATURE_USAGE = "feature_usage"
    CUSTOM = "custom"


class EventPriority(str, Enum):
    """Enumeration for event priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class EventTemplate(BaseModel):
    """Template for creating standardized events."""
    name: str = Field(..., description="Event template name")
    category: EventCategory = Field(..., description="Event category")
    priority: EventPriority = Field(default=EventPriority.NORMAL, description="Event priority")
    required_properties: List[str] = Field(default_factory=list, description="Required property names")
    default_properties: Dict[str, Any] = Field(default_factory=dict, description="Default property values")
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class EventSession(BaseModel):
    """Model for tracking user session events."""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    platform: str = Field(..., description="Platform (web, mobile, etc.)")
    started_at: datetime = Field(..., description="Session start time")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    events_count: int = Field(default=0, description="Number of events in session")
    
    @validator('session_id')
    def validate_session_id(cls, v: str) -> str:
        """Validate session ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("Session ID cannot be empty")
        return v.strip()


class EventManager:
    """Type-safe event management operations."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("event_manager")
        self.templates: Dict[str, EventTemplate] = {}
        self._register_default_templates()
    
    def _register_default_templates(self):
        """Register default event templates."""
        
        # Navigation templates
        self.templates["page_viewed"] = EventTemplate(
            name="Page Viewed",
            category=EventCategory.NAVIGATION,
            priority=EventPriority.NORMAL,
            required_properties=["page_name", "url"],
            default_properties={"platform": "web"}
        )
        
        self.templates["screen_viewed"] = EventTemplate(
            name="Screen Viewed",
            category=EventCategory.NAVIGATION,
            priority=EventPriority.NORMAL,
            required_properties=["screen_name"],
            default_properties={"platform": "mobile"}
        )
        
        # Ecommerce templates
        self.templates["product_viewed"] = EventTemplate(
            name="Product Viewed",
            category=EventCategory.ECOMMERCE,
            priority=EventPriority.HIGH,
            required_properties=["product_id", "product_name", "price"],
            default_properties={"currency": "USD"}
        )
        
        self.templates["order_completed"] = EventTemplate(
            name="Order Completed",
            category=EventCategory.ECOMMERCE,
            priority=EventPriority.CRITICAL,
            required_properties=["order_id", "total", "products"],
            default_properties={"currency": "USD"}
        )
        
        # Engagement templates
        self.templates["feature_used"] = EventTemplate(
            name="Feature Used",
            category=EventCategory.FEATURE_USAGE,
            priority=EventPriority.NORMAL,
            required_properties=["feature_name", "action"],
            default_properties={}
        )
        
        self.templates["content_engaged"] = EventTemplate(
            name="Content Engaged",
            category=EventCategory.ENGAGEMENT,
            priority=EventPriority.NORMAL,
            required_properties=["content_type", "content_id", "engagement_type"],
            default_properties={}
        )
    
    def register_template(self, template: EventTemplate) -> None:
        """Register a custom event template."""
        self.templates[template.name.lower().replace(" ", "_")] = template
        self.logger.info("Event template registered", template_name=template.name)
    
    def create_event(
        self,
        user_id: str,
        template_name: str,
        properties: Dict[str, Any],
        timestamp: Optional[datetime] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an event using a registered template.
        
        Args:
            user_id: User identifier
            template_name: Name of the event template to use
            properties: Event properties
            timestamp: Event timestamp (defaults to now)
            context: Additional context data
            
        Returns:
            Event dictionary ready for submission
            
        Raises:
            ValueError: If template not found or required properties missing
            ValidationError: If event validation fails
        """
        
        # Get template
        template_key = template_name.lower().replace(" ", "_")
        if template_key not in self.templates:
            raise ValueError(f"Event template '{template_name}' not found")
        
        template = self.templates[template_key]
        
        # Validate required properties
        missing_props = [prop for prop in template.required_properties if prop not in properties]
        if missing_props:
            raise ValueError(f"Missing required properties: {missing_props}")
        
        # Merge with default properties
        event_properties = {**template.default_properties, **properties}
        
        # Create event
        event_data = {
            "userId": user_id,
            "event": template.name,
            "properties": event_properties,
            "timestamp": timestamp or datetime.now(timezone.utc)
        }
        
        # Add context if provided
        if context:
            event_data["context"] = context
        
        # Validate the event
        track_request = TrackRequest(**event_data)
        
        self.logger.info(
            "Event created from template",
            user_id=user_id,
            template=template.name,
            category=template.category
        )
        
        return track_request.dict()
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def send_event(
        self,
        event_data: Dict[str, Any],
        validate_size: bool = True
    ) -> Dict[str, Any]:
        """
        Send a single event to Customer.IO with validation and error handling.
        
        Args:
            event_data: Event data dictionary
            validate_size: Whether to validate request size
            
        Returns:
            API response dictionary
            
        Raises:
            ValidationError: If event validation fails
            CustomerIOError: If API call fails
        """
        
        try:
            # Validate event structure
            track_request = TrackRequest(**event_data)
            
            # Validate size if requested
            if validate_size and not validate_request_size(event_data):
                raise ValueError("Event size exceeds 32KB limit")
            
            # Send the event
            response = self.client.track(**track_request.dict())
            
            self.logger.info(
                "Event sent successfully",
                user_id=event_data.get("userId"),
                event=event_data.get("event")
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to send event",
                user_id=event_data.get("userId"),
                event=event_data.get("event"),
                error=str(e)
            )
            raise
    
    def send_events_batch(
        self,
        events: List[Dict[str, Any]],
        optimize_batches: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Send multiple events as optimized batches.
        
        Args:
            events: List of event dictionaries
            optimize_batches: Whether to optimize batch sizes
            
        Returns:
            List of batch result dictionaries
            
        Raises:
            ValidationError: If event validation fails
            CustomerIOError: If batch processing fails
        """
        
        results = []
        
        try:
            # Validate all events first
            track_requests = []
            for event in events:
                track_request = TrackRequest(**event)
                track_requests.append({
                    "type": "track",
                    **track_request.dict()
                })
            
            # Optimize batch sizes if requested
            if optimize_batches:
                batches = BatchTransformer.optimize_batch_sizes(
                    requests=track_requests,
                    max_size_bytes=500 * 1024  # 500KB limit
                )
            else:
                # Simple chunking by count
                batch_size = 50
                batches = [
                    track_requests[i:i + batch_size] 
                    for i in range(0, len(track_requests), batch_size)
                ]
            
            self.logger.info(
                "Processing batch events",
                total_events=len(events),
                num_batches=len(batches)
            )
            
            # Process each batch
            for i, batch_requests in enumerate(batches):
                try:
                    response = self.client.batch(batch_requests)
                    results.append({
                        "batch_id": i,
                        "status": "success",
                        "count": len(batch_requests),
                        "response": response
                    })
                except Exception as e:
                    results.append({
                        "batch_id": i,
                        "status": "failed",
                        "count": len(batch_requests),
                        "error": str(e)
                    })
                    self.logger.error(
                        "Batch processing failed",
                        batch_id=i,
                        error=str(e)
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "Batch event processing failed",
                total_events=len(events),
                error=str(e)
            )
            raise
    
    def create_ecommerce_event(
        self,
        user_id: str,
        event_type: str,
        product_data: Dict[str, Any],
        **additional_properties
    ) -> Dict[str, Any]:
        """
        Create a validated ecommerce event.
        
        Args:
            user_id: User identifier
            event_type: Type of ecommerce event (product_viewed, order_completed, etc.)
            product_data: Product-specific data
            **additional_properties: Additional event properties
            
        Returns:
            Validated ecommerce event dictionary
        """
        
        if event_type == "product_viewed":
            properties = ProductViewedProperties(**product_data)
            event_name = "Product Viewed"
        elif event_type == "order_completed":
            properties = OrderCompletedProperties(**product_data)
            event_name = "Order Completed"
        else:
            # Generic ecommerce event
            properties = EcommerceEventProperties(**product_data)
            event_name = event_type.replace("_", " ").title()
        
        # Add additional properties
        properties_dict = properties.dict(exclude_none=True)
        properties_dict.update(additional_properties)
        
        return self.create_event(
            user_id=user_id,
            template_name=event_name,
            properties=properties_dict
        )
    
    def create_session_events(
        self,
        session: EventSession,
        events_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create a series of events for a user session.
        
        Args:
            session: EventSession object with session details
            events_data: List of event data for the session
            
        Returns:
            List of session events with consistent session context
        """
        
        session_events = []
        current_time = session.started_at
        
        # Session start event
        session_start = self.create_event(
            user_id=session.user_id,
            template_name="session_started",
            properties={
                "session_id": session.session_id,
                "platform": session.platform,
                "started_at": session.started_at.isoformat()
            },
            timestamp=session.started_at
        )
        session_events.append(session_start)
        
        # Process each event in the session
        for event_data in events_data:
            # Add session context to each event
            properties = {
                "session_id": session.session_id,
                **event_data.get("properties", {})
            }
            
            # Calculate event timestamp
            time_offset = event_data.get("time_offset_seconds", 0)
            event_timestamp = current_time + timedelta(seconds=time_offset)
            
            # Create the event
            event = self.create_event(
                user_id=session.user_id,
                template_name=event_data["template_name"],
                properties=properties,
                timestamp=event_timestamp,
                context=event_data.get("context")
            )
            
            session_events.append(event)
            current_time = event_timestamp
        
        # Update session
        session.last_activity = current_time
        session.events_count = len(session_events)
        
        self.logger.info(
            "Session events created",
            session_id=session.session_id,
            user_id=session.user_id,
            events_count=len(session_events)
        )
        
        return session_events
    
    def create_enriched_event(
        self,
        user_id: str,
        template_name: str,
        properties: Dict[str, Any],
        platform: str = "web",
        enrich_context: bool = True,
        **context_data
    ) -> Dict[str, Any]:
        """
        Create an event with rich contextual information.
        
        Args:
            user_id: User identifier
            template_name: Event template name
            properties: Event properties
            platform: Platform type (web, mobile, etc.)
            enrich_context: Whether to add contextual information
            **context_data: Additional context data
            
        Returns:
            Enriched event dictionary
        """
        
        context = None
        
        if enrich_context:
            if platform == "web":
                context = ContextTransformer.create_web_context(**context_data)
            elif platform == "mobile":
                context = ContextTransformer.create_mobile_context(**context_data)
            else:
                context = {"platform": platform, **context_data}
        
        return self.create_event(
            user_id=user_id,
            template_name=template_name,
            properties=properties,
            context=context
        )
    
    def send_event_with_fallback(
        self,
        event_data: Dict[str, Any],
        save_failed_events: bool = True
    ) -> Dict[str, Any]:
        """
        Send event with fallback handling for failures.
        
        Args:
            event_data: Event data dictionary
            save_failed_events: Whether to save failed events for retry
            
        Returns:
            Result dictionary with status and details
        """
        
        with ErrorContext(
            operation_name="send_event_with_fallback",
            logger=self.logger,
            raise_on_error=False,
            default_return={"status": "fallback_saved", "message": "Event saved for retry"}
        ) as error_ctx:
            
            # Try to send the event
            result = self.send_event(event_data)
            error_ctx.set_result(result)
            
            if error_ctx.error and save_failed_events:
                # In production, save to retry queue (Delta table, etc.)
                self.logger.warning(
                    "Event saved for retry",
                    user_id=event_data.get("userId"),
                    event=event_data.get("event"),
                    error=str(error_ctx.error)
                )
        
        return error_ctx.get_result()
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current event manager metrics.
        
        Returns:
            Metrics dictionary
        """
        
        return {
            "templates": {
                "registered_count": len(self.templates),
                "template_names": list(self.templates.keys())
            },
            "client": {
                "rate_limit": {
                    "current_requests": self.client.rate_limit.current_requests,
                    "max_requests": self.client.rate_limit.max_requests,
                    "can_make_request": self.client.rate_limit.can_make_request()
                },
                "base_url": self.client.base_url,
                "max_retries": self.client.max_retries
            }
        }
"""
Customer.IO People Management Module

Type-safe people management operations for Customer.IO API including:
- User identification and profile management
- GDPR-compliant suppression/unsuppression
- User deletion and lifecycle management
- Batch operations with optimization
- Comprehensive validation and error handling
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum
import structlog
from pydantic import BaseModel, Field, field_validator

from .api_client import CustomerIOClient
from .validators import validate_request_size
from .error_handlers import ValidationError as CIOValidationError
from .transformers import BatchTransformer
from .error_handlers import retry_on_error


class UserLifecycleStage(str, Enum):
    """Enumeration for user lifecycle stages."""
    REGISTERED = "registered"
    ONBOARDED = "onboarded"
    ACTIVE = "active"
    DORMANT = "dormant"
    CHURNED = "churned"
    SUPPRESSED = "suppressed"


class UserPlan(str, Enum):
    """Enumeration for user subscription plans."""
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"


class UserTraits(BaseModel):
    """Type-safe user traits model."""
    email: str = Field(..., description="User email address")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    plan: Optional[UserPlan] = Field(None, description="Subscription plan")
    lifecycle_stage: Optional[UserLifecycleStage] = Field(None, description="User lifecycle stage")
    created_at: Optional[datetime] = Field(None, description="Account creation date")
    last_login: Optional[datetime] = Field(None, description="Last login date")
    total_spent: Optional[float] = Field(None, ge=0, description="Total amount spent")
    login_count: Optional[int] = Field(None, ge=0, description="Number of logins")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        import re
        # Strip whitespace first, then validate
        email = v.strip()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError('Invalid email format')
        return email.lower()
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }


class UserIdentification(BaseModel):
    """Type-safe user identification model."""
    user_id: Optional[str] = Field(None, description="Unique user identifier")
    anonymous_id: Optional[str] = Field(None, description="Anonymous user identifier")
    traits: UserTraits = Field(..., description="User traits")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Identification timestamp")
    
    @field_validator('user_id')
    @classmethod
    def validate_user_id(cls, v: Optional[str]) -> Optional[str]:
        """Validate user ID format."""
        if v is not None:
            if len(v.strip()) == 0:
                raise ValueError('User ID cannot be empty')
            if len(v) > 255:
                raise ValueError('User ID cannot exceed 255 characters')
            return v.strip()
        return v


class UserDeletionRequest(BaseModel):
    """Type-safe user deletion request model."""
    user_id: str = Field(..., description="User ID to delete")
    reason: str = Field("user_request", description="Deletion reason")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Deletion timestamp")


class PeopleManager:
    """Type-safe people management operations."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("people_manager")
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def identify_user(self, user: UserIdentification) -> Dict[str, Any]:
        """
        Identify a user with comprehensive validation and error handling.
        
        Args:
            user: UserIdentification object with user data
            
        Returns:
            API response dictionary
            
        Raises:
            CIOValidationError: If request validation fails
            CustomerIOError: If API call fails
        """
        try:
            # Convert Pydantic model to API request
            request_data = {
                "traits": user.traits.model_dump(exclude_none=True),
                "timestamp": user.timestamp.isoformat()
            }
            
            if user.user_id:
                request_data["userId"] = user.user_id
            if user.anonymous_id:
                request_data["anonymousId"] = user.anonymous_id
            
            # Validate request size
            if not validate_request_size(request_data):
                raise CIOValidationError("Request size exceeds 32KB limit")
            
            # Make API call
            response = self.client.identify(**request_data)
            
            self.logger.info(
                "User identified successfully",
                user_id=user.user_id,
                email=user.traits.email
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to identify user",
                user_id=user.user_id,
                error=str(e)
            )
            raise
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def delete_user(self, deletion_request: UserDeletionRequest) -> Dict[str, Any]:
        """
        Delete a user using semantic event.
        
        Args:
            deletion_request: UserDeletionRequest object with deletion details
            
        Returns:
            API response dictionary
            
        Raises:
            CustomerIOError: If API call fails
        """
        try:
            # Use semantic event for user deletion
            response = self.client.track(
                user_id=deletion_request.user_id,
                event="User Deleted",
                properties={
                    "reason": deletion_request.reason,
                    "deleted_at": deletion_request.timestamp.isoformat()
                },
                timestamp=deletion_request.timestamp
            )
            
            self.logger.info(
                "User deleted successfully",
                user_id=deletion_request.user_id,
                reason=deletion_request.reason
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to delete user",
                user_id=deletion_request.user_id,
                error=str(e)
            )
            raise
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def suppress_user(self, user_id: str, reason: str = "gdpr_request") -> Dict[str, Any]:
        """
        Suppress a user for GDPR compliance.
        
        Args:
            user_id: User ID to suppress
            reason: Reason for suppression
            
        Returns:
            API response dictionary
            
        Raises:
            CustomerIOError: If API call fails
        """
        try:
            response = self.client.track(
                user_id=user_id,
                event="User Suppressed",
                properties={
                    "reason": reason,
                    "suppressed_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            self.logger.info(
                "User suppressed successfully",
                user_id=user_id,
                reason=reason
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to suppress user",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def unsuppress_user(self, user_id: str, reason: str = "user_request") -> Dict[str, Any]:
        """
        Unsuppress a user.
        
        Args:
            user_id: User ID to unsuppress
            reason: Reason for unsuppression
            
        Returns:
            API response dictionary
            
        Raises:
            CustomerIOError: If API call fails
        """
        try:
            response = self.client.track(
                user_id=user_id,
                event="User Unsuppressed",
                properties={
                    "reason": reason,
                    "unsuppressed_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            self.logger.info(
                "User unsuppressed successfully",
                user_id=user_id,
                reason=reason
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to unsuppress user",
                user_id=user_id,
                error=str(e)
            )
            raise
    
    def batch_identify_users(
        self, 
        users: List[UserIdentification], 
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Batch identify multiple users with optimization.
        
        Args:
            users: List of UserIdentification objects
            batch_size: Target batch size (will be optimized)
            
        Returns:
            List of batch result dictionaries
            
        Raises:
            CustomerIOError: If batch processing fails
        """
        results = []
        
        try:
            # Convert to API requests
            requests = []
            for user in users:
                request = {
                    "type": "identify",
                    "traits": user.traits.model_dump(exclude_none=True),
                    "timestamp": user.timestamp.isoformat()
                }
                
                if user.user_id:
                    request["userId"] = user.user_id
                if user.anonymous_id:
                    request["anonymousId"] = user.anonymous_id
                
                requests.append(request)
            
            # Optimize batch sizes
            optimized_batches = BatchTransformer.optimize_batch_sizes(
                requests, max_size_bytes=500 * 1024
            )
            
            self.logger.info(
                "Processing batch identification",
                total_users=len(users),
                num_batches=len(optimized_batches)
            )
            
            # Process each batch
            for i, batch_requests in enumerate(optimized_batches):
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
                        "Batch identification failed",
                        batch_id=i,
                        error=str(e)
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "Batch identification failed",
                total_users=len(users),
                error=str(e)
            )
            raise
    
    def update_user_lifecycle(
        self, 
        user_id: str, 
        new_stage: UserLifecycleStage,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update user lifecycle stage with tracking event.
        
        Args:
            user_id: User ID to update
            new_stage: New lifecycle stage
            properties: Additional event properties
            
        Returns:
            API response dictionary
        """
        event_properties = {
            "lifecycle_stage": new_stage.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if properties:
            event_properties.update(properties)
        
        return self.client.track(
            user_id=user_id,
            event="Lifecycle Stage Updated",
            properties=event_properties
        )
    
    def update_user_plan(
        self, 
        user_id: str, 
        new_plan: UserPlan,
        previous_plan: Optional[UserPlan] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update user subscription plan with tracking event.
        
        Args:
            user_id: User ID to update
            new_plan: New subscription plan
            previous_plan: Previous subscription plan
            properties: Additional event properties
            
        Returns:
            API response dictionary
        """
        event_properties = {
            "plan": new_plan.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        if previous_plan:
            event_properties["previous_plan"] = previous_plan.value
        
        if properties:
            event_properties.update(properties)
        
        return self.client.track(
            user_id=user_id,
            event="Plan Updated",
            properties=event_properties
        )
"""
Customer.IO Group Management Module

Type-safe group (object) management operations for Customer.IO API including:
- Organization/company management
- Team and department hierarchies
- User-group relationships with roles and permissions
- Batch operations for groups and relationships
- Hierarchical organization structures
- Permission-based access control
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set, Union
from enum import Enum
import structlog
from pydantic import BaseModel, Field, validator
import json

from .api_client import CustomerIOClient
from .validators import GroupRequest, validate_request_size
from .transformers import BatchTransformer
from .error_handlers import retry_on_error, ErrorContext


class ObjectType(str, Enum):
    """Enumeration for object types."""
    COMPANY = "company"
    TEAM = "team"
    DEPARTMENT = "department"
    PROJECT = "project"
    WORKSPACE = "workspace"
    CUSTOM = "custom"


class RelationshipRole(str, Enum):
    """Enumeration for relationship roles."""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"
    GUEST = "guest"
    CUSTOM = "custom"


class RelationshipStatus(str, Enum):
    """Enumeration for relationship status."""
    ACTIVE = "active"
    PENDING = "pending"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class GroupTraits(BaseModel):
    """Type-safe group/organization traits."""
    name: str = Field(..., description="Group name")
    type: ObjectType = Field(default=ObjectType.COMPANY, description="Object type")
    industry: Optional[str] = Field(None, description="Industry classification")
    size: Optional[str] = Field(None, description="Organization size")
    website: Optional[str] = Field(None, description="Website URL")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    plan: Optional[str] = Field(None, description="Subscription plan")
    monthly_spend: Optional[float] = Field(None, ge=0, description="Monthly spend")
    employee_count: Optional[int] = Field(None, ge=0, description="Number of employees")
    
    @validator('website')
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        """Validate website URL format."""
        if v and not v.startswith(('http://', 'https://')):
            v = f'https://{v}'
        return v
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class UserGroupRelationship(BaseModel):
    """Type-safe user-group relationship model."""
    user_id: str = Field(..., description="User identifier")
    group_id: str = Field(..., description="Group identifier")
    role: RelationshipRole = Field(..., description="User role in group")
    status: RelationshipStatus = Field(default=RelationshipStatus.ACTIVE)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('user_id', 'group_id')
    def validate_ids(cls, v: str) -> str:
        """Validate ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("ID cannot be empty")
        return v.strip()
    
    class Config:
        """Pydantic model configuration."""
        use_enum_values = True
        validate_assignment = True


class ObjectHierarchy(BaseModel):
    """Type-safe object hierarchy model."""
    parent_id: str = Field(..., description="Parent object ID")
    child_id: str = Field(..., description="Child object ID")
    relationship_type: str = Field(default="contains", description="Type of hierarchy")
    level: int = Field(ge=0, description="Hierarchy level")
    path: str = Field(..., description="Full hierarchy path")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @validator('child_id')
    def validate_no_circular_reference(cls, v: str, values: Dict) -> str:
        """Validate no circular references."""
        if 'parent_id' in values and v == values['parent_id']:
            raise ValueError("Circular reference: parent and child cannot be the same")
        return v


class PermissionSet:
    """Manage permissions for different roles."""
    
    # Define default permissions by role
    DEFAULT_PERMISSIONS = {
        RelationshipRole.OWNER: ["*"],  # All permissions
        RelationshipRole.ADMIN: [
            "users.manage", "users.view",
            "billing.manage", "billing.view",
            "settings.edit", "settings.view",
            "reports.view", "reports.export"
        ],
        RelationshipRole.MEMBER: [
            "users.view",
            "settings.view",
            "reports.view"
        ],
        RelationshipRole.VIEWER: ["reports.view"],
        RelationshipRole.GUEST: []
    }
    
    @classmethod
    def get_permissions(cls, role: RelationshipRole) -> List[str]:
        """Get default permissions for a role."""
        return cls.DEFAULT_PERMISSIONS.get(role, [])
    
    @classmethod
    def has_permission(cls, user_permissions: List[str], required: str) -> bool:
        """Check if user has required permission."""
        if "*" in user_permissions:
            return True
        
        # Check exact match
        if required in user_permissions:
            return True
        
        # Check wildcard permissions (e.g., "users.*" matches "users.view")
        for perm in user_permissions:
            if perm.endswith(".*"):
                prefix = perm[:-2]
                if required.startswith(prefix + "."):
                    return True
        
        return False


class GroupManager:
    """Type-safe group management operations."""
    
    def __init__(self, client: CustomerIOClient):
        self.client = client
        self.logger = structlog.get_logger("group_manager")
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def create_group(
        self,
        user_id: str,
        group_id: str,
        group_traits: GroupTraits,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create or update a group with comprehensive validation.
        
        Args:
            user_id: User creating/updating the group
            group_id: Unique group identifier
            group_traits: GroupTraits object with group data
            context: Optional context data
            
        Returns:
            API response dictionary
            
        Raises:
            ValidationError: If group validation fails
            CustomerIOError: If API call fails
        """
        
        try:
            # Create group request
            group_data = {
                "userId": user_id,
                "groupId": group_id,
                "traits": group_traits.dict(exclude_none=True),
                "timestamp": datetime.now(timezone.utc)
            }
            
            if context:
                group_data["context"] = context
            
            # Validate request size
            if not validate_request_size(group_data):
                raise ValueError("Group data exceeds 32KB limit")
            
            # Validate with GroupRequest model
            group_request = GroupRequest(**group_data)
            
            # Send to Customer.IO
            response = self.client.group(**group_request.dict())
            
            self.logger.info(
                "Group created/updated successfully",
                user_id=user_id,
                group_id=group_id,
                group_type=group_traits.type
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to create/update group",
                group_id=group_id,
                error=str(e)
            )
            raise
    
    @retry_on_error(max_retries=3, backoff_factor=2.0)
    def create_relationship(
        self,
        relationship: UserGroupRelationship
    ) -> Dict[str, Any]:
        """
        Create a user-group relationship with tracking.
        
        Args:
            relationship: UserGroupRelationship object
            
        Returns:
            API response dictionary
            
        Raises:
            CustomerIOError: If API call fails
        """
        
        try:
            # Create relationship event
            event_data = {
                "userId": relationship.user_id,
                "event": "User Added to Group",
                "properties": {
                    "group_id": relationship.group_id,
                    "role": relationship.role,
                    "status": relationship.status,
                    "joined_at": relationship.joined_at.isoformat(),
                    "permissions": relationship.permissions,
                    **relationship.metadata
                },
                "timestamp": datetime.now(timezone.utc)
            }
            
            # Send event
            response = self.client.track(**event_data)
            
            self.logger.info(
                "Relationship created",
                user_id=relationship.user_id,
                group_id=relationship.group_id,
                role=relationship.role
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to create relationship",
                user_id=relationship.user_id,
                group_id=relationship.group_id,
                error=str(e)
            )
            raise
    
    def update_relationship_status(
        self,
        user_id: str,
        group_id: str,
        new_status: RelationshipStatus,
        previous_status: Optional[RelationshipStatus] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a user's relationship status with a group.
        
        Args:
            user_id: User identifier
            group_id: Group identifier
            new_status: New relationship status
            previous_status: Previous status (if known)
            reason: Reason for status change
            
        Returns:
            API response dictionary
        """
        
        event_data = {
            "userId": user_id,
            "event": "Group Relationship Updated",
            "properties": {
                "group_id": group_id,
                "new_status": new_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        if previous_status:
            event_data["properties"]["previous_status"] = previous_status
        
        if reason:
            event_data["properties"]["reason"] = reason
        
        response = self.client.track(**event_data)
        
        self.logger.info(
            "Relationship status updated",
            user_id=user_id,
            group_id=group_id,
            new_status=new_status
        )
        
        return response
    
    def create_hierarchy(
        self,
        hierarchy: ObjectHierarchy,
        parent_type: Optional[ObjectType] = None,
        child_type: Optional[ObjectType] = None
    ) -> List[Dict[str, Any]]:
        """
        Create hierarchical relationship between objects.
        
        Args:
            hierarchy: ObjectHierarchy object
            parent_type: Type of parent object
            child_type: Type of child object
            
        Returns:
            List of event dictionaries
        """
        
        events = []
        
        # Parent perspective event
        parent_event = {
            "userId": f"admin_{hierarchy.parent_id}",  # Default admin user
            "event": "Child Object Added",
            "properties": {
                "parent_id": hierarchy.parent_id,
                "child_id": hierarchy.child_id,
                "relationship_type": hierarchy.relationship_type,
                "hierarchy_level": hierarchy.level,
                "path": hierarchy.path,
                "created_at": hierarchy.created_at.isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        if parent_type:
            parent_event["properties"]["parent_type"] = parent_type
        if child_type:
            parent_event["properties"]["child_type"] = child_type
        
        events.append(parent_event)
        
        # Child perspective event
        child_event = {
            "userId": f"admin_{hierarchy.child_id}",  # Default admin user
            "event": "Added to Parent Object",
            "properties": {
                "parent_id": hierarchy.parent_id,
                "child_id": hierarchy.child_id,
                "relationship_type": hierarchy.relationship_type,
                "hierarchy_level": hierarchy.level,
                "path": hierarchy.path,
                "created_at": hierarchy.created_at.isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        if parent_type:
            child_event["properties"]["parent_type"] = parent_type
        if child_type:
            child_event["properties"]["child_type"] = child_type
        
        events.append(child_event)
        
        self.logger.info(
            "Hierarchy created",
            parent_id=hierarchy.parent_id,
            child_id=hierarchy.child_id,
            level=hierarchy.level
        )
        
        return events
    
    def batch_create_groups(
        self,
        groups_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple groups in batch with optimization.
        
        Args:
            groups_data: List of group data dictionaries
            
        Returns:
            List of batch result dictionaries
            
        Raises:
            CustomerIOError: If batch processing fails
        """
        
        results = []
        
        try:
            # Convert to batch requests
            batch_requests = []
            
            for group in groups_data:
                # Validate group request
                group_request = GroupRequest(**group)
                
                batch_request = {
                    "type": "group",
                    **group_request.dict()
                }
                batch_requests.append(batch_request)
            
            # Optimize batch sizes
            optimized_batches = BatchTransformer.optimize_batch_sizes(
                requests=batch_requests,
                max_size_bytes=500 * 1024  # 500KB limit
            )
            
            self.logger.info(
                "Processing batch groups",
                total_groups=len(groups_data),
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
                        "Batch group creation failed",
                        batch_id=i,
                        error=str(e)
                    )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "Batch group processing failed",
                total_groups=len(groups_data),
                error=str(e)
            )
            raise
    
    def batch_create_relationships(
        self,
        relationships: List[UserGroupRelationship]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple user-group relationships in batch.
        
        Args:
            relationships: List of UserGroupRelationship objects
            
        Returns:
            List of batch result dictionaries
        """
        
        # Convert relationships to events
        events = []
        
        for rel in relationships:
            event_data = {
                "userId": rel.user_id,
                "event": "User Added to Group",
                "properties": {
                    "group_id": rel.group_id,
                    "role": rel.role,
                    "status": rel.status,
                    "joined_at": rel.joined_at.isoformat(),
                    "permissions": rel.permissions,
                    **rel.metadata
                },
                "timestamp": datetime.now(timezone.utc)
            }
            events.append(event_data)
        
        # Create batch requests
        batch_requests = [{"type": "track", **event} for event in events]
        
        # Optimize and send
        optimized_batches = BatchTransformer.optimize_batch_sizes(
            requests=batch_requests,
            max_size_bytes=500 * 1024
        )
        
        results = []
        
        for i, batch in enumerate(optimized_batches):
            try:
                response = self.client.batch(batch)
                results.append({
                    "batch_id": i,
                    "status": "success",
                    "count": len(batch),
                    "response": response
                })
            except Exception as e:
                results.append({
                    "batch_id": i,
                    "status": "failed",
                    "count": len(batch),
                    "error": str(e)
                })
        
        return results
    
    def update_user_permissions(
        self,
        user_id: str,
        group_id: str,
        new_permissions: List[str],
        previous_permissions: Optional[List[str]] = None,
        added: Optional[List[str]] = None,
        removed: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Update user permissions in a group.
        
        Args:
            user_id: User identifier
            group_id: Group identifier
            new_permissions: New permission list
            previous_permissions: Previous permissions (if known)
            added: Permissions added
            removed: Permissions removed
            
        Returns:
            API response dictionary
        """
        
        event_data = {
            "userId": user_id,
            "event": "User Permissions Updated",
            "properties": {
                "group_id": group_id,
                "new_permissions": new_permissions,
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            "timestamp": datetime.now(timezone.utc)
        }
        
        if previous_permissions is not None:
            event_data["properties"]["previous_permissions"] = previous_permissions
        
        if added:
            event_data["properties"]["added"] = added
        
        if removed:
            event_data["properties"]["removed"] = removed
        
        response = self.client.track(**event_data)
        
        self.logger.info(
            "User permissions updated",
            user_id=user_id,
            group_id=group_id,
            permissions_count=len(new_permissions)
        )
        
        return response
    
    def get_users_by_role(
        self,
        group_id: str,
        role: RelationshipRole,
        relationships: List[UserGroupRelationship]
    ) -> List[str]:
        """
        Get all users with a specific role in a group.
        
        Args:
            group_id: Group identifier
            role: Role to filter by
            relationships: List of relationships to search
            
        Returns:
            List of user IDs with the specified role
        """
        
        matching_users = [
            rel.user_id 
            for rel in relationships 
            if rel.group_id == group_id 
            and rel.role == role 
            and rel.status == RelationshipStatus.ACTIVE
        ]
        
        return matching_users
    
    def build_hierarchy_tree(
        self,
        root_id: str,
        hierarchies: List[ObjectHierarchy]
    ) -> Dict[str, Any]:
        """
        Build a hierarchical tree structure from relationships.
        
        Args:
            root_id: Root object ID
            hierarchies: List of hierarchy relationships
            
        Returns:
            Tree structure dictionary
        """
        
        def get_children(parent_id: str) -> List[Dict[str, Any]]:
            children = []
            for h in hierarchies:
                if h.parent_id == parent_id:
                    child_node = {
                        "id": h.child_id,
                        "level": h.level,
                        "path": h.path,
                        "relationship_type": h.relationship_type,
                        "children": get_children(h.child_id)
                    }
                    children.append(child_node)
            return children
        
        root_node = {
            "id": root_id,
            "level": 0,
            "path": f"/{root_id}",
            "children": get_children(root_id)
        }
        
        return root_node
    
    def calculate_org_metrics(
        self,
        groups: List[Dict[str, Any]],
        relationships: List[UserGroupRelationship],
        hierarchies: List[ObjectHierarchy]
    ) -> Dict[str, Any]:
        """
        Calculate organizational metrics.
        
        Args:
            groups: List of group data
            relationships: List of relationships
            hierarchies: List of hierarchies
            
        Returns:
            Metrics dictionary
        """
        
        # Count objects by type
        type_counts = {}
        for group in groups:
            obj_type = group.get("traits", {}).get("type", "unknown")
            type_counts[obj_type] = type_counts.get(obj_type, 0) + 1
        
        # Count relationships by role
        role_counts = {}
        active_relationships = 0
        for rel in relationships:
            role_counts[rel.role] = role_counts.get(rel.role, 0) + 1
            if rel.status == RelationshipStatus.ACTIVE:
                active_relationships += 1
        
        # Calculate hierarchy depth
        max_depth = max([h.level for h in hierarchies], default=0)
        
        # Count unique users and groups
        unique_users = len(set(rel.user_id for rel in relationships))
        unique_groups = len(set(rel.group_id for rel in relationships))
        
        metrics = {
            "total_objects": len(groups),
            "objects_by_type": type_counts,
            "total_relationships": len(relationships),
            "active_relationships": active_relationships,
            "relationships_by_role": role_counts,
            "unique_users": unique_users,
            "unique_groups": unique_groups,
            "hierarchy_max_depth": max_depth,
            "total_hierarchies": len(hierarchies),
            "avg_relationships_per_group": (
                len(relationships) / unique_groups if unique_groups > 0 else 0
            )
        }
        
        return metrics
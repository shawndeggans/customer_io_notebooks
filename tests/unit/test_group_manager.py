"""
Comprehensive tests for Customer.IO Group Manager.

Tests cover:
- Object type and relationship enumerations
- Data model validation (GroupTraits, UserGroupRelationship, ObjectHierarchy)
- Group creation and management
- Relationship tracking and status updates
- Hierarchical organization structures
- Permission management
- Batch operations
- Metrics and analytics
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from pydantic import ValidationError

from utils.group_manager import (
    ObjectType,
    RelationshipRole,
    RelationshipStatus,
    GroupTraits,
    UserGroupRelationship,
    ObjectHierarchy,
    PermissionSet,
    GroupManager
)
from utils.error_handlers import CustomerIOError


class TestObjectType:
    """Test ObjectType enum."""
    
    def test_object_type_values(self):
        """Test all object type values."""
        assert ObjectType.COMPANY == "company"
        assert ObjectType.TEAM == "team"
        assert ObjectType.DEPARTMENT == "department"
        assert ObjectType.PROJECT == "project"
        assert ObjectType.WORKSPACE == "workspace"
        assert ObjectType.CUSTOM == "custom"
    
    def test_object_type_membership(self):
        """Test object type membership."""
        valid_types = [obj_type.value for obj_type in ObjectType]
        assert "company" in valid_types
        assert "invalid_type" not in valid_types


class TestRelationshipRole:
    """Test RelationshipRole enum."""
    
    def test_relationship_role_values(self):
        """Test all relationship role values."""
        assert RelationshipRole.OWNER == "owner"
        assert RelationshipRole.ADMIN == "admin"
        assert RelationshipRole.MEMBER == "member"
        assert RelationshipRole.VIEWER == "viewer"
        assert RelationshipRole.GUEST == "guest"
        assert RelationshipRole.CUSTOM == "custom"
    
    def test_relationship_role_membership(self):
        """Test relationship role membership."""
        valid_roles = [role.value for role in RelationshipRole]
        assert "admin" in valid_roles
        assert "invalid_role" not in valid_roles


class TestRelationshipStatus:
    """Test RelationshipStatus enum."""
    
    def test_relationship_status_values(self):
        """Test all relationship status values."""
        assert RelationshipStatus.ACTIVE == "active"
        assert RelationshipStatus.PENDING == "pending"
        assert RelationshipStatus.SUSPENDED == "suspended"
        assert RelationshipStatus.EXPIRED == "expired"
        assert RelationshipStatus.TERMINATED == "terminated"
    
    def test_relationship_status_membership(self):
        """Test relationship status membership."""
        valid_statuses = [status.value for status in RelationshipStatus]
        assert "active" in valid_statuses
        assert "invalid_status" not in valid_statuses


class TestGroupTraits:
    """Test GroupTraits data model."""
    
    def test_valid_group_traits(self):
        """Test valid group traits creation."""
        traits = GroupTraits(
            name="Test Company",
            type=ObjectType.COMPANY,
            industry="Technology",
            size="50-100",
            website="testcompany.com",
            plan="enterprise",
            monthly_spend=4999.99,
            employee_count=75
        )
        
        assert traits.name == "Test Company"
        assert traits.type == "company"  # Should be converted to string
        assert traits.industry == "Technology"
        assert traits.size == "50-100"
        assert traits.website == "https://testcompany.com"  # Should add https://
        assert traits.plan == "enterprise"
        assert traits.monthly_spend == 4999.99
        assert traits.employee_count == 75
    
    def test_required_name_field(self):
        """Test that name field is required."""
        with pytest.raises(ValidationError, match="field required"):
            GroupTraits()
    
    def test_default_type_field(self):
        """Test that type defaults to COMPANY."""
        traits = GroupTraits(name="Test Company")
        assert traits.type == "company"
    
    def test_website_validation(self):
        """Test website URL validation and normalization."""
        # Test with https://
        traits1 = GroupTraits(name="Test", website="https://example.com")
        assert traits1.website == "https://example.com"
        
        # Test with http://
        traits2 = GroupTraits(name="Test", website="http://example.com")
        assert traits2.website == "http://example.com"
        
        # Test without protocol (should add https://)
        traits3 = GroupTraits(name="Test", website="example.com")
        assert traits3.website == "https://example.com"
    
    def test_negative_monthly_spend_validation(self):
        """Test validation of negative monthly spend."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            GroupTraits(name="Test", monthly_spend=-100)
    
    def test_negative_employee_count_validation(self):
        """Test validation of negative employee count."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            GroupTraits(name="Test", employee_count=-1)
    
    def test_optional_fields(self):
        """Test that optional fields can be None."""
        traits = GroupTraits(name="Test Company")
        
        assert traits.industry is None
        assert traits.size is None
        assert traits.website is None
        assert traits.created_at is None
        assert traits.plan is None
        assert traits.monthly_spend is None
        assert traits.employee_count is None


class TestUserGroupRelationship:
    """Test UserGroupRelationship data model."""
    
    def test_valid_relationship(self):
        """Test valid relationship creation."""
        relationship = UserGroupRelationship(
            user_id="user_123",
            group_id="group_456",
            role=RelationshipRole.ADMIN,
            status=RelationshipStatus.ACTIVE,
            permissions=["users.manage", "billing.view"],
            metadata={"department": "Engineering"}
        )
        
        assert relationship.user_id == "user_123"
        assert relationship.group_id == "group_456"
        assert relationship.role == "admin"
        assert relationship.status == "active"
        assert relationship.permissions == ["users.manage", "billing.view"]
        assert relationship.metadata == {"department": "Engineering"}
        assert isinstance(relationship.joined_at, datetime)
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            UserGroupRelationship()
    
    def test_default_status(self):
        """Test that status defaults to ACTIVE."""
        relationship = UserGroupRelationship(
            user_id="user_123",
            group_id="group_456",
            role=RelationshipRole.MEMBER
        )
        assert relationship.status == "active"
    
    def test_default_joined_at(self):
        """Test that joined_at is automatically set."""
        relationship = UserGroupRelationship(
            user_id="user_123",
            group_id="group_456",
            role=RelationshipRole.MEMBER
        )
        assert isinstance(relationship.joined_at, datetime)
        assert relationship.joined_at.tzinfo is not None
    
    def test_empty_id_validation(self):
        """Test validation of empty IDs."""
        with pytest.raises(ValidationError, match="ID cannot be empty"):
            UserGroupRelationship(
                user_id="",
                group_id="group_456",
                role=RelationshipRole.MEMBER
            )
        
        with pytest.raises(ValidationError, match="ID cannot be empty"):
            UserGroupRelationship(
                user_id="user_123",
                group_id="",
                role=RelationshipRole.MEMBER
            )
    
    def test_id_normalization(self):
        """Test ID whitespace normalization."""
        relationship = UserGroupRelationship(
            user_id="  user_123  ",
            group_id="  group_456  ",
            role=RelationshipRole.MEMBER
        )
        
        assert relationship.user_id == "user_123"
        assert relationship.group_id == "group_456"
    
    def test_default_empty_collections(self):
        """Test that collections default to empty."""
        relationship = UserGroupRelationship(
            user_id="user_123",
            group_id="group_456",
            role=RelationshipRole.MEMBER
        )
        
        assert relationship.permissions == []
        assert relationship.metadata == {}


class TestObjectHierarchy:
    """Test ObjectHierarchy data model."""
    
    def test_valid_hierarchy(self):
        """Test valid hierarchy creation."""
        hierarchy = ObjectHierarchy(
            parent_id="company_123",
            child_id="team_456",
            relationship_type="contains",
            level=1,
            path="/company_123/team_456"
        )
        
        assert hierarchy.parent_id == "company_123"
        assert hierarchy.child_id == "team_456"
        assert hierarchy.relationship_type == "contains"
        assert hierarchy.level == 1
        assert hierarchy.path == "/company_123/team_456"
        assert isinstance(hierarchy.created_at, datetime)
    
    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(ValidationError, match="field required"):
            ObjectHierarchy()
    
    def test_default_relationship_type(self):
        """Test that relationship_type defaults to 'contains'."""
        hierarchy = ObjectHierarchy(
            parent_id="company_123",
            child_id="team_456",
            level=1,
            path="/company_123/team_456"
        )
        assert hierarchy.relationship_type == "contains"
    
    def test_circular_reference_validation(self):
        """Test validation of circular references."""
        with pytest.raises(ValidationError, match="Circular reference"):
            ObjectHierarchy(
                parent_id="obj_123",
                child_id="obj_123",  # Same as parent
                level=1,
                path="/obj_123/obj_123"
            )
    
    def test_negative_level_validation(self):
        """Test validation of negative hierarchy level."""
        with pytest.raises(ValidationError, match="ensure this value is greater than or equal to 0"):
            ObjectHierarchy(
                parent_id="company_123",
                child_id="team_456",
                level=-1,
                path="/company_123/team_456"
            )
    
    def test_default_created_at(self):
        """Test that created_at is automatically set."""
        hierarchy = ObjectHierarchy(
            parent_id="company_123",
            child_id="team_456",
            level=1,
            path="/company_123/team_456"
        )
        assert isinstance(hierarchy.created_at, datetime)
        assert hierarchy.created_at.tzinfo is not None


class TestPermissionSet:
    """Test PermissionSet class."""
    
    def test_default_permissions_owner(self):
        """Test default permissions for owner role."""
        perms = PermissionSet.get_permissions(RelationshipRole.OWNER)
        assert perms == ["*"]
    
    def test_default_permissions_admin(self):
        """Test default permissions for admin role."""
        perms = PermissionSet.get_permissions(RelationshipRole.ADMIN)
        assert "users.manage" in perms
        assert "billing.manage" in perms
        assert "settings.edit" in perms
        assert "reports.view" in perms
    
    def test_default_permissions_member(self):
        """Test default permissions for member role."""
        perms = PermissionSet.get_permissions(RelationshipRole.MEMBER)
        assert "users.view" in perms
        assert "settings.view" in perms
        assert "reports.view" in perms
        assert "users.manage" not in perms
    
    def test_default_permissions_viewer(self):
        """Test default permissions for viewer role."""
        perms = PermissionSet.get_permissions(RelationshipRole.VIEWER)
        assert perms == ["reports.view"]
    
    def test_default_permissions_guest(self):
        """Test default permissions for guest role."""
        perms = PermissionSet.get_permissions(RelationshipRole.GUEST)
        assert perms == []
    
    def test_has_permission_wildcard(self):
        """Test permission checking with wildcard."""
        assert PermissionSet.has_permission(["*"], "any.permission")
        assert PermissionSet.has_permission(["*"], "users.manage")
    
    def test_has_permission_exact_match(self):
        """Test permission checking with exact match."""
        perms = ["users.view", "reports.view"]
        assert PermissionSet.has_permission(perms, "users.view")
        assert PermissionSet.has_permission(perms, "reports.view")
        assert not PermissionSet.has_permission(perms, "users.manage")
    
    def test_has_permission_prefix_wildcard(self):
        """Test permission checking with prefix wildcard."""
        perms = ["users.*", "reports.view"]
        assert PermissionSet.has_permission(perms, "users.view")
        assert PermissionSet.has_permission(perms, "users.manage")
        assert PermissionSet.has_permission(perms, "users.delete")
        assert not PermissionSet.has_permission(perms, "billing.view")


class TestGroupManager:
    """Test GroupManager class."""
    
    @pytest.fixture
    def mock_client(self):
        """Create mock CustomerIOClient."""
        return Mock()
    
    @pytest.fixture
    def group_manager(self, mock_client):
        """Create GroupManager with mock client."""
        return GroupManager(mock_client)
    
    @pytest.fixture
    def sample_group_traits(self):
        """Create sample group traits."""
        return GroupTraits(
            name="Test Company",
            type=ObjectType.COMPANY,
            industry="Technology",
            size="50-100",
            plan="enterprise"
        )
    
    @pytest.fixture
    def sample_relationship(self):
        """Create sample relationship."""
        return UserGroupRelationship(
            user_id="user_123",
            group_id="group_456",
            role=RelationshipRole.ADMIN,
            permissions=["users.manage", "billing.view"]
        )
    
    def test_group_manager_initialization(self, mock_client):
        """Test GroupManager initialization."""
        manager = GroupManager(mock_client)
        
        assert manager.client == mock_client
        assert manager.logger is not None
    
    @patch('utils.group_manager.validate_request_size', return_value=True)
    def test_create_group_success(self, mock_validate, group_manager, sample_group_traits):
        """Test successful group creation."""
        group_manager.client.group.return_value = {"status": "success"}
        
        result = group_manager.create_group(
            user_id="user_123",
            group_id="group_456",
            group_traits=sample_group_traits
        )
        
        assert result == {"status": "success"}
        group_manager.client.group.assert_called_once()
        
        # Check call arguments
        call_args = group_manager.client.group.call_args[1]
        assert call_args["userId"] == "user_123"
        assert call_args["groupId"] == "group_456"
        assert "traits" in call_args
    
    @patch('utils.group_manager.validate_request_size', return_value=False)
    def test_create_group_size_validation_failure(self, mock_validate, group_manager, sample_group_traits):
        """Test group creation with size validation failure."""
        with pytest.raises(ValueError, match="Group data exceeds 32KB limit"):
            group_manager.create_group(
                user_id="user_123",
                group_id="group_456",
                group_traits=sample_group_traits
            )
    
    def test_create_group_api_error(self, group_manager, sample_group_traits):
        """Test group creation with API error."""
        group_manager.client.group.side_effect = CustomerIOError("API error")
        
        with pytest.raises(CustomerIOError, match="API error"):
            group_manager.create_group(
                user_id="user_123",
                group_id="group_456",
                group_traits=sample_group_traits
            )
    
    def test_create_relationship_success(self, group_manager, sample_relationship):
        """Test successful relationship creation."""
        group_manager.client.track.return_value = {"status": "success"}
        
        result = group_manager.create_relationship(sample_relationship)
        
        assert result == {"status": "success"}
        group_manager.client.track.assert_called_once()
        
        # Check event structure
        call_args = group_manager.client.track.call_args[1]
        assert call_args["userId"] == "user_123"
        assert call_args["event"] == "User Added to Group"
        assert call_args["properties"]["group_id"] == "group_456"
        assert call_args["properties"]["role"] == "admin"
    
    def test_update_relationship_status_success(self, group_manager):
        """Test successful relationship status update."""
        group_manager.client.track.return_value = {"status": "success"}
        
        result = group_manager.update_relationship_status(
            user_id="user_123",
            group_id="group_456",
            new_status=RelationshipStatus.SUSPENDED,
            previous_status=RelationshipStatus.ACTIVE,
            reason="Payment failure"
        )
        
        assert result == {"status": "success"}
        
        call_args = group_manager.client.track.call_args[1]
        assert call_args["event"] == "Group Relationship Updated"
        assert call_args["properties"]["new_status"] == "suspended"
        assert call_args["properties"]["previous_status"] == "active"
        assert call_args["properties"]["reason"] == "Payment failure"
    
    def test_create_hierarchy_success(self, group_manager):
        """Test successful hierarchy creation."""
        hierarchy = ObjectHierarchy(
            parent_id="company_123",
            child_id="team_456",
            level=1,
            path="/company_123/team_456"
        )
        
        events = group_manager.create_hierarchy(
            hierarchy=hierarchy,
            parent_type=ObjectType.COMPANY,
            child_type=ObjectType.TEAM
        )
        
        assert len(events) == 2  # Parent and child perspective
        assert events[0]["event"] == "Child Object Added"
        assert events[1]["event"] == "Added to Parent Object"
        assert events[0]["properties"]["parent_id"] == "company_123"
        assert events[0]["properties"]["child_id"] == "team_456"
    
    def test_batch_create_groups_success(self, group_manager):
        """Test successful batch group creation."""
        groups_data = [
            {
                "userId": "user_1",
                "groupId": "group_1",
                "traits": {"name": "Group 1", "type": "company"},
                "timestamp": datetime.now(timezone.utc)
            },
            {
                "userId": "user_2",
                "groupId": "group_2",
                "traits": {"name": "Group 2", "type": "team"},
                "timestamp": datetime.now(timezone.utc)
            }
        ]
        
        group_manager.client.batch.return_value = {"status": "success"}
        
        results = group_manager.batch_create_groups(groups_data)
        
        assert len(results) >= 1
        assert results[0]["status"] == "success"
        assert results[0]["count"] == 2
        group_manager.client.batch.assert_called()
    
    def test_batch_create_relationships_success(self, group_manager):
        """Test successful batch relationship creation."""
        relationships = [
            UserGroupRelationship(
                user_id="user_1",
                group_id="group_456",
                role=RelationshipRole.MEMBER
            ),
            UserGroupRelationship(
                user_id="user_2",
                group_id="group_456",
                role=RelationshipRole.ADMIN
            )
        ]
        
        group_manager.client.batch.return_value = {"status": "success"}
        
        results = group_manager.batch_create_relationships(relationships)
        
        assert len(results) >= 1
        assert results[0]["status"] == "success"
        group_manager.client.batch.assert_called()
    
    def test_update_user_permissions_success(self, group_manager):
        """Test successful user permission update."""
        group_manager.client.track.return_value = {"status": "success"}
        
        result = group_manager.update_user_permissions(
            user_id="user_123",
            group_id="group_456",
            new_permissions=["users.view", "reports.view", "reports.export"],
            previous_permissions=["users.view", "reports.view"],
            added=["reports.export"],
            removed=[]
        )
        
        assert result == {"status": "success"}
        
        call_args = group_manager.client.track.call_args[1]
        assert call_args["event"] == "User Permissions Updated"
        assert len(call_args["properties"]["new_permissions"]) == 3
        assert call_args["properties"]["added"] == ["reports.export"]
    
    def test_get_users_by_role(self, group_manager):
        """Test getting users by role."""
        relationships = [
            UserGroupRelationship(
                user_id="user_1",
                group_id="group_456",
                role=RelationshipRole.ADMIN,
                status=RelationshipStatus.ACTIVE
            ),
            UserGroupRelationship(
                user_id="user_2",
                group_id="group_456",
                role=RelationshipRole.MEMBER,
                status=RelationshipStatus.ACTIVE
            ),
            UserGroupRelationship(
                user_id="user_3",
                group_id="group_456",
                role=RelationshipRole.MEMBER,
                status=RelationshipStatus.SUSPENDED
            )
        ]
        
        members = group_manager.get_users_by_role(
            group_id="group_456",
            role=RelationshipRole.MEMBER,
            relationships=relationships
        )
        
        assert len(members) == 1  # Only active members
        assert "user_2" in members
        assert "user_3" not in members  # Suspended
    
    def test_build_hierarchy_tree(self, group_manager):
        """Test building hierarchy tree."""
        hierarchies = [
            ObjectHierarchy(
                parent_id="company_123",
                child_id="dept_456",
                level=1,
                path="/company_123/dept_456"
            ),
            ObjectHierarchy(
                parent_id="dept_456",
                child_id="team_789",
                level=2,
                path="/company_123/dept_456/team_789"
            )
        ]
        
        tree = group_manager.build_hierarchy_tree(
            root_id="company_123",
            hierarchies=hierarchies
        )
        
        assert tree["id"] == "company_123"
        assert tree["level"] == 0
        assert len(tree["children"]) == 1
        assert tree["children"][0]["id"] == "dept_456"
        assert len(tree["children"][0]["children"]) == 1
        assert tree["children"][0]["children"][0]["id"] == "team_789"
    
    def test_calculate_org_metrics(self, group_manager):
        """Test organizational metrics calculation."""
        groups = [
            {"traits": {"type": "company"}},
            {"traits": {"type": "team"}},
            {"traits": {"type": "team"}}
        ]
        
        relationships = [
            UserGroupRelationship(
                user_id="user_1",
                group_id="group_1",
                role=RelationshipRole.ADMIN,
                status=RelationshipStatus.ACTIVE
            ),
            UserGroupRelationship(
                user_id="user_2",
                group_id="group_1",
                role=RelationshipRole.MEMBER,
                status=RelationshipStatus.ACTIVE
            ),
            UserGroupRelationship(
                user_id="user_1",
                group_id="group_2",
                role=RelationshipRole.MEMBER,
                status=RelationshipStatus.SUSPENDED
            )
        ]
        
        hierarchies = [
            ObjectHierarchy(
                parent_id="company_123",
                child_id="team_456",
                level=1,
                path="/company_123/team_456"
            )
        ]
        
        metrics = group_manager.calculate_org_metrics(
            groups=groups,
            relationships=relationships,
            hierarchies=hierarchies
        )
        
        assert metrics["total_objects"] == 3
        assert metrics["objects_by_type"]["company"] == 1
        assert metrics["objects_by_type"]["team"] == 2
        assert metrics["total_relationships"] == 3
        assert metrics["active_relationships"] == 2
        assert metrics["unique_users"] == 2
        assert metrics["unique_groups"] == 2
        assert metrics["hierarchy_max_depth"] == 1
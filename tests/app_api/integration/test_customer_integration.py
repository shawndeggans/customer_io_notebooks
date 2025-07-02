"""
Integration tests for Customer.IO App API customer management functions.

Tests customer CRUD operations, search, activities, messages, segments,
and suppression with support for different test data modes.
"""

import pytest
from datetime import datetime, timezone
import uuid

from .base import BaseAppAPIIntegrationTest
from .conftest import skip_without_app_credentials, skip_in_existing_mode
from src.app_api import client as app_client


@skip_without_app_credentials
class TestCustomerManagementIntegration(BaseAppAPIIntegrationTest):
    """Test customer management functionality with real App API."""
    
    def test_search_customers_with_existing_data(
        self,
        app_auth,
        test_email,
        test_data_mode
    ):
        """Test searching for customers."""
        # Search by email
        try:
            result = app_client.search_customers(
                auth=app_auth,
                email=test_email,
                limit=10
            )
        except Exception as e:
            self.handle_api_error(e, "Searching customers")
        
        # Verify response structure
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["customers"])
        
        customers = result.get("customers", [])
        assert isinstance(customers, list), "Customers should be a list"
        
        # Note: In existing mode, we might not find customers if test email doesn't exist
        # This is OK - the test validates the API call works, not that specific data exists
    
    def test_get_customer_details(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test retrieving customer details."""
        # Ensure customer exists if in existing mode
        if test_data_mode == "existing":
            try:
                self.ensure_test_customer_exists(
                    app_auth,
                    test_customer_id,
                    test_email
                )
            except Exception as e:
                if "404" in str(e):
                    pytest.skip(f"Customer {test_customer_id} not found and cannot be created")
                else:
                    raise
        
        # Get customer details
        try:
            result = app_client.get_customer(
                auth=app_auth,
                customer_id=test_customer_id
            )
        except Exception as e:
            if "404" in str(e) and test_data_mode == "existing":
                pytest.skip(f"Customer {test_customer_id} not found in workspace")
            else:
                self.handle_api_error(e, f"Getting customer {test_customer_id}")
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["customer"])
        
        customer = result["customer"]
        assert customer["id"] == test_customer_id, "Customer ID should match"
        
        # Email might be in different places depending on the response
        if "email" in customer:
            assert customer["email"] == test_email
        elif "attributes" in customer and "email" in customer["attributes"]:
            assert customer["attributes"]["email"] == test_email
    
    def test_get_customer_attributes(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test retrieving customer attributes."""
        # Ensure customer exists
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth,
                test_customer_id,
                test_email
            )
        
        # Get attributes
        result = app_client.get_customer_attributes(
            auth=app_auth,
            customer_id=test_customer_id
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["customer"])
        
        customer = result["customer"]
        assert "attributes" in customer, "Attributes should be present"
        attributes = customer["attributes"]
        assert isinstance(attributes, dict), "Attributes should be a dictionary"
    
    def test_get_customer_activities(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test retrieving customer activities."""
        # Ensure customer exists
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth,
                test_customer_id,
                test_email
            )
        
        # Get activities
        result = app_client.get_customer_activities(
            auth=app_auth,
            customer_id=test_customer_id,
            limit=20
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["activities"])
        
        activities = result["activities"]
        assert isinstance(activities, list), "Activities should be a list"
        
        # Check activity structure if any exist
        if activities:
            activity = activities[0]
            assert "type" in activity, "Activity should have type"
            assert "timestamp" in activity or "created_at" in activity, "Activity should have timestamp"
    
    def test_get_customer_messages(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test retrieving customer message history."""
        # Ensure customer exists
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth,
                test_customer_id,
                test_email
            )
        
        # Get messages
        result = app_client.get_customer_messages(
            auth=app_auth,
            customer_id=test_customer_id,
            limit=10,
            type="email"
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["messages"])
        
        messages = result["messages"]
        assert isinstance(messages, list), "Messages should be a list"
        
        # Check message structure if any exist
        if messages:
            message = messages[0]
            assert "id" in message or "delivery_id" in message, "Message should have ID"
            assert "type" in message or "object_type" in message, "Message should have type"
    
    def test_get_customer_segments(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test retrieving customer segment membership."""
        # Ensure customer exists
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth,
                test_customer_id,
                test_email
            )
        
        # Get segments
        result = app_client.get_customer_segments(
            auth=app_auth,
            customer_id=test_customer_id,
            limit=20
        )
        
        # Verify response
        self.assert_successful_response(result)
        self.assert_api_response(result, expected_keys=["segments"])
        
        segments = result["segments"]
        assert isinstance(segments, list), "Segments should be a list"
        
        # Check segment structure if any exist
        if segments:
            segment = segments[0]
            assert "id" in segment, "Segment should have ID"
            assert "name" in segment, "Segment should have name"
    
    @skip_in_existing_mode
    def test_create_and_delete_customer(
        self,
        app_auth,
        cleanup_tracker
    ):
        """Test creating and deleting a customer."""
        # Generate unique customer data
        timestamp = int(datetime.now(timezone.utc).timestamp())
        unique_id = uuid.uuid4().hex[:8]
        customer_id = f"test_create_delete_{timestamp}_{unique_id}"
        email = f"{customer_id}@test.example.com"
        
        # Create customer
        create_result = app_client.create_customer(
            auth=app_auth,
            id=customer_id,
            email=email,
            attributes={
                "first_name": "Create",
                "last_name": "Delete Test",
                "created_via": "integration_test"
            }
        )
        
        # Track for cleanup
        self.track_created_customer(customer_id)
        cleanup_tracker["customers"].append(customer_id)
        
        # Verify creation
        self.assert_successful_response(create_result)
        self.assert_api_response(create_result, expected_keys=["customer"])
        
        created_customer = create_result["customer"]
        assert created_customer["id"] == customer_id
        
        # Wait for consistency
        self.wait_for_eventual_consistency()
        
        # Verify customer exists
        self.assert_customer_exists(app_auth, customer_id)
        
        # Delete customer
        delete_result = app_client.delete_customer(
            auth=app_auth,
            customer_id=customer_id
        )
        
        # Verify deletion
        self.assert_successful_response(delete_result)
        
        # Wait for consistency
        self.wait_for_eventual_consistency()
        
        # Verify customer no longer exists
        self.assert_customer_not_exists(app_auth, customer_id)
        
        # Remove from tracking since it's deleted
        self.created_customers.discard(customer_id)
    
    @pytest.mark.modifies_data
    def test_update_customer_with_restoration(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test updating customer attributes with restoration."""
        # Ensure customer exists
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth,
                test_customer_id,
                test_email
            )
        
        # Get original state
        original_state = self.get_customer_state(app_auth, test_customer_id)
        self.track_customer_modification(test_customer_id, original_state)
        
        # Update customer
        update_timestamp = self.generate_test_timestamp()
        update_result = app_client.update_customer(
            auth=app_auth,
            customer_id=test_customer_id,
            attributes={
                "last_test_update": update_timestamp,
                "test_mode": test_data_mode,
                "integration_test": True
            }
        )
        
        # Verify update
        self.assert_successful_response(update_result)
        
        # Wait for consistency
        self.wait_for_eventual_consistency()
        
        # Verify attributes were updated
        attributes_result = app_client.get_customer_attributes(
            auth=app_auth,
            customer_id=test_customer_id
        )
        
        attributes = attributes_result["customer"]["attributes"]
        assert attributes.get("last_test_update") == update_timestamp
        assert attributes.get("integration_test") is True
        
        # Restore original state
        self.restore_customer_state(app_auth, test_customer_id, original_state)
    
    @pytest.mark.modifies_data
    def test_customer_suppression_toggle(
        self,
        app_auth,
        test_customer_id,
        test_email,
        test_data_mode
    ):
        """Test suppressing and unsuppressing a customer."""
        # Ensure customer exists
        if test_data_mode == "existing":
            self.ensure_test_customer_exists(
                app_auth,
                test_customer_id,
                test_email
            )
        
        # Get original suppression state
        original_customer = app_client.get_customer(app_auth, test_customer_id)
        original_suppressed = original_customer.get("customer", {}).get("suppressed", False)
        
        try:
            # Suppress customer
            suppress_result = app_client.manage_customer_suppression(
                auth=app_auth,
                customer_id=test_customer_id,
                suppress=True
            )
            
            self.assert_successful_response(suppress_result)
            
            # Wait for consistency
            self.wait_for_eventual_consistency()
            
            # Verify suppression
            suppressed_customer = app_client.get_customer(app_auth, test_customer_id)
            assert suppressed_customer["customer"].get("suppressed") is True
            
            # Unsuppress customer
            unsuppress_result = app_client.manage_customer_suppression(
                auth=app_auth,
                customer_id=test_customer_id,
                suppress=False
            )
            
            self.assert_successful_response(unsuppress_result)
            
            # Wait for consistency
            self.wait_for_eventual_consistency()
            
            # Verify unsuppression
            unsuppressed_customer = app_client.get_customer(app_auth, test_customer_id)
            assert unsuppressed_customer["customer"].get("suppressed") is False
            
        finally:
            # Restore original suppression state
            if original_suppressed != unsuppressed_customer["customer"].get("suppressed", False):
                app_client.manage_customer_suppression(
                    auth=app_auth,
                    customer_id=test_customer_id,
                    suppress=original_suppressed
                )
    
    def test_customer_not_found_error(self, app_auth):
        """Test error handling for non-existent customer."""
        non_existent_id = f"non_existent_{uuid.uuid4().hex}"
        
        with pytest.raises(Exception) as exc_info:
            app_client.get_customer(app_auth, non_existent_id)
        
        assert "404" in str(exc_info.value) or "not found" in str(exc_info.value).lower()
    
    def test_search_pagination(self, app_auth):
        """Test customer search pagination."""
        # First page
        first_page = app_client.search_customers(
            auth=app_auth,
            limit=5
        )
        
        self.assert_successful_response(first_page)
        customers = first_page.get("customers", [])
        
        # If we have customers, test pagination
        if len(customers) >= 5:
            # Get next page using last customer ID
            last_customer_id = customers[-1]["id"]
            
            second_page = app_client.search_customers(
                auth=app_auth,
                limit=5,
                start=last_customer_id
            )
            
            self.assert_successful_response(second_page)
            second_customers = second_page.get("customers", [])
            
            # Verify we got different customers
            if second_customers:
                first_ids = {c["id"] for c in customers}
                second_ids = {c["id"] for c in second_customers}
                assert not first_ids.intersection(second_ids), "Pages should not overlap"
    
    def test_invalid_customer_creation(self, app_auth):
        """Test error handling for invalid customer creation."""
        # Try to create customer without email
        with pytest.raises(ValueError) as exc_info:
            app_client.create_customer(
                auth=app_auth,
                email=""  # Empty email
            )
        
        assert "email is required" in str(exc_info.value).lower()
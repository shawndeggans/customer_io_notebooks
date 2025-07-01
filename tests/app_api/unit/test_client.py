"""Tests for App API client functions."""
import pytest
from unittest.mock import Mock, patch
import requests
from src.app_api.client import send_transactional, trigger_broadcast, send_push, search_customers, get_customer, get_customer_activities, get_customer_attributes, get_customer_messages, get_customer_segments, delete_customer, update_customer, create_customer, manage_customer_suppression
from src.app_api.auth import AppAPIAuth


class TestAppAPIClient:
    """Test App API client functionality."""
    
    @pytest.fixture
    def mock_auth(self):
        """Create mock authentication object."""
        auth = Mock(spec=AppAPIAuth)
        auth.base_url = "https://api.customer.io"
        auth.get_rate_limit_delay.return_value = 0.01
        return auth
    
    @pytest.fixture
    def mock_session(self):
        """Create mock requests session."""
        session = Mock(spec=requests.Session)
        session.headers = Mock()
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"id": "msg_123", "status": "sent"}
        session.post.return_value = response
        return session
    
    @patch('time.sleep')
    def test_send_transactional_email_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful transactional email sending."""
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = send_transactional(
                auth=mock_auth,
                transactional_message_id=123,
                to="test@example.com",
                identifiers={"id": "user_123"},
                message_data={"name": "John"}
            )
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "https://api.customer.io/v1/send/email",
            json={
                "transactional_message_id": 123,
                "to": "test@example.com",
                "identifiers": {"id": "user_123"},
                "message_data": {"name": "John"}
            }
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("transactional")
        mock_sleep.assert_called_once_with(0.01)
        
        # Verify result
        assert result == {"id": "msg_123", "status": "sent"}
    
    @patch('time.sleep')
    def test_send_transactional_api_error(self, mock_sleep, mock_auth, mock_session):
        """Test transactional email sending with API error."""
        # Set up error response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Invalid email"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.post.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                send_transactional(
                    auth=mock_auth,
                    transactional_message_id=123,
                    to="invalid-email",
                    identifiers={"id": "user_123"}
                )
    
    @patch('time.sleep')
    def test_trigger_broadcast_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful broadcast triggering."""
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = trigger_broadcast(
                auth=mock_auth,
                broadcast_id=456,
                data={"segment_id": "seg_789"},
                recipients={"emails": ["test@example.com"]}
            )
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "https://api.customer.io/v1/campaigns/456/triggers",
            json={
                "data": {"segment_id": "seg_789"},
                "recipients": {"emails": ["test@example.com"]}
            }
        )
        
        # Verify rate limiting (broadcasts use different rate)
        mock_auth.get_rate_limit_delay.assert_called_once_with("broadcast")
        
        assert result == {"id": "msg_123", "status": "sent"}
    
    @patch('time.sleep')
    def test_send_push_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful push notification sending."""
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = send_push(
                auth=mock_auth,
                identifiers={"id": "user_123"},
                title="Test Push",
                message="Hello World",
                device_tokens=["token_123"]
            )
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "https://api.customer.io/v1/send/push",
            json={
                "identifiers": {"id": "user_123"},
                "title": "Test Push", 
                "message": "Hello World",
                "device_tokens": ["token_123"]
            }
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("transactional")
        
        assert result == {"id": "msg_123", "status": "sent"}
    
    def test_send_transactional_missing_required_params(self, mock_auth):
        """Test transactional email with missing required parameters."""
        with pytest.raises(ValueError):
            send_transactional(
                auth=mock_auth,
                transactional_message_id=123
                # Missing 'to' and 'identifiers'
            )
    
    def test_trigger_broadcast_missing_broadcast_id(self, mock_auth):
        """Test broadcast trigger with missing broadcast_id."""
        with pytest.raises(ValueError):
            trigger_broadcast(
                auth=mock_auth,
                broadcast_id=None,
                data={"test": "data"}
            )
    
    def test_send_push_missing_required_params(self, mock_auth):
        """Test push notification with missing required parameters.""" 
        with pytest.raises(ValueError):
            send_push(
                auth=mock_auth,
                identifiers={"id": "user_123"}
                # Missing title, message, and device_tokens
            )
    
    @patch('time.sleep')
    def test_search_customers_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer search."""
        # Setup mock response for customer search
        search_response = {
            "customers": [
                {
                    "id": "cust_123",
                    "email": "test@example.com",
                    "attributes": {"name": "Test User"}
                },
                {
                    "id": "cust_456", 
                    "email": "user@example.com",
                    "attributes": {"name": "Another User"}
                }
            ],
            "meta": {
                "count": 2,
                "limit": 50,
                "start": "cust_123"
            }
        }
        
        mock_session.get.return_value.json.return_value = search_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = search_customers(
                auth=mock_auth,
                email="test@example.com",
                limit=50
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers",
            params={
                "email": "test@example.com",
                "limit": 50
            }
        )
        
        # Verify rate limiting (general endpoints use 0.1 sec delay)
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == search_response
        assert len(result["customers"]) == 2
        assert result["customers"][0]["email"] == "test@example.com"
    
    @patch('time.sleep')
    def test_search_customers_with_filters(self, mock_sleep, mock_auth, mock_session):
        """Test customer search with multiple filter parameters."""
        search_response = {
            "customers": [{"id": "cust_789", "email": "filtered@example.com"}],
            "meta": {"count": 1, "limit": 10}
        }
        
        mock_session.get.return_value.json.return_value = search_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = search_customers(
                auth=mock_auth,
                email="filtered@example.com",
                limit=10,
                start="cust_100"
            )
        
        # Verify API call with multiple parameters
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers",
            params={
                "email": "filtered@example.com",
                "limit": 10,
                "start": "cust_100"
            }
        )
        
        assert result == search_response
    
    @patch('time.sleep')
    def test_search_customers_api_error(self, mock_sleep, mock_auth, mock_session):
        """Test customer search with API error."""
        # Set up error response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Invalid search parameters"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                search_customers(
                    auth=mock_auth,
                    email="invalid-email-format"
                )
    
    def test_search_customers_no_parameters(self, mock_auth):
        """Test customer search with no search parameters."""
        with pytest.raises(ValueError):
            search_customers(auth=mock_auth)
    
    @patch('time.sleep')
    def test_search_customers_pagination(self, mock_sleep, mock_auth, mock_session):
        """Test customer search with pagination parameters."""
        search_response = {
            "customers": [{"id": "cust_001", "email": "page@example.com"}],
            "meta": {"count": 1, "limit": 25, "start": "cust_001"}
        }
        
        mock_session.get.return_value.json.return_value = search_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = search_customers(
                auth=mock_auth,
                limit=25,
                start="cust_000"
            )
        
        # Verify pagination parameters in API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers",
            params={
                "limit": 25,
                "start": "cust_000"
            }
        )
        
        assert result["meta"]["limit"] == 25
    
    @patch('time.sleep')
    def test_get_customer_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer profile retrieval."""
        customer_response = {
            "customer": {
                "id": "cust_123",
                "email": "test@example.com",
                "attributes": {
                    "name": "Test User",
                    "plan": "premium",
                    "signup_date": "2024-01-01"
                },
                "created_at": 1704067200,
                "updated_at": 1704153600
            }
        }
        
        mock_session.get.return_value.json.return_value = customer_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer(
                auth=mock_auth,
                customer_id="cust_123"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123"
        )
        
        # Verify rate limiting (general endpoints)
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == customer_response
        assert result["customer"]["id"] == "cust_123"
        assert result["customer"]["email"] == "test@example.com"
    
    @patch('time.sleep')
    def test_get_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer profile retrieval when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer(
                    auth=mock_auth,
                    customer_id="nonexistent_customer"
                )
    
    @patch('time.sleep')
    def test_get_customer_api_error(self, mock_sleep, mock_auth, mock_session):
        """Test customer profile retrieval with API error."""
        # Set up 400 response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Invalid customer ID format"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer(
                    auth=mock_auth,
                    customer_id="invalid_id_format"
                )
    
    def test_get_customer_missing_id(self, mock_auth):
        """Test customer profile retrieval with missing customer_id."""
        with pytest.raises(ValueError):
            get_customer(auth=mock_auth, customer_id="")
        
        with pytest.raises(ValueError):
            get_customer(auth=mock_auth, customer_id=None)
    
    @patch('time.sleep')
    def test_get_customer_with_minimal_data(self, mock_sleep, mock_auth, mock_session):
        """Test customer profile retrieval with minimal customer data."""
        minimal_response = {
            "customer": {
                "id": "cust_minimal",
                "attributes": {}
            }
        }
        
        mock_session.get.return_value.json.return_value = minimal_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer(
                auth=mock_auth,
                customer_id="cust_minimal"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_minimal"
        )
        
        # Verify minimal data handling
        assert result == minimal_response
        assert result["customer"]["id"] == "cust_minimal"
        assert result["customer"]["attributes"] == {}
    
    @patch('time.sleep')
    def test_get_customer_activities_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer activity history retrieval."""
        activities_response = {
            "activities": [
                {
                    "type": "event",
                    "name": "purchase",
                    "timestamp": 1704067200,
                    "data": {
                        "product_id": "prod_123",
                        "amount": 99.99
                    }
                },
                {
                    "type": "email", 
                    "name": "email_opened",
                    "timestamp": 1704153600,
                    "data": {
                        "campaign_id": "camp_456",
                        "subject": "Welcome!"
                    }
                }
            ],
            "meta": {
                "count": 2,
                "limit": 50,
                "start": "act_123"
            }
        }
        
        mock_session.get.return_value.json.return_value = activities_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_activities(
                auth=mock_auth,
                customer_id="cust_123",
                limit=50
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/activities",
            params={"limit": 50}
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == activities_response
        assert len(result["activities"]) == 2
        assert result["activities"][0]["name"] == "purchase"
    
    @patch('time.sleep')
    def test_get_customer_activities_with_filters(self, mock_sleep, mock_auth, mock_session):
        """Test customer activity history with filter parameters."""
        filtered_response = {
            "activities": [
                {
                    "type": "email",
                    "name": "email_delivered", 
                    "timestamp": 1704240000
                }
            ],
            "meta": {"count": 1, "limit": 10}
        }
        
        mock_session.get.return_value.json.return_value = filtered_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_activities(
                auth=mock_auth,
                customer_id="cust_456",
                limit=10,
                start="act_100",
                type="email"
            )
        
        # Verify API call with filters
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_456/activities",
            params={
                "limit": 10,
                "start": "act_100", 
                "type": "email"
            }
        )
        
        assert result == filtered_response
    
    @patch('time.sleep')
    def test_get_customer_activities_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer activity history when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer_activities(
                    auth=mock_auth,
                    customer_id="nonexistent_customer"
                )
    
    def test_get_customer_activities_missing_id(self, mock_auth):
        """Test customer activity history with missing customer_id."""
        with pytest.raises(ValueError):
            get_customer_activities(auth=mock_auth, customer_id="")
        
        with pytest.raises(ValueError):
            get_customer_activities(auth=mock_auth, customer_id=None)
    
    @patch('time.sleep')
    def test_get_customer_activities_empty_result(self, mock_sleep, mock_auth, mock_session):
        """Test customer activity history with no activities."""
        empty_response = {
            "activities": [],
            "meta": {
                "count": 0,
                "limit": 50
            }
        }
        
        mock_session.get.return_value.json.return_value = empty_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_activities(
                auth=mock_auth,
                customer_id="cust_no_activity"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_no_activity/activities",
            params={}
        )
        
        # Verify empty result handling
        assert result == empty_response
        assert len(result["activities"]) == 0
        assert result["meta"]["count"] == 0
    
    @patch('time.sleep')
    def test_get_customer_attributes_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer attributes retrieval."""
        attributes_response = {
            "customer": {
                "id": "cust_123",
                "attributes": {
                    "email": "test@example.com",
                    "name": "Test User",
                    "plan": "premium",
                    "signup_date": "2024-01-01",
                    "total_purchases": 5,
                    "last_login": 1704153600
                }
            }
        }
        
        mock_session.get.return_value.json.return_value = attributes_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_attributes(
                auth=mock_auth,
                customer_id="cust_123"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/attributes"
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == attributes_response
        assert result["customer"]["id"] == "cust_123"
        assert result["customer"]["attributes"]["email"] == "test@example.com"
        assert result["customer"]["attributes"]["plan"] == "premium"
    
    @patch('time.sleep')
    def test_get_customer_attributes_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer attributes retrieval when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer_attributes(
                    auth=mock_auth,
                    customer_id="nonexistent_customer"
                )
    
    @patch('time.sleep')
    def test_get_customer_attributes_api_error(self, mock_sleep, mock_auth, mock_session):
        """Test customer attributes retrieval with API error."""
        # Set up 400 response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Invalid customer ID format"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer_attributes(
                    auth=mock_auth,
                    customer_id="invalid_format"
                )
    
    def test_get_customer_attributes_missing_id(self, mock_auth):
        """Test customer attributes retrieval with missing customer_id."""
        with pytest.raises(ValueError):
            get_customer_attributes(auth=mock_auth, customer_id="")
        
        with pytest.raises(ValueError):
            get_customer_attributes(auth=mock_auth, customer_id=None)
    
    @patch('time.sleep')
    def test_get_customer_attributes_minimal_data(self, mock_sleep, mock_auth, mock_session):
        """Test customer attributes retrieval with minimal attributes."""
        minimal_response = {
            "customer": {
                "id": "cust_minimal",
                "attributes": {
                    "email": "minimal@example.com"
                }
            }
        }
        
        mock_session.get.return_value.json.return_value = minimal_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_attributes(
                auth=mock_auth,
                customer_id="cust_minimal"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_minimal/attributes"
        )
        
        # Verify minimal data handling
        assert result == minimal_response
        assert result["customer"]["id"] == "cust_minimal"
        assert len(result["customer"]["attributes"]) == 1
        assert result["customer"]["attributes"]["email"] == "minimal@example.com"
    
    @patch('time.sleep')
    def test_get_customer_messages_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer message history retrieval."""
        messages_response = {
            "messages": [
                {
                    "id": "msg_123",
                    "type": "email",
                    "campaign": {
                        "id": "camp_456",
                        "name": "Welcome Series"
                    },
                    "created_at": 1704067200,
                    "sent_at": 1704067260,
                    "delivered_at": 1704067320,
                    "opened_at": 1704067500,
                    "clicked_at": 1704067600,
                    "subject": "Welcome to our platform!",
                    "state": "delivered"
                },
                {
                    "id": "msg_789",
                    "type": "push",
                    "campaign": {
                        "id": "camp_101",
                        "name": "Daily Notifications"
                    },
                    "created_at": 1704153600,
                    "sent_at": 1704153660,
                    "delivered_at": 1704153720,
                    "title": "Don't miss out!",
                    "body": "Check out what's new",
                    "state": "delivered"
                }
            ],
            "meta": {
                "count": 2,
                "limit": 50,
                "start": "msg_123"
            }
        }
        
        mock_session.get.return_value.json.return_value = messages_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_messages(
                auth=mock_auth,
                customer_id="cust_123",
                limit=50
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/messages",
            params={"limit": 50}
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == messages_response
        assert len(result["messages"]) == 2
        assert result["messages"][0]["type"] == "email"
        assert result["messages"][1]["type"] == "push"
    
    @patch('time.sleep')
    def test_get_customer_messages_with_filters(self, mock_sleep, mock_auth, mock_session):
        """Test customer message history with filter parameters."""
        filtered_response = {
            "messages": [
                {
                    "id": "msg_email_001",
                    "type": "email",
                    "campaign": {
                        "id": "camp_newsletter",
                        "name": "Weekly Newsletter"
                    },
                    "created_at": 1704240000,
                    "sent_at": 1704240060,
                    "delivered_at": 1704240120,
                    "subject": "Weekly Update",
                    "state": "delivered"
                }
            ],
            "meta": {"count": 1, "limit": 10}
        }
        
        mock_session.get.return_value.json.return_value = filtered_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_messages(
                auth=mock_auth,
                customer_id="cust_456",
                limit=10,
                start="msg_100",
                type="email"
            )
        
        # Verify API call with filters
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_456/messages",
            params={
                "limit": 10,
                "start": "msg_100",
                "type": "email"
            }
        )
        
        assert result == filtered_response
        assert result["messages"][0]["type"] == "email"
    
    @patch('time.sleep')
    def test_get_customer_messages_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer message history when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer_messages(
                    auth=mock_auth,
                    customer_id="nonexistent_customer"
                )
    
    def test_get_customer_messages_missing_id(self, mock_auth):
        """Test customer message history with missing customer_id."""
        with pytest.raises(ValueError):
            get_customer_messages(auth=mock_auth, customer_id="")
        
        with pytest.raises(ValueError):
            get_customer_messages(auth=mock_auth, customer_id=None)
    
    @patch('time.sleep')
    def test_get_customer_messages_empty_result(self, mock_sleep, mock_auth, mock_session):
        """Test customer message history with no messages."""
        empty_response = {
            "messages": [],
            "meta": {
                "count": 0,
                "limit": 50
            }
        }
        
        mock_session.get.return_value.json.return_value = empty_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_messages(
                auth=mock_auth,
                customer_id="cust_no_messages"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_no_messages/messages",
            params={}
        )
        
        # Verify empty result handling
        assert result == empty_response
        assert len(result["messages"]) == 0
        assert result["meta"]["count"] == 0
    
    @patch('time.sleep')
    def test_get_customer_segments_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer segment membership retrieval."""
        segments_response = {
            "segments": [
                {
                    "id": "seg_123",
                    "name": "Premium Users",
                    "description": "Users with premium subscription",
                    "type": "dynamic",
                    "state": "active",
                    "created_at": 1704067200,
                    "updated_at": 1704153600,
                    "membership": {
                        "added_at": 1704067200,
                        "reason": "attribute_match"
                    }
                },
                {
                    "id": "seg_456",
                    "name": "High Value Customers",
                    "description": "Customers with high lifetime value",
                    "type": "static",
                    "state": "active",
                    "created_at": 1703980800,
                    "updated_at": 1704240000,
                    "membership": {
                        "added_at": 1704100000,
                        "reason": "manual_addition"
                    }
                }
            ],
            "meta": {
                "count": 2,
                "limit": 50
            }
        }
        
        mock_session.get.return_value.json.return_value = segments_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_segments(
                auth=mock_auth,
                customer_id="cust_123"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/segments",
            params={}
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == segments_response
        assert len(result["segments"]) == 2
        assert result["segments"][0]["name"] == "Premium Users"
        assert result["segments"][1]["type"] == "static"
    
    @patch('time.sleep')
    def test_get_customer_segments_with_pagination(self, mock_sleep, mock_auth, mock_session):
        """Test customer segment membership with pagination parameters."""
        paginated_response = {
            "segments": [
                {
                    "id": "seg_789",
                    "name": "Newsletter Subscribers",
                    "type": "dynamic",
                    "state": "active",
                    "membership": {
                        "added_at": 1704326400,
                        "reason": "event_triggered"
                    }
                }
            ],
            "meta": {
                "count": 1,
                "limit": 10,
                "start": "seg_789"
            }
        }
        
        mock_session.get.return_value.json.return_value = paginated_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_segments(
                auth=mock_auth,
                customer_id="cust_456",
                limit=10,
                start="seg_700"
            )
        
        # Verify API call with pagination
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_456/segments",
            params={
                "limit": 10,
                "start": "seg_700"
            }
        )
        
        assert result == paginated_response
        assert result["segments"][0]["name"] == "Newsletter Subscribers"
    
    @patch('time.sleep')
    def test_get_customer_segments_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer segment membership when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                get_customer_segments(
                    auth=mock_auth,
                    customer_id="nonexistent_customer"
                )
    
    def test_get_customer_segments_missing_id(self, mock_auth):
        """Test customer segment membership with missing customer_id."""
        with pytest.raises(ValueError):
            get_customer_segments(auth=mock_auth, customer_id="")
        
        with pytest.raises(ValueError):
            get_customer_segments(auth=mock_auth, customer_id=None)
    
    @patch('time.sleep')
    def test_get_customer_segments_empty_result(self, mock_sleep, mock_auth, mock_session):
        """Test customer segment membership with no segments."""
        empty_response = {
            "segments": [],
            "meta": {
                "count": 0,
                "limit": 50
            }
        }
        
        mock_session.get.return_value.json.return_value = empty_response
        mock_session.get.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = get_customer_segments(
                auth=mock_auth,
                customer_id="cust_no_segments"
            )
        
        # Verify API call
        mock_session.get.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_no_segments/segments",
            params={}
        )
        
        # Verify empty result handling
        assert result == empty_response
        assert len(result["segments"]) == 0
        assert result["meta"]["count"] == 0
    
    @patch('time.sleep')
    def test_delete_customer_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer deletion."""
        delete_response = {
            "meta": {
                "request_id": "req_123"
            }
        }
        
        mock_session.delete.return_value.json.return_value = delete_response
        mock_session.delete.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = delete_customer(
                auth=mock_auth,
                customer_id="cust_123"
            )
        
        # Verify API call
        mock_session.delete.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123"
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == delete_response
        assert "request_id" in result["meta"]
    
    @patch('time.sleep')
    def test_delete_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer deletion when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.delete.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                delete_customer(
                    auth=mock_auth,
                    customer_id="nonexistent_customer"
                )
    
    @patch('time.sleep')
    def test_delete_customer_api_error(self, mock_sleep, mock_auth, mock_session):
        """Test customer deletion with API error."""
        # Set up 400 response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Cannot delete customer with active campaigns"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.delete.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                delete_customer(
                    auth=mock_auth,
                    customer_id="cust_with_campaigns"
                )
    
    def test_delete_customer_missing_id(self, mock_auth):
        """Test customer deletion with missing customer_id."""
        with pytest.raises(ValueError):
            delete_customer(auth=mock_auth, customer_id="")
        
        with pytest.raises(ValueError):
            delete_customer(auth=mock_auth, customer_id=None)
    
    @patch('time.sleep')
    def test_delete_customer_with_suppress_option(self, mock_sleep, mock_auth, mock_session):
        """Test customer deletion with suppress option."""
        delete_response = {
            "meta": {
                "request_id": "req_456"
            }
        }
        
        mock_session.delete.return_value.json.return_value = delete_response
        mock_session.delete.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = delete_customer(
                auth=mock_auth,
                customer_id="cust_123",
                suppress=True
            )
        
        # Verify API call with suppress parameter
        mock_session.delete.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123",
            params={"suppress": True}
        )
        
        assert result == delete_response
    
    @patch('time.sleep')
    def test_update_customer_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer update."""
        update_response = {
            "customer": {
                "id": "cust_123",
                "email": "updated@example.com",
                "attributes": {
                    "name": "Updated Name",
                    "plan": "premium",
                    "updated_at": 1704240000
                }
            }
        }
        
        mock_session.put.return_value.json.return_value = update_response
        mock_session.put.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = update_customer(
                auth=mock_auth,
                customer_id="cust_123",
                attributes={
                    "name": "Updated Name",
                    "plan": "premium"
                }
            )
        
        # Verify API call
        mock_session.put.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123",
            json={
                "attributes": {
                    "name": "Updated Name",
                    "plan": "premium"
                }
            }
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == update_response
        assert result["customer"]["attributes"]["name"] == "Updated Name"
    
    @patch('time.sleep')
    def test_update_customer_with_email(self, mock_sleep, mock_auth, mock_session):
        """Test customer update with email change."""
        update_response = {
            "customer": {
                "id": "cust_123",
                "email": "newemail@example.com",
                "attributes": {
                    "email": "newemail@example.com",
                    "name": "John Doe"
                }
            }
        }
        
        mock_session.put.return_value.json.return_value = update_response
        mock_session.put.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = update_customer(
                auth=mock_auth,
                customer_id="cust_123",
                email="newemail@example.com",
                attributes={
                    "name": "John Doe"
                }
            )
        
        # Verify API call with email
        mock_session.put.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123",
            json={
                "email": "newemail@example.com",
                "attributes": {
                    "name": "John Doe"
                }
            }
        )
        
        assert result == update_response
    
    @patch('time.sleep')
    def test_update_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer update when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.put.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                update_customer(
                    auth=mock_auth,
                    customer_id="nonexistent_customer",
                    attributes={"name": "Test"}
                )
    
    def test_update_customer_missing_id(self, mock_auth):
        """Test customer update with missing customer_id."""
        with pytest.raises(ValueError):
            update_customer(auth=mock_auth, customer_id="", attributes={"name": "Test"})
        
        with pytest.raises(ValueError):
            update_customer(auth=mock_auth, customer_id=None, attributes={"name": "Test"})
    
    def test_update_customer_missing_data(self, mock_auth):
        """Test customer update with no update data."""
        with pytest.raises(ValueError):
            update_customer(auth=mock_auth, customer_id="cust_123")
    
    @patch('time.sleep')
    def test_update_customer_validation_error(self, mock_sleep, mock_auth, mock_session):
        """Test customer update with validation error."""
        # Set up 400 response
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Invalid email format"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.put.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                update_customer(
                    auth=mock_auth,
                    customer_id="cust_123",
                    email="invalid-email"
                )
    
    @patch('time.sleep')
    def test_create_customer_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer creation."""
        create_response = {
            "customer": {
                "id": "cust_new_123",
                "email": "newcustomer@example.com",
                "attributes": {
                    "name": "New Customer",
                    "plan": "basic",
                    "created_at": 1704326400
                },
                "created_at": 1704326400
            }
        }
        
        mock_session.post.return_value.json.return_value = create_response
        mock_session.post.return_value.status_code = 201
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = create_customer(
                auth=mock_auth,
                email="newcustomer@example.com",
                attributes={
                    "name": "New Customer",
                    "plan": "basic"
                }
            )
        
        # Verify API call
        mock_session.post.assert_called_once_with(
            "https://api.customer.io/v1/customers",
            json={
                "email": "newcustomer@example.com",
                "attributes": {
                    "name": "New Customer",
                    "plan": "basic"
                }
            }
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == create_response
        assert result["customer"]["email"] == "newcustomer@example.com"
        assert result["customer"]["attributes"]["name"] == "New Customer"
    
    @patch('time.sleep')
    def test_create_customer_with_id(self, mock_sleep, mock_auth, mock_session):
        """Test customer creation with custom ID."""
        create_response = {
            "customer": {
                "id": "custom_id_123",
                "email": "customer@example.com",
                "attributes": {
                    "name": "Customer with ID"
                }
            }
        }
        
        mock_session.post.return_value.json.return_value = create_response
        mock_session.post.return_value.status_code = 201
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = create_customer(
                auth=mock_auth,
                id="custom_id_123",
                email="customer@example.com",
                attributes={
                    "name": "Customer with ID"
                }
            )
        
        # Verify API call with custom ID
        mock_session.post.assert_called_once_with(
            "https://api.customer.io/v1/customers",
            json={
                "id": "custom_id_123",
                "email": "customer@example.com",
                "attributes": {
                    "name": "Customer with ID"
                }
            }
        )
        
        assert result == create_response
    
    @patch('time.sleep')
    def test_create_customer_duplicate_email(self, mock_sleep, mock_auth, mock_session):
        """Test customer creation with duplicate email."""
        # Set up 409 conflict response
        error_response = Mock()
        error_response.status_code = 409
        error_response.json.return_value = {"error": "Customer with this email already exists"}
        error_response.raise_for_status.side_effect = requests.HTTPError("409 Conflict")
        mock_session.post.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                create_customer(
                    auth=mock_auth,
                    email="existing@example.com",
                    attributes={"name": "Duplicate"}
                )
    
    def test_create_customer_missing_email(self, mock_auth):
        """Test customer creation with missing or empty email."""
        with pytest.raises(ValueError):
            create_customer(auth=mock_auth, email="", attributes={"name": "Empty Email"})
        
        with pytest.raises(ValueError):
            create_customer(auth=mock_auth, email=None, attributes={"name": "None Email"})
    
    @patch('time.sleep')
    def test_create_customer_validation_error(self, mock_sleep, mock_auth, mock_session):
        """Test customer creation with validation error."""
        # Set up 400 response for validation error
        error_response = Mock()
        error_response.status_code = 400
        error_response.json.return_value = {"error": "Invalid email format"}
        error_response.raise_for_status.side_effect = requests.HTTPError("400 Client Error")
        mock_session.post.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                create_customer(
                    auth=mock_auth,
                    email="invalid-email-format",
                    attributes={"name": "Invalid Email"}
                )
    
    @patch('time.sleep')
    def test_manage_customer_suppression_suppress_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer suppression."""
        suppress_response = {
            "customer": {
                "id": "cust_123",
                "email": "customer@example.com",
                "suppressed": True,
                "suppressed_at": 1704326400
            }
        }
        
        mock_session.put.return_value.json.return_value = suppress_response
        mock_session.put.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = manage_customer_suppression(
                auth=mock_auth,
                customer_id="cust_123",
                suppress=True
            )
        
        # Verify API call
        mock_session.put.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/suppress",
            json={"suppress": True}
        )
        
        # Verify rate limiting
        mock_auth.get_rate_limit_delay.assert_called_once_with("general")
        mock_sleep.assert_called_once()
        
        # Verify result
        assert result == suppress_response
        assert result["customer"]["suppressed"]
    
    @patch('time.sleep')
    def test_manage_customer_suppression_unsuppress_success(self, mock_sleep, mock_auth, mock_session):
        """Test successful customer unsuppression."""
        unsuppress_response = {
            "customer": {
                "id": "cust_123",
                "email": "customer@example.com",
                "suppressed": False,
                "unsuppressed_at": 1704326400
            }
        }
        
        mock_session.put.return_value.json.return_value = unsuppress_response
        mock_session.put.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = manage_customer_suppression(
                auth=mock_auth,
                customer_id="cust_123",
                suppress=False
            )
        
        # Verify API call
        mock_session.put.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/suppress",
            json={"suppress": False}
        )
        
        assert result == unsuppress_response
        assert not result["customer"]["suppressed"]
    
    @patch('time.sleep')
    def test_manage_customer_suppression_customer_not_found(self, mock_sleep, mock_auth, mock_session):
        """Test customer suppression when customer not found."""
        # Set up 404 response
        error_response = Mock()
        error_response.status_code = 404
        error_response.json.return_value = {"error": "Customer not found"}
        error_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.put.return_value = error_response
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            with pytest.raises(requests.HTTPError):
                manage_customer_suppression(
                    auth=mock_auth,
                    customer_id="nonexistent_customer",
                    suppress=True
                )
    
    def test_manage_customer_suppression_missing_id(self, mock_auth):
        """Test customer suppression with missing customer_id."""
        with pytest.raises(ValueError):
            manage_customer_suppression(auth=mock_auth, customer_id="", suppress=True)
        
        with pytest.raises(ValueError):
            manage_customer_suppression(auth=mock_auth, customer_id=None, suppress=True)
    
    def test_manage_customer_suppression_missing_suppress_flag(self, mock_auth):
        """Test customer suppression with missing suppress flag."""
        with pytest.raises(ValueError):
            manage_customer_suppression(auth=mock_auth, customer_id="cust_123")
    
    @patch('time.sleep')
    def test_manage_customer_suppression_with_reason(self, mock_sleep, mock_auth, mock_session):
        """Test customer suppression with reason."""
        suppress_response = {
            "customer": {
                "id": "cust_123",
                "email": "customer@example.com",
                "suppressed": True,
                "suppressed_at": 1704326400,
                "suppression_reason": "GDPR request"
            }
        }
        
        mock_session.put.return_value.json.return_value = suppress_response
        mock_session.put.return_value.status_code = 200
        
        with patch('src.app_api.client.requests.Session', return_value=mock_session):
            result = manage_customer_suppression(
                auth=mock_auth,
                customer_id="cust_123",
                suppress=True,
                reason="GDPR request"
            )
        
        # Verify API call with reason
        mock_session.put.assert_called_once_with(
            "https://api.customer.io/v1/customers/cust_123/suppress",
            json={
                "suppress": True,
                "reason": "GDPR request"
            }
        )
        
        assert result == suppress_response
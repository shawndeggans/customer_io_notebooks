"""App API client functions."""
import time
import requests
from typing import Dict, Any, Optional, List
from .auth import AppAPIAuth


def send_transactional(
    auth: AppAPIAuth,
    transactional_message_id: int,
    to: Optional[str] = None,
    identifiers: Optional[Dict[str, Any]] = None,
    message_data: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send a transactional email message.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    transactional_message_id : int
        ID of the transactional message to send
    to : str, optional
        Email address to send to (required if identifiers not provided)
    identifiers : Dict[str, Any], optional
        Customer identifiers (required if to not provided)
    message_data : Dict[str, Any], optional
        Data to populate message template
    **kwargs
        Additional parameters for the API call
        
    Returns
    -------
    Dict[str, Any]
        API response data
        
    Raises
    ------
    ValueError
        If required parameters are missing
    requests.HTTPError
        If API request fails
    """
    if not to and not identifiers:
        raise ValueError("Either 'to' or 'identifiers' must be provided")
    
    # Build request payload
    payload = {
        "transactional_message_id": transactional_message_id,
        **kwargs
    }
    
    if to:
        payload["to"] = to
    if identifiers:
        payload["identifiers"] = identifiers
    if message_data:
        payload["message_data"] = message_data
    
    # Rate limiting
    delay = auth.get_rate_limit_delay("transactional")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.post(
        f"{auth.base_url}/v1/send/email",
        json=payload
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def trigger_broadcast(
    auth: AppAPIAuth,
    broadcast_id: int,
    data: Optional[Dict[str, Any]] = None,
    recipients: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Trigger an API-triggered broadcast.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    broadcast_id : int
        ID of the broadcast to trigger
    data : Dict[str, Any], optional
        Data to send with the broadcast
    recipients : Dict[str, Any], optional
        Recipient targeting information
    **kwargs
        Additional parameters for the API call
        
    Returns
    -------
    Dict[str, Any]
        API response data
        
    Raises
    ------
    ValueError
        If broadcast_id is None
    requests.HTTPError
        If API request fails
    """
    if broadcast_id is None:
        raise ValueError("broadcast_id is required")
    
    # Build request payload
    payload = {**kwargs}
    
    if data:
        payload["data"] = data
    if recipients:
        payload["recipients"] = recipients
    
    # Rate limiting (broadcasts have different rate limit)
    delay = auth.get_rate_limit_delay("broadcast")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.post(
        f"{auth.base_url}/v1/campaigns/{broadcast_id}/triggers",
        json=payload
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def send_push(
    auth: AppAPIAuth,
    identifiers: Dict[str, Any],
    title: Optional[str] = None,
    message: Optional[str] = None,
    device_tokens: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Send a push notification.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    identifiers : Dict[str, Any]
        Customer identifiers
    title : str, optional
        Push notification title
    message : str, optional
        Push notification message
    device_tokens : List[str], optional
        Specific device tokens to target
    **kwargs
        Additional parameters for the API call
        
    Returns
    -------
    Dict[str, Any]
        API response data
        
    Raises
    ------
    ValueError
        If required parameters are missing
    requests.HTTPError
        If API request fails
    """
    if not title or not message or not device_tokens:
        raise ValueError("title, message, and device_tokens are required")
    
    # Build request payload
    payload = {
        "identifiers": identifiers,
        "title": title,
        "message": message,
        "device_tokens": device_tokens,
        **kwargs
    }
    
    # Rate limiting
    delay = auth.get_rate_limit_delay("transactional")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.post(
        f"{auth.base_url}/v1/send/push",
        json=payload
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def search_customers(
    auth: AppAPIAuth,
    email: Optional[str] = None,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Search for customers in Customer.IO.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    email : str, optional
        Email address to search for
    limit : int, optional
        Maximum number of customers to return (default: 50, max: 50)
    start : str, optional
        Customer ID to start results from (for pagination)
    **kwargs
        Additional search parameters
        
    Returns
    -------
    Dict[str, Any]
        API response containing customers and metadata
        
    Raises
    ------
    ValueError
        If no search parameters are provided
    requests.HTTPError
        If API request fails
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> results = search_customers(auth, email="user@example.com", limit=10)
    >>> print(f"Found {len(results['customers'])} customers")
    """
    # Validate that at least one search parameter is provided
    if not any([email, limit, start]) and not kwargs:
        raise ValueError("At least one search parameter must be provided")
    
    # Build query parameters
    params = {}
    
    if email:
        params["email"] = email
    if limit:
        params["limit"] = limit
    if start:
        params["start"] = start
    
    # Add any additional parameters
    params.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.get(
        f"{auth.base_url}/v1/customers",
        params=params
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def get_customer(
    auth: AppAPIAuth,
    customer_id: str
) -> Dict[str, Any]:
    """
    Retrieve a specific customer profile from Customer.IO.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
        
    Returns
    -------
    Dict[str, Any]
        API response containing customer profile data
        
    Raises
    ------
    ValueError
        If customer_id is empty or None
    requests.HTTPError
        If API request fails (404 for not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> customer = get_customer(auth, customer_id="cust_123")
    >>> print(f"Customer: {customer['customer']['email']}")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.get(
        f"{auth.base_url}/v1/customers/{customer_id}"
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def get_customer_activities(
    auth: AppAPIAuth,
    customer_id: str,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve activity history for a specific customer.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
    limit : int, optional
        Maximum number of activities to return
    start : str, optional
        Activity ID to start results from (for pagination)
    type : str, optional
        Filter activities by type (e.g., "email", "event", "push")
    **kwargs
        Additional filter parameters
        
    Returns
    -------
    Dict[str, Any]
        API response containing customer activities and metadata
        
    Raises
    ------
    ValueError
        If customer_id is empty or None
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> activities = get_customer_activities(auth, customer_id="cust_123", limit=20)
    >>> print(f"Found {len(activities['activities'])} activities")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Build query parameters
    params = {}
    
    if limit:
        params["limit"] = limit
    if start:
        params["start"] = start
    if type:
        params["type"] = type
    
    # Add any additional parameters
    params.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.get(
        f"{auth.base_url}/v1/customers/{customer_id}/activities",
        params=params
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def get_customer_attributes(
    auth: AppAPIAuth,
    customer_id: str
) -> Dict[str, Any]:
    """
    Retrieve attributes for a specific customer.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
        
    Returns
    -------
    Dict[str, Any]
        API response containing customer attributes
        
    Raises
    ------
    ValueError
        If customer_id is empty or None
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> attributes = get_customer_attributes(auth, customer_id="cust_123")
    >>> print(f"Customer email: {attributes['customer']['attributes']['email']}")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.get(
        f"{auth.base_url}/v1/customers/{customer_id}/attributes"
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def get_customer_messages(
    auth: AppAPIAuth,
    customer_id: str,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    type: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve message history for a specific customer.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
    limit : int, optional
        Maximum number of messages to return
    start : str, optional
        Message ID to start results from (for pagination)
    type : str, optional
        Filter messages by type (e.g., "email", "push", "in_app", "sms")
    **kwargs
        Additional filter parameters
        
    Returns
    -------
    Dict[str, Any]
        API response containing customer messages and metadata
        
    Raises
    ------
    ValueError
        If customer_id is empty or None
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> messages = get_customer_messages(auth, customer_id="cust_123", type="email", limit=20)
    >>> print(f"Found {len(messages['messages'])} email messages")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Build query parameters
    params = {}
    
    if limit:
        params["limit"] = limit
    if start:
        params["start"] = start
    if type:
        params["type"] = type
    
    # Add any additional parameters
    params.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.get(
        f"{auth.base_url}/v1/customers/{customer_id}/messages",
        params=params
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def get_customer_segments(
    auth: AppAPIAuth,
    customer_id: str,
    limit: Optional[int] = None,
    start: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Retrieve segment membership for a specific customer.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
    limit : int, optional
        Maximum number of segments to return
    start : str, optional
        Segment ID to start results from (for pagination)
    **kwargs
        Additional filter parameters
        
    Returns
    -------
    Dict[str, Any]
        API response containing customer segments and metadata
        
    Raises
    ------
    ValueError
        If customer_id is empty or None
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> segments = get_customer_segments(auth, customer_id="cust_123", limit=20)
    >>> print(f"Customer belongs to {len(segments['segments'])} segments")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Build query parameters
    params = {}
    
    if limit:
        params["limit"] = limit
    if start:
        params["start"] = start
    
    # Add any additional parameters
    params.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.get(
        f"{auth.base_url}/v1/customers/{customer_id}/segments",
        params=params
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def delete_customer(
    auth: AppAPIAuth,
    customer_id: str,
    suppress: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Delete a customer from Customer.IO.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
    suppress : bool, optional
        Whether to suppress the customer from future messaging
    **kwargs
        Additional parameters for the API call
        
    Returns
    -------
    Dict[str, Any]
        API response containing deletion confirmation
        
    Raises
    ------
    ValueError
        If customer_id is empty or None
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> result = delete_customer(auth, customer_id="cust_123", suppress=True)
    >>> print(f"Customer deleted: {result['meta']['request_id']}")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Build query parameters
    params = {}
    
    if suppress is not None:
        params["suppress"] = suppress
    
    # Add any additional parameters
    params.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    if params:
        response = session.delete(
            f"{auth.base_url}/v1/customers/{customer_id}",
            params=params
        )
    else:
        response = session.delete(
            f"{auth.base_url}/v1/customers/{customer_id}"
        )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def update_customer(
    auth: AppAPIAuth,
    customer_id: str,
    email: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Update a customer's information in Customer.IO.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
    email : str, optional
        New email address for the customer
    attributes : Dict[str, Any], optional
        Customer attributes to update
    **kwargs
        Additional parameters for the API call
        
    Returns
    -------
    Dict[str, Any]
        API response containing updated customer data
        
    Raises
    ------
    ValueError
        If customer_id is empty or None, or if no update data is provided
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> result = update_customer(auth, customer_id="cust_123", 
    ...                         email="newemail@example.com",
    ...                         attributes={"name": "Updated Name", "plan": "premium"})
    >>> print(f"Customer updated: {result['customer']['email']}")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Validate that at least some update data is provided
    if not email and not attributes and not kwargs:
        raise ValueError("At least one of email, attributes, or additional parameters must be provided")
    
    # Build request payload
    payload = {}
    
    if email:
        payload["email"] = email
    if attributes:
        payload["attributes"] = attributes
    
    # Add any additional parameters
    payload.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.put(
        f"{auth.base_url}/v1/customers/{customer_id}",
        json=payload
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()


def create_customer(
    auth: AppAPIAuth,
    email: str,
    id: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create a new customer in Customer.IO.
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    email : str
        Email address for the new customer (required)
    id : str, optional
        Custom identifier for the customer
    attributes : Dict[str, Any], optional
        Customer attributes to set
    **kwargs
        Additional parameters for the API call
        
    Returns
    -------
    Dict[str, Any]
        API response containing created customer data
        
    Raises
    ------
    ValueError
        If email is empty or None
    requests.HTTPError
        If API request fails (409 for duplicate email, 400 for validation errors, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> result = create_customer(auth, email="newcustomer@example.com",
    ...                         attributes={"name": "New Customer", "plan": "basic"})
    >>> print(f"Customer created: {result['customer']['id']}")
    """
    # Validate email is provided
    if not email:
        raise ValueError("email is required and cannot be empty")
    
    # Build request payload
    payload = {"email": email}
    
    if id:
        payload["id"] = id
    if attributes:
        payload["attributes"] = attributes
    
    # Add any additional parameters
    payload.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.post(
        f"{auth.base_url}/v1/customers",
        json=payload
    )
    
    if response.status_code != 201:
        response.raise_for_status()
    
    return response.json()


def manage_customer_suppression(
    auth: AppAPIAuth,
    customer_id: str,
    suppress: Optional[bool] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Manage customer suppression status (suppress or unsuppress).
    
    Parameters
    ----------
    auth : AppAPIAuth
        Authentication object for API access
    customer_id : str
        Unique identifier for the customer
    suppress : bool, optional
        True to suppress the customer, False to unsuppress, required
    **kwargs
        Additional parameters for the API call (e.g., reason)
        
    Returns
    -------
    Dict[str, Any]
        API response containing suppression status
        
    Raises
    ------
    ValueError
        If customer_id is empty, None, or suppress is not provided
    requests.HTTPError
        If API request fails (404 for customer not found, etc.)
        
    Example
    -------
    >>> auth = AppAPIAuth(api_token="your_token")
    >>> result = manage_customer_suppression(auth, customer_id="cust_123", suppress=True)
    >>> print(f"Customer suppression updated: {result['customer']['suppressed']}")
    """
    # Validate customer_id is provided
    if not customer_id:
        raise ValueError("customer_id is required and cannot be empty")
    
    # Validate suppress is provided
    if suppress is None:
        raise ValueError("suppress is required (True to suppress, False to unsuppress)")
    
    # Build request payload
    payload = {"suppress": suppress}
    
    # Add any additional parameters
    payload.update(kwargs)
    
    # Rate limiting for general endpoints
    delay = auth.get_rate_limit_delay("general")
    time.sleep(delay)
    
    # Make API request
    session = requests.Session()
    session.headers.update(auth.get_headers())
    
    response = session.put(
        f"{auth.base_url}/v1/customers/{customer_id}/suppress",
        json=payload
    )
    
    if response.status_code != 200:
        response.raise_for_status()
    
    return response.json()
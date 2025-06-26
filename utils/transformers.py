"""
Customer.IO Data Transformers

Utilities for transforming data between different formats for Customer.IO API interactions.
Handles conversions between Spark DataFrames, Pandas DataFrames, and API request formats.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Union
import json
import uuid

# Optional PySpark imports for Databricks environments
try:
    from pyspark.sql import DataFrame as SparkDataFrame
    from pyspark.sql.types import StructType, StructField, StringType, TimestampType, MapType
    from pyspark.sql import functions as F
    PYSPARK_AVAILABLE = True
except ImportError:
    SparkDataFrame = None
    PYSPARK_AVAILABLE = False

import pandas as pd


class CustomerTransformer:
    """Transformer for customer/user data between different formats."""
    
    @staticmethod
    def spark_to_identify_requests(
        df,  # Type hint removed for optional PySpark
        user_id_col: str = "user_id",
        email_col: str = "email",
        traits_cols: List[str] = None,
        timestamp_col: str = "created_at"
    ) -> List[Dict[str, Any]]:
        """
        Transform Spark DataFrame to Customer.IO identify requests.
        
        Args:
            df: Spark DataFrame containing customer data
            user_id_col: Column name for user ID
            email_col: Column name for email
            traits_cols: List of columns to include as traits
            timestamp_col: Column name for timestamp
            
        Returns:
            List of identify request dictionaries
            
        Raises:
            ImportError: If PySpark is not available
        """
        if not PYSPARK_AVAILABLE:
            raise ImportError("PySpark is required for spark_to_identify_requests but is not installed")
            
        if not hasattr(df, 'collect'):
            raise ValueError("Input must be a Spark DataFrame")
        # Collect data to driver (be careful with large datasets)
        rows = df.collect()
        requests = []
        
        for row in rows:
            # Build traits dictionary
            traits = {}
            
            # Add email if present
            if email_col in row.asDict() and row[email_col]:
                traits["email"] = row[email_col]
            
            # Add specified trait columns
            if traits_cols:
                for col in traits_cols:
                    if col in row.asDict() and row[col] is not None:
                        traits[col] = str(row[col])
            
            # Build request
            request = {
                "userId": row[user_id_col] if user_id_col in row.asDict() else None,
                "traits": traits
            }
            
            # Add timestamp if present
            if timestamp_col in row.asDict() and row[timestamp_col]:
                if isinstance(row[timestamp_col], datetime):
                    request["timestamp"] = row[timestamp_col].isoformat()
                else:
                    request["timestamp"] = row[timestamp_col]
            
            requests.append(request)
        
        return requests
    
    @staticmethod
    def pandas_to_identify_requests(
        df: pd.DataFrame,
        user_id_col: str = "user_id",
        email_col: str = "email",
        traits_cols: List[str] = None,
        timestamp_col: str = "created_at"
    ) -> List[Dict[str, Any]]:
        """
        Transform Pandas DataFrame to Customer.IO identify requests.
        
        Args:
            df: Pandas DataFrame containing customer data
            user_id_col: Column name for user ID
            email_col: Column name for email
            traits_cols: List of columns to include as traits
            timestamp_col: Column name for timestamp
            
        Returns:
            List of identify request dictionaries
        """
        requests = []
        
        for _, row in df.iterrows():
            # Build traits dictionary
            traits = {}
            
            # Add email if present
            if email_col in df.columns and pd.notna(row[email_col]):
                traits["email"] = row[email_col]
            
            # Add specified trait columns
            if traits_cols:
                for col in traits_cols:
                    if col in df.columns and pd.notna(row[col]):
                        traits[col] = str(row[col])
            
            # Build request
            request = {
                "userId": row[user_id_col] if user_id_col in df.columns and pd.notna(row[user_id_col]) else None,
                "traits": traits
            }
            
            # Add timestamp if present
            if timestamp_col in df.columns and pd.notna(row[timestamp_col]):
                if isinstance(row[timestamp_col], datetime):
                    request["timestamp"] = row[timestamp_col].isoformat()
                else:
                    request["timestamp"] = str(row[timestamp_col])
            
            requests.append(request)
        
        return requests
    
    @staticmethod
    def normalize_traits(traits: Dict[str, Any]) -> Dict[str, str]:
        """
        Normalize traits dictionary to string values for Customer.IO API.
        
        Args:
            traits: Dictionary of trait values
            
        Returns:
            Dictionary with string values
        """
        normalized = {}
        
        for key, value in traits.items():
            if value is None:
                continue
            elif isinstance(value, (str, int, float, bool)):
                normalized[key] = str(value)
            elif isinstance(value, datetime):
                normalized[key] = value.isoformat()
            elif isinstance(value, (list, dict)):
                normalized[key] = json.dumps(value)
            else:
                normalized[key] = str(value)
        
        return normalized


class EventTransformer:
    """Transformer for event data between different formats."""
    
    @staticmethod
    def spark_to_track_requests(
        df: SparkDataFrame,
        user_id_col: str = "user_id",
        event_name_col: str = "event_name",
        properties_cols: List[str] = None,
        timestamp_col: str = "timestamp"
    ) -> List[Dict[str, Any]]:
        """
        Transform Spark DataFrame to Customer.IO track requests.
        
        Args:
            df: Spark DataFrame containing event data
            user_id_col: Column name for user ID
            event_name_col: Column name for event name
            properties_cols: List of columns to include as properties
            timestamp_col: Column name for timestamp
            
        Returns:
            List of track request dictionaries
        """
        rows = df.collect()
        requests = []
        
        for row in rows:
            # Build properties dictionary
            properties = {}
            
            if properties_cols:
                for col in properties_cols:
                    if col in row.asDict() and row[col] is not None:
                        properties[col] = str(row[col])
            
            # Build request
            request = {
                "userId": row[user_id_col] if user_id_col in row.asDict() else None,
                "event": row[event_name_col] if event_name_col in row.asDict() else "Unknown Event",
                "properties": properties
            }
            
            # Add timestamp if present
            if timestamp_col in row.asDict() and row[timestamp_col]:
                if isinstance(row[timestamp_col], datetime):
                    request["timestamp"] = row[timestamp_col].isoformat()
                else:
                    request["timestamp"] = row[timestamp_col]
            
            requests.append(request)
        
        return requests
    
    @staticmethod
    def create_ecommerce_event(
        event_name: str,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        product_id: Optional[str] = None,
        order_id: Optional[str] = None,
        price: Optional[float] = None,
        quantity: Optional[int] = None,
        currency: str = "USD",
        **additional_properties
    ) -> Dict[str, Any]:
        """
        Create a standardized ecommerce event for Customer.IO.
        
        Args:
            event_name: Name of the ecommerce event
            user_id: User identifier
            anonymous_id: Anonymous user identifier
            product_id: Product identifier
            order_id: Order identifier
            price: Product/order price
            quantity: Product quantity
            currency: Currency code
            **additional_properties: Additional event properties
            
        Returns:
            Track request dictionary
        """
        # Build properties
        properties = {}
        
        if product_id:
            properties["product_id"] = product_id
        if order_id:
            properties["order_id"] = order_id
        if price is not None:
            properties["price"] = price
        if quantity is not None:
            properties["quantity"] = quantity
        
        properties["currency"] = currency
        properties.update(additional_properties)
        
        # Build request
        request = {
            "event": event_name,
            "properties": properties,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if user_id:
            request["userId"] = user_id
        if anonymous_id:
            request["anonymousId"] = anonymous_id
        
        return request
    
    @staticmethod
    def create_mobile_app_event(
        event_name: str,
        user_id: Optional[str] = None,
        anonymous_id: Optional[str] = None,
        app_version: Optional[str] = None,
        os_version: Optional[str] = None,
        device_model: Optional[str] = None,
        **additional_properties
    ) -> Dict[str, Any]:
        """
        Create a standardized mobile app event for Customer.IO.
        
        Args:
            event_name: Name of the mobile app event
            user_id: User identifier
            anonymous_id: Anonymous user identifier
            app_version: Application version
            os_version: Operating system version
            device_model: Device model
            **additional_properties: Additional event properties
            
        Returns:
            Track request dictionary
        """
        # Build properties
        properties = {}
        
        if app_version:
            properties["app_version"] = app_version
        if os_version:
            properties["os_version"] = os_version
        if device_model:
            properties["device_model"] = device_model
        
        properties.update(additional_properties)
        
        # Build request
        request = {
            "event": event_name,
            "properties": properties,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if user_id:
            request["userId"] = user_id
        if anonymous_id:
            request["anonymousId"] = anonymous_id
        
        return request


class GroupTransformer:
    """Transformer for group/organization data."""
    
    @staticmethod
    def spark_to_group_requests(
        df: SparkDataFrame,
        user_id_col: str = "user_id",
        group_id_col: str = "group_id",
        traits_cols: List[str] = None,
        timestamp_col: str = "created_at"
    ) -> List[Dict[str, Any]]:
        """
        Transform Spark DataFrame to Customer.IO group requests.
        
        Args:
            df: Spark DataFrame containing group association data
            user_id_col: Column name for user ID
            group_id_col: Column name for group ID
            traits_cols: List of columns to include as traits
            timestamp_col: Column name for timestamp
            
        Returns:
            List of group request dictionaries
        """
        rows = df.collect()
        requests = []
        
        for row in rows:
            # Build traits dictionary
            traits = {}
            
            if traits_cols:
                for col in traits_cols:
                    if col in row.asDict() and row[col] is not None:
                        traits[col] = str(row[col])
            
            # Build request
            request = {
                "userId": row[user_id_col] if user_id_col in row.asDict() else None,
                "groupId": row[group_id_col] if group_id_col in row.asDict() else None,
                "traits": traits
            }
            
            # Add timestamp if present
            if timestamp_col in row.asDict() and row[timestamp_col]:
                if isinstance(row[timestamp_col], datetime):
                    request["timestamp"] = row[timestamp_col].isoformat()
                else:
                    request["timestamp"] = row[timestamp_col]
            
            requests.append(request)
        
        return requests


class BatchTransformer:
    """Transformer for batch operations."""
    
    @staticmethod
    def create_batch_request(
        identify_requests: List[Dict[str, Any]] = None,
        track_requests: List[Dict[str, Any]] = None,
        group_requests: List[Dict[str, Any]] = None,
        max_batch_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Create batch requests from individual request lists.
        
        Args:
            identify_requests: List of identify requests
            track_requests: List of track requests
            group_requests: List of group requests
            max_batch_size: Maximum number of requests per batch
            
        Returns:
            List of batch request dictionaries
        """
        all_requests = []
        
        # Add identify requests
        if identify_requests:
            for req in identify_requests:
                req["type"] = "identify"
                all_requests.append(req)
        
        # Add track requests
        if track_requests:
            for req in track_requests:
                req["type"] = "track"
                all_requests.append(req)
        
        # Add group requests
        if group_requests:
            for req in group_requests:
                req["type"] = "group"
                all_requests.append(req)
        
        # Split into batches
        batches = []
        for i in range(0, len(all_requests), max_batch_size):
            batch = all_requests[i:i + max_batch_size]
            batches.append({"batch": batch})
        
        return batches
    
    @staticmethod
    def estimate_batch_size(requests: List[Dict[str, Any]]) -> int:
        """
        Estimate the size of a batch request in bytes.
        
        Args:
            requests: List of requests to estimate
            
        Returns:
            Estimated size in bytes
        """
        batch_data = {"batch": requests}
        return len(json.dumps(batch_data).encode('utf-8'))
    
    @staticmethod
    def optimize_batch_sizes(
        requests: List[Dict[str, Any]],
        max_size_bytes: int = 500 * 1024  # 500KB
    ) -> List[List[Dict[str, Any]]]:
        """
        Optimize batch sizes to stay within size limits.
        
        Args:
            requests: List of requests to batch
            max_size_bytes: Maximum batch size in bytes
            
        Returns:
            List of optimized batches
        """
        batches = []
        current_batch = []
        current_size = 0
        
        for request in requests:
            # Estimate size of adding this request
            test_batch = current_batch + [request]
            test_size = BatchTransformer.estimate_batch_size(test_batch)
            
            if test_size > max_size_bytes and current_batch:
                # Current batch is at capacity, start a new one
                batches.append(current_batch)
                current_batch = [request]
                current_size = BatchTransformer.estimate_batch_size(current_batch)
            else:
                # Add request to current batch
                current_batch.append(request)
                current_size = test_size
        
        # Add the last batch if it has requests
        if current_batch:
            batches.append(current_batch)
        
        return batches


class ContextTransformer:
    """Transformer for context data."""
    
    @staticmethod
    def create_web_context(
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        url: Optional[str] = None,
        referrer: Optional[str] = None,
        locale: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create context object for web events.
        
        Args:
            ip: Client IP address
            user_agent: User agent string
            url: Current page URL
            referrer: Referrer URL
            locale: User locale
            timezone: User timezone
            
        Returns:
            Context dictionary
        """
        context = {}
        
        if ip:
            context["ip"] = ip
        if user_agent:
            context["userAgent"] = user_agent
        if locale:
            context["locale"] = locale
        if timezone:
            context["timezone"] = timezone
        
        # Page context
        page_context = {}
        if url:
            page_context["url"] = url
        if referrer:
            page_context["referrer"] = referrer
        
        if page_context:
            context["page"] = page_context
        
        return context
    
    @staticmethod
    def create_mobile_context(
        app_name: Optional[str] = None,
        app_version: Optional[str] = None,
        os_name: Optional[str] = None,
        os_version: Optional[str] = None,
        device_model: Optional[str] = None,
        device_id: Optional[str] = None,
        locale: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create context object for mobile events.
        
        Args:
            app_name: Application name
            app_version: Application version
            os_name: Operating system name
            os_version: Operating system version
            device_model: Device model
            device_id: Device identifier
            locale: User locale
            timezone: User timezone
            
        Returns:
            Context dictionary
        """
        context = {}
        
        if locale:
            context["locale"] = locale
        if timezone:
            context["timezone"] = timezone
        
        # App context
        app_context = {}
        if app_name:
            app_context["name"] = app_name
        if app_version:
            app_context["version"] = app_version
        
        if app_context:
            context["app"] = app_context
        
        # Device context
        device_context = {}
        if device_model:
            device_context["model"] = device_model
        if device_id:
            device_context["id"] = device_id
        
        if device_context:
            context["device"] = device_context
        
        # OS context
        os_context = {}
        if os_name:
            os_context["name"] = os_name
        if os_version:
            os_context["version"] = os_version
        
        if os_context:
            context["os"] = os_context
        
        return context


# Utility Functions

def add_request_id(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add a unique request ID to a request for tracking purposes.
    
    Args:
        request: Request dictionary
        
    Returns:
        Request with added request ID
    """
    request_copy = request.copy()
    if "context" not in request_copy:
        request_copy["context"] = {}
    
    request_copy["context"]["requestId"] = str(uuid.uuid4())
    return request_copy


def add_timestamp(request: Dict[str, Any], timestamp: Optional[datetime] = None) -> Dict[str, Any]:
    """
    Add timestamp to a request if not already present.
    
    Args:
        request: Request dictionary
        timestamp: Timestamp to add (defaults to now)
        
    Returns:
        Request with added timestamp
    """
    request_copy = request.copy()
    
    if "timestamp" not in request_copy:
        if timestamp is None:
            timestamp = datetime.now(timezone.utc)
        
        request_copy["timestamp"] = timestamp.isoformat()
    
    return request_copy


def validate_request_structure(request: Dict[str, Any], request_type: str) -> bool:
    """
    Validate that a request has the required structure for its type.
    
    Args:
        request: Request dictionary to validate
        request_type: Type of request (identify, track, group, etc.)
        
    Returns:
        True if valid, False otherwise
    """
    # Check for required user identification
    if not request.get("userId") and not request.get("anonymousId"):
        return False
    
    # Type-specific validation
    if request_type == "track":
        return bool(request.get("event"))
    elif request_type == "group":
        return bool(request.get("groupId"))
    elif request_type == "identify":
        return True  # Only requires user identification
    
    return False
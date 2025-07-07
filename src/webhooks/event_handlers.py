"""Event handlers for Customer.io webhook events."""
from abc import ABC, abstractmethod
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging


class BaseEventHandler(ABC):
    """Base class for handling Customer.io webhook events."""
    
    def __init__(self, spark_session=None):
        """
        Initialize event handler.
        
        Parameters
        ----------
        spark_session : SparkSession, optional
            Spark session for Delta Lake operations
        """
        self.spark = spark_session
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process specific event type.
        
        Parameters
        ----------
        event_data : Dict[str, Any]
            Webhook event data
            
        Returns
        -------
        Dict[str, Any]
            Processed event data
        """
        pass
    
    def save_to_delta(self, data: Dict[str, Any], table_path: str, partition_cols: Optional[List[str]] = None):
        """
        Save event data to Delta table.
        
        Parameters
        ----------
        data : Dict[str, Any]
            Event data to save
        table_path : str
            Delta table path
        partition_cols : List[str], optional
            Columns to partition by
        """
        if not self.spark:
            self.logger.warning("No Spark session available, skipping Delta save")
            return
        
        try:
            df = self.spark.createDataFrame([data])
            
            if partition_cols:
                df.write \
                    .mode("append") \
                    .partitionBy(partition_cols) \
                    .format("delta") \
                    .save(table_path)
            else:
                df.write \
                    .mode("append") \
                    .format("delta") \
                    .save(table_path)
                    
            self.logger.info(f"Saved event to Delta table: {table_path}")
        except Exception as e:
            self.logger.error(f"Error saving to Delta: {e}")
            raise


class EmailEventHandler(BaseEventHandler):
    """Handle email events: drafted, attempted, sent, delivered, opened, clicked, etc."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process email events according to OpenAPI spec."""
        try:
            # Extract common fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate required fields
            if not all([event_id, object_type, timestamp, metric]):
                raise ValueError("Missing required event fields")
            
            if object_type != "email":
                raise ValueError(f"Invalid object_type for email handler: {object_type}")
            
            # Process event data
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "email_address": data.get("identifiers", {}).get("email"),
                "delivery_id": data.get("delivery_id"),
                "campaign_id": data.get("campaign_id"),
                "action_id": data.get("action_id"),
                "journey_id": data.get("journey_id"),
                "parent_action_id": data.get("parent_action_id"),
                "subject": data.get("subject"),
                "recipient": data.get("recipient"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Add metric-specific fields
            if metric == "clicked":
                processed_event.update({
                    "href": data.get("href"),
                    "link_id": data.get("link_id"),
                    "machine_click": data.get("machine", False)
                })
            elif metric == "opened":
                processed_event.update({
                    "proxied": data.get("proxied", False),
                    "prefetched": data.get("prefetched", False)
                })
            elif metric in ["bounced", "failed", "dropped", "undeliverable"]:
                processed_event["failure_message"] = data.get("failure_message")
            elif metric == "converted":
                processed_event["conversion_event_id"] = data.get("conversion_event_id")
            elif metric == "unsubscribed":
                processed_event["unsubscribe_event_id"] = data.get("unsubscribe_event_id")
            
            self.logger.info(f"Processed email event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing email event: {e}")
            raise


class CustomerEventHandler(BaseEventHandler):
    """Handle customer events: subscribed, unsubscribed, subscription_preferences_changed."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process customer events according to OpenAPI spec."""
        try:
            # Extract common fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate
            if object_type != "customer":
                raise ValueError(f"Invalid object_type for customer handler: {object_type}")
            
            valid_metrics = ["subscribed", "unsubscribed", "cio_subscription_preferences_changed"]
            if metric not in valid_metrics:
                raise ValueError(f"Invalid metric for customer event: {metric}")
            
            # Process event
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "email_address": data.get("email_address"),
                "identifiers": json.dumps(data.get("identifiers", {})),
                "processed_at": datetime.now().isoformat()
            }
            
            # Handle subscription preferences changes
            if metric == "cio_subscription_preferences_changed":
                processed_event["content"] = data.get("content")
                processed_event["delivery_type"] = event_data.get("delivery_type")
            
            self.logger.info(f"Processed customer event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing customer event: {e}")
            raise


class SMSEventHandler(BaseEventHandler):
    """Handle SMS events: drafted, attempted, sent, delivered, clicked, etc."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process SMS events according to OpenAPI spec."""
        try:
            # Extract fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate
            if object_type != "sms":
                raise ValueError(f"Invalid object_type for SMS handler: {object_type}")
            
            # Process event
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "delivery_id": data.get("delivery_id"),
                "recipient": data.get("recipient"),  # MSISDN phone number
                "campaign_id": data.get("campaign_id"),
                "action_id": data.get("action_id"),
                "journey_id": data.get("journey_id"),
                "parent_action_id": data.get("parent_action_id"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Add metric-specific fields
            if metric == "sent" and "content" in data:
                processed_event["content"] = data.get("content")
            elif metric == "clicked":
                processed_event.update({
                    "href": data.get("href"),
                    "link_id": data.get("link_id")
                })
            elif metric in ["bounced", "failed"]:
                processed_event["failure_message"] = data.get("failure_message")
            elif metric == "converted":
                processed_event["conversion_event_id"] = data.get("conversion_event_id")
            
            self.logger.info(f"Processed SMS event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing SMS event: {e}")
            raise


class PushEventHandler(BaseEventHandler):
    """Handle push notification events: drafted, attempted, sent, delivered, opened, etc."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process push events according to OpenAPI spec."""
        try:
            # Extract fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate
            if object_type != "push":
                raise ValueError(f"Invalid object_type for push handler: {object_type}")
            
            # Process event
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "delivery_id": data.get("delivery_id"),
                "campaign_id": data.get("campaign_id"),
                "action_id": data.get("action_id"),
                "journey_id": data.get("journey_id"),
                "parent_action_id": data.get("parent_action_id"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Handle recipients array
            recipients = data.get("recipients", [])
            if recipients:
                # For simplicity, store as JSON string
                processed_event["recipients"] = json.dumps(recipients)
                # Extract first device_id for primary tracking
                if isinstance(recipients, list) and len(recipients) > 0:
                    processed_event["primary_device_id"] = recipients[0].get("device_id")
            
            # Add metric-specific fields
            if metric == "sent" and "content" in data:
                processed_event["content"] = data.get("content")
            elif metric == "clicked":
                processed_event.update({
                    "href": data.get("href"),
                    "link_id": data.get("link_id")
                })
            elif metric in ["bounced", "dropped", "failed", "undeliverable"]:
                processed_event["failure_message"] = data.get("failure_message")
            elif metric == "converted":
                processed_event["conversion_event_id"] = data.get("conversion_event_id")
            
            self.logger.info(f"Processed push event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing push event: {e}")
            raise


class InAppEventHandler(BaseEventHandler):
    """Handle in-app message events."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process in-app events according to OpenAPI spec."""
        try:
            # Extract fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate
            if object_type != "in_app":
                raise ValueError(f"Invalid object_type for in-app handler: {object_type}")
            
            # Process event
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "delivery_id": data.get("delivery_id"),
                "campaign_id": data.get("campaign_id"),
                "action_id": data.get("action_id"),
                "journey_id": data.get("journey_id"),
                "parent_action_id": data.get("parent_action_id"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Add metric-specific fields
            if metric == "sent" and "content" in data:
                processed_event["content"] = data.get("content")
            elif metric == "clicked":
                processed_event.update({
                    "href": data.get("href"),
                    "link_id": data.get("link_id")
                })
            elif metric == "converted":
                processed_event["conversion_event_id"] = data.get("conversion_event_id")
            elif metric == "failed":
                processed_event["failure_message"] = data.get("failure_message")
            
            self.logger.info(f"Processed in-app event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing in-app event: {e}")
            raise


class SlackEventHandler(BaseEventHandler):
    """Handle Slack message events."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Slack events according to OpenAPI spec."""
        try:
            # Extract fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate
            if object_type != "slack":
                raise ValueError(f"Invalid object_type for Slack handler: {object_type}")
            
            # Process event
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "delivery_id": data.get("delivery_id"),
                "campaign_id": data.get("campaign_id"),
                "action_id": data.get("action_id"),
                "journey_id": data.get("journey_id"),
                "parent_action_id": data.get("parent_action_id"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Add Slack-specific fields
            if metric == "sent" and "content" in data:
                processed_event["content"] = data.get("content")
            elif metric == "clicked":
                processed_event.update({
                    "href": data.get("href"),
                    "link_id": data.get("link_id")
                })
            elif metric in ["failed", "dropped"]:
                processed_event["failure_message"] = data.get("failure_message")
            
            self.logger.info(f"Processed Slack event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing Slack event: {e}")
            raise


class WebhookEventHandler(BaseEventHandler):
    """Handle webhook events (Customer.io's webhook delivery tracking)."""
    
    def handle_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process webhook events according to OpenAPI spec."""
        try:
            # Extract fields
            event_id = event_data.get("event_id")
            object_type = event_data.get("object_type")
            timestamp = event_data.get("timestamp")
            metric = event_data.get("metric")
            data = event_data.get("data", {})
            
            # Validate
            if object_type != "webhook":
                raise ValueError(f"Invalid object_type for webhook handler: {object_type}")
            
            # Process event
            processed_event = {
                "event_id": event_id,
                "object_type": object_type,
                "metric": metric,
                "timestamp": timestamp,
                "event_date": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d"),
                "customer_id": data.get("customer_id"),
                "delivery_id": data.get("delivery_id"),
                "campaign_id": data.get("campaign_id"),
                "action_id": data.get("action_id"),
                "journey_id": data.get("journey_id"),
                "parent_action_id": data.get("parent_action_id"),
                "processed_at": datetime.now().isoformat()
            }
            
            # Add webhook-specific fields
            if metric == "sent":
                processed_event.update({
                    "webhook_url": data.get("webhook_url"),
                    "content": data.get("content") if "content" in data else None
                })
            elif metric == "clicked":
                processed_event.update({
                    "href": data.get("href"),
                    "link_id": data.get("link_id")
                })
            elif metric in ["failed", "dropped"]:
                processed_event["failure_message"] = data.get("failure_message")
            
            self.logger.info(f"Processed webhook event: {metric} for {event_id}")
            return processed_event
            
        except Exception as e:
            self.logger.error(f"Error processing webhook event: {e}")
            raise


# Event handler factory
def get_event_handler(object_type: str, spark_session=None) -> BaseEventHandler:
    """
    Get appropriate event handler for object type.
    
    Parameters
    ----------
    object_type : str
        Type of event object
    spark_session : SparkSession, optional
        Spark session for Delta operations
        
    Returns
    -------
    BaseEventHandler
        Event handler instance
        
    Raises
    ------
    ValueError
        If object_type is not supported
    """
    handlers = {
        "email": EmailEventHandler,
        "customer": CustomerEventHandler,
        "sms": SMSEventHandler,
        "push": PushEventHandler,
        "in_app": InAppEventHandler,
        "slack": SlackEventHandler,
        "webhook": WebhookEventHandler
    }
    
    handler_class = handlers.get(object_type)
    if not handler_class:
        raise ValueError(f"No handler available for object_type: {object_type}")
    
    return handler_class(spark_session)
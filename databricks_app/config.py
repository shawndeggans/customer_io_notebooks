"""Configuration for Customer.io webhook processor."""
import os
from typing import List


class WebhookConfig:
    """Configuration for Customer.io webhook processing."""
    
    # Customer.io webhook signing key (from environment/secrets)
    WEBHOOK_SIGNING_KEY = os.environ.get('CUSTOMERIO_WEBHOOK_SECRET', '')
    
    # Delta table locations (for Databricks)
    DELTA_BASE_PATH = os.environ.get('DELTA_BASE_PATH', '/mnt/customerio')
    WEBHOOK_LANDING_PATH = f"{DELTA_BASE_PATH}/webhook_landing/"
    PROCESSED_EVENTS_PATH = f"{DELTA_BASE_PATH}/processed_events/"
    
    # Webhook validation settings
    TIMESTAMP_TOLERANCE = 300  # 5 minutes in seconds
    
    # Supported event types from OpenAPI spec
    SUPPORTED_EVENT_TYPES = [
        "customer", "email", "push", "in_app", "sms", "slack", "webhook"
    ]
    
    # Email event metrics
    EMAIL_METRICS = [
        "drafted", "attempted", "sent", "delivered", "opened", "clicked",
        "converted", "unsubscribed", "bounced", "dropped", "spammed", 
        "failed", "undeliverable"
    ]
    
    # Customer event metrics
    CUSTOMER_METRICS = [
        "subscribed", "unsubscribed", "cio_subscription_preferences_changed"
    ]
    
    # SMS event metrics
    SMS_METRICS = [
        "drafted", "attempted", "sent", "delivered", "clicked",
        "converted", "bounced", "failed"
    ]
    
    # Push event metrics
    PUSH_METRICS = [
        "drafted", "attempted", "delivered", "sent", "opened", "clicked",
        "converted", "bounced", "dropped", "failed", "undeliverable"
    ]
    
    # In-app event metrics
    IN_APP_METRICS = [
        "drafted", "attempted", "sent", "opened", "clicked",
        "converted", "failed"
    ]
    
    # Slack event metrics
    SLACK_METRICS = [
        "drafted", "attempted", "sent", "clicked", "failed", "dropped"
    ]
    
    # Webhook event metrics
    WEBHOOK_METRICS = [
        "drafted", "attempted", "sent", "clicked", "failed", "dropped"
    ]
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Flask configuration
    FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
    FLASK_DEBUG = FLASK_ENV == 'development'
    
    # Databricks configuration
    DATABRICKS_HOST = os.environ.get('DATABRICKS_HOST', '')
    DATABRICKS_TOKEN = os.environ.get('DATABRICKS_TOKEN', '')
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration."""
        errors = []
        
        if not cls.WEBHOOK_SIGNING_KEY:
            errors.append("CUSTOMERIO_WEBHOOK_SECRET environment variable is required")
        
        if cls.FLASK_ENV == 'production':
            if not cls.DATABRICKS_HOST:
                errors.append("DATABRICKS_HOST environment variable is required in production")
            if not cls.DATABRICKS_TOKEN:
                errors.append("DATABRICKS_TOKEN environment variable is required in production")
        
        if errors:
            raise ValueError(f"Configuration errors: {'; '.join(errors)}")
    
    @classmethod
    def get_metric_list(cls, object_type: str) -> List[str]:
        """Get valid metrics for an object type."""
        metric_map = {
            "email": cls.EMAIL_METRICS,
            "customer": cls.CUSTOMER_METRICS,
            "sms": cls.SMS_METRICS,
            "push": cls.PUSH_METRICS,
            "in_app": cls.IN_APP_METRICS,
            "slack": cls.SLACK_METRICS,
            "webhook": cls.WEBHOOK_METRICS
        }
        return metric_map.get(object_type, [])


# Event subscription configuration for webhook setup
WEBHOOK_EVENT_SUBSCRIPTIONS = [
    # Email events
    "email_drafted", "email_attempted", "email_sent", "email_delivered",
    "email_opened", "email_clicked", "email_converted", "email_unsubscribed",
    "email_bounced", "email_dropped", "email_spammed", "email_failed",
    "email_undeliverable",
    
    # Customer events
    "customer_subscribed", "customer_unsubscribed", 
    "customer_cio_subscription_preferences_changed",
    
    # SMS events
    "sms_drafted", "sms_attempted", "sms_sent", "sms_delivered",
    "sms_clicked", "sms_converted", "sms_bounced", "sms_failed",
    
    # Push events
    "push_drafted", "push_attempted", "push_sent", "push_delivered",
    "push_opened", "push_clicked", "push_converted", "push_bounced",
    "push_dropped", "push_failed", "push_undeliverable",
    
    # In-app events
    "in_app_drafted", "in_app_attempted", "in_app_sent", "in_app_opened",
    "in_app_clicked", "in_app_converted", "in_app_failed",
    
    # Slack events
    "slack_drafted", "slack_attempted", "slack_sent", "slack_clicked",
    "slack_failed", "slack_dropped",
    
    # Webhook events
    "webhook_drafted", "webhook_attempted", "webhook_sent", "webhook_clicked",
    "webhook_failed", "webhook_dropped"
]
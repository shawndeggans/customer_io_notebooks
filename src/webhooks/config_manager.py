"""Customer.io Webhook Configuration Manager."""
import requests
import json
from typing import Dict, Any, List, Optional
import logging


class CustomerIOWebhookManager:
    """Manage Customer.io reporting webhooks via API."""
    
    def __init__(self, api_token: str, base_url: str = "https://api.customer.io", region: str = "us"):
        """
        Initialize webhook manager.
        
        Parameters
        ----------
        api_token : str
            Customer.io App API bearer token
        base_url : str
            API base URL (default: https://api.customer.io)
        region : str
            Region (us or eu)
        """
        self.api_token = api_token
        self.base_url = base_url if region == "us" else "https://api-eu.customer.io"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def create_webhook(
        self, 
        webhook_url: str, 
        events: List[str], 
        name: str = "Databricks Webhook",
        disabled: bool = False,
        full_resolution: bool = True,
        with_content: bool = True
    ) -> Dict[str, Any]:
        """
        Create a new reporting webhook.
        
        Parameters
        ----------
        webhook_url : str
            URL to receive webhook events
        events : List[str]
            List of events to subscribe to
        name : str
            Name for the webhook
        disabled : bool
            Whether webhook starts disabled
        full_resolution : bool
            Send all events (not just first/last)
        with_content : bool
            Include message content in events
            
        Returns
        -------
        Dict[str, Any]
            Created webhook details
            
        Raises
        ------
        Exception
            If webhook creation fails
        """
        payload = {
            "name": name,
            "endpoint": webhook_url,
            "disabled": disabled,
            "full_resolution": full_resolution,
            "with_content": with_content,
            "events": events
        }
        
        self.logger.info(f"Creating webhook: {name} -> {webhook_url}")
        
        response = requests.post(
            f"{self.base_url}/v1/reporting_webhooks",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            webhook = response.json()
            self.logger.info(f"Webhook created successfully: {webhook.get('id')}")
            return webhook
        else:
            error_msg = f"Failed to create webhook: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def list_webhooks(self) -> List[Dict[str, Any]]:
        """
        List all reporting webhooks.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of webhook configurations
            
        Raises
        ------
        Exception
            If request fails
        """
        self.logger.info("Listing webhooks")
        
        response = requests.get(
            f"{self.base_url}/v1/reporting_webhooks",
            headers=self.headers
        )
        
        if response.status_code == 200:
            webhooks = response.json()
            self.logger.info(f"Found {len(webhooks)} webhooks")
            return webhooks
        else:
            error_msg = f"Failed to list webhooks: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def get_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """
        Get specific webhook details.
        
        Parameters
        ----------
        webhook_id : str
            Webhook ID
            
        Returns
        -------
        Dict[str, Any]
            Webhook configuration
            
        Raises
        ------
        Exception
            If request fails
        """
        self.logger.info(f"Getting webhook: {webhook_id}")
        
        response = requests.get(
            f"{self.base_url}/v1/reporting_webhooks/{webhook_id}",
            headers=self.headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Failed to get webhook: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def update_webhook(
        self,
        webhook_id: str,
        webhook_url: Optional[str] = None,
        events: Optional[List[str]] = None,
        name: Optional[str] = None,
        disabled: Optional[bool] = None,
        full_resolution: Optional[bool] = None,
        with_content: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update an existing webhook.
        
        Parameters
        ----------
        webhook_id : str
            Webhook ID to update
        webhook_url : str, optional
            New webhook URL
        events : List[str], optional
            New event list
        name : str, optional
            New name
        disabled : bool, optional
            Enable/disable webhook
        full_resolution : bool, optional
            Full resolution setting
        with_content : bool, optional
            Content inclusion setting
            
        Returns
        -------
        Dict[str, Any]
            Updated webhook details
            
        Raises
        ------
        Exception
            If update fails
        """
        # Build update payload with only provided fields
        payload = {}
        if webhook_url is not None:
            payload["endpoint"] = webhook_url
        if events is not None:
            payload["events"] = events
        if name is not None:
            payload["name"] = name
        if disabled is not None:
            payload["disabled"] = disabled
        if full_resolution is not None:
            payload["full_resolution"] = full_resolution
        if with_content is not None:
            payload["with_content"] = with_content
        
        self.logger.info(f"Updating webhook: {webhook_id}")
        
        response = requests.put(
            f"{self.base_url}/v1/reporting_webhooks/{webhook_id}",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            webhook = response.json()
            self.logger.info(f"Webhook updated successfully: {webhook_id}")
            return webhook
        else:
            error_msg = f"Failed to update webhook: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a webhook.
        
        Parameters
        ----------
        webhook_id : str
            Webhook ID to delete
            
        Returns
        -------
        bool
            True if deletion successful
            
        Raises
        ------
        Exception
            If deletion fails
        """
        self.logger.info(f"Deleting webhook: {webhook_id}")
        
        response = requests.delete(
            f"{self.base_url}/v1/reporting_webhooks/{webhook_id}",
            headers=self.headers
        )
        
        if response.status_code == 204:
            self.logger.info(f"Webhook deleted successfully: {webhook_id}")
            return True
        else:
            error_msg = f"Failed to delete webhook: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def test_webhook(self, webhook_id: str) -> bool:
        """
        Test a webhook by sending a test event.
        
        Parameters
        ----------
        webhook_id : str
            Webhook ID to test
            
        Returns
        -------
        bool
            True if test successful
            
        Raises
        ------
        Exception
            If test fails
        """
        self.logger.info(f"Testing webhook: {webhook_id}")
        
        response = requests.post(
            f"{self.base_url}/v1/reporting_webhooks/{webhook_id}/test",
            headers=self.headers
        )
        
        if response.status_code == 200:
            self.logger.info(f"Webhook test sent successfully: {webhook_id}")
            return True
        else:
            error_msg = f"Failed to test webhook: {response.status_code} - {response.text}"
            self.logger.error(error_msg)
            raise Exception(error_msg)


def setup_databricks_webhook(
    api_token: str,
    databricks_webhook_url: str,
    region: str = "us"
) -> Dict[str, Any]:
    """
    Set up Customer.io webhook for Databricks app.
    
    Parameters
    ----------
    api_token : str
        Customer.io App API token
    databricks_webhook_url : str
        Your Databricks app webhook URL
    region : str
        Region (us or eu)
        
    Returns
    -------
    Dict[str, Any]
        Created webhook details
    """
    # Complete list of webhook events from OpenAPI spec
    webhook_events = [
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
    
    manager = CustomerIOWebhookManager(api_token, region=region)
    
    try:
        # Check if webhook already exists
        existing_webhooks = manager.list_webhooks()
        for webhook in existing_webhooks:
            if webhook.get("endpoint") == databricks_webhook_url:
                print(f"Webhook already exists: {webhook.get('id')}")
                return webhook
        
        # Create new webhook
        webhook = manager.create_webhook(
            webhook_url=databricks_webhook_url,
            events=webhook_events,
            name="Databricks Analytics Webhook",
            full_resolution=True,
            with_content=True
        )
        
        print(f"Webhook created successfully!")
        print(f"Webhook ID: {webhook.get('id')}")
        print(f"Webhook endpoint: {webhook.get('endpoint')}")
        print(f"Events subscribed: {len(webhook.get('events', []))}")
        print("\nIMPORTANT: Save the webhook signing key for authentication")
        
        return webhook
        
    except Exception as e:
        print(f"Error setting up webhook: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    import os
    
    api_token = os.environ.get("CUSTOMERIO_APP_API_TOKEN")
    databricks_url = os.environ.get("DATABRICKS_WEBHOOK_URL")
    
    if not api_token or not databricks_url:
        print("Please set CUSTOMERIO_APP_API_TOKEN and DATABRICKS_WEBHOOK_URL environment variables")
    else:
        setup_databricks_webhook(api_token, databricks_url)
"""Customer.io Webhook Receiver - Databricks App."""
from flask import Flask, request, Response, jsonify
import json
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.webhooks import (
    verify_signature,
    parse_event,
    validate_webhook_headers,
    route_webhook_event,
    get_event_handler
)

# Initialize Flask app
app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@app.route('/webhook/customerio', methods=['POST'])
def handle_customerio_webhook():
    """Main Customer.io webhook endpoint."""
    try:
        # Get request data
        payload_body = request.get_data()
        headers = dict(request.headers)
        
        # Validate headers
        try:
            timestamp, signature = validate_webhook_headers(headers)
        except ValueError as e:
            logger.warning(f"Invalid headers: {e}")
            return Response(f'Bad Request: {e}', status=400)
        
        # Get webhook secret from environment
        webhook_secret = os.environ.get('CUSTOMERIO_WEBHOOK_SECRET')
        if not webhook_secret:
            logger.error("CUSTOMERIO_WEBHOOK_SECRET not configured")
            return Response('Server Configuration Error', status=500)
        
        # Verify webhook signature
        if not verify_signature(
            payload_body.decode('utf-8'),
            signature,
            timestamp,
            webhook_secret
        ):
            logger.warning("Invalid webhook signature")
            return Response('Unauthorized', status=401)
        
        # Parse JSON payload
        try:
            event_data = parse_event(payload_body.decode('utf-8'))
        except ValueError as e:
            logger.error(f"Invalid JSON payload: {e}")
            return Response(f'Bad Request: {e}', status=400)
        
        # Log raw event for debugging
        logger.info(f"Received webhook event: {event_data.get('object_type')} - {event_data.get('metric')}")
        
        # Save raw webhook data (for audit trail)
        save_raw_webhook_data(event_data)
        
        # Route and process the event
        try:
            routed_event = route_webhook_event(event_data)
            object_type = routed_event["object_type"]
            
            # Get appropriate handler (without Spark for now)
            handler = get_event_handler(object_type, spark_session=None)
            processed_event = handler.handle_event(event_data)
            
            # Log successful processing
            logger.info(
                f"Successfully processed {object_type} event: "
                f"{event_data.get('event_id')} - {routed_event.get('metric')}"
            )
            
            # In production, save to Delta Lake here
            # For now, just log the processed event
            logger.debug(f"Processed event data: {json.dumps(processed_event, indent=2)}")
            
        except ValueError as e:
            logger.error(f"Event processing error: {e}")
            return Response(f'Bad Request: {e}', status=400)
        except Exception as e:
            logger.error(f"Unexpected error processing event: {e}", exc_info=True)
            return Response('Internal Server Error', status=500)
        
        return Response('OK', status=200)
        
    except Exception as e:
        logger.error(f"Webhook endpoint error: {e}", exc_info=True)
        return Response('Internal Server Error', status=500)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "customerio-webhook-processor",
        "version": "1.0.0"
    })


@app.route('/', methods=['GET'])
def index():
    """Root endpoint."""
    return jsonify({
        "service": "Customer.io Webhook Processor",
        "endpoints": {
            "/webhook/customerio": "POST - Receive Customer.io webhooks",
            "/health": "GET - Health check",
            "/": "GET - This message"
        }
    })


def save_raw_webhook_data(event_data):
    """
    Save raw webhook data for audit trail.
    
    In production, this would save to Delta Lake.
    For now, just log it.
    """
    try:
        raw_event = {
            "received_at": datetime.now().isoformat(),
            "event_id": event_data.get("event_id"),
            "object_type": event_data.get("object_type"),
            "metric": event_data.get("metric"),
            "timestamp": event_data.get("timestamp"),
            "event_data": json.dumps(event_data)
        }
        
        logger.info(f"Raw webhook data: {json.dumps(raw_event)}")
        
        # In production with Spark:
        # df = spark.createDataFrame([raw_event])
        # df.write.mode("append").partitionBy("date_partition").format("delta").save(path)
        
    except Exception as e:
        logger.error(f"Error saving raw webhook data: {e}")


if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Customer.io webhook processor on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
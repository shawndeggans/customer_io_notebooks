# Customer.io Webhook Processor - Databricks App

This Databricks App receives and processes Customer.io reporting webhooks, storing the data in Delta Lake for analytics.

## Features

- **Webhook Authentication**: HMAC-SHA256 signature verification per Customer.io spec
- **Event Processing**: Handles all 7 Customer.io event types (email, SMS, push, in-app, customer, Slack, webhook)
- **Delta Lake Storage**: Structured storage for analytics (when deployed to Databricks)
- **Health Monitoring**: Health check endpoint for monitoring
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## Local Development

### Prerequisites

- Python 3.8+
- pip or uv package manager

### Setup

1. Install dependencies:
```bash
cd databricks_app
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export CUSTOMERIO_WEBHOOK_SECRET="your_webhook_signing_key"
export FLASK_ENV=development
```

3. Run the app:
```bash
python app.py
```

The app will start on http://localhost:5000

### Testing

1. Run the test script:
```bash
export CUSTOMERIO_WEBHOOK_SECRET="test_webhook_secret"
python test_webhook.py
```

2. Test with curl:
```bash
# Health check
curl http://localhost:5000/health

# Root endpoint
curl http://localhost:5000/
```

## Databricks Deployment

### Prerequisites

- Databricks workspace with Apps enabled
- Databricks CLI configured
- Customer.io webhook signing secret stored in Databricks secrets

### Deployment Steps

1. Create webhook secret in Databricks:
```bash
databricks secrets create-scope --scope customerio
databricks secrets put --scope customerio --key webhook_signing_key
```

2. Deploy the app:
```bash
databricks apps deploy --config databricks.yml
```

3. Get the app URL:
```bash
databricks apps list
```

### Configuration

The app uses the following environment variables:

- `CUSTOMERIO_WEBHOOK_SECRET`: Webhook signing key (required)
- `FLASK_ENV`: Flask environment (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)
- `DELTA_BASE_PATH`: Base path for Delta tables (default: /mnt/customerio)
- `DATABRICKS_HOST`: Databricks host (for production)
- `DATABRICKS_TOKEN`: Databricks token (for production)

## API Endpoints

### POST /webhook/customerio

Receives Customer.io webhook events.

**Headers:**
- `X-CIO-Signature`: HMAC signature (required)
- `X-CIO-Timestamp`: Unix timestamp (required)
- `Content-Type`: application/json

**Response:**
- 200 OK: Event processed successfully
- 400 Bad Request: Invalid headers or payload
- 401 Unauthorized: Invalid signature
- 500 Internal Server Error: Processing error

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "service": "customerio-webhook-processor",
  "version": "1.0.0"
}
```

### GET /

Service information endpoint.

**Response:**
```json
{
  "service": "Customer.io Webhook Processor",
  "endpoints": {
    "/webhook/customerio": "POST - Receive Customer.io webhooks",
    "/health": "GET - Health check",
    "/": "GET - This message"
  }
}
```

## Event Types Supported

### Email Events
- drafted, attempted, sent, delivered, opened, clicked, converted
- unsubscribed, bounced, dropped, spammed, failed, undeliverable

### Customer Events
- subscribed, unsubscribed, cio_subscription_preferences_changed

### SMS Events
- drafted, attempted, sent, delivered, clicked, converted, bounced, failed

### Push Events
- drafted, attempted, delivered, sent, opened, clicked, converted
- bounced, dropped, failed, undeliverable

### In-App Events
- drafted, attempted, sent, opened, clicked, converted, failed

### Slack Events
- drafted, attempted, sent, clicked, failed, dropped

### Webhook Events
- drafted, attempted, sent, clicked, failed, dropped

## Monitoring

### Logs

The app logs all webhook events with the following information:
- Event type and metric
- Event ID
- Processing status
- Error details (if any)

### Metrics (when deployed to Databricks)

Monitor the following Delta tables:
- `webhook_landing/`: Raw webhook data
- `processed_events/email_events`: Processed email events
- `processed_events/customer_events`: Processed customer events
- `processed_events/sms_events`: Processed SMS events
- etc.

## Troubleshooting

### Common Issues

1. **401 Unauthorized**: Check webhook signing key
2. **400 Bad Request**: Verify payload format and headers
3. **500 Internal Server Error**: Check logs for processing errors

### Debug Mode

Enable debug logging:
```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
```

## Security

- All webhooks are authenticated using HMAC-SHA256
- Timestamp validation prevents replay attacks (5-minute window)
- Secrets are stored in Databricks secret scope
- No sensitive data is logged
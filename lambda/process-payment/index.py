import json
import boto3
import random
import uuid
from datetime import datetime
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

EVENT_BUS = os.environ["EVENT_BUS"]

eventbridge = boto3.client("events")

def lambda_handler(event, context):

    try:
        order = event["detail"]

        order_id = order["order_id"]

        payment_status = "SUCCESS" if random.random() > 0.2 else "FAILED"

        if payment_status == "SUCCESS":
            event_type = "PaymentSucceeded"
        else:
            event_type = "PaymentFailed"
        
        logger.info(f"Payment status for {order_id}: {payment_status}")

        payment_id = str(uuid.uuid4())

        payment = {
            "payment_id": payment_id,
            "order_id": order_id,
            "status": payment_status,
            "created_at": datetime.utcnow().isoformat(),
            "processed_at": datetime.utcnow().isoformat()
        }

        eventbridge.put_events(
            Entries=[
                {
                    "Source": "ecommerce.payments",
                    "DetailType": event_type,
                    "Detail": json.dumps(payment),
                    "EventBusName": EVENT_BUS
                }
            ]
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "order_id": order_id,
                "payment_status": payment_status
            })
        }

    except Exception as e:
        logger.error(f"Error processing payment: {str(e)}")

        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Internal server error"})
        }

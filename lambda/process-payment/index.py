import json
import boto3
import random
from datetime import datetime

eventbridge = boto3.client("events")

def lambda_handler(event, context):

    order = event["detail"]

    order_id = order["order_id"]

    payment_status = "SUCCESS" if random.random() > 0.2 else "FAILED"

    if payment_status == "SUCCESS":
        event_type = "PaymentSucceeded"
    else:
        event_type = "PaymentFailed"

    eventbridge.put_events(
        Entries=[
            {
                "Source": "ecommerce.payments",
                "DetailType": event_type,
                "Detail": json.dumps({
                    "order_id": order_id,
                    "status": payment_status,
                    "processed_at": datetime.utcnow().isoformat()
                }),
                "EventBusName": "default"
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
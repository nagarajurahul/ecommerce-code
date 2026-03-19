import json
import boto3
from datetime import datetime
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# INVENTORY_TABLE=os.environ["INVENTORY_TABLE"]
EVENT_BUS = os.environ["EVENT_BUS"]

dynamodb = boto3.resource("dynamodb")
# inventory_table = dynamodb.Table(INVENTORY_TABLE)
eventbridge = boto3.client("events")

def lambda_handler(event, context):

    # EventBridge already sends dict → no json.loads needed
    detail = event["detail"]

    order_id = detail["order_id"]

    # IMPORTANT: you need items in event → ensure previous lambda sends it
    items = detail.get("items", [])

    logger.info(f"Updating inventory for order {order_id}")

    for item in items:
        product_id = item["product_id"]
        quantity = item["quantity"]

        # try:
        #     inventory_table.update_item(
        #         Key={"product_id": product_id},
        #         UpdateExpression="SET stock = stock - :qty",
        #         ConditionExpression="stock >= :qty",
        #         ExpressionAttributeValues={
        #             ":qty": quantity
        #         }
        #     )

        # except Exception as e:
        #     logger.error(f"Inventory update failed for {product_id}: {str(e)}")
        #     raise e

    # Emit next event
    eventbridge.put_events(
        Entries=[
            {
                "Source": "ecommerce.inventory",
                "DetailType": "InventoryUpdated",
                "Detail": json.dumps({
                    "order_id": order_id,
                    "updated_at": datetime.utcnow().isoformat()
                }),
                "EventBusName": EVENT_BUS
            }
        ]
    )

    return {
        "statusCode": 200,
        "body": json.dumps({
            "order_id": order_id,
            "status": "INVENTORY_UPDATED"
        })
    }
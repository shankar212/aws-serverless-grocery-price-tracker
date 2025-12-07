import boto3
from decimal import Decimal

sns = boto3.client("sns")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("GroceryPrices")

TOPIC_ARN = "arn:aws:sns:ap-south-1:248189910762:PriceDropTopic"


def lambda_handler(event, context):
    for record in event["Records"]:

        # Only INSERT triggers for your scraper
        if record["eventName"] != "INSERT":
            continue

        new = record["dynamodb"].get("NewImage")
        if not new:
            continue

        item = new["item"]["S"]
        new_price = float(Decimal(new["price"]["N"]))

        # Query existing items for the same product
        response = table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key("item").eq(item)
        )

        items = response.get("Items", [])

        # No previous price → skip alert
        if len(items) < 2:
            continue

        # Sort by timestamp descending → latest first
        items_sorted = sorted(items, key=lambda x: x["timestamp"], reverse=True)

        latest = items_sorted[0]
        previous = items_sorted[1]

        previous_price = float(previous["price"])

        # Trigger alert only if price dropped
        if new_price < previous_price:
            diff = round(previous_price - new_price, 2)

            message = (
                f"🔥 Price Drop Alert!\n\n"
                f"Item: {item}\n"
                f"Old Price: ₹{previous_price}\n"
                f"New Price: ₹{new_price}\n"
                f"Drop: ₹{diff}"
            )

            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=message,
                Subject="🔥 Grocery Price Drop Alert"
            )

    return {"status": "done"}

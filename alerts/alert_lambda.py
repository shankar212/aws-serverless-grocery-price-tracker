import boto3
from decimal import Decimal

sns = boto3.client("sns")

TOPIC_ARN = "arn:aws:sns:ap-south-1:248189910762:PriceDropTopic"

def lambda_handler(event, context):
    for record in event["Records"]:

        # We only want MODIFY events (updates)
        if record["eventName"] != "MODIFY":
            continue

        old_data = record["dynamodb"]["OldImage"]
        new_data = record["dynamodb"]["NewImage"]

        item = new_data["item"]["S"]
        old_price = float(Decimal(old_data["price"]["N"]))
        new_price = float(Decimal(new_data["price"]["N"]))

        # Trigger alert only when price DROPS (new_price < old_price)
        if new_price < old_price:
            message = f"Price Drop Alert!\n{item} is now ₹{new_price}"
            sns.publish(
                TopicArn=TOPIC_ARN,
                Message=message,
                Subject="🔥 Grocery Price Drop Alert"
            )

    return {"status": "done"}

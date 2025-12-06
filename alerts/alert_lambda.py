import boto3
from decimal import Decimal

sns = boto3.client("sns")

# your email notification topic ARN will be added later
TOPIC_ARN = "arn:aws:sns:ap-south-1:248189910762:PriceDropTopic"

def lambda_handler(event, context):
    for record in event["Records"]:
        if record["eventName"] == "INSERT":
            new = record["dynamodb"]["NewImage"]

            item = new["item"]["S"]
            price = float(Decimal(new["price"]["N"]))

            # Example threshold: Send alert if price < 100
            if price < 100:
                message = f"Price Drop Alert!\n{item} is now ₹{price}"
                sns.publish(
                    TopicArn=TOPIC_ARN,
                    Message=message,
                    Subject="🔥 Price Drop Alert"
                )

    return {"status": "done"}

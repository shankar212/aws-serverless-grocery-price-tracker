import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('GroceryPrices')

def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    return obj

def lambda_handler(event, context):
    response = table.scan()
    items = response.get("Items", [])
    latest = {}

    for item in items:
        name = item["item"]
        timestamp = item["timestamp"]

        if name not in latest or timestamp > latest[name]["timestamp"]:
            latest[name] = item

    return {
        "statusCode": 200,
        "body": json.dumps(decimal_to_float(latest)),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }

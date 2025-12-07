import re
import requests
import boto3
import time
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('GroceryPrices')

PRODUCTS = {
    "Daawat Basmati Rice 5kg": 40075197,
    "Aashirvaad Atta 10kg": 126906,
    "Fortune Sunlite Sunflower Oil 500ml": 274145,
    "Tata Salt 1kg": 241600,
    "BB Popular Sugar 5kg": 30005417,
    "Britannia Milk Bikis 500g": 40197802,
    "Nandini Goodlife Milk 1L": 100285703,
    "Surf Excel Matic Front Load 2kg": 228623,
    "Red Label Tea 1kg": 102871,
    "Maggi Masala 560g": 266109
}

def extract_price(html):
    # First try offer_sp
    match = re.search(r'"offer_sp"\s*:\s*([0-9]+\.[0-9]+)', html)
    
    # Fallback: prim_price
    if not match:
        match = re.search(r'"prim_price":\{"sp":"([0-9]+\.[0-9]+)"', html)

    if match:
        # ALWAYS convert to Decimal to avoid DynamoDB float errors
        return Decimal(match.group(1))
    
    return None

def lambda_handler(event, context):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }

    results = {}

    for item, product_id in PRODUCTS.items():
        url = f"https://www.bigbasket.com/pd/{product_id}/"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            html = response.text
        except Exception as e:
            results[item] = f"Request failed: {str(e)}"
            continue

        price = extract_price(html)

        if price is None:
            results[item] = "Price not found"
            continue

        # SAVE TO DYNAMODB
        table.put_item(
            Item={
                "item": item,
                "timestamp": datetime.utcnow().isoformat(),
                "price": price,         # Decimal ✔
                "store": "BigBasket"
            }
        )

        results[item] = float(price)

        time.sleep(1)  # Prevent rate limiting

    return {
        "message": "Scraper completed successfully",
        "results": results
    }

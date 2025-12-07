# 🧪 Lambda Alert Test Instructions

Great --- your **alert Lambda is successfully updated**.\
Let's **test it thoroughly** to confirm email alerts are working!

------------------------------------------------------------------------

## ✅ STEP 1 --- Insert a Test Item (Previous Price)

Run:

``` bash
aws dynamodb put-item --table-name GroceryPrices ^
  --item "{\"item\":{\"S\":\"alertTest\"},\"timestamp\":{\"S\":\"2025-12-07T09:35:00Z\"},\"price\":{\"N\":\"200\"},\"store\":{\"S\":\"TestStore\"}}" ^
  --region ap-south-1
```

This creates the **first price entry** --- no alert should fire yet.

------------------------------------------------------------------------

## ✅ STEP 2 --- Insert a New LOWER Price (Trigger Alert)

``` bash
aws dynamodb put-item --table-name GroceryPrices ^
  --item "{\"item\":{\"S\":\"alertTest\"},\"timestamp\":{\"S\":\"2025-12-07T09:36:00Z\"},\"price\":{\"N\":\"150\"},\"store\":{\"S\":\"TestStore\"}}" ^
  --region ap-south-1
```

This will trigger `alertLambda`.

------------------------------------------------------------------------

## 🔔 Expected Email Alert

You should receive:

> 🔥 **Price Drop Alert!**\
> `alertTest` dropped by **₹50**\
> Old Price: **₹200**\
> New Price: **₹150**

------------------------------------------------------------------------

## 📘 STEP 3 --- View Lambda Logs (Optional)

``` bash
aws logs tail /aws/lambda/priceDropAlert --since 5m
```

Look for:

    Price dropped: sending SNS alert

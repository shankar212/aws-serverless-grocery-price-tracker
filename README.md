# 🛒 **AWS Serverless Grocery Price Monitoring System**

Track grocery prices across online stores, store them in DynamoDB, visualize them in a dashboard, and receive **email alerts** when prices drop — fully automated using AWS.

![AWS](https://img.shields.io/badge/AWS-FF9900?style=flat&logo=amazonaws&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9+-3776ab?style=flat&logo=python&logoColor=white)
![Serverless](https://img.shields.io/badge/Serverless-FD5750?style=flat&logo=serverless&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ⭐ **Features**

### ✅ **1. Automatic Price Scraping (BigBasket, Amazon, etc.)**

* AWS Lambda scrapes product prices automatically.
* Uses BeautifulSoup4 for HTML parsing.
* Stores results in DynamoDB with timestamps.
* Runs daily via EventBridge cron schedule.

### ✅ **2. Serverless Storage & History**

* DynamoDB table **GroceryPrices** stores:
  * Item name
  * Current price
  * Store source
  * Timestamp of price update
  * Historical price tracking

### ✅ **3. Static Dashboard (S3 + CloudFront)**

* Shows latest prices visually in an interactive table.
* Hosted on CloudFront for global, fast access.
* Real-time price comparison across stores.
* Fully responsive design.

### ✅ **4. Real-Time Price-Drop Email Alerts**

* DynamoDB Streams detect price changes automatically.
* Triggers Lambda function instantly.
* Lambda publishes to SNS topic.
* You receive **email alert** in seconds when prices drop.
<img width="1136" height="403" alt="image" src="https://github.com/user-attachments/assets/ba4424ae-9f2c-4d5e-8a6a-b5776737be82" />

### ✅ **5. 100% Serverless Architecture- No servers to manage**

* No EC2 instances, no servers to maintain.
* Pay only for actual usage.
* Scales automatically.
* Near-zero management overhead.

---

## 🏗️ **Architecture Diagram**

```
            +---------------------+
            | EventBridge (Cron)  |
            |  Daily Schedule     |
            | (e.g., 9 AM UTC)    |
            +----------+----------+
                       |
                       v
              +--------------------+
              | Lambda: Scraper    |
              | scrapePrices()     |
              +-------+------------+
                      |
                      | Extracts prices
                      | from web sources
                      |
                      v
            +----------------------+
            | DynamoDB Table       |
            | GroceryPrices        |
            | - item (PK)          |
            | - store (SK)         |
            | - price              |
            | - timestamp          |
            +----------+-----------+
                       |
        DynamoDB Stream Event
        (NEW_AND_OLD_IMAGES)
                       |
                       v
              +-------------------+
              | Lambda: Alerts    |
              | priceDropAlert()  |
              +---------+---------+
                        |
                (if price < threshold)
                        |
                        v
              +-------------------+
              | SNS Email Topic   |
              +-------------------+
                        |
                        v
              ✉️ Email to subscriber


   Dashboard Infrastructure
   ┌──────────────────────┐
   │   S3 Static Site     │
   │   (dashboard/)       │
   │  - index.html        │
   │  - main.js           │
   │  - styles.css        │
   └──────────┬───────────┘
              │
              v
   ┌──────────────────────┐
   │ CloudFront CDN       │
   │ (Global Distribution)│
   └──────────┬───────────┘
              │
              v
   https://d123456.cloudfront.net
```

---

## 📦 **Project Structure**

```
grocery-price-tracker/
│
├── scraper/
│   ├── lambda_function.py      # Main scraper lambda
│   ├── requirements.txt        # Python dependencies
│   ├── output.json             # Sample output
│   └── [AWS SDK libraries]     # boto3, botocore, etc.
│
├── alerts/
│   ├── alert_lambda.py         # Price drop alert lambda
│   └── test_item.json          # Test data for alerts
│
├── api/
│   └── get_prices.py           # API Gateway handler (optional)
│
├── dashboard/
│   ├── index.html              # Dashboard UI
│   ├── styles.css              # Styling
│   └── main.js                 # Frontend logic
│
└── README.md                   # This file
```

---

## 🚀 **How the System Works**

### **1️⃣ Scraping Prices (Daily)**

**EventBridge Rule:**
```
- Schedule: cron(0 9 * * ? *)  [Daily at 6 AM UTC]
- Target: Lambda → scrapePrices
```

**Scraper Lambda Process:**
1. Makes HTTP requests to BigBasket, Amazon, etc.
2. Uses BeautifulSoup4 to extract HTML.
3. Parses product name, price, and store.
4. Transforms data to:

```json
{
  "item": "Daawat Basmati Rice 5kg",
  "store": "BigBasket",
  "price": 327.6,
  "timestamp": "2025-12-07T09:30:00Z"
}
```

5. Inserts into DynamoDB table.

**DynamoDB Item Structure:**
```
PrimaryKey: item (String)       → "Daawat Basmati Rice 5kg"
SortKey:    store (String)      → "BigBasket"
Attributes: 
  - price (Number)              → 327.6
  - timestamp (String)          → "2025-12-07T09:30:00Z"
  - url (String)                → "https://..."
  - currency (String)           → "INR"
```

---

### **2️⃣ DynamoDB Streams Detect Changes**

When a price update occurs, DynamoDB Streams captures:

```
{
  "eventID": "xyz123",
  "eventName": "INSERT" or "MODIFY",
  "dynamodb": {
    "OldImage": { "item": {...}, "price": 330 },
    "NewImage": { "item": {...}, "price": 327 }
  }
}
```

**Stream Configuration:**
- View Type: `NEW_AND_OLD_IMAGES`
- Enabled: ✅ Yes
- Destination: Lambda Alert Function

---

### **3️⃣ Alert Lambda Sends Email**

When `NewImage.price < OldImage.price`:

```python
message = f"""
Price Drop Alert! 🔥

{item} just dropped!

Old Price: ₹{old_price}
New Price: ₹{new_price}
Saving: ₹{old_price - new_price}

Store: {store}
Updated: {timestamp}
"""
```

**SNS Publishing:**
```python
sns.publish(
    TopicArn="arn:aws:sns:ap-south-1:ACCOUNT:PriceDropTopic",
    Message=message,
    Subject="🔥 Price Drop Alert"
)
```

You receive the email instantly!

---

### **4️⃣ Dashboard Displays Latest Prices**

**Static HTML/JS Dashboard:**
1. Hosted in S3 bucket
2. Distributed via CloudFront
3. JavaScript fetches data from DynamoDB or API Gateway
4. Displays in interactive table

**Sample Dashboard Table:**

| Item                      | Store    | Price   | Updated         | Trend |
|---------------------------|----------|---------|-----------------|-------|
| Daawat Basmati Rice 5kg   | BigBasket| ₹327.60 | 2025-12-07 9:30 | ↓ -₹2.40 |
| Tata Salt 1kg             | Amazon   | ₹28.50  | 2025-12-07 9:25 | → No change |
| Sunflower Oil 1L          | BigBasket| ₹142.00 | 2025-12-06 10:15| ↑ +₹5.00 |

---

## 🛠️ **AWS Services & Configuration**

| Service              | Component                           | Purpose                     |
| -------------------- | ----------------------------------- | --------------------------- |
| **Lambda**           | `scrapePrices`                      | Runs scraper (triggered by EventBridge) |
| **Lambda**           | `priceDropAlert`                    | Sends email alerts          |
| **DynamoDB**         | `GroceryPrices` table               | Stores price history        |
| **DynamoDB Streams** | `GroceryPrices` stream              | Detects price change events |
| **SNS**              | `PriceDropTopic`                    | Email notification topic    |
| **EventBridge**      | Scraper cron rule                   | Daily scraping schedule     |
| **S3**               | `grocery-dashboard-*`               | Hosts dashboard HTML/CSS/JS |
| **CloudFront**       | `d*.cloudfront.net`                 | CDN for dashboard           |
| **CloudWatch**       | Logs for all Lambdas                | Debugging & monitoring      |

### **DynamoDB Table Details**

```
Table Name: GroceryPrices
Region: ap-south-1
Billing Mode: PAY_PER_REQUEST (on-demand)

Primary Key:
  - Partition Key (PK): item (String)
  - Sort Key (SK): store (String)

Attributes:
  - price (Number)
  - timestamp (String, ISO-8601)
  - url (String, optional)
  - currency (String)

Streams:
  - View Type: NEW_AND_OLD_IMAGES
  - Lambda Consumer: priceDropAlert
```

---

## 📋 **Setup Instructions**

### **Prerequisites**

* AWS Account with sufficient permissions
* AWS CLI configured with credentials
* Python 3.9+
* pip or conda

### **Step 1: Create DynamoDB Table**

```bash
aws dynamodb create-table \
  --table-name GroceryPrices \
  --attribute-definitions \
    AttributeName=item,AttributeType=S \
    AttributeName=store,AttributeType=S \
  --key-schema \
    AttributeName=item,KeyType=HASH \
    AttributeName=store,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
  --region ap-south-1
```

### **Step 2: Create SNS Topic**

```bash
aws sns create-topic \
  --name PriceDropTopic \
  --region ap-south-1

# Subscribe email
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-south-1:ACCOUNT_ID:PriceDropTopic \
  --protocol email \
  --notification-endpoint your-email@example.com \
  --region ap-south-1
```

Confirm subscription via email link.

### **Step 3: Package & Deploy Scraper Lambda**

```bash
cd scraper

# Install dependencies
pip install -r requirements.txt -t .

# Create deployment package
Compress-Archive -Path * -DestinationPath ../scraper.zip -Force

cd ..

# Create Lambda function
aws lambda create-function \
  --function-name scrapePrices \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://scraper.zip \
  --timeout 60 \
  --region ap-south-1
```

### **Step 4: Package & Deploy Alert Lambda**

```bash
cd alerts

# Create deployment package
Compress-Archive -Path alert_lambda.py -DestinationPath ../alert.zip -Force

cd ..

# Create Lambda function
aws lambda create-function \
  --function-name priceDropAlert \
  --runtime python3.9 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler alert_lambda.lambda_handler \
  --zip-file fileb://alert.zip \
  --timeout 30 \
  --region ap-south-1

# Add environment variable
aws lambda update-function-configuration \
  --function-name priceDropAlert \
  --environment Variables="{TOPIC_ARN=arn:aws:sns:ap-south-1:ACCOUNT_ID:PriceDropTopic}" \
  --region ap-south-1
```

### **Step 5: Create EventBridge Rule**

```bash
# Create rule
aws events put-rule \
  --name DailyPriceScraper \
  --schedule-expression "cron(0 9 * * ? *)" \
  --region ap-south-1

# Add Lambda as target
aws events put-targets \
  --rule DailyPriceScraper \
  --targets "Id"="1","Arn"="arn:aws:lambda:ap-south-1:ACCOUNT_ID:function:scrapePrices" \
  --region ap-south-1

# Grant EventBridge permission to invoke Lambda
aws lambda add-permission \
  --function-name scrapePrices \
  --statement-id AllowEventBridgeInvoke \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:ap-south-1:ACCOUNT_ID:rule/DailyPriceScraper \
  --region ap-south-1
```

### **Step 6: Create DynamoDB Stream → Lambda Trigger**

```bash
# Get Stream ARN
STREAM_ARN=$(aws dynamodb describe-table \
  --table-name GroceryPrices \
  --query 'Table.LatestStreamArn' \
  --output text \
  --region ap-south-1)

# Create Event Source Mapping
aws lambda create-event-source-mapping \
  --event-source-arn $STREAM_ARN \
  --function-name priceDropAlert \
  --enabled \
  --batch-size 1 \
  --starting-position LATEST \
  --region ap-south-1

# Grant Lambda permission to read from stream
aws lambda add-permission \
  --function-name priceDropAlert \
  --statement-id DynamoDBStreamAccess \
  --action lambda:InvokeFunction \
  --principal dynamodb.amazonaws.com \
  --region ap-south-1
```

### **Step 7: Deploy Dashboard to S3 + CloudFront**

```bash
# Create S3 bucket
aws s3 mb s3://grocery-dashboard-$(date +%s) --region ap-south-1

# Upload dashboard files
aws s3 sync dashboard/ s3://grocery-dashboard-BUCKET_NAME/ --region ap-south-1

# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://distribution-config.json
```

(See CloudFront setup in Advanced Configuration section below)

---

## 🔑 **IAM Permissions Required**

### **Lambda Execution Role Policy**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:ACCOUNT_ID:table/GroceryPrices"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetRecords",
        "dynamodb:GetShardIterator",
        "dynamodb:DescribeStream",
        "dynamodb:ListStreams",
        "dynamodb:ListShards"
      ],
      "Resource": "arn:aws:dynamodb:ap-south-1:ACCOUNT_ID:table/GroceryPrices/stream/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:ap-south-1:ACCOUNT_ID:PriceDropTopic"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:ap-south-1:ACCOUNT_ID:log-group:/aws/lambda/*"
    }
  ]
}
```

### **S3 Bucket Policy (Dashboard)**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::grocery-dashboard-BUCKET_NAME/*"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::grocery-dashboard-BUCKET_NAME/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

---

## 🧪 **Testing the System**

### **✔️ Test 1: Manual DynamoDB Insert**

Insert a test item with low price:

```bash
aws dynamodb put-item \
  --table-name GroceryPrices \
  --item '{
    "item": {"S": "Test Rice 5kg"},
    "store": {"S": "TestStore"},
    "price": {"N": "99.50"},
    "timestamp": {"S": "2025-12-07T10:00:00Z"}
  }' \
  --region ap-south-1
```

**Expected Result:**
* Check CloudWatch logs for `priceDropAlert` Lambda
* Email should arrive in inbox with alert

### **✔️ Test 2: Trigger Scraper Lambda Manually**

```bash
aws lambda invoke \
  --function-name scrapePrices \
  --region ap-south-1 \
  response.json

cat response.json
```

**Expected Result:**
* Items inserted into DynamoDB
* CloudWatch logs show successful execution
* No errors in response

### **✔️ Test 3: Check Dashboard**

```bash
# Get your CloudFront URL
aws cloudfront list-distributions --region ap-south-1 | grep DomainName

# Open in browser
# https://d<random>.cloudfront.net
```

**Expected Result:**
* Loads successfully
* Shows product table
* Displays prices and timestamps

### **✔️ Test 4: Verify Email Alert System**

Update price to lower value:

```bash
aws dynamodb put-item \
  --table-name GroceryPrices \
  --item '{
    "item": {"S": "Test Rice 5kg"},
    "store": {"S": "TestStore"},
    "price": {"N": "85.00"},
    "timestamp": {"S": "2025-12-07T10:05:00Z"}
  }' \
  --region ap-south-1
```

**Expected Result:**
* DynamoDB Stream triggers alert Lambda
* Email arrives: "Test Rice 5kg dropped from ₹99.50 to ₹85.00"

---

## 📊 **Monitoring & Logging**

### **CloudWatch Logs**

View logs for each Lambda:

```bash
# Scraper Lambda logs
aws logs tail /aws/lambda/scrapePrices --follow --region ap-south-1

# Alert Lambda logs
aws logs tail /aws/lambda/priceDropAlert --follow --region ap-south-1
```

### **DynamoDB Metrics**

```bash
# Check consumed capacity
aws cloudwatch get-metric-statistics \
  --namespace AWS/DynamoDB \
  --metric-name ConsumedWriteCapacityUnits \
  --dimensions Name=TableName,Value=GroceryPrices \
  --statistics Sum \
  --start-time 2025-12-07T00:00:00Z \
  --end-time 2025-12-08T00:00:00Z \
  --period 3600 \
  --region ap-south-1
```

---

## 💰 **Cost Estimation (Monthly)**

| Service         | Usage              | Cost      |
|-----------------|-------------------|-----------|
| **DynamoDB**    | ~1000 writes/month | ~$1.00    |
| **Lambda**      | ~50 invocations    | ~$0.20    |
| **S3**          | ~1GB storage       | ~$0.02    |
| **SNS**         | 30 emails/month    | ~$0.10    |
| **CloudFront**  | 1GB transfer       | ~$0.10    |
| **Total**       | -                  | ~$1.50    |

Very cost-effective! ✅

---

## 🔒 **Security Best Practices**

### ✅ **1. Secrets Management**

Store API keys and credentials in AWS Secrets Manager:

```bash
aws secretsmanager create-secret \
  --name grocery-tracker-credentials \
  --secret-string '{"api_key":"xxx","password":"yyy"}' \
  --region ap-south-1
```

Retrieve in Lambda:

```python
import boto3
import json

secrets = boto3.client('secretsmanager')
response = secrets.get_secret_value(SecretId='grocery-tracker-credentials')
credentials = json.loads(response['SecretString'])
```

### ✅ **2. VPC Isolation** (Optional)

Deploy Lambdas in VPC for isolated network:

```bash
aws lambda update-function-configuration \
  --function-name scrapePrices \
  --vpc-config SubnetIds=subnet-xxx,SecurityGroupIds=sg-xxx \
  --region ap-south-1
```

### ✅ **3. S3 Bucket Encryption**

Enable default encryption:

```bash
aws s3api put-bucket-encryption \
  --bucket grocery-dashboard-BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }' \
  --region ap-south-1
```

### ✅ **4. CloudWatch Alarms**

Alert on Lambda errors:

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name PriceScraperErrors \
  --alarm-description "Alert if scraper Lambda fails" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 1 \
  --comparison-operator GreaterThanOrEqualToThreshold \
  --evaluation-periods 1 \
  --dimensions Name=FunctionName,Value=scrapePrices \
  --alarm-actions arn:aws:sns:ap-south-1:ACCOUNT_ID:PriceDropTopic \
  --region ap-south-1
```

---

## 🚀 **Deployment via CloudFormation (Optional)**

For infrastructure-as-code, use CloudFormation template:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Grocery Price Tracker Serverless Architecture'

Resources:
  GroceryPricesTable:
    Type: AWS::DynamoDB::Table
    Properties:
      TableName: GroceryPrices
      BillingMode: PAY_PER_REQUEST
      AttributeDefinitions:
        - AttributeName: item
          AttributeType: S
        - AttributeName: store
          AttributeType: S
      KeySchema:
        - AttributeName: item
          KeyType: HASH
        - AttributeName: store
          KeyType: RANGE
      StreamSpecification:
        StreamViewType: NEW_AND_OLD_IMAGES

  PriceDropTopic:
    Type: AWS::SNS::Topic
    Properties:
      TopicName: PriceDropTopic

  ScraperLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: DynamoDBAccess
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: dynamodb:PutItem
                Resource: !GetAtt GroceryPricesTable.Arn

  AlertLambdaRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: lambda.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
      Policies:
        - PolicyName: SNSPublish
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: sns:Publish
                Resource: !Ref PriceDropTopic

  DailyScraperRule:
    Type: AWS::Events::Rule
    Properties:
      ScheduleExpression: cron(0 9 * * ? *)
      State: ENABLED

Outputs:
  GroceryPricesTableName:
    Value: !Ref GroceryPricesTable
    
  PriceDropTopicArn:
    Value: !Ref PriceDropTopic
```

Deploy:

```bash
aws cloudformation create-stack \
  --stack-name grocery-tracker \
  --template-body file://cloudformation.yaml \
  --capabilities CAPABILITY_IAM \
  --region ap-south-1
```

---

## 📈 **Future Enhancements**

### 🟦 **Phase 2: Advanced Features**

- [ ] Add more product scrapers (Flipkart, Blinkit, Swiggy Instamart)
- [ ] Multi-store price comparison
- [ ] Historical price graphs (using Amazon QuickSight or ChartJS)
- [ ] User authentication (Cognito)
- [ ] User-specific alert preferences
- [ ] REST API (API Gateway + Lambda)
- [ ] Mobile app (React Native / Flutter)
- [ ] Telegram / WhatsApp notifications
- [ ] Machine learning price predictions
- [ ] Scheduled price reports (weekly digest)

### 🟦 **Phase 3: Production Hardening**

- [ ] Rate limiting & DDoS protection (WAF)
- [ ] Advanced caching (ElastiCache)
- [ ] Multi-region deployment
- [ ] Disaster recovery & backups
- [ ] Performance optimization (Lambda layers)
- [ ] Cost optimization (Spot instances, Reserved capacity)

---

## 🧑‍💻 **Development Workflow**

### **Local Testing**

```bash
# Install dependencies locally
pip install boto3 beautifulsoup4 requests

# Test scraper
python scraper/lambda_function.py

# Test alert
python alerts/alert_lambda.py
```

### **Updating Lambda Functions**

```bash
# Scraper update
cd scraper
pip install -r requirements.txt -t .
Compress-Archive -Path * -DestinationPath ../scraper.zip -Force
aws lambda update-function-code \
  --function-name scrapePrices \
  --zip-file fileb://../scraper.zip \
  --region ap-south-1

# Alert update
cd ../alerts
Compress-Archive -Path alert_lambda.py -DestinationPath ../alert.zip -Force
aws lambda update-function-code \
  --function-name priceDropAlert \
  --zip-file fileb://../alert.zip \
  --region ap-south-1
```

### **Updating Dashboard**

```bash
aws s3 sync dashboard/ s3://grocery-dashboard-BUCKET_NAME/ \
  --delete \
  --region ap-south-1

# Invalidate CloudFront cache
aws cloudfront create-invalidation \
  --distribution-id DISTRIBUTION_ID \
  --paths "/*" \
  --region ap-south-1
```

---

## 🐛 **Troubleshooting**

### **Problem: Alerts not sending**

1. Check SNS topic subscription is confirmed
2. Verify email address in subscription
3. Check Lambda logs:
   ```bash
   aws logs tail /aws/lambda/priceDropAlert --follow --region ap-south-1
   ```
4. Verify IAM permissions for SNS:Publish

### **Problem: Scraper not running**

1. Check EventBridge rule is enabled:
   ```bash
   aws events describe-rule --name DailyPriceScraper --region ap-south-1
   ```
2. Verify Lambda execution role has DynamoDB access
3. Check Lambda timeout (should be ≥60 seconds)
4. Review CloudWatch logs for errors

### **Problem: Dashboard shows no data**

1. Verify DynamoDB table has items:
   ```bash
   aws dynamodb scan --table-name GroceryPrices --region ap-south-1
   ```
2. Check S3 bucket permissions
3. Verify CloudFront distribution is active
4. Clear browser cache and reload

### **Problem: High AWS costs**

1. Review DynamoDB consumed capacity
2. Check for Lambda throttling or excessive errors
3. Review S3 transfer costs (use CloudFront caching)
4. Consider reserved capacity for predictable workloads

---

## 📚 **API Reference**

### **DynamoDB Table Schema**

```
GET /GroceryPrices?item=Rice
→ Returns latest price for Rice across all stores

POST /GroceryPrices
{
  "item": "Daawat Rice 5kg",
  "store": "BigBasket",
  "price": 327.60,
  "timestamp": "2025-12-07T09:30:00Z"
}
→ Inserts new price record
```

### **Lambda Environment Variables**

**Scraper Lambda:**
```
DYNAMODB_TABLE = GroceryPrices
REGION = ap-south-1
LOG_LEVEL = INFO
```

**Alert Lambda:**
```
TOPIC_ARN = arn:aws:sns:ap-south-1:ACCOUNT_ID:PriceDropTopic
PRICE_DROP_THRESHOLD = 100 (rupees)
```

---

## 📄 **License**

MIT License – free to use, modify, and distribute.

```
Copyright (c) 2025 Shankar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🌟 **Why This Project Matters**

### **For Your Resume:**

✅ **Real-world cloud engineering** – End-to-end serverless system  
✅ **AWS expertise** – Lambda, DynamoDB, SNS, EventBridge, S3, CloudFront  
✅ **Full-stack architecture** – Backend automation + frontend dashboard  
✅ **Event-driven design** – Streams, triggers, async processing  
✅ **Scalability** – Handles thousands of items effortlessly  
✅ **Cost optimization** – Serverless = pay per use  

### **For Interviews:**

Great for discussing:
* How would you scale this to 1M items?
* How would you add user authentication?
* How would you optimize costs?
* What happens if the scraper fails?
* How do you handle concurrent updates?

### **For GitHub Portfolio:**

* Impressive AWS project
* Shows practical DevOps skills
* Demonstrates system design thinking
* Well-documented, production-ready code

---

## 📞 **Support & Questions**

For issues or questions:
1. Check CloudWatch logs
2. Review AWS documentation
3. Test with manual inserts
4. Verify IAM permissions

---

## 🎯 **Quick Links**

* [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
* [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)
* [EventBridge Guide](https://docs.aws.amazon.com/eventbridge/)
* [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [AWS Serverless Best Practices](https://serverless.com/blog/serverless-best-practices)

---

**Last Updated:** December 7, 2025  
**Status:** ✅ Production Ready  
**Version:** 1.0.0

---

**Author:** Rathod Shanker  
**Email:** shankerr7780@gmail.com

Made with ❤️ for cloud engineers & DevOps enthusiasts.

---
title : "Deploy Lambda Analyzer"
date : 2024-01-01
weight : 2
chapter : false
pre : " <b> 5.4.2 </b> "
---

### Add Configuration Variables for the Analyzer

The Analyzer requires two variables to support the spike detection logic. Add the following variables to `terraform/variables.tf`:

```hcl
# Multiplier used to detect abnormal cost increases.
# If the current cost exceeds the historical average multiplied by this value,
# it will be considered an abnormal spike.
variable "spike_multiplier" {
  description = "Spike multiplier: if cost > historical average * this multiplier, it is considered an abnormal spike"
  type        = number
  default     = 1.5 # Trigger an alert when the current cost exceeds 1.5x the historical average.
}

# Number of historical days used to calculate the average cost.
variable "history_days" {
  description = "Number of historical days used to calculate the average cost (for spike detection)"
  type        = number
  default     = 7 # Calculate the average cost over the last 7 days.
}
```

### Write the Lambda Analyzer Code

Create the file `terraform/lambda/analyzer/handler.py`, which contains the Python source code for the Lambda Analyzer function.

This function is automatically triggered whenever it receives a notification message from the Amazon SQS queue (sent by the Collector). The processing workflow consists of three steps:

1. **Retrieve data**: Extracts the file path from the SQS message, then retrieves the corresponding cost data from Amazon S3.
2. **Perform intelligent analysis**: Calculates the total daily cost and identifies the top five most expensive AWS services. Additionally, it reads historical cost files stored in Amazon S3 to calculate the average cost over the previous seven days.
3. **Make an alert decision**: Evaluates the current cost against two conditions:

- Does the current cost exceed the predefined budget threshold?
- Has the current cost increased abnormally compared to the historical average?

If either condition is met, the function sends a detailed email notification to the user via Amazon SNS.

```python
"""
Functions:
    1. Triggered by events from Amazon SQS (sent by the Collector)
    2. Read the corresponding cost data from Amazon S3
    3. Compare the total cost against the budget threshold and detect anomalies
       (abnormal spikes compared to the historical average, if applicable)
    4. If the threshold is exceeded or an anomaly is detected, send an alert through Amazon SNS

Failed processing events are automatically moved to the Dead Letter Queue (DLQ)
by Amazon SQS according to the configured redrive policy.
"""

import boto3
import os
import json

# Read configuration from environment variables (provided by Terraform)
BUCKET_NAME = os.environ["BUCKET_NAME"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
COST_THRESHOLD = float(os.environ.get("COST_THRESHOLD", "10"))

# Spike multiplier: cost > average * multiplier => anomaly
SPIKE_MULTIPLIER = float(os.environ.get("SPIKE_MULTIPLIER", "1.5"))

# Number of historical days used to calculate the average
HISTORY_DAYS = int(os.environ.get("HISTORY_DAYS", "7"))

s3_client = boto3.client("s3")
sns_client = boto3.client("sns")

def read_cost_from_s3(s3_key: str) -> dict:
    # Read the cost data (.json) file from Amazon S3
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    return json.loads(response["Body"].read())

def compute_total_and_top(cost_data: dict) -> dict:
    """Sum total costs + top most expensive services from Cost Explorer data."""
    total_cost = 0.0
    service_costs = {}
    for result in cost_data.get("ResultsByTime", []):
        for group in result.get("Groups", []):
            service = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            service_costs[service] = service_costs.get(service, 0.0) + amount
            total_cost += amount
    top_services = sorted(service_costs.items(), key=lambda x: x[1], reverse=True)[:5]
    return {"total_cost": round(total_cost, 4), "top_services": top_services}

def get_historical_average(current_date: str) -> float:
    # Calculate the average cost of the previous HISTORY_DAYS days before the current date,
    # read from the files stored in S3. Return 0 if there is no historical data
    dt = datetime.strptime(current_date, "%Y-%m-%d")
    totals = []
    for i in range(1, HISTORY_DAYS + 1):
        day = dt - timedelta(days = i)
        key = f"cost-data/year={day.year}/month={day.month:02d}/day={day.day:02d}/cost_{day.strftime('%Y-%m-%d')}.json"
        try:
            data = read_cost_from_s3(key)
            totals.append(compute_total_and_top(data)["total_cost"])
        except s3_client.exceptions.NoSuchKey:
            continue
        except Exception:
            continue
    if not totals:
        return 0.0
    return round(sum(totals) / len(totals), 4)

def classify_severity(total: float, avg: float) -> tuple:
    # Classify alert levels based on fixed thresholds and spike detection.
    # Returns (severity, reasons[])

    reasons = []
    severity = "INFO"

    # Exceeds budget threshold
    if total > COST_THRESHOLD:
        reasons.append(f"Budget threshold exceeded (${COST_THRESHOLD:.2f})")
        severity = "WARNING"

    # Spike compared to historical average
    if avg > 0 and total > avg * SPIKE_MULTIPLIER:
        pct = ((total - avg) / avg) * 100
        reasons.append(f"Cost spike detected: {pct:.0f}% above historical average {HISTORY_DAYS} day (${avg:.2f})")
        severity = "CRITICAL"
    
    return severity, reasons

def send_alert(date_str: str, analysis: dict) -> None:
    # Send an SNS alert when the cost exceeds the threshold
    total = analysis["total_cost"]

    lines = [
        "AWS COST ALERT - CloudCost Insight",
        "",
        f"Day: {date_str}",
        f"Total cost: ${total:.4f}",
        f"Alert threshold: ${COST_THRESHOLD:.2f}",
        "",
        f"Top Service by cost:",
    ]
    for service, cost in analysis["top_services"]:
        lines.append(f" - {service}: ${cost:.4f}")

    message = "\n".join(lines)

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"[CloudCost Insight] Cost alert for date {date_str}",
        Message=message,
    )

def lambda_handler(event, context):
    """Process SQS batch and only retry failed records."""
    processed = 0
    batch_item_failures = []

    for record in event.get("Records", []):
        try:
            process_record(record)
            processed += 1
        except Exception as error:
            message_id = record["messageId"]
            print(f"[Analyzer] Failed record {message_id}: {error}")
            batch_item_failures.append({"itemIdentifier": message_id})

    print(f"[Analyzer] Processed={processed}, Failed={len(batch_item_failures)}")
    return {"batchItemFailures": batch_item_failures}
```

### Configure the IAM Role and Deploy the Analyzer

**1.** Next, create the file `terraform/lambda_analyzer.tf`. This file is responsible for provisioning all the AWS infrastructure required to run the Lambda Analyzer function. It automatically performs the following tasks:

- **Grant security permissions**: Creates the IAM permissions required for the Analyzer function to read cost data from Amazon S3, receive messages from Amazon SQS, and publish alerts through Amazon SNS.
- **Package and deploy**: Automatically compresses the Python source code into a ZIP file and uploads it to AWS to create a fully functional Lambda function.
- **Configure automatic integration**: Establishes a direct event source mapping between the Amazon SQS queue and the Analyzer function. Whenever a new cost notification appears in the queue, the Analyzer is automatically invoked to process it.

Without these infrastructure configurations, the Python source code alone would not be enough for AWS to know how to execute the function or what resources it is allowed to access. This Terraform configuration connects **Amazon S3**, **Simple Queue Service (SQS)**, **Simple Notification Service (SNS)**, and **Lambda** into a fully automated and end-to-end processing pipeline.

```hcl
# IAM role for the Analyzer
resource "aws_iam_role" "analyzer" {
  name               = "${var.project_name}-analyzer-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "analyzer_policy" {
  # Read cost data from Amazon S3
  statement {
    sid       = "S3ReadCostData"
    effect    = "Allow"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.cost_data.arn}/*"]
  }

  # ListBucket policy
  statement {
    sid = "S3ListBucket"
    effect = "Allow"
    actions = ["s3:ListBucket]
    resources = [aws_s3_bucket.cost_data.arn8]
  }

  # Receive and delete messages from the primary SQS queue
  statement {
    sid    = "SQSConsume"
    effect = "Allow"
    actions = [
      "sqs:ReceiveMessage",
      "sqs:DeleteMessage",
      "sqs:GetQueueAttributes"
    ]
    resources = [aws_sqs_queue.events.arn]
  }

  # Publish alerts through Amazon SNS
  statement {
    sid       = "SNSPublish"
    effect    = "Allow"
    actions   = ["sns:Publish"]
    resources = [aws_sns_topic.cost_alerts.arn]
  }

  # Write logs to Amazon CloudWatch
  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:*:*:*"]
  }
}

resource "aws_iam_role_policy" "analyzer" {
  name   = "${var.project_name}-analyzer-policy"
  role   = aws_iam_role.analyzer.id
  policy = data.aws_iam_policy_document.analyzer_policy.json
}

# Package the source code
data "archive_file" "analyzer_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/analyzer"
  output_path = "${path.module}/build/analyzer.zip"
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "analyzer" {
  name              = "/aws/lambda/${var.project_name}-analyzer"
  retention_in_days = 14
}

# Lambda Analyzer function
resource "aws_lambda_function" "analyzer" {
  function_name = "${var.project_name}-analyzer"
  role          = aws_iam_role.analyzer.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 128

  filename         = data.archive_file.analyzer_zip.output_path
  source_code_hash = data.archive_file.analyzer_zip.output_base64sha256

  environment {
    variables = {
      BUCKET_NAME        = aws_s3_bucket.cost_data.id
      SNS_TOPIC_ARN      = aws_sns_topic.cost_alerts.arn
      COST_THRESHOLD_USD = var.cost_threshold_usd
      SPIKE_MULTIPLIER   = var.spike_multiplier
      HISTORY_DAYS       = var.history_days
    }
  }

  depends_on = [aws_cloudwatch_log_group.analyzer]
}

# Connect Amazon SQS to the Lambda Analyzer
resource "aws_lambda_event_source_mapping" "sqs_to_analyzer" {
  event_source_arn = aws_sqs_queue.events.arn
  function_name    = aws_lambda_function.analyzer.arn
  batch_size       = 10
  enabled          = true

  # Lambda retries records only when the Analyzer reports an error.
  function_response_types = ["ResponseBatchItemFailures"]
}
```

**2.** Open the `terraform/outputs.tf` file and add the following configuration to the end of the file:

```hcl
# Output IAM Role ARN for Lambda Analyzer to the console
output "analyzer_role_arn" {
  description = "ARN of the IAM Role for Lambda Analyzer"
  value       = aws_iam_role.analyzer.arn
}
```

### Next

- [Monitoring](5-Workshop/5.5-Monitoring/)
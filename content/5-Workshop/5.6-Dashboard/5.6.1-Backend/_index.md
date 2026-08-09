---
title : "Backend"
date : 2024-01-01
weight : 1
chapter : false
pre : " <b> 5.6.1 </b> "
---

### Write the Lambda API Code

We will create the file `lambda/api/handler.py`. This function reads all cost data stored in S3, aggregates it into a JSON response (total cost, daily costs with status, and top services), and returns it to the Web Frontend.

```python
# Provide cost data for the Web Dashboard:
# - Read cost data files from S3 (written by the Collector)
# - Aggregate them into JSON: daily costs, service costs, total cost, and status
# - Return the data to the Frontend (via API Gateway) for chart rendering

# Invoked by API Gateway (HTTP GET). Returns JSON with CORS headers so the web frontend can access it.

import os
import json
import boto3
from datetime import datetime, timedelta
from collections import defaultdict

BUCKET_NAME = os.environ["BUCKET_NAME"]
COST_THRESHOLD = float(os.environ.get("COST_THRESHOLD_USD", "10"))
SPIKE_MULTIPLIER = float(os.environ.get("SPIKE_MULTIPLIER", "1.5"))
# Maximum number of days of data returned to the dashboard
MAX_DAYS = int(os.environ.get("MAX_DAYS", "30"))

s3_client = boto3.client("s3")


def _cors_response(status_code: int, body: dict) -> dict:
    """Return a response with CORS headers so the web frontend can access it."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps(body, default=str),
    }


def list_cost_files() -> list:
    """List all cost data files in S3 (under the cost-data/ prefix)."""
    keys = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="cost-data/"):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                keys.append(obj["Key"])
    return sorted(keys)


def read_cost_file(key: str) -> dict:
    """Read a JSON cost data file from S3."""
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
    return json.loads(response["Body"].read())


def parse_daily(cost_data: dict) -> tuple:
    """Extract (date, total cost, service cost dictionary) from Cost Explorer data."""
    day = None
    total = 0.0
    services = defaultdict(float)
    for result in cost_data.get("ResultsByTime", []):
        day = result.get("TimePeriod", {}).get("Start")
        for group in result.get("Groups", []):
            svc = group["Keys"][0]
            amount = float(group["Metrics"]["UnblendedCost"]["Amount"])
            services[svc] += amount
            total += amount
    return day, round(total, 2), dict(services)


def lambda_handler(event, context):
    """Invoked by API Gateway (HTTP GET). Returns aggregated data for the dashboard."""
    try:
        keys = list_cost_files()[-MAX_DAYS:]  # Retrieve at most the most recent MAX_DAYS of data

        daily_costs = []  # [{date, total, status}]
        service_totals = defaultdict(float)  # Total cost by service (full term)
        grand_total = 0.0

        # Read each file, synthesize
        for key in keys:
            data = read_cost_file(key)
            day, total, services = parse_daily(data)
            if day is None:
                continue
            daily_costs.append({"date": day, "total": total})
            grand_total += total
            for svc, amt in services.items():
                service_totals[svc] += amt

        # Daily status (based on threshold + moving average)
        for i, d in enumerate(daily_costs):
            prev = [x["total"] for x in daily_costs[max(0, i - HISTORY_DAYS) : i]]
            avg = sum(prev) / len(prev) if prev else 0
            if avg > 0 and d["total"] > avg * SPIKE_MULTIPLIER:
                d["status"] = "CRITICAL"
            elif d["total"] > COST_THRESHOLD:
                d["status"] = "WARNING"
            else:
                d["status"] = "NORMAL"

        # Top most expensive services
        top_services = sorted(service_totals.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]

        result = {
            "grand_total": round(grand_total, 2),
            "threshold": COST_THRESHOLD,
            "days_count": len(daily_costs),
            "daily_costs": daily_costs,
            "top_services": [
                {"service": s, "cost": round(c, 2)} for s, c in top_services
            ],
        }
        return _response(200, result)

    except Exception:
        logger.exception("Unexpected error while loading cost dashboard data")
        return _response(500, {"error": "Internal server error"})
```

The most important part here is the **CORS headers** included in the response. CORS stands for Cross-Origin Resource Sharing, a mechanism that allows resources to be shared across different origins. This mechanism exists to protect web users. By default, web browsers enforce a strict security policy: they do not allow a web page hosted on one domain to freely access data from another domain. This prevents malicious websites from secretly stealing users' personal information.

However, in our project, the Web Frontend is hosted on Amazon S3 and distributed through CloudFront under its own domain name, while the data is served by API Gateway, which uses a completely different domain. Without CORS, the user's browser would immediately block requests for cost data, preventing the dashboard from displaying charts because it would assume the web page was attempting to access data from another origin without permission.

For this reason, the Lambda function must include the appropriate **CORS headers** in its response. In particular, the header "Access-Control-Allow-Origin": "*" allows requests from any origin.

### Create API Gateway

Next, we create the file `terraform/api_gateway.tf` to deploy the Lambda API and expose it through an HTTP API Gateway. Users will call this endpoint to retrieve cost data.

```hcl
# IAM role for the Lambda API
resource "aws_iam_role" "api" {
  name               = "${var.project_name}-api-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "api_policy" {
  # Grant permission to read cost data from S3
  statement {
    sid     = "S3ReadCostData"
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:ListBucket"]     # Permission to retrieve files and list objects
    resources = [
      aws_s3_bucket.cost_data.arn,                  # Permission on the S3 bucket
      "${aws_s3_bucket.cost_data.arn}/*"            # Permission on objects within the bucket
    ]
  }

  # Grant permission to write logs to CloudWatch
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

# Attach the policy to the Lambda API role
resource "aws_iam_role_policy" "api" {
  name   = "${var.project_name}-api-policy"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.api_policy.json
}

# Package the Python source code into a ZIP file
data "archive_file" "api_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/api"
  output_path = "${path.module}/build/api.zip"
}

# Create a CloudWatch Log Group for the Lambda API
resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${var.project_name}-api"
  retention_in_days = 14
}

# Lambda API function
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.api.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30            # Maximum execution time: 30 seconds
  memory_size   = 128           # Allocate 128 MB of memory

  filename         = data.archive_file.api_zip.output_path
  source_code_hash = data.archive_file.api_zip.output_base64sha256      # Track the hash to detect source code changes

  # Environment variables
  environment {
    variables = {
      BUCKET_NAME        = aws_s3_bucket.cost_data.id
      COST_THRESHOLD_USD = var.cost_threshold_usd
      SPIKE_MULTIPLIER   = var.spike_multiplier
      HISTORY_DAYS       = var.history_days
      MAX_DAYS           = "30"
    }
  }

  # Ensure the Log Group is created before the Lambda function
  depends_on = [aws_cloudwatch_log_group.api]
}

# HTTP API Gateway
resource "aws_apigatewayv2_api" "dashboard" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  description   = "API that provides cost data for the Web Dashboard"

  # Enable CORS so the web frontend can access the API
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "OPTIONS"]
    allow_headers = ["Content-Type"]
  }
}

# Integrate API Gateway with Lambda
resource "aws_apigatewayv2_integration" "api" {
  api_id                 = aws_apigatewayv2_api.dashboard.id
  integration_type       = "AWS_PROXY"      # Use proxy integration to automatically forward requests and responses
  integration_uri        = aws_lambda_function.api.invoke_arn # Target Lambda function
  payload_format_version = "2.0"
}

# Route: GET /costs
resource "aws_apigatewayv2_route" "costs" {
  api_id    = aws_apigatewayv2_api.dashboard.id
  route_key = "GET /costs"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

# Default stage (auto-deploy enabled)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.dashboard.id
  name        = "$default"
  auto_deploy = true
}

# Allow API Gateway to invoke the Lambda function
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.dashboard.execution_arn}/*/*"
}
```

**2.** Open the `terraform/outputs.tf` file and add the following configuration at the end of the file.

```hcl
# API Gateway
output "api_endpoint" {
  description = "API endpoint URL (for web frontend calls)"
  value       = "${trim(aws_apigatewayv2_stage.default.invoke_url, "/")}/costs" # dọn dẹp dấu gạch ngang bị thừa
}

output "api_function_name" {
  description = "Lambda API function name"
  value       = aws_lambda_function.api.function_name
}
```

### Deploy and Test the API

**1.** Before deploying the API, we need to ensure that cost data already exists in the S3 bucket. Cost data is available only after it has been collected over a 24-hour period. Normally, if you have just deployed the system, no cost data will be available yet. In this case, we can use a script to generate simulated data:

- Create the file `terraform/generate-simulated-data/simulated_data.py` to generate sample data. This script simulates cost data and uploads it to the S3 bucket.

```python
import sys
import json
import subprocess
from datetime import datetime, timedelta

# Generate simulated cost data
def make_cost_json(services: dict, date_str) -> dict:
    groups = [
        {
            "Keys": [name],     # AWS service name
            "Metrics": {"UnblendedCost": {"Amount": f"{amount:.2f}", "Unit": "USD"}}    # Corresponding cost
        }
        for name, amount in services.items()    # Iterate through each provided service
    ]
    return {
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": date_str, "End": date_str},     # Time period
                "Total": {},
                "Groups": groups,   # List of services
                "Estimated": False,
            }
        ]
    }

# Generate the S3 object key (partitioned by year/month/day)
def s3_key_for(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"cost-data/year={dt.year}/month={dt.month:02d}/day={dt.day:02d}/cost_{date_str}.json"

# Create JSON, save it to a temporary file, then upload it to S3 using the AWS CLI
def upload(bucket: str, date_str: str, services: dict):
    data = make_cost_json(services, date_str)
    fname = f"/tmp/cost_{date_str}.json"      # Temporary file path

    # Write JSON to the temporary file
    with open(fname, "w") as f:
        json.dump(data, f)

    # Get the destination key in S3
    key = s3_key_for(date_str)

    # Upload the temporary file to S3
    subprocess.run(["aws", "s3", "cp", fname, f"s3://{bucket}/{key}"], check=True)
    total = sum(services.values())
    print(f"{date_str}: total ${total:.2f} -> s3://{bucket}/{key}")

    # Return the S3 key and the total cost
    return key, total

# Generate simulated SQS events
def sqs_event(date_str: str, key: str, total: float) -> str:
    body = json.dumps({"date": date_str, "s3_key": key, "total_cost": round(total, 4)})
    return json.dumps({"Records": [{"body": body}]}, indent=2)


def main():
    # Check whether the bucket name has been provided
    if len(sys.argv) < 2:
        print("Usage: python test_data.py <BUCKET_NAME>")
        sys.exit(1)

    # Exit if no bucket name is provided
    bucket = sys.argv[1]

    # Assume today's date
    base = datetime(2026, 6, 1)

    # Define test scenarios
    scenarios = {
        "INFO": {
            "hist_daily": {"AWS Lambda": 3.0, "Amazon S3": 2.0}, # ~$5/history days
            "test_day": {"AWS Lambda": 4.0, "Amazon S3": 2.0}, # $6 <= 10, no spike
            "test_date": "2026-07-17",
        },
        "WARNING": {
            "hist_daily": {"Amazon EC2": 6.0, "Amazon S3": 3.0}, # ~$9/history day
            "test_day": {"Amazon EC2": 8.0, "Amazon S3": 4.0}, # $12 > 10, but 9*1.5 = 13.5
            "test_date": "2026-06-25",
        },
        "CRITICAL": {
            "hist_daily": {"AWS Lambda": 2.0, "Amazon S3": 1.0},  # ~$3/history day
            "test_day": {"Amazon EC2": 45.0, "Amazon RDS": 7.0}, # $52 > 3*1.5 = 4.5
            "test_date": "2026-07-05",
        },
    }

    for name, sc in scenarios.items():
        print(f"\n===== SCENARIO {name} =====")
        test_dt = datetime.strptime(sc["test_date"], "%Y-%m-%d")

        # Upload the 7 historical days before the test date
        for i in range(1, 8):
            hist_date = (test_dt - timedelta(days=i)).strftime("%Y-%m-%d")
            upload(bucket, hist_date, sc["hist_daily"])

        # Upload the cost data for the test day
        key, total = upload(bucket, sc["test_date"], sc["test_day"])

        print(f"\n >>> SQS event for testing the {name} scenario (paste this into the Lambda Test Console): ")
        print(sqs_event(sc["test_date"], key, total))


if __name__ == "__main__":
    main()
```

**2.** Next, deploy the infrastructure from the Terminal:

```bash
terraform apply
```

**3.** Retrieve the bucket name:

```bash
terraform output cost_data_bucket_name
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_1.png)

**4.** Run script to generate simulated data:

```bash
python3 test/test_data.py <BUCKET_NAME>
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_2.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_3.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_4.png)

**5.** Verify the generated data in the AWS Console:

- Open **Amazon S3**.
- Select your bucket.

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_5.png)

- You should now see the folders containing the simulated cost data.
- Open the folders and verify that the JSON files containing the cost data have been created.

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_6.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_7.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_8.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_9.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_10.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_11.png)

**6.** After verifying that everything works correctly, retrieve the API endpoint URL:

```bash
terraform output api_endpoint
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_13.png)

**7.** Access the link that appears in the Terminal, you will see the returned data in JSON format. You can also click **Pretty-print** to view it more visually:

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_14.png)

### Next Content

- [Frontend](../5.6.2-Frontend/)
---
title : "Backend"
date : 2024-01-01
weight : 1
chapter : false
pre : " <b> 5.6.1 </b> "
---

### Viết Code Lambda API

Chúng ta sẽ tạo file `lambda/api/handler.py`. Hàm này đọc toàn bộ dữ liệu chi phí trong S3, tổng hợp thành JSON (tổng chi phí, chi phí theo ngày kèm trạng thái, top dịch vụ) và trả về cho Web Frontend.

```python
# cung cấp dữ liệu chi phí cho Web Dashboard:
# - đọc các file dữ liệu chi phí từ S3 (do Collector ghi)
# - tổng hợp thành JSON: chi phí theo ngày, theo dịch vụ, tổng, trạng thái
# - Trả về cho Frontend (qua api gateway) để vẽ biểu đồ

# được gọi bởi API gateway (HTTP GET). Trả Json kèm CORS header để web gọi được

import json
import logging
import os
from collections import defaultdict

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BUCKET_NAME = os.environ["BUCKET_NAME"]
COST_THRESHOLD = float(os.environ.get("COST_THRESHOLD_USD", "10"))
SPIKE_MULTIPLIER = float(os.environ.get("SPIKE_MULTIPLIER", "1.5"))
HISTORY_DAYS = int(os.environ.get("HISTORY_DAYS", "14"))
# Số ngày dữ liệu tối đa trả về cho dashboard
MAX_DAYS = int(os.environ.get("MAX_DAYS", "30"))

s3_client = boto3.client("s3")


def _response(status_code: int, body: dict) -> dict:
    """Trả response kèm CORS header để web frontend gọi được."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def list_cost_files() -> list:
    """Liệt kê các file dữ liệu chi phí trong S3 (dưới prefix cost-data/)."""
    keys = []
    paginator = s3_client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=BUCKET_NAME, Prefix="cost-data/"):
        for obj in page.get("Contents", []):
            if obj["Key"].endswith(".json"):
                keys.append(obj["Key"])
    return sorted(keys)


def read_cost_file(key: str) -> dict:
    """Đọc 1 file dữ liệu chi phí JSON từ S3."""
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=key)
    return json.loads(response["Body"].read())


def parse_daily(cost_data: dict) -> tuple:
    """Từ dữ liệu Cost Explorer, trả về (ngày, tổng chi phí, dict chi phí theo dịch vụ)."""
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
    """Được API Gateway gọi (HTTP GET). Trả dữ liệu tổng hợp cho dashboard."""
    try:
        keys = list_cost_files()[-MAX_DAYS:]  # lấy tối đa MAX_DAYS ngày gần nhất

        daily_costs = []  # [{date, total, status}]
        service_totals = defaultdict(float)  # tổng chi phí theo dịch vụ (toàn kỳ)
        grand_total = 0.0

        # Đọc từng file, tổng hợp
        for key in keys:
            data = read_cost_file(key)
            day, total, services = parse_daily(data)
            if day is None:
                continue
            daily_costs.append({"date": day, "total": total})
            grand_total += total
            for svc, amt in services.items():
                service_totals[svc] += amt

        # Tính trạng thái từng ngày (dựa ngưỡng + trung bình động)
        for i, d in enumerate(daily_costs):
            prev = [x["total"] for x in daily_costs[max(0, i - HISTORY_DAYS) : i]]
            avg = sum(prev) / len(prev) if prev else 0
            if avg > 0 and d["total"] > avg * SPIKE_MULTIPLIER:
                d["status"] = "CRITICAL"
            elif d["total"] > COST_THRESHOLD:
                d["status"] = "WARNING"
            else:
                d["status"] = "NORMAL"

        # Top dịch vụ tốn chi phí nhất
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

Điểm quan trọng ở đây là **CORS header** trong response. CORS là viết tắt của cơ chế chia sẻ tài nguyên giữa các nguồn gốc khác nhau. Cơ chế này tồn tại để bảo vệ an toàn cho người dùng Web. Mặc định, các trình duyệt Web đều có một quy tắt bảo mật rất nghiêm ngặt: chúng không ch phép một trang Web ở tên miền này được phép tự ý gọi và lấy dữ liệu từ một tên miền khác. Điều này giúp ngăn chặn các trang Web giả mạo âm thầm đánh cắp thông tin cá nhân của bạn.

Tuy nhiên, trong dự án của chúng ta, giao diện Web Frontend được lưu trữ trên hệ thống S3 và CloudFront với một tên miền riêng, trong khi dữ liệu lại được cung cấp bởi API Gateway nằm ở một tên miền hoàn toàn khác. Nếu không có cơ chế CORS, trình duyệt của người dùng sẽ ngay lập tức chặn đứng việc tải dữ liệu chi phí để vẽ biểu đồ vì nó lầm tưởng trang Web của chúng ta đang cố gắng đánh cắp dữ liệu trái phép.

Đó là lý do hàm trả về kết quả phải đính kèm các thống số **CORS header**. Đặc biệt là thông số `"Access-Control-Allow-Origin": "*"` giúp cho phép truy cập từ mọi nguồn khác nhau.

### Tạo API Gateway

**1.** Chúng ta tạo file `terraform/api_gateway.tf` để triển khai Lambda API và expose nó qua HTTP API Gateway. Người dùng sẽ gọi tới endpoint này để lấy dữ liệu.

```hcl
# IAM role cho Lambda API
resource "aws_iam_role" "api" {
  name               = "${var.project_name}-api-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

data "aws_iam_policy_document" "api_policy" {
  # Cấp quyền đọc dữ liệu chi phí từ S3
  statement {
    sid     = "S3ReadCostData"
    effect  = "Allow"
    actions = ["s3:GetObject", "s3:ListBucket"]     # Quyền lấy file và xem danh sách file
    resources = [
      aws_s3_bucket.cost_data.arn,                  # Quyền thao tác trên S3 bucket
      "${aws_s3_bucket.cost_data.arn}/*"            # Quyền thao tác trên các file trong S3 bucket
    ]
  }

  # Cấp quyền ghi log hoạt động lên CloudWatch
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

# Gán Policy vừa định nghĩa vào role của Lambda API
resource "aws_iam_role_policy" "api" {
  name   = "${var.project_name}-api-policy"
  role   = aws_iam_role.api.id
  policy = data.aws_iam_policy_document.api_policy.json
}

# Nén thư mục code python thành file zip
data "archive_file" "api_zip" {
  type        = "zip"
  source_dir  = "${path.module}/lambda/api"
  output_path = "${path.module}/build/api.zip"
}

# Tạo nhóm Log cho Lambda API trên CloudWatch
resource "aws_cloudwatch_log_group" "api" {
  name              = "/aws/lambda/${var.project_name}-api"
  retention_in_days = 14
}

# Hàm Lambda API
resource "aws_lambda_function" "api" {
  function_name = "${var.project_name}-api"
  role          = aws_iam_role.api.arn
  handler       = "handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 30            # Thời gian chạy tối đa là 30s
  memory_size   = 128           # Dung lượng cấp phát 128MB

  filename         = data.archive_file.api_zip.output_path
  source_code_hash = data.archive_file.api_zip.output_base64sha256      # Theo dõi mã băm để phát hiện thay đổi code

  # Biến môi trường
  environment {
    variables = {
      BUCKET_NAME        = aws_s3_bucket.cost_data.id
      COST_THRESHOLD_USD = var.cost_threshold_usd
      SPIKE_MULTIPLIER   = var.spike_multiplier
      HISTORY_DAYS       = var.history_days
      MAX_DAYS           = "30"
    }
  }

  # Đảm bảo Lambda tạo sau Log Group
  depends_on = [aws_cloudwatch_log_group.api]
}

# HTTP API gateway
resource "aws_apigatewayv2_api" "dashboard" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
  description   = "API provides cost data for the Web Dashboard"

  # bật CORS để web frontend gọi được
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "OPTIONS"]
    allow_headers = ["Content-Type"]
  }
}

# tích hợp API gateway với lambda
resource "aws_apigatewayv2_integration" "api" {
  api_id                 = aws_apigatewayv2_api.dashboard.id
  integration_type       = "AWS_PROXY"      # Dùng cơ chế proxy để tự động chuyển tiếp toàn bộ request/response
  integration_uri        = aws_lambda_function.api.invoke_arn # Trỏ đến hàm Lambda cần kích hoạt
  payload_format_version = "2.0"
}

# route: get/costs
resource "aws_apigatewayv2_route" "costs" {
  api_id    = aws_apigatewayv2_api.dashboard.id
  route_key = "GET /costs"
  target    = "integrations/${aws_apigatewayv2_integration.api.id}"
}

# state mặc định (tự động deploy)
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.dashboard.id
  name        = "$default"
  auto_deploy = true
}

# cho phép API gateway gọi Lambda
resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.dashboard.execution_arn}/*/*"
}
```

**2.** Mở file `terraform/outputs.tf` và thêm cấu hình sau và cuối file.

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

### Triển khai và kiểm thử API

**1.** Trước khi triển khai API, chúng ta cần đảm bảo rằng đã có dữ liệu chi phí trong S3 bucket. Dữ liệu chi phí cần được tổng hợp sau 24 giờ. Thông thường, khi chúng ta chỉ vừa mới triển khai hệ thống thì sẽ chưa có dữ liệu chi phí. Trong trường hợp này, chúng ta có thể sử dụng script để sinh ra dữ liệu mô phỏng:

- Chúng ta sẽ tạo file `terraform/generate-simulated-data/simulated_data.py` để sinh ra dữ liệu giả lập. File này sẽ mô phỏng dữ liệu chi phí và ghi vào S3 bucket.

```python

import sys
import json
import subprocess
from datetime import datetime, timedelta

# Sinh dữ liệu mô phỏng
def make_cost_json(services: dict, date_str) -> dict:
    groups = [
        {
            "Keys": [name],     # tên dịch vụ AWS
            "Metrics": {"UnblendedCost": {"Amount": f"{amount:.2f}", "Unit": "USD"}}    # chi phí tương ứng
        }
        for name, amount in services.items()    # chạy vòng lặp qua từng dịch vụ truyền vào
    ]
    return {
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": date_str, "End": date_str},     # thời gian áp dụng
                "Total": {},
                "Groups": groups,   # danh sách dịch vụ
                "Estimated": False,
            }
        ]
    }

# sinh ra đường dẫn S3 (chia thư mục theo năm/tháng/ngày)
def s3_key_for(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"cost-data/year={dt.year}/month={dt.month:02d}/day={dt.day:02d}/cost_{date_str}.json"

# Tạo JSON, lưu ra file tạm rồi dùng AWS CLI tải lên S3
def upload(bucket: str, date_str: str, services: dict):
    data = make_cost_json(services, date_str)
    fname = f"/tmp/cost_{date_str}.json"      # đường dẫn file lưu tạm trên máy
    
    # ghi json ra file tạm
    with open(fname, "w") as f:
        json.dump(data, f)
    
    # lấy đường dẫn đích trên S3
    key = s3_key_for(date_str)

    # copy file tạm lên S3
    subprocess.run(["aws", "s3", "cp", fname, f"s3://{bucket}/{key}"], check = True)
    total = sum(services.values())
    print(f"{date_str}: total ${total:.2f} -> s3://{bucket}/{key}")
    
    # trả về đường dẫn và tổng chi phí
    return key, total

# Tạo các sự kiện giả lập để đưa vào SQS
def sqs_event(date_str: str, key: str, total: float) -> str:
    body = json.dumps({"date": date_str, "s3_key": key, "total_cost": round(total, 4)})
    return json.dumps({"Records": [{"body": body}]}, indent = 2)


def main():
    # kiểm tra xem người dùng đã nhập tên bucket chưa
    if len(sys.argv) < 2:
        print("Cách dùng: python test_data.py <BUCKET_NAME>")
        sys.exit(1)
    
    # thoát chương trình nếu chưa nhập
    bucket = sys.argv[1]

    # giả định ngày hôm nay
    base = datetime(2026, 6, 1)

    # Khai báo các kịch bản test
    scenarios = {
        "INFO": {
            "hist_daily": {"AWS Lambda": 3.0, "Amazon S3": 2.0}, # ~$5/history days
            "test_day": {"AWS Lambda": 4.0, "Amazon S3": 2.0}, # $6 <= 10, không đột biến
            "test_date": "2026-07-17",
        },
        "WARNING": {
            "hist_daily": {"Amazon EC2": 6.0, "Amazon S3": 3.0}, # ~9$/ history day
            "test_day": {"Amazon EC2": 8.0, "Amazon S3": 4.0}, # $12 > 10, nhưng 9*1.5 = 13.5
            "test_date": "2026-06-25",
        },
        "CRITICAL": {
            "hist_daily": {"AWS Lambda": 2.0, "Amazon S3": 1.0},  # ~$3/ history day
            "test_day": {"Amazon EC2": 45.0, "Amazon RDS": 7.0}, # $52 > 3*1.5 = 4.5
            "test_date": "2026-07-05",
        },
    }

    for name, sc in scenarios.items():
        print(f"\n===== SCENARIO {name} =====")
        test_dt = datetime.strptime(sc["test_date"], "%Y-%m-%d")
        
        # upload 7 ngày lịch sử trước ngày test
        for i in range(1, 8):
            hist_date = (test_dt - timedelta(days = i)).strftime("%Y-%m-%d")
            upload(bucket, hist_date, sc["hist_daily"])

        # upload dữ liệu của ngày test chính thức
        key, total = upload(bucket, sc["test_date"], sc["test_day"])

        print(f"\n >>> Event SQS to test scenario {name} (past this into Lambda Test Console): ")
        print(sqs_event(sc["test_date"], key, total))


if __name__ == "__main__":
    main()
```

**2.** Tiếp theo trên Terminal, chúng ta tiến hành triển khai:

```bash
terraform apply
```

**3.** Lấy tên bucket:

```bash
terraform output cost_data_bucket_name
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_1.png)

**4.** Chạy Script sinh dữ liệu mô phỏng:

```bash
python3 test/test_data.py <BUCKET_NAME>
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_2.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_3.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_4.png)

**5.** Kiểm tra trên cửa số Console AWS:

- Truy cập vào **Amazon S3**.
- Chọn trên Bucket của bạn.

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_5.png)

- Lúc này, bạn sẽ thấy các thư mục chứa dữ liệu chi phí mô phỏng đã được sinh ra.
- Truy cập vào các thư mục để kiểm chứng xem dữ liệu chi phí đã có hay chưa ở các file JSON.

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_6.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_7.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_8.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_9.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_10.png)

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_11.png)

**6.** Sau khi đã kiểm chứng thành công, chúng ta sẽ tiến hành lấy URL endpoint của API:

```bash
terraform output api_endpoint
```

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_13.png)

**7.** Truy cập vào đường dẫn hiện ra trên Terminal, bạn sẽ thấy dữ liệu trả về dưới dạng JSON. Bạn cũng có thể bấm chọn **Pretty-print** để xem một cách trực quan hơn:

![Script](/workshop-fcaj-intern/images/5-Workshop/5.6-Dashboard/5.6.1-Backend/backend_15.png)

### Nội dung tiếp theo

- [Frontend](../5.6.2-Frontend/)




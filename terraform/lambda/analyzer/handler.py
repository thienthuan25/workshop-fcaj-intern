"""
Chức năng:
    1. Được kích hoạt bởi sự kiện từ SQS (do Collector gửi)
    2. Đọc dữ liệu chi phí tương ứng từ S3
    3. So sánh tổng chi phí với ngưỡng ngân sách (threshold) + phát hiện bất thường
        (tăng đột biến so với mức trung bình lịch sử - nếu có)
    4. Nếu vượt ngưỡng / bất thường -> gửi cảnh báo qua SNS

Sự kiện xử lý lỗi sẽ được SQS tự động chuyển vào DLQ (theo redrive policy)
"""

import json
import os
from datetime import datetime, timedelta

import boto3

# Đọc cấu hình từ biến môi trường (Terraform truyền vào)
BUCKET_NAME = os.environ["BUCKET_NAME"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
COST_THRESHOLD = float(os.environ.get("COST_THRESHOLD_USD", "10"))

# Hệ số tăng đột biến: chi phí > trung bình * hệ số này  => bất thường
SPIKE_MULTIPLIER = float(os.environ.get("SPIKE_MULTIPLIER", "1.5"))
# Số ngày lịch sử dùng để tính trung bình
HISTORY_DAYS = int(os.environ.get("HISTORY_DAYS", "7"))

s3_client = boto3.client("s3")
sns_client = boto3.client("sns")


def read_cost_from_s3(s3_key: str) -> dict:
    # Đọc file dữ liệu chi phí (.json) từ S3
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
    return json.loads(response["Body"].read())


def compute_total_and_top(cost_data: dict) -> dict:
    """Tính tổng chi phí + top dịch vụ tốn nhất từ dữ liệu Cost Explorer."""
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
    # Tính chi phí trung bình của HISTORY_DAYS ngày trước trước ngày hiện tại,
    # đọc từ các file đã luuw trong S3. Trả về 0 nếu chưa có lịch sử
    dt = datetime.strptime(current_date, "%Y-%m-%d")
    totals = []
    for i in range(1, HISTORY_DAYS + 1):
        day = dt - timedelta(days=i)
        key = f"cost-data/year={day.year}/month={day.month:02d}/day={day.day:02d}/cost_{day.strftime('%Y-%m-%d')}.json"
        try:
            data = read_cost_from_s3(key)
            totals.append(compute_total_and_top(data)["total_cost"])
        except s3_client.exceptions.NoSuchKey:
            print(f"[Analyzer] Historical file not found, skipping: {key}")
            continue
        except Exception as error:
            print(f"[Analyzer] Failed to read historical file {key}: {error}")
            raise
    if not totals:
        return 0.0
    return round(sum(totals) / len(totals), 4)


def classify_severity(total: float, avg: float) -> tuple:
    # Phân loại mức độ cảnh báo dựa trên ngưỡng cố định và tăng đột biến.
    # trả về (severity, reasons[])

    reasons = []
    severity = "INFO"

    # vượt ngưỡng ngân sách
    if total > COST_THRESHOLD:
        reasons.append(f"Budget threshold exceeded (${COST_THRESHOLD:.2f})")
        severity = "WARNING"

    # tăng đột biến so với trung bình lịch sử
    if avg > 0 and total > avg * SPIKE_MULTIPLIER:
        pct = ((total - avg) / avg) * 100
        reasons.append(
            f"Cost spike detected: {pct:.0f}% above historical average {HISTORY_DAYS} day (${avg:.2f})"
        )
        severity = "CRITICAL"

    return severity, reasons


def send_alert(
    date_str: str, analysis: dict, severity: str, reasons: list, avg: float
) -> None:
    # Gửi cảnh báo qua SNS khi chi phí vượt ngưỡng
    total = analysis["total_cost"]

    lines = [
        f"[{severity}] AWS COST ALERT - CloudCost Insight",
        "",
        f"Day: {date_str}",
        f"Total cost: ${total:.2f}",
        f"Alert threshold: ${COST_THRESHOLD:.2f}",
        f"Historical average ({HISTORY_DAYS} days): ${avg:.2f}",
        "",
        "Reasons:",
    ]
    for r in reasons:
        lines.append(f" - {r}")

    lines.extend(["", "Top Service by cost:"])

    for service, cost in analysis["top_services"]:
        lines.append(f" - {service}: ${cost:.2f}")

    message = "\n".join(lines)

    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"[{severity}] CloudCost Insight Alert for {date_str}",
        Message=message,
    )


def process_record(record: dict) -> None:
    """Xử lý một SQS record; exception sẽ được caller báo lại cho Lambda."""
    body = json.loads(record["body"])
    date_str = body["date"]
    s3_key = body["s3_key"]

    print(f"[Analyzer] Processing cost data for date {date_str} (key={s3_key})")

    # 1. Đọc dữ liệu chi phí ngày hiện tại
    cost_data = read_cost_from_s3(s3_key)
    analysis = compute_total_and_top(cost_data)
    total = analysis["total_cost"]

    # 2. Tính trung bình lịch sử để phát hiện tăng đột biến
    avg = get_historical_average(date_str)
    print(
        f"[Analyzer] Total: ${total:.2f} | Average {HISTORY_DAYS} Day: ${avg:.2f} | Threshold: ${COST_THRESHOLD:.2f}"
    )

    # 3. Phân loại mức độ & quyết định cảnh báo
    severity, reasons = classify_severity(total, avg)
    if reasons:
        print(f"[Analyzer] {severity}! Reason: {reasons}. Send alert to SNS.")
        send_alert(date_str, analysis, severity, reasons, avg)
    else:
        print("[Analyzer] Normal cost, no need to alert.")


def lambda_handler(event, context):
    """Xử lý SQS batch và chỉ retry các record thất bại."""
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
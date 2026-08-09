---
title : "Tạo SQS Queue và Dead Letter Queue"
date : 2024-01-01 
weight : 5
chapter : false
pre : " <b> 5.3.5 </b> "
---

Tiếp theo, chúng ta sẽ tạo file `terraform/sqs.tf`. File này được sử dụng để khởi tại dịch vụ hàng đợi **Amazon Simple Queue Service** (SQS), bao gồm một hàng đợi chính và một hàng đợi lỗi **Dead Letter Queue** (DLQ).

Thay vì để hàm Lambda thu thập dữ liệu (Collector) gọi trực tiếp hàm Lambda phân tích (Analyzer), chúng ta dùng SQS đứng ở giữa làm bộ đệm dữ liệu:

- **Chống mất dữ liệu:** Khi Collector lấy xong dữ liệu chi phí, nó chỉ việc ném một tin nhắn vào SQS Queue rồi nghỉ, Analyzer sẽ từ từ đọc tin nhắn từ Queue ra để xử lý. Nhờ vậy, nếu Analyzer bị quả tải hoặc tạm thời dừng hoạt động, tin nhắn vẫn được lưu an toàn trong Queue chờ xử lý sau.
- **Xử lý lỗi an toàn (Dead Letter Queue):** Nếu một tin nhắn bị lỗi và Analyzer thử xử lý lại 3 lần vẫn thất bại, tin nhắn đó sẽ bị đẩy sang một khu vực riêng gọi là **Dead Letter Queue**. Điều này giúp hệ thống không bị mắc kẹt vào một lỗi vô tận, đồng thời cho phép người quản trị giữ lại tin nhắn lỗi đó để điều tra nguyên nhân sau này.

```hcl
# Tạo DLQ
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-dlq"
  message_retention_seconds = 1209600 # Thời gian lưu trữ tối đa là 14 ngày.
}

# Tạo hàng đợi chính.
# Nếu một tin nhắn xử lý thất bại quá 3 lần, nó sẽ tự động bị đẩy sang hàng đợi DLQ ở trên để tránh kẹt hệ thống.
resource "aws_sqs_queue" "events" {
  name                       = "${var.project_name}-events"
  visibility_timeout_seconds = 300    # Thời gian ẩn tin nhắn khi đang được xử lý, phải >= timeout của Analyzer Lambda.
  message_retention_seconds  = 345600 # Thời gian giữ tin nhắn ở đây là 4 ngày.

  # Di chuyển các sự kiện lỗi đến DLQ sau 3 lần xử lý không thành công.
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}
```

### Nội dung tiếp theo

- [Tạo EventBridge Rule lập lịch](../5.3.6-EventBridge-Rule/)
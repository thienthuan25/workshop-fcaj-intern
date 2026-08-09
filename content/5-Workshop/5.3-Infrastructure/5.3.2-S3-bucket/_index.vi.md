---
title : "Tạo S3 Bucket lưu dữ liệu chi phí"
date : 2024-01-01 
weight : 2
chapter : false
pre : " <b> 5.3.2 </b> "
---

Trong phần này, chúng ta sẽ tạo file `terraform/s3.tf` để định nghĩa bucket lưu trữ dữ liệu chi phí. Bucket này được cấu hình bảo mật đầy đủ:

- Chặn truy cập public
- Bật mã hóa
- Versioning
- Quản lý vòng đời dữ liệu

```hcl
# Khởi tạo một S3 Bucket mới dùng để chứa dữ liệu.
# Tên của Bucket được tạo ra sẽ có dạng: <project_name>-cost-data-<aws_account_id> để đảm bảo không bị trùng lặp.
resource "aws_s3_bucket" "cost_data" {
  bucket        = "${var.project_name}-cost-data-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

# Chặn mọi quyền truy cập công khai vào bucket từ internet.
resource "aws_s3_bucket_public_access_block" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Bật mã hóa phía máy chủ để bảo vệ an toàn cho dữ liệu được lưu trữ (AES256)
resource "aws_s3_bucket_server_side_encryption_configuration" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Bật Versioning giúp ngăn chặn tình trạng mất dữ liệu do thao tác nhầm.
resource "aws_s3_bucket_versioning" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Cấu hình Lifecycle.
resource "aws_s3_bucket_lifecycle_configuration" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  rule {
    id     = "archive-old-cost-data"
    status = "Enabled"

    filter {}

    transition {
      days          = 90    # dữ liệu tồn tại quá 90 ngày sẽ được tự động chuyển sang lớp lưu trữ STANDARD_IA - truy cập không thường xuyên
      storage_class = "STANDARD_IA"
    }
  }
}

# Lấy thông tin tài khoản AWS hiện tại (ACCOUNT ID)
data "aws_caller_identity" "current" {}
```

### Nội dung tiếp theo

- [Tạo IAM Role cho Lambda](../5.3.3-IAM-Role/)

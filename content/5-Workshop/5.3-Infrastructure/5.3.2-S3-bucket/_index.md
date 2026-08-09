---
title : "Create an Amazon S3 Bucket for Cost Data Storage"
date : 2024-01-01
weight : 2
chapter : false
pre : " <b> 5.3.2 </b> "
---

In this section, we will create the `terraform/s3.tf` file to define an Amazon S3 bucket for storing cost data. This bucket is configured with several security and data protection features, including:

- Block public access
- Server side encryption
- Versioning
- Lifecycle management

```hcl
# Create an S3 bucket for storing cost data.
# The bucket name follows the format <project_name>-cost-data-<aws_account_id> to ensure global uniqueness.
resource "aws_s3_bucket" "cost_data" {
  bucket        = "${var.project_name}-cost-data-${data.aws_caller_identity.current.account_id}"
  force_destroy = true
}

# Block all forms of public access to the bucket.
resource "aws_s3_bucket_public_access_block" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server side encryption to protect stored data using AES256.
resource "aws_s3_bucket_server_side_encryption_configuration" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enable versioning to help protect data from accidental deletion or modification.
resource "aws_s3_bucket_versioning" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Configure lifecycle management.
resource "aws_s3_bucket_lifecycle_configuration" "cost_data" {
  bucket = aws_s3_bucket.cost_data.id

  rule {
    id     = "archive-old-cost-data"
    status = "Enabled"

    filter {}

    transition {
      days          = 90    # Objects older than 90 days are automatically moved to the STANDARD_IA storage class for infrequently accessed data.
      storage_class = "STANDARD_IA"
    }
  }
}

# Retrieve information about the current AWS account, including the account ID.
data "aws_caller_identity" "current" {}
```

### Next Content

- [Create an IAM Role for Lambda](../5.3.3-IAM-Role/)
---
title : "Create an Amazon SQS Queue and a Dead Letter Queue"
date : 2024-01-01
weight : 5
chapter : false
pre : " <b> 5.3.5 </b> "
---

Next, we will create the `lambda/sqs.tf` file. This file provisions the **Amazon Simple Queue Service** (SQS), including a primary queue and a **Dead Letter Queue (DLQ)**.

Instead of allowing the Lambda Collector function to invoke the Lambda Analyzer function directly, we place Amazon SQS between them to act as a message buffer:

- **Prevent data loss:** After the Collector retrieves cost data, it only needs to send a message to the SQS queue and complete its task. The Analyzer then reads messages from the queue and processes them at its own pace. If the Analyzer is overloaded or temporarily unavailable, the messages remain safely stored in the queue until they can be processed.
- **Handle processing failures safely:** If a message cannot be processed successfully after three retry attempts, it is automatically moved to a separate queue called the **Dead Letter Queue**. This prevents the system from becoming stuck on the same failed message and allows administrators to inspect failed messages later to identify the root cause.

```hcl
# Create the Dead Letter Queue.
resource "aws_sqs_queue" "dlq" {
  name                      = "${var.project_name}-dlq"
  message_retention_seconds = 1209600 # Maximum message retention period is 14 days.
}

# Create the primary queue.
# If a message fails to be processed more than three times, it is automatically moved to the DLQ to prevent processing from being blocked.
resource "aws_sqs_queue" "events" {
  name                       = "${var.project_name}-events"
  visibility_timeout_seconds = 300    # The message visibility timeout must be greater than or equal to the Analyzer Lambda timeout.
  message_retention_seconds  = 345600 # Messages are retained for 4 days.

  # Move failed events to the Dead Letter Queue after three failed processing attempts.
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}
```

### Next Content

- [Create an Amazon EventBridge Schedule](../5.3.6-EventBridge-Rule/)
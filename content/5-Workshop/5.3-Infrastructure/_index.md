---
title : "Provision Infrastructure with Terraform"
date : 2024-01-01
weight : 3
chapter : false
pre : " <b> 5.3. </b> "
---

### Overview

In this section, you will provision the core infrastructure for the CloudCost Insight system using Terraform. These foundational resources will be used by the Lambda functions in the following sections. They include storage for cost data, an event queue, a notification service, and a scheduling service.

![CloudCost Insight Architecture](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Contents

1. [Declare Input Variables](5.3.1-Variables/)
2. [Create an Amazon S3 Bucket for Cost Data Storage](5.3.2-S3-bucket/)
3. [Create an IAM Role for Lambda](5.3.3-IAM-Role/)
4. [Create an Amazon SNS Topic for Cost Alerts](5.3.4-SNS-Topic/)
5. [Create an Amazon SQS Queue and a Dead Letter Queue](5.3.5-SQS-Queue-DLQ/)
6. [Create an Amazon EventBridge Schedule](5.3.6-EventBridge-Rule/)
7. [Define Terraform Outputs](5.3.7-Outputs/)
8. [Deploy the Infrastructure](5.3.8-Deploy-infrastructure/)
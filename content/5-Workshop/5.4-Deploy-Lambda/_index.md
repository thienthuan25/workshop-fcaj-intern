---
title : "Deploying Lambda Functions"
date : 2024-01-01
weight : 4
chapter : false
pre : " <b> 5.4. </b> "
---

### Overview

In this section, we will deploy the two Lambda functions that serve as the processing layer of the **CloudCost Insight** system:

- **Lambda Collector** is responsible for collecting cost data from the Cost Explorer API, storing the data in Amazon S3, and sending events to Amazon SQS.
- **Lambda Analyzer** consumes events from Amazon SQS, analyzes the cost data, and sends alerts through Amazon SNS whenever abnormal costs are detected.

We will deploy each Lambda function step by step. Each function includes a Python implementation and its corresponding Terraform configuration.

![CloudCost Insight Architecture](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Contents

1. [Lambda Collector](../5.4-Deploy-Lambda/5.4.1-Lambda-Collector/)
2. [Lambda Analyzer](../5.4-Deploy-Lambda/5.4.2-Lambda-Analyzer/)
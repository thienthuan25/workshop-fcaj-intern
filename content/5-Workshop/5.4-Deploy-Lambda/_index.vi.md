---
title : "Triển khai Lambda"
date : 2024-01-01 
weight : 4 
chapter : false
pre : " <b> 5.4. </b> "
---

### Tổng quan

Trong phần này, chúng ta sẽ triển khai hai hàm Lambda làm xử lý của hệ thống **CloudCost Insight**:

- **Lambda Collector** chịu trách nhiệm thu thập dữ liệu chi phí từ Cost Explorer API, lưu vào S3 và đẩy sự kiện vào SQS.
- **Lambda Analyzer** tiêu thụ sự kiện từ SQS, phân tích dữ liệu và gửi cảnh báo qua SQS khi phát hiện chi phí bất thường.

Chúng ta sẽ triển khai lần lượt từng hàm, mỗi hàm gồm phần code Python và cấu hình Terraform tương ứng.

![CloudCost Insight Architecture](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Nội dung

1. [Lambda Collector](../5.4-Deploy-Lambda/5.4.1-Lambda-Collector/)
2. [Lambda Analyzer](../5.4-Deploy-Lambda/5.4.2-Lambda-Analyzer/)

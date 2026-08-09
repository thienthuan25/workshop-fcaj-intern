---
title : "Dựng hạ tầng bằng Terraform"
date : 2024-01-01 
weight : 3
chapter : false
pre : " <b> 5.3. </b> "
---

### Tổng quan

Trong phần này, chúng ta sẽ dựng các thành phần hạ tầng nền cho hệ thống CloudCost Insight bằng Terraform. Đây là các tài nguyên cốt lõi mà các hàm Lambda sẽ sử dụng ở những phần sau, bao gồm nơi lưu trữ dữ liệu, hàng đợi sự kiện, kênh cảnh bảo và lập lịch.

![CloudCost Insight Architecture](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Nội dung

1. [Khai báo các biến đầu vào](5.3.1-Variables/)
2. [Tạo S3 Bucket lưu dữ liệu chi phí](5.3.2-S3-bucket/)
3. [Tạo IAM Role cho Lambda](5.3.3-IAM-Role/)
4. [Tạo SNS Topic cảnh báo](5.3.4-SNS-Topic/)
5. [Tạo SQS Queue và Dead Letter Queue](5.3.5-SQS-Queue-DLQ/)
6. [Tạo EventBridge Rule lập lịch](5.3.6-EventBridge-Rule/)
7. [Khai báo Outputs](5.3.7-Outputs/)
8. [Triển khai hạ tầng](5.3.8-Deploy-infrastructure/)

---
title : "Giám sát"
date : 2024-01-01
weight : 5
chapter : false
pre : " <b> 5.5 </b> "
---

### Tổng quan

Ở các phần trước, hệ thống đã có thể tự động thu thập, phân tích và gửi cảnh báo chi phí. Tuy nhiên, khi chúng ta thêm một lớp giám sát để đảm bảo bản thân hệ thống luôn hoạt động tin cậy. Nếu một hàm Lambda gặp lỗi mà không ai biết, hệ thống sẽ không còn hoạt động chính xác.

Trong phần này, chúng ta sẽ cấu hình CloudWatch Alarm để giám sát sức khỏe hệ thống. Có hai loại sự cố cần được cảnh báo:

- Khi một hàm Lambda phát sinh lỗi trong quá trình hoạt động.
- Khi có sự kiện xử lý thất bại rơi vào **Dead Letter Queue**.

Các Alarm này sẽ gửi thông báo qua chính SNS topic đã tạo, giúp bạn nhận được email cảnh báo ngay khi hệ thống gặp trục trặc.

{{% notice note %}}
Lưu ý: Phân biệt hai loại cảnh báo trong hệ thống:<br><br>
&bull; Cảnh báo chi phí (từ Analyzer) thông báo chi phí vượt ngưỡng.<br>
&bull; Cảnh báo sự cố (từ CloudWatch Alarm) thông báo khi bản thân hệ thống gặp lỗi.
{{% /notice %}}

![Monitoring](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Nội dung

1. [Cấu hình CloudWatch Alarm cho Lambda](../5.5-Monitoring/5.5.1-Lambda-alarm-error/)
2. [Cấu hình CloudWatch Alarm cho SQS DLQ](../5.5-Monitoring/5.5.2-Lambda-DLQ-error/)
3. [Triển khai](../5.5-Monitoring/5.5.3-Deploy/)




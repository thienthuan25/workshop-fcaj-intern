---
title : "Giao diện Web"
date : 2024-01-01
weight : 6
chapter : false
pre : " <b> 5.6. </b> "
---

### Giới thiệu

Trong phần này, chúng ta sẽ xây dựng một Web Dashboard tự xây để trực quan hóa dữ liệu chi phí. Thay vì dùng một dịch vụ BI có sẵn, chúng ta tự phát triển toàn bộ để làm chủ hoàn toàn giao diện và dữ liệu, đồng thời giữ chi phí ở mức thấp nhât.

Web Dash board gồm hai phần chính:

- **Backend** gồm một hàm Lambda API đọc dữ liệu chi phí từ S3 và một API Gateway để expose endpoint cho Web gọi.
- **Frontend** là một trang Web tĩnh dùng `Chart.js` để vẽ biểu đồ, được host lên S3 và phân phối qua CloudFront.

![Dashboard](/workshop-fcaj-intern/images/2-Proposal/diagram_architecture.png)

### Nội dung

1. [Backend](../5.6-Dashboard/5.6.1-Backend/)
2. [Frontend](../5.6-Dashboard/5.6.2-Frontend/)
3. [Xác thực với Cognito](../5.6-Dashboard/5.6.3-Authentication-Cognito/)



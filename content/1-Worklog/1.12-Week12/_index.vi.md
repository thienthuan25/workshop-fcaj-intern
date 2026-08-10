---
title: "Worklog Tuần 12"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 1.12. </b> "
---

### Mục tiêu tuần 12:

* Tiếp tục viết, rà soát và hoàn thiện Workshop CloudCost Insight theo hướng dẫn từng bước.
* Kiểm tra khả năng build Hugo và cập nhật Workshop lên GitHub Pages.
* Nghiên cứu chủ đề, nội dung và cách đăng bài blog trên AWS Study Group.
* Viết các bài blog chia sẻ kiến thức AWS, trải nghiệm xây dựng CloudCost Insight và định hướng mở rộng hệ thống.
* Chuẩn bị kịch bản, dữ liệu và môi trường để quay demo project.
* Quay video demo, trình bày toàn bộ luồng hoạt động của CloudCost Insight.
* Duy trì phối hợp cùng nhóm: trao đổi kế hoạch trước khi làm và tổng hợp kết quả sau mỗi ngày.

### Các công việc triển khai trong tuần:

| Thứ | Công việc | Ngày bắt đầu | Ngày hoàn thành | Nguồn tài liệu |
| --- | --- | --- | --- | --- |
| 2 | - Tiếp tục viết Workshop step-by-step: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Hoàn thiện các phần triển khai hạ tầng, Lambda Collector, Lambda Analyzer, giám sát và cảnh báo. <br>&emsp; + Bổ sung hướng dẫn kiểm thử SQS partial batch failure, Dead Letter Queue và xử lý lỗi khi Analyzer không đọc được dữ liệu từ S3. <br>&emsp; + Chuẩn bị hình ảnh minh họa, log và kết quả mong đợi cho từng bước kiểm thử. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 27/07/2026 | 27/07/2026 | - FCAJ Workshop Template. <br> - AWS Lambda Documentation: <br> https://docs.aws.amazon.com/lambda/ |
| 3 | - Hoàn thiện Workshop về Dashboard, bảo mật và CI/CD: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Hoàn thiện hướng dẫn xây dựng Web Dashboard, xác thực bằng Amazon Cognito và cấu hình API Gateway JWT Authorizer. <br>&emsp; + Bổ sung các nội dung kiểm thử JWT authentication, CORS và cập nhật phiên bản frontend trên CloudFront. <br>&emsp; + Hoàn thiện phần CI/CD, branch protection và dọn dẹp tài nguyên. <br>&emsp; + Kiểm tra Hugo Workshop build thành công và cập nhật nội dung lên GitHub Pages. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 28/07/2026 | 28/07/2026 | - Amazon Cognito Documentation: <br> https://docs.aws.amazon.com/cognito/ <br> - GitHub Actions Documentation: <br> https://docs.github.com/en/actions |
| 4 | - Nghiên cứu và viết Blog 1, Blog 2: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Nghiên cứu cách xây dựng nội dung và đăng bài trên AWS Study Group. <br>&emsp; + Viết Blog 1 về những kiến thức và trải nghiệm thực tế khi xây dựng hệ thống CloudCost Insight theo kiến trúc Serverless. <br>&emsp; + Nghiên cứu Amazon EventBridge Scheduler và viết Blog 2 về khả năng thay thế cron job trong các hệ thống AWS. <br>&emsp; + Rà soát nội dung, hình ảnh và tài liệu tham khảo trước khi đăng bài. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 29/07/2026 | 29/07/2026 | - AWS Study Group. <br> - AWS Compute Blog: <br> https://aws.amazon.com/blogs/compute/ <br> - Amazon EventBridge Scheduler Documentation: <br> https://docs.aws.amazon.com/scheduler/ |
| 5 | - Nghiên cứu và viết Blog 3; chuẩn bị quay demo project: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Nghiên cứu Amazon Bedrock AgentCore và ý tưởng mở rộng CloudCost Insight thành AI FinOps Agent. <br>&emsp; + Viết Blog 3 về Amazon Bedrock AgentCore, AgentCore Runtime, Gateway, Identity, Memory và Observability. <br>&emsp; + Chuẩn bị kịch bản demo, kiểm tra lại môi trường AWS, dữ liệu chi phí mô phỏng, Dashboard và các email cảnh báo. <br>&emsp; + Xác định các nội dung cần trình bày trong video: kiến trúc, luồng xử lý, bảo mật, kiểm thử và CI/CD. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 30/07/2026 | 30/07/2026 | - Amazon Bedrock AgentCore Documentation. <br> - CloudCost Insight Workshop. |
| 6 | - Quay demo CloudCost Insight và rà soát tài liệu: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Quay video demo toàn bộ hệ thống CloudCost Insight. <br>&emsp; + Trình bày kiến trúc Serverless, luồng thu thập dữ liệu, phân tích chi phí, cảnh báo SNS, DLQ, CloudWatch Alarm, Dashboard và Cognito authentication. <br>&emsp; + Trình bày quy trình CI/CD với GitHub Actions, HCP Terraform và branch protection. <br>&emsp; + Kiểm tra lại Workshop, các bài blog và kết quả demo. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 31/07/2026 | 31/07/2026 | - CloudCost Insight Workshop. <br> - AWS Management Console. <br> - GitHub Repository. |

### Kết quả đạt được tuần 12:

* **Hoàn thiện Workshop step-by-step:** Đã tiếp tục viết, rà soát và hoàn thiện Workshop CloudCost Insight theo hướng dẫn từng bước. Workshop mô tả toàn bộ quy trình từ chuẩn bị môi trường, triển khai hạ tầng bằng Terraform, xây dựng Lambda, Dashboard, Cognito, kiểm thử hệ thống, CI/CD cho đến dọn dẹp tài nguyên.
* **Bổ sung đầy đủ nội dung kiểm thử và bảo mật:** Đã bổ sung các phần kiểm thử quan trọng như SQS partial batch failure, Dead Letter Queue, xử lý lỗi S3 tại Analyzer, xác thực JWT bằng Amazon Cognito, kiểm thử CORS và cập nhật frontend để tránh sử dụng phiên bản bị cache cũ. Các phần được kèm theo kết quả mong đợi, log và hình ảnh minh họa.
* **Kiểm tra và cập nhật Workshop:** Đã kiểm tra Hugo Workshop build thành công, rà soát bố cục, code mẫu, hình ảnh và liên kết nội dung. Workshop được cập nhật lên GitHub Pages để có thể truy cập và thực hiện theo.
* **Nghiên cứu và đăng bài blog:** Đã nghiên cứu cách xây dựng nội dung blog kỹ thuật và hoàn thành ba bài viết trên AWS Study Group. Các bài viết chia sẻ trải nghiệm xây dựng CloudCost Insight, giới thiệu Amazon EventBridge Scheduler và đề xuất hướng mở rộng hệ thống thành AI FinOps Agent với Amazon Bedrock AgentCore.
* **Chuẩn bị demo project:** Đã chuẩn bị kịch bản demo, kiểm tra môi trường AWS, dữ liệu chi phí mô phỏng, Dashboard, Cognito authentication, cảnh báo SNS và các thành phần giám sát. Các nội dung demo được sắp xếp theo luồng hoạt động thực tế của hệ thống.
* **Hoàn thành quay demo CloudCost Insight:** Đã quay video demo trình bày kiến trúc và các luồng hoạt động chính của CloudCost Insight, bao gồm thu thập dữ liệu chi phí, phân tích bất thường, cảnh báo, xử lý lỗi, giám sát, Dashboard có xác thực người dùng và quy trình CI/CD tự động.
* **Phối hợp cùng nhóm:** Duy trì trao đổi kế hoạch công việc trước khi thực hiện và tổng hợp kết quả vào cuối mỗi ngày. Việc chia sẻ tiến độ giúp các thành viên nắm được tình hình thực hiện Workshop, bài blog và video demo của nhóm.
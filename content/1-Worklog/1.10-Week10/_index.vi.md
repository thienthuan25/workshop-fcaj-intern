---
title: "Worklog Tuần 10"
date: 2024-01-01
weight: 2
chapter: false
pre: " <b> 1.10. </b> "
---

### Mục tiêu tuần 10:

* Xây dựng web frontend cho dashboard (`index.html`, `style.css`, `script.js`), dùng Chart.js trực quan hóa dữ liệu chi phí.
* Host frontend lên AWS bằng S3 Web Hosting và CloudFront với HTTPS.
* Bổ sung xác thực Dashboard bằng Amazon Cognito và JWT Authorizer cho API Gateway.
* Kiểm thử end-to-end toàn bộ luồng Dashboard, từ đăng nhập Cognito tới API và dữ liệu chi phí.
* Hoàn thiện và nâng cấp Dashboard: tinh chỉnh biểu đồ, thêm chế độ sáng/tối và chuyển đổi song ngữ EN/VI.
* Duy trì phối hợp cùng nhóm: trao đổi kế hoạch trước khi làm và tổng hợp kết quả sau mỗi ngày.

### Các công việc triển khai trong tuần:

| Thứ | Công việc | Ngày bắt đầu | Ngày hoàn thành | Nguồn tài liệu |
| --- | --- | --- | --- | --- |
| 2 | - Viết web frontend (giao diện và logic): <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Viết `index.html` (cấu trúc trang) và `style.css` (giao diện). <br>&emsp; + Viết `script.js` gọi API endpoint, xử lý JSON và vẽ biểu đồ bằng Chart.js. <br>&emsp; + Vẽ các biểu đồ: xu hướng chi phí (đường ngưỡng + đánh dấu bất thường), top dịch vụ, lịch sử cảnh báo, KPI. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 13/07/2026 | 13/07/2026 | - Chart.js Documentation: <br> https://www.chartjs.org/docs/latest/ <br> - MDN Fetch API: <br> https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API |
| 3 | - Host frontend lên AWS (S3 + CloudFront): <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Tạo S3 bucket (Web Hosting) và upload 3 file giao diện bằng Terraform. <br>&emsp; + Cấu hình CloudFront (HTTPS) và Origin Access Control để bảo mật, chặn truy cập public trực tiếp vào S3. <br>&emsp; + Lấy link CloudFront để truy cập Dashboard. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 14/07/2026 | 14/07/2026 | - Amazon CloudFront + S3: <br> https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/GettingStarted.SimpleDistribution.html <br> - Terraform aws_cloudfront_distribution: <br> https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudfront_distribution |
| 4 | - Bổ sung xác thực Dashboard với Amazon Cognito: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Tạo Cognito User Pool, App Client và Cognito Domain bằng Terraform. <br>&emsp; + Cấu hình API Gateway JWT Authorizer để chỉ chấp nhận request có JWT hợp lệ. <br>&emsp; + Cập nhật CORS, chỉ cho phép domain CloudFront của Dashboard gọi API từ trình duyệt. <br>&emsp; + Tích hợp luồng đăng nhập Authorization Code Flow với PKCE vào `script.js`; bổ sung nút đăng nhập và đăng xuất. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 15/07/2026 | 15/07/2026 | - Amazon Cognito Developer Guide: <br> https://docs.aws.amazon.com/cognito/ <br> - API Gateway JWT Authorizer: <br> https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-jwt-authorizer.html |
| 5 | - Kiểm thử end-to-end và tinh chỉnh Dashboard: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Truy cập Dashboard qua link CloudFront trên trình duyệt và đăng nhập bằng Cognito. <br>&emsp; + Xác minh luồng: trình duyệt tới CloudFront/S3, Cognito xác thực và cấp JWT, Dashboard gọi API Gateway, Lambda API đọc dữ liệu từ S3. <br>&emsp; + Kiểm tra các biểu đồ hiển thị đúng dữ liệu chi phí và trạng thái bất thường. <br>&emsp; + Điều chỉnh kích thước biểu đồ donut cho cân đối, bổ sung tooltip hiển thị số tiền kèm ký hiệu `$`. <br>&emsp; + Thêm chức năng chuyển đổi giao diện sáng/tối (dark mode) bằng CSS variables. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 16/07/2026 | 16/07/2026 |  |
| 6 | - Thêm chức năng chuyển đổi song ngữ (EN/VI) và kiểm thử hoàn thiện: <br>&emsp; + Trao đổi với nhóm về kế hoạch công việc trong ngày trước khi bắt đầu. <br>&emsp; + Xây dựng từ điển song ngữ Anh/Việt cho các nhãn, tiêu đề, thông báo xác thực và biểu đồ. <br>&emsp; + Thêm nút chuyển ngôn ngữ, cập nhật giao diện và vẽ lại biểu đồ theo ngôn ngữ được chọn. <br>&emsp; + Kiểm thử lại toàn bộ Dashboard ở cả hai ngôn ngữ, bao gồm đăng nhập, tải dữ liệu, biểu đồ và chế độ sáng/tối. <br>&emsp; + Cuối ngày tổng hợp và chia sẻ kết quả với nhóm. | 17/07/2026 | 17/07/2026 |  |

### Kết quả đạt được tuần 10:

* **Hoàn thành web frontend cho Dashboard:** Đã xây dựng giao diện Dashboard được tổ chức thành 3 file riêng biệt (`index.html`, `style.css`, `script.js`) theo nguyên tắc separation of concerns. Dashboard dùng thư viện Chart.js để trực quan hóa dữ liệu chi phí với các biểu đồ xu hướng chi phí theo ngày, đường ngưỡng, đánh dấu ngày bất thường, tỷ trọng theo dịch vụ, top dịch vụ tốn chi phí và các chỉ số KPI.
* **Host frontend lên AWS thành công:** Đã đưa Web Dashboard lên S3 kết hợp CloudFront và cung cấp đường dẫn HTTPS để người dùng truy cập. Origin Access Control được áp dụng để chỉ CloudFront có quyền đọc nội dung từ S3, ngăn truy cập public trực tiếp vào web bucket.
* **Bổ sung xác thực với Amazon Cognito:** Đã triển khai Cognito User Pool, App Client và Cognito Domain để quản lý người dùng. Dashboard sử dụng Authorization Code Flow với PKCE để người dùng đăng nhập và nhận JWT. API Gateway được cấu hình JWT Authorizer, chỉ cho phép request có token hợp lệ truy cập dữ liệu chi phí. CORS cũng được giới hạn để chỉ domain CloudFront của dự án có thể gọi API từ trình duyệt.
* **Kiểm thử end-to-end Web Dashboard:** Đã kiểm chứng thành công toàn bộ luồng hoạt động: người dùng truy cập Dashboard qua CloudFront, đăng nhập bằng Cognito, nhận JWT, sau đó Dashboard gọi API Gateway tới Lambda API và S3 để lấy dữ liệu chi phí. Biểu đồ hiển thị đúng dữ liệu và trạng thái bất thường.
* **Tinh chỉnh giao diện và thêm chế độ sáng/tối:** Đã điều chỉnh kích thước biểu đồ donut cho cân đối, bổ sung tooltip hiển thị số tiền kèm ký hiệu `$`. Thêm chức năng chuyển đổi giao diện sáng/tối bằng CSS variables, giúp người dùng lựa chọn giao diện phù hợp và cải thiện trải nghiệm sử dụng.
* **Thêm chức năng song ngữ (EN/VI):** Đã xây dựng cơ chế chuyển đổi song ngữ Anh/Việt cho nhãn, tiêu đề, thông báo xác thực và nhãn biểu đồ. Dashboard được kiểm thử lại ở cả hai ngôn ngữ, bảo đảm giao diện và dữ liệu hiển thị nhất quán.
* **Phối hợp cùng nhóm:** Duy trì thói quen làm việc nhóm hiệu quả trong suốt tuần. Trước khi bắt đầu công việc mỗi ngày, tôi trao đổi kế hoạch với các thành viên trong nhóm, và cuối mỗi ngày tổng hợp lại kết quả đã làm để cả nhóm cùng nắm tiến độ.
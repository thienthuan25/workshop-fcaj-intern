---
title : "Triển khai hạ tầng"
date : 2024-01-01 
weight : 8
chapter : false
pre : " <b> 5.3.8 </b> "
---

Trước khi tiến hành triển khai hạ tầng, chúng ta cần tạo thêm một file có tên là `terraform/teraform.tfvars`.

Ở phần đầu tiên, chúng ta đã tạo file `variables.tf` để khai báo danh sách các biến (như tên dự án, môi trường, email...) và đặt các giá trị mặc định cho chúng. File `terraform.tfvars` chính là nơi chúng ta điền các giá trị thực tế mà bạn muốn áp dụng cho dự án. Việc tách biệt này giúp bộ code Terraform trở nên linh hoạt và có thể tái sử dụng. Khi bạn muốn đưa code này cho người khác chạy, hoặc muốn đổi sang tài khoản email khác, đổi tên dự án, bạn chỉ cần sửa file `terraform.tfvars` này mà không sợ làm hỏng các đoạn code cấu hình hạ tầng phức tạp ở những file khác. Terraform sẽ tự động tìm và nạp các giá trị từ file có tên `.tfvars` này khi chạy.

```hcl
# important
aws_region          = "us-east-1" # region mà bạn muốn đặt cho dự án
environment         = "dev" # môi trường của dự án (dev, test, prod)
project_name        = "[TÊN_DỰ_ÁN_CỦA_BẠN]"
alert_email         = "[EMAIL]" # email mà bạn muốn nhận thông báo
schedule_expression = "rate(1 day)" # Lịch trình chạy (đặt tùy chọn)
```

Sau khi hoàn thành các file trên, tại thư mục dự án chứa các file Terraform trên Terminal, chúng ta sẽ thực hiện các lệnh sau để tiến hành triển khai:

**1.** Xem trước các tài nguyên được tạo.

```bash
terraform plan
```

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_1.png)

**2.** Triển khai hạ tầng.

```bash
terraform apply
```
![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_2.png)

- Gõ `yes` để xác nhận.

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_3.png)

**3.** Sau khi hoàn tất, Terraform sẽ hiển thị các giá trị outputs đã khai báo.

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_5.png)

**4.** Kiểm tra và xác nhận Email.

Sau khi triển khai, bạn hãy kiểm tra các tài nguyên đã được tạo trên AWS Console.

- S3 Bucket:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_6.png)

- SQS Queue:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_7.png)

- SNS Topic:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_8.png)

- EventBridge rule:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_9.png)

- Xác nhận Email:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_10.png)

Click `Confirm subscription`:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_11.png)

### Nội dung tiếp theo

- [Triển khai Lambda Collector](5-Workshop/5.4-Deploy-Lambda/)





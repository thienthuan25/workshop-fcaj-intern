---
title : "Chuẩn bị Code Terraform"
date : 2024-01-01
weight : 3
chapter : false
pre : " <b> 5.2.3. </b> "
---

### Công cụ cần cài đặt

Trong workshop này, chúng ta thực hiện các thao tác dòng lệnh trên môi trường **WSL2** (Windows Subsystem for Linux) thay vì **Command Prompt** (CMD) hoặc **PowerShell** của Windows. Có một số lý do chính cho lựa chọn này:

+ **Môi trường Linux thống nhất:** Hầu hết các công cụ hạ tầng như **Terraform**, **AWS CLI** và các script triển khai đều được thiết kế và tối ưu cho môi trường Unix/Linux. WSL2 cung cấp một môi trường Linux thật sự ngay trên Windows, giúp tránh các khác biệt về đường dẫn, biến môi trường và cách xử lý dòng lệnh so với CMD hay PowerShell.
+ **Đồng nhất với môi trường triển khai thực tế:** Các server và pipeline CI/CD trên AWS thường chạy trên Linux. Làm việc trên WSL2 giúp môi trường phát triển của bạn gần với môi trường production, giảm rủi ro lỗi phát sinh do khác biệt hệ điều hành.
+ **Hỗ trợ tốt các công cụ dòng lệnh:** WSL2 hỗ trợ đầy đủ các tiện ích Linux như **bash**, các lệnh xử lý chuỗi và quản lý file, giúp việc viết và chạy script trở nên thuận tiện hơn.
+ **Tương thích tốt với công cụ phát triển:** WSL2 tích hợp mượt mà với các trình soạn thảo như **Visual Studio Code**, cho phép vừa viết code vừa chạy lệnh trong cùng một môi trường.

Nhìn chung, WSL2 mang lại trải nghiệm nhất quán và ổn định hơn khi làm việc với các công cụ hạ tầng đám mây, đặc biệt là Terraform.

Đối với hệ điều hành **macOS**, bạn chỉ cần mở Terminal và trải nghiệm sử dụng gần như hoàn toàn tương đồng với môi trường WSL trên Windows.

Trước khi bắt đầu, hãy bảo đảm rằng các công cụ sau đã được cài đặt:

+ **Terraform** phiên bản 1.5 trở lên để triển khai hạ tầng theo mô hình Infrastructure as Code.
+ **AWS CLI** để tương tác với các dịch vụ AWS và thực hiện các bước kiểm thử từ dòng lệnh.
+ **Python** phiên bản 3.12 trở lên để phát triển các hàm Lambda.

Bạn có thể kiểm tra các công cụ đã được cài đặt thành công bằng cách chạy các lệnh sau:

```bash
terraform version
aws --version
python3 --version
```

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_1.png)

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_2.png)

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_3.png)

### Cấu hình AWS Credentials cho CLI

Trên cửa sổ terminal, cấu hình AWS credentials để AWS CLI có thể xác thực và thực thi các lệnh trong suốt quá trình triển khai cũng như kiểm thử hệ thống:

```bash
aws configure
```

Lần lượt nhập các thông tin sau:

```
AWS Access Key ID       [None]: <ACCESS_KEY_ID>
AWS Secret Access Key   [None]: <SECRET_ACCESS_KEY>
Default region name     [None]: us-east-1
Default output format   [None]:
```

Sau khi cấu hình xong, hãy giới hạn quyền truy cập vào file credentials để chỉ tài khoản hiện tại có thể đọc được:

```bash
chmod 600 ~/.aws/credentials
```

Kiểm tra lại credentials để bảo đảm việc xác thực đã thành công:

```bash
aws sts get-caller-identity
```

### Cấu hình nền tảng Terraform

Tại thư mục gốc của dự án, tạo thư mục mới có tên là `terraform`. Thư mục này chứa các file Terraform dùng để triển khai hạ tầng AWS.

Tạo file `version.tf` để khai báo phiên bản Terraform, cấu hình kết nối với HCP Terraform và thiết lập AWS Provider. Thay `TEN-TO-CHUC` bằng tên Organization của bạn và `TEN-WORKSPACE` bằng tên Workspace đã tạo trên HCP Terraform.

```hcl
terraform {
  required_version = ">= 1.5.0"

  cloud {
    organization = "TEN-TO-CHUC"

    workspaces {
      name = "TEN-WORKSPACE"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.92"
    }

    # provider archive
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "CloudCost-Insight"
      ManageBy    = "Terraform"
      Environment = var.environment
    }
  }
}
```

### Kết nối và khởi tạo tài nguyên

Trong terminal, chuyển đến thư mục chứa các file Terraform, sau đó chạy lệnh dưới đây để đăng nhập và kết nối Terraform CLI với HCP Terraform:

```bash
terraform login
```

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_4.png)

+ Mở đường dẫn được hiển thị trên cửa sổ terminal:

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_5.png)

+ Nhập **Description** nếu muốn để dễ dàng nhận biết token.
+ Chọn thời gian hết hạn cho API Token.
+ Nhấn **Generate token**.

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_6.png)

+ Copy Token vừa tạo vào Terminal:

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_7.png)

+ Sau khi đăng nhập thành công, khởi tạo Terraform để tải tài provider và kết nối **Workspace**:

```bash
cd terraform
terraform init
```

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_8.png)

Sau khi hoàn thành các bước trên, môi trường làm việc đã được cấu hình đầy đủ và sẵn sàng để triển khai hệ thống **CloudCost Insight** trong các phần tiếp theo.

### Chuẩn bị Git và cấu hình .gitignore

Vì dự án được quản lý bằng **Git** và đẩy mã nguồn lên **GitHub**, chúng ta cần cấu hình để loại bỏ các file không nên đưa lên repository. Việc này giúp bảo vệ thông tin nhạy cảm và giữ cho repository gọn gàng.

Tại thư mục gốc của dự án, tạo file `.gitignore` với nội dung sau:

```gitignore
# ===== Hugo =====
public/
.hugo_build.lock

# ===== System & IDE =====
.DS_Store
.vscode/

# ===== Terraform =====
.terraform/
*.tfstate
*.tfstate.*
*.tfvars
crash.log
```

- Thư mục `.terraform/`: Đây là nơi Terraform lưu cache các provider được tải về khi chạy `terraform init`. Thư mục này có dung lượng lớn và có thể tái tạo dễ dàng nên không cần đưa lên repository.
- Các file `*.tfstate`, `*.tfstate.*`: Đây là file trạng thái hạ tầng, có thể chứa thông tin nhạy cảm. Vì dự án sử dụng HCP Terraform để quản lý remote state, trạng thái đã được lưu tập trung trên HCP nên không cần lưu cục bộ trong repository.
- Các file `*.tfvars`: Đây là nơi chứa giá trị biến thật như email nhận cảnh báo, nên không đưa lên repository để tránh lộ thông tin. Chúng ta chỉ giữ lại file mẫu `*.tfvars.example`.

### Nội dung tiếp theo

- [Dựng hạ tầng bằng Terraform](5-Workshop/5.3-Infrastructure/)
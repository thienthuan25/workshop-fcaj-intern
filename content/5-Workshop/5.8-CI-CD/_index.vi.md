---
title : "CI/CD"
date : 2024-01-01
weight : 8
chapter : false
pre : " <b> 5.8. </b> "
---

Trong phần này, dự án CloudCost Insight áp dụng quy trình CI/CD bằng GitHub Actions nhằm tự động kiểm tra chất lượng mã nguồn và triển khai hạ tầng AWS một cách nhất quán.

Mỗi thay đổi được thực hiện trên nhánh riêng và gửi qua Pull Request sẽ được hệ thống tự động kiểm tra. Quá trình này bao gồm: lint và chạy unit test cho mã Python Lambda, kiểm tra định dạng và xác thực cấu hình Terraform, tạo Terraform plan, đồng thời kiểm tra cú pháp JavaScript của Dashboard. Thay đổi chỉ được merge vào nhánh main khi tất cả các bài kiểm tra đều thành công và được phê duyệt.

Sau khi gộp mã, workflow CD tự động chạy Terraform Apply thông qua HCP Terraform để cập nhật hạ tầng AWS. Quy trình này giúp giảm rủi ro triển khai thủ công, phát hiện lỗi sớm và bảo đảm môi trường triển khai luôn nhất quán với mã nguồn.

### Tạo Workflow CI

**1.** Đầu tiên, chúng ta sẽ cấu hình file **ci.yml** trong thư mục **.github/workflows**:

```yaml
# Tên hiển thị của workflow trên tab Actions của GitHub
name: CI

# Chạy CI khi tạo/cập nhật Pull Request vào main
# hoặc khi có commit được push trực tiếp lên main
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

# CI chỉ cần đọc mã nguồn để kiểm tra, không có quyền ghi hoặc deploy
permissions:
  contents: read

jobs:
  # Job 1: Kiểm tra cú pháp mã nguồn Python của các Lambda functions
  python:
    name: Check Python Lambda code
    runs-on: ubuntu-latest

    steps:
      # Tải mã nguồn để kiểm tra
      - name: Checkout source
        uses: actions/checkout@v5

      # Cài đặt Python theo phiên bản Lambda đang sử dụng
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      # Biên dịch các file Python để phát hiện lỗi cú pháp
      - name: Check Python syntax
        run: |
          python -m compileall terraform/lambda terraform/test

  # Job 2: Kiểm tra định dạng và tính hợp lệ của cấu hình Terraform
  terraform:
    name: Validate Terraform
    runs-on: ubuntu-latest

    steps:
      # Tải mã nguồn Terraform về máy ảo CI
      - name: Checkout source
        uses: actions/checkout@v5

      # Cài đặt Terraform với đúng phiên bản của dự án
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.5.7"
          # Không bọc output Terraform để log hiển thị rõ ràng hơn
          terraform_wrapper: false

      # Kiểm tra các file .tf có đúng định dạng chuẩn hay không
      # -check chỉ báo lỗi, không tự chỉnh sửa file
      - name: Check Terraform formatting
        working-directory: terraform
        run: terraform fmt -check -recursive

      # Khởi tạo Terraform để tải provider, nhưng không kết nối HCP Terraform backend
      # CI chỉ kiểm tra cấu hình và không tạo, sửa hoặc xóa tài nguyên AWS
      - name: Initialize Terraform without remote backend
        working-directory: terraform
        run: terraform init -backend=false

      # Kiểm tra cú pháp, biến, resource và các tham chiếu trong Terraform
      - name: Validate Terraform configuration
        working-directory: terraform
        run: terraform validate

  # Job 3: Kiểm tra cú pháp JavaScript của Web Dashboard
  frontend:
    name: Check dashboard JavaScript
    runs-on: ubuntu-latest

    steps:
      # Tải mã nguồn frontend về máy ảo CI
      - name: Checkout source
        uses: actions/checkout@v5

      # Kiểm tra cú pháp script.js mà không chạy Dashboard trên trình duyệt
      - name: Check JavaScript syntax
        run: node --check terraform/web/script.js
```

**2.** Tạo Unit test cho Lambda

Bạn cần tạo thư mục **tests** từ thư mục gốc của dự án rồi tạo file **conftest.py** trong thư mục này:

```python
import importlib.util
from pathlib import Path

# pyrefly: ignore [missing-import]
import pytest

# Xác định thư mục gốc của project từ vị trí file tests/conftest.py.
# parents[1] tương ứng với thư mục cha của thư mục tests.
ROOT_DIR = Path(__file__).resolve().parents[1]


# Fixture tự động chạy trước mỗi test.
# Thiết lập biến môi trường giả để boto3 không dùng AWS credentials thật
# và các Lambda handler có đủ cấu hình cần thiết khi được import.
@pytest.fixture(autouse=True)
def aws_environment(monkeypatch):
    """Cấu hình môi trường giả phục vụ unit test Lambda."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")

    # Các giá trị tài nguyên AWS giả dùng trong quá trình test.
    monkeypatch.setenv("BUCKET_NAME", "test-cost-data-bucket")
    monkeypatch.setenv(
        "QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/events"
    )
    monkeypatch.setenv(
        "SNS_TOPIC_ARN",
        "arn:aws:sns:us-east-1:123456789012:cost-alerts",
    )

    # Các biến cấu hình cho logic phân tích chi phí.
    monkeypatch.setenv("COST_THRESHOLD_USD", "10")
    monkeypatch.setenv("SPIKE_MULTIPLIER", "1.5")
    monkeypatch.setenv("HISTORY_DAYS", "7")
    monkeypatch.setenv("MAX_DAYS", "30")


def load_lambda_module(module_name: str, relative_path: str):
    """
    Import trực tiếp từng file handler.py bằng tên module riêng.

    Cách này tránh xung đột vì Collector, Analyzer và API
    đều có thể sử dụng tên file handler.py.
    """
    # Tạo đường dẫn tuyệt đối đến file Lambda cần kiểm thử.
    path = ROOT_DIR / relative_path

    # Tạo thông tin module từ đường dẫn file.
    spec = importlib.util.spec_from_file_location(module_name, path)

    # Tạo module Python mới và thực thi mã nguồn trong file handler.py.
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Trả về module để các file test gọi hàm cần kiểm thử.
    return module
```

File **conftest.py** cung cấp cấu hình và các thành phần dùng chung cho toàn bộ quá trình unit test bằng pytest. Mục đích của file này bao gồm việc thiết lập môi trường ảo để đảm bảo các hàm Lambda khi chạy test sẽ sử dụng các biến môi trường và AWS credentials giả. Điều này giúp hệ thống test hoàn toàn cô lập, không gọi nhầm API thật của AWS gây phát sinh chi phí hay lỗi không mong muốn.

File cũng cung cấp tiện ích **load_lambda_module** giúp tải các file Lambda một cách độc lập. Do các Lambda đều dùng chung tên file là **handler.py**, tiện ích này giúp import chúng dưới các tên module riêng biệt để tránh xung đột mã nguồn.

Tiếp theo, chúng ta tạo file **test_analyzer.py**:

```python
# Import hàm hỗ trợ để tải trực tiếp Lambda Analyzer từ file handler.py.
from conftest import load_lambda_module


def sample_cost_data():
    """
    Tạo dữ liệu Cost Explorer giả.

    Dữ liệu này thay thế kết quả gọi AWS Cost Explorer thật,
    giúp unit test chạy độc lập và không phát sinh chi phí AWS.
    """
    return {
        "ResultsByTime": [
            {
                "Groups": [
                    {
                        "Keys": ["Amazon EC2"],
                        "Metrics": {"UnblendedCost": {"Amount": "8.50"}},
                    },
                    {
                        "Keys": ["Amazon S3"],
                        "Metrics": {"UnblendedCost": {"Amount": "2.00"}},
                    },
                    {
                        "Keys": ["AWS Lambda"],
                        "Metrics": {"UnblendedCost": {"Amount": "1.25"}},
                    },
                ]
            }
        ]
    }


def test_compute_total_and_top_services():
    """
    Kiểm tra Analyzer tính đúng tổng chi phí
    và sắp xếp các dịch vụ theo chi phí giảm dần.
    """
    # Tải module Analyzer để gọi trực tiếp hàm cần kiểm thử.
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # Phân tích dữ liệu chi phí giả.
    result = analyzer.compute_total_and_top(sample_cost_data())

    # Tổng chi phí kỳ vọng: 8.50 + 2.00 + 1.25 = 11.75 USD.
    assert result["total_cost"] == 11.75

    # Danh sách dịch vụ phải được sắp xếp theo chi phí từ cao xuống thấp.
    assert result["top_services"] == [
        ("Amazon EC2", 8.5),
        ("Amazon S3", 2.0),
        ("AWS Lambda", 1.25),
    ]


def test_classify_severity_returns_info_for_normal_cost():
    """Kiểm tra chi phí bình thường được phân loại ở mức INFO."""
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # Chi phí 6 USD chưa vượt ngưỡng 10 USD và không tăng đột biến.
    severity, reasons = analyzer.classify_severity(total=6, avg=5)

    # Không cần gửi cảnh báo khi chi phí nằm trong mức bình thường.
    assert severity == "INFO"
    assert reasons == []


def test_classify_severity_returns_warning_when_threshold_exceeded():
    """Kiểm tra chi phí vượt ngưỡng ngân sách được phân loại WARNING."""
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # Chi phí 12 USD vượt ngưỡng ngân sách 10 USD,
    # nhưng chưa đủ lớn để được xem là tăng đột biến.
    severity, reasons = analyzer.classify_severity(total=12, avg=9)

    assert severity == "WARNING"
    assert "Budget threshold exceeded ($10.00)" in reasons


def test_classify_severity_returns_critical_for_cost_spike():
    """Kiểm tra chi phí tăng đột biến được phân loại CRITICAL."""
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # Chi phí 20 USD cao hơn 1.5 lần mức trung bình 5 USD,
    # vì vậy được nhận diện là một đột biến chi phí.
    severity, reasons = analyzer.classify_severity(total=20, avg=5)

    assert severity == "CRITICAL"

    # Xác nhận lý do cảnh báo có thông tin về tăng đột biến chi phí.
    assert any("Cost spike detected" in reason for reason in reasons)
```

File **test_analyzer.py** chứa các kịch bản kiểm thử dành riêng cho Lambda Analyzer. Nhiệm vụ của nó là kiểm chứng logic tính toán chi phí bằng cách đảm bảo hệ thống đọc đúng định dạng dữ liệu giả lập, cộng dồn chính xác tổng chi phí trong ngày và xếp hạng đúng các dịch vụ tiêu tốn nhiều tiền nhất.

File này cũng đảm bảo tính chính xác của cơ chế cảnh báo thông qua việc kiểm tra kỹ lưỡng các điều kiện phân loại mức độ nghiêm trọng dựa trên ngưỡng ngân sách và mức độ tăng đột biến so với trung bình lịch sử. Điều này đặc biệt quan trọng để ngăn ngừa rủi ro báo động giả hoặc bỏ sót các sự cố vượt chi phí thực sự.

Tiếp theo, chúng ta tạo file **test_api.py**:

```python
# Import hàm hỗ trợ để tải trực tiếp Lambda API từ file handler.py.
from conftest import load_lambda_module


def test_parse_daily_returns_total_and_services():
    """
    Kiểm tra Lambda API đọc đúng dữ liệu Cost Explorer của một ngày,
    tính tổng chi phí và nhóm chi phí theo từng dịch vụ.
    """
    # Tải module API Lambda để gọi hàm parse_daily cần kiểm thử.
    api = load_lambda_module(
        "api_handler",
        "terraform/lambda/api/handler.py",
    )

    # Dữ liệu Cost Explorer giả của ngày 2026-07-15.
    # Không gọi Cost Explorer thật trong unit test.
    cost_data = {
        "ResultsByTime": [
            {
                "TimePeriod": {"Start": "2026-07-15"},
                "Groups": [
                    {
                        "Keys": ["Amazon EC2"],
                        "Metrics": {"UnblendedCost": {"Amount": "5.25"}},
                    },
                    {
                        "Keys": ["Amazon S3"],
                        "Metrics": {"UnblendedCost": {"Amount": "1.50"}},
                    },
                ],
            }
        ]
    }

    # Phân tích dữ liệu giả, nhận ngày, tổng chi phí và chi phí từng dịch vụ.
    day, total, services = api.parse_daily(cost_data)

    # Xác nhận API lấy đúng ngày từ TimePeriod.
    assert day == "2026-07-15"

    # Xác nhận tổng chi phí: 5.25 + 1.50 = 6.75 USD.
    assert total == 6.75

    # Xác nhận chi phí được nhóm đúng theo từng dịch vụ AWS.
    assert services == {
        "Amazon EC2": 5.25,
        "Amazon S3": 1.5,
    }


def test_cors_response_returns_json_response():
    """
    Kiểm tra hàm tạo HTTP response của API Lambda.

    Response phải có mã trạng thái, header JSON
    và body được chuyển thành chuỗi JSON.
    """
    # Tải module API Lambda.
    api = load_lambda_module(
        "api_handler",
        "terraform/lambda/api/handler.py",
    )

    # Tạo response mẫu với HTTP status 200 và dữ liệu JSON đơn giản.
    response = api._response(200, {"status": "ok"})

    # Xác nhận Lambda trả về mã trạng thái HTTP chính xác.
    assert response["statusCode"] == 200

    # Xác nhận response được khai báo là dữ liệu JSON.
    assert response["headers"]["Content-Type"] == "application/json"

    # Xác nhận body đã được chuyển đổi thành chuỗi JSON đúng định dạng.
    assert response["body"] == '{"status": "ok"}'
```

File **test_api.py** tập trung kiểm thử các chức năng của Lambda API. Mục đích chính là kiểm tra logic trích xuất dữ liệu, đảm bảo API có thể phân tích chính xác cấu trúc dữ liệu thô giả lập từ Cost Explorer, lấy đúng ngày tháng, tính toán chuẩn xác tổng chi phí và nhóm chi phí theo từng dịch vụ riêng biệt.

File này cũng đảm bảo định dạng phản hồi bằng cách kiểm tra xem hàm Lambda có tạo ra đúng cấu trúc kết quả mà API Gateway yêu cầu hay không. Việc này rất quan trọng để đảm bảo Web Dashboard có thể đọc được dữ liệu mà không gặp lỗi định dạng.

Tiếp theo, chúng ta tạo file **test_collector.py**:

```python
# MagicMock tạo các đối tượng giả lập để unit test không gọi AWS thật.
from unittest.mock import MagicMock

# Import hàm hỗ trợ để tải trực tiếp Lambda Collector từ file handler.py.
from conftest import load_lambda_module


def test_get_cost_data_calls_cost_explorer():
    """
    Kiểm tra Collector gọi AWS Cost Explorer với đúng tham số
    để lấy chi phí theo ngày và theo từng dịch vụ.
    """
    # Tải module Lambda Collector cần kiểm thử.
    collector = load_lambda_module(
        "collector_handler",
        "terraform/lambda/collector/handler.py",
    )

    # Thay thế Cost Explorer client thật bằng mock.
    # Nhờ đó test không cần AWS credentials và không gọi API AWS.
    collector.ce_client = MagicMock()
    collector.ce_client.get_cost_and_usage.return_value = {"ResultsByTime": []}

    # Gọi hàm lấy dữ liệu chi phí trong khoảng thời gian một ngày.
    result = collector.get_cost_data("2026-07-01", "2026-07-02")

    # Xác nhận Collector trả về cấu trúc dữ liệu mong đợi.
    assert result == {
        "ResultsByTime": [],
        "GroupDefinitions": [{"Type": "DIMENSION", "Key": "SERVICE"}],
    }

    # Xác nhận hàm gọi Cost Explorer đúng một lần với đúng cấu hình.
    # Dữ liệu được lấy theo ngày, dùng chỉ số UnblendedCost
    # và được nhóm theo AWS service.
    collector.ce_client.get_cost_and_usage.assert_called_once_with(
        TimePeriod={"Start": "2026-07-01", "End": "2026-07-02"},
        Granularity="DAILY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )


def test_save_to_s3_uses_partitioned_key():
    """
    Kiểm tra Collector lưu dữ liệu vào S3 theo cấu trúc phân vùng
    year/month/day để dễ quản lý và truy vấn dữ liệu chi phí.
    """
    collector = load_lambda_module(
        "collector_handler",
        "terraform/lambda/collector/handler.py",
    )

    # Thay thế S3 client thật bằng mock để không ghi file lên AWS S3.
    collector.s3_client = MagicMock()

    # Lưu dữ liệu mẫu với ngày 2026-07-15.
    key = collector.save_to_s3({"ResultsByTime": []}, "2026-07-15")

    # Xác nhận đường dẫn S3 được tạo đúng theo cấu trúc phân vùng.
    assert key == "cost-data/year=2026/month=07/day=15/cost_2026-07-15.json"

    # Xác nhận Collector thực hiện một lần gọi S3 put_object.
    collector.s3_client.put_object.assert_called_once()

    # Lấy các tham số đã được truyền vào hàm put_object.
    call = collector.s3_client.put_object.call_args.kwargs

    # Xác nhận dữ liệu được ghi vào bucket giả đã cấu hình trong conftest.py.
    assert call["Bucket"] == "test-cost-data-bucket"
    assert call["Key"] == key
    assert call["ContentType"] == "application/json"


def test_send_event_to_sqs_contains_expected_values():
    """
    Kiểm tra Collector gửi event vào SQS sau khi lưu dữ liệu vào S3.

    Event cần có ngày, S3 key và tổng chi phí để Analyzer xử lý tiếp.
    """
    collector = load_lambda_module(
        "collector_handler",
        "terraform/lambda/collector/handler.py",
    )

    # Thay thế SQS client thật bằng mock để không gửi message lên AWS.
    collector.sqs_client = MagicMock()

    # Gửi event mẫu chứa ngày, vị trí file S3 và tổng chi phí.
    collector.send_event_to_sqs(
        "2026-07-15",
        "cost-data/example.json",
        12.34,
    )

    # Xác nhận Collector gửi đúng một message vào SQS.
    collector.sqs_client.send_message.assert_called_once()

    # Lấy các tham số của lần gọi send_message.
    call = collector.sqs_client.send_message.call_args.kwargs

    # Xác nhận message được gửi đến queue events.
    assert call["QueueUrl"].endswith("/events")

    # Xác nhận nội dung message có các trường dữ liệu cần thiết.
    assert '"date": "2026-07-15"' in call["MessageBody"]
    assert '"total_cost": 12.34' in call["MessageBody"]
```

File **test_collector.py** kiểm tra toàn bộ chuỗi quy trình làm việc của Lambda Collector. Vì đây là thành phần tương tác trực tiếp với các dịch vụ AWS, file này sử dụng kỹ thuật giả lập thông qua **MagicMock** để không tốn phí. Mục đích chính là kiểm tra kết nối Cost Explorer nhằm đảm bảo hàm gọi API AWS truyền đúng các tham số cấu hình.

Quá trình kiểm tra logic lưu trữ S3 xác nhận dữ liệu phân tích được ghi đúng vào Bucket mong muốn và hệ thống sinh ra đường dẫn file chuẩn xác.

Cuối cùng, việc đảm bảo luồng sự kiện kiểm tra nội dung tin nhắn gửi vào SQS Queue xem có chứa đầy đủ các khóa dữ liệu thiết yếu để Lambda Analyzer có thể tiếp nhận và xử lý.

Kế tiếp, bạn cần tạo file **requirements-dev.txt** ở thư mục gốc của dự án:

```text
boto3>=1.34,<2
pytest>=8,<10
ruff>=0.6,<1
```

File này có nhiệm vụ liệt kê các thư viện Python chỉ dành riêng cho quá trình phát triển và kiểm thử. Những thư viện này không được đóng gói lên môi trường AWS Lambda thực tế.

Sau đó, tiến hành tạo file **pyproject.toml**:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]
```

File này giúp chuẩn hóa và tối ưu quy trình CI/CD. Chức năng cụ thể bao gồm giới hạn phạm vi tìm kiếm kiểm thử mặc định tại thư mục tests để giảm thiểu độ trễ. Nó cũng xác định phiên bản môi trường đích là **Python 3.12** nhằm đảm bảo sự đồng nhất tuyệt đối với hệ thống AWS Lambda.

Cuối cùng, kích hoạt các tập quy tắc cốt lõi nhằm kiểm soát lỗi cú pháp và đảm bảo tính toàn vẹn của mã nguồn, đồng thời vô hiệu hóa quy tắc giới hạn độ dài dòng để tạo sự linh hoạt khi khai báo các cấu trúc dữ liệu phức tạp.

Để tiếp tục, bạn hãy kích hoạt **venv** bằng dòng lệnh trên Terminal như sau:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Cài đặt **dependency** và chạy kiểm tra:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
ruff check terraform/lambda tests
```

Tự động sửa các lỗi logic bằng lệnh:

```bash
ruff check terraform/lambda tests --fix
```

Tự động định dạng lại code:

```bash
ruff format terraform/lambda tests
```

Trong lúc chạy các dòng lệnh, trên cửa sổ Terminal có thể xuất hiện thông báo thất bại nếu code của bạn bị lỗi định dạng hoặc không đồng bộ. Bạn có thể tự sửa lại lỗi rồi chạy lại các lệnh kiểm tra. Kết quả mong đợi sẽ hiển thị như hình dưới đây.

![CI/CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/ci_2.png)

Sau khi đã vượt qua toàn bộ các bước kiểm tra, chúng ta tiến hành sửa Job **python** trong file **ci.yml**:

```yaml
python:
    name: Lint and test Python Lambda code
    runs-on: ubuntu-latest

    steps:
      - name: Checkout source
        uses: actions/checkout@v5

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt

      - name: Lint Python code
        run: ruff check terraform/lambda tests --output-format=github

      - name: Run unit tests
        run: pytest -q
```

Mục đích của việc sửa đổi Job **python** là để nâng cấp hệ thống CI từ việc chỉ kiểm tra lỗi cơ bản lên thành một bộ lọc kiểm duyệt mã nguồn toàn diện. Trước đây Job này chỉ gọi lệnh kiểm tra lỗi cú pháp, nhưng nay chúng ta cần mang các kịch bản Unit Test và công cụ cấu hình vào chạy thực tế. Job mới này sẽ cài đặt các công cụ cần thiết thông qua file **requirements-dev.txt**. Nó sẽ tự động chạy kiểm tra định dạng và lập tức đánh dấu lỗi, từ chối cho phép gộp code nếu phát hiện sai sót. Đồng thời, nó tự động giả lập và kiểm tra toàn bộ logic của hệ thống để đảm bảo mã nguồn mới không phá vỡ các chức năng cũ trước khi triển khai lên AWS.

**3.** Terraform Plan CI

Bước này sẽ tự động chạy lên kế hoạch Terraform khi bạn mở **Pull Request** vào nhánh chính. Đầu tiên, chúng ta sẽ tiến hành kiểm tra Workspace HCP Terraform. Bạn hãy vào Workspace của bạn, chọn **General** trong phần Cài đặt và xác nhận chế độ thực thi là **Remote**.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_1.png)

Tiếp theo, bạn cần tạo Token cho **HCP Terraform API**. Truy cập phần Cài đặt Tài khoản, chọn mục Tokens và nhấn tạo Token mới.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_2.png)

Đặt mô tả và thời hạn cho Token, nhấn nút tạo rồi lưu ngay giá trị này lại.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_3.png)

Bước kế tiếp là lưu Token vào **GitHub Secret**. Bạn mở cài đặt **GitHub repository**, điều hướng đến phần quản lý **Secret and variables**, sau đó tạo một Secret mới cho kho lưu trữ.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_4.png)

Bạn đặt tên cho Secret và dán Token vừa tạo vào trường tương ứng.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_5.png)

Sau khi đã cấu hình xong, chúng ta cập nhật Job **Terraform** trong file **ci.yml**:

```yaml
      - name: Create speculative Terraform plan
        if: >
          github.event_name == 'pull_request' &&
          github.event.pull_request.head.repo.full_name == github.repository
        working-directory: terraform
        env:
          TF_TOKEN_app_terraform_io: ${{ secrets.TF_API_TOKEN }}
        run: |
          terraform init -input=false -reconfigure
          terraform plan -input=false -no-color
```

Trước đây, Job **Terraform** chỉ dừng lại ở mức kiểm tra lỗi đánh máy và cú pháp cơ bản. Khi thêm lệnh chạy thử nghiệm, hệ thống CI sẽ chỉ ra chính xác những tài nguyên AWS nào sắp bị tạo mới, sửa đổi hoặc xóa bỏ. Việc này giúp chúng ta dễ dàng phát hiện các thay đổi phá hủy ngay từ giai đoạn xem xét đề xuất.

Khác với bước khởi tạo cục bộ, bước này sử dụng Token để kết nối trực tiếp với HCP Terraform. Nhờ vậy, lệnh lập kế hoạch có thể đọc được file trạng thái hiện tại, so sánh mã nguồn mới với hạ tầng thực tế để đưa ra bản đánh giá chính xác tuyệt đối. Điều kiện tích hợp đảm bảo rằng quy trình mô phỏng hạ tầng này chỉ được kích hoạt khi có đề xuất gộp code, đóng vai trò như một bài test cuối cùng bắt buộc trước khi áp dụng thực tế.

Bây giờ chúng ta sẽ tiến hành kiểm tra bằng cách tạo đề xuất mới. Bạn tạo nhánh mới:

```bash
git checkout -b ci/terraform-plan
```

Tiếp theo, hãy đẩy các luồng công việc lên kho lưu trữ:

```bash
git add .github/workflows/ci.yml
git commit -m "Add Terraform plan to CI"
git push -u origin ci/terraform-plan
```

Sau đó, bạn mở đề xuất gộp mã từ nhánh mới vào nhánh chính.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_6.png)

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_7.png)

Lúc này Workspace **HCP Terraform** chưa có giá trị cho biến bắt buộc vì biến này được định nghĩa trong file ẩn không đẩy lên mạng do chứa dữ liệu cá nhân. Do đó, bạn cần gán giá trị cho biến này trực tiếp trong Workspace.

Bạn vào trang quản lý Workspace, mở phần Biến số và thêm địa chỉ email vào.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_8.png)

Kết quả mong muốn trong luồng hành động **GitHub** sẽ hiển thị trạng thái hoàn thành.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_9.png)

Khi mọi thứ đã sẵn sàng, bạn kéo xuống và chọn nút gộp mã để hoàn tất.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_10.png)

Quá trình gộp mã thành công sẽ hiện thông báo xác nhận.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_11.png)

### Tạo Workflow CD

Vì Terraform chạy từ xa trên HCP Terraform, hệ thống GitHub không trực tiếp gọi AWS. Bước tiếp theo yêu cầu chuẩn bị môi trường sản xuất được bảo vệ để hệ thống yêu cầu phê duyệt trước khi thực thi lệnh áp dụng hạ tầng.

Bạn cần tạo môi trường sản xuất trên GitHub bằng cách vào kho lưu trữ, mở phần Cài đặt và chọn tạo môi trường mới.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_1.png)

Bạn nhập tên môi trường là production rồi nhấn nút cấu hình.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_2.png)

Trong môi trường này, bạn bật tùy chọn yêu cầu người phê duyệt và thêm các tài khoản được phép duyệt quy trình.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_3.png)

Ở phần thiết lập nhánh, bạn giới hạn chỉ cho phép nhánh chính được triển khai.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_4.png)

Thêm nhánh chính vào rồi lưu cấu hình.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_5.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_6.png)

Sau đó xác nhận thành công và lưu lại các quy tắc bảo vệ.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_7.png)

Thiết lập này sẽ khiến Job triển khai luôn chờ phê duyệt trước khi có thể dùng Secret hay chạy lệnh áp dụng.

Tiếp theo, bạn sẽ tạo Token HCP dành riêng cho quá trình **CD**. Trong bảng điều khiển HCP Terraform, bạn truy cập vào tổ chức của mình và chọn mục **Teams**.

Tại trang của nhóm chủ sở hữu, bạn nhấn vào phần quản lý Token.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_1.png)

Chọn tùy chọn tạo Token mới cho nhóm.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_2.png)

Bạn điền mô tả, chọn thời hạn và lưu lại giá trị Token vừa tạo.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_3.png)

Trở lại GitHub, bạn vào cài đặt môi trường production vừa tạo và thêm Secret mới.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_4.png)

Đặt tên cho Secret, dán giá trị Token vào và lưu lại.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_5.png)


Kế tiếp, bạn cần tạo file **terraform-apply.yml** trong thư mục luồng công việc. Luồng công việc này chỉ chạy sau khi mã nguồn được gộp vào nhánh chính.

Nó sẽ chờ bạn phê duyệt ở môi trường production trước khi thực sự triển khai hạ tầng lên AWS.

```yaml
name: Terraform Apply

on:
  # Tự động chạy khi thay đổi Terraform được merge/push vào nhánh main
  push:
    branches: [main]
    paths:
      # Chỉ chạy CD khi có thay đổi hạ tầng Terraform
      - "terraform/**"
      # Cho phép workflow chạy khi chính file này được cập nhật
      - ".github/workflows/terraform-apply.yml"

  # Cho phép chạy thủ công workflow từ GitHub Actions khi cần
  workflow_dispatch:

# Workflow chỉ cần quyền đọc mã nguồn từ repository
permissions:
  contents: read

# Ngăn nhiều lần terraform apply chạy đồng thời trên production
# Các lần chạy mới sẽ xếp hàng chờ, không hủy lần apply đang chạy
concurrency:
  group: terraform-production
  cancel-in-progress: false

jobs:
  apply:
    name: Apply Terraform to production
    runs-on: ubuntu-latest
    environment: production

    env:
      # Cho Terraform biết lệnh đang chạy trong môi trường tự động hóa
      TF_IN_AUTOMATION: "true"

      # Token xác thực với HCP Terraform, lấy từ GitHub Environment Secret
      # Giá trị token không hiển thị trong log GitHub Actions
      TF_TOKEN_app_terraform_io: ${{ secrets.TF_API_TOKEN }}

    steps:
      - name: Checkout source
        uses: actions/checkout@v5

      # Cài đặt Terraform với đúng phiên bản dự án sử dụng
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.5.7"
          # Hiển thị log Terraform trực tiếp để dễ kiểm tra lỗi
          terraform_wrapper: false

      # Khởi tạo Terraform và kết nối đến HCP Terraform remote backend
      # HCP Terraform sẽ quản lý state và thực hiện remote run
      - name: Initialize HCP Terraform
        working-directory: terraform
        run: terraform init -input=false

      # Áp dụng cấu hình Terraform đã có lên môi trường production
      - name: Apply Terraform
        working-directory: terraform
        run: terraform apply -input=false -auto-approve -no-color
```

Quá trình áp dụng Terraform sẽ tạo kế hoạch mới rồi thực thi. Việc này giúp tránh tình trạng áp dụng một kế hoạch đã cũ sau khi bạn xem xét đề xuất.

Bây giờ bạn tiến hành tạo nhánh và đẩy thay đổi lên:

```bash
git checkout -b cd/terraform-apply
git add .github/workflows/terraform-apply.yml
git commit -m "Add protected Terraform apply workflow"
git push -u origin cd/terraform-apply
```

Tiếp đó, bạn mở **Pull Request**, chờ hệ thống kiểm tra xanh toàn bộ rồi nhấn nút gộp.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_1.png)

Ngay sau khi gộp, bạn điều hướng sang phần hành động của **GitHub** để kiểm tra tiến trình áp dụng. Luồng công việc sẽ ở trạng thái chờ đánh giá.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_2.png)

Bạn nhấn vào phần **Review deployment**, chọn môi trường production và xác nhận phê duyệt.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_3.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_4.png)

Tiếp theo, bạn có thể theo dõi trực tiếp trên bảng điều khiển **HCP Terraform** để kiểm tra tiến trình thực thi.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_5.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_6.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_7.png)

Ở lần chạy đầu tiên, nếu hạ tầng hiện tại đã khớp với trạng thái cấu hình, hệ thống sẽ báo không có thay đổi. Ngược lại, việc triển khai có thể tạo hoặc cập nhật tài nguyên AWS và phát sinh chi phí, vì vậy bạn luôn phải đọc kỹ nhật ký trước khi phê duyệt.

Môi trường GitHub đã hỗ trợ luồng đánh giá an toàn trước khi cấp quyền truy cập biến bí mật để triển khai.

Cuối cùng, chúng ta sẽ thiết lập quy tắc bảo vệ cho nhánh chính. Việc bảo vệ nhánh giúp ngăn ngừa hạ tầng khỏi các thay đổi chưa được kiểm tra kỹ lưỡng. Mọi thay đổi bắt buộc phải đi qua đề xuất gộp mã, vượt qua các kiểm tra hệ thống và được phê duyệt trước khi sáp nhập vào nhánh chính. Điều này cực kỳ quan trọng vì quá trình gộp mã có thể tự động kích hoạt luồng triển khai và thay đổi tài nguyên AWS. Sự bảo vệ này giảm thiểu rủi ro triển khai sai sót hoặc làm gián đoạn hệ thống.

Bạn truy cập phần cài đặt nhánh trong kho lưu trữ và thêm quy tắc bảo vệ truyền thống.

![Branch protection rule](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/branchprotectionrule_1.png)

Bạn đánh dấu vào các tùy chọn yêu cầu đề xuất gộp mã, bắt buộc vượt qua các bài kiểm tra trạng thái và yêu cầu nhánh phải được cập nhật trước khi sáp nhập.

![Branch protection rule](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/branchprotectionrule_3.png)

Kéo xuống dưới, bạn thêm các bài kiểm tra bắt buộc bao gồm đánh giá cú pháp bảng điều khiển, chạy kiểm thử mã **Python** và xác thực cấu hình **Terraform**.

![Branch protection rule](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/branchprotectionrule_4.png)

Sau cùng, bạn nhấn lưu lại các thay đổi. Hệ thống sẽ yêu cầu kiểm tra lại nếu nhánh chính có cập nhật mới hơn nhánh đang đề xuất. Quy trình chuẩn lúc này sẽ là tạo nhánh, đẩy thay đổi, mở đề xuất, vượt qua kiểm tra, gộp vào nhánh chính và chờ phê duyệt triển khai.

Chúng ta đã hoàn thành phần tích hợp và triển khai liên tục cho dự án **CloudCost Insight**. Mọi thay đổi giờ đây đều được tự động kiểm tra chất lượng chặt chẽ qua **GitHub Actions** trước khi được sáp nhập.

Khi quá trình sáp nhập hoàn tất, hệ thống tự động cập nhật hạ tầng AWS qua HCP Terraform.

Sự kết hợp với môi trường bảo vệ của GitHub đảm bảo việc triển khai luôn an toàn, nhất quán và hạn chế tối đa thao tác thủ công.

### Nội dung tiếp theo

[Dọn dẹp tài nguyên](5-Workshop/5.9-Cleanup/)
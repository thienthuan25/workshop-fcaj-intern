---
title : "CI/CD"
date : 2024-01-01
weight : 8
chapter : false
pre : " <b> 5.8. </b> "
---

In this section, the CloudCost Insight project applies a CI/CD pipeline using GitHub Actions to automatically verify source code quality and deploy AWS infrastructure consistently.

Each change is made on a separate branch and submitted via a Pull Request, which is then automatically checked by the system. This process includes: linting and running unit tests for the Python Lambda code, checking formatting and validating Terraform configuration, creating a Terraform plan, and checking the JavaScript syntax of the Dashboard. Changes are only merged into the main branch when all tests succeed and are approved.

After merging, the CD workflow automatically runs Terraform Apply via HCP Terraform to update the AWS infrastructure. This process helps reduce manual deployment risks, detects errors early, and ensures the deployment environment is always consistent with the source code.

### Create CI Workflow

**1.** First, we will configure the **ci.yml** file in the **.github/workflows** directory:

```yaml
# Display name of the workflow on the GitHub Actions tab
name: CI

# Run CI when creating/updating a Pull Request to main
# or when a commit is pushed directly to main
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

# CI only needs to read the source code to check, no write or deploy permissions
permissions:
  contents: read

jobs:
  # Job 1: Check Python source code syntax of Lambda functions
  python:
    name: Check Python Lambda code
    runs-on: ubuntu-latest

    steps:
      # Checkout source code for checking
      - name: Checkout source
        uses: actions/checkout@v5

      # Set up Python with the version used by Lambda
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      # Compile Python files to detect syntax errors
      - name: Check Python syntax
        run: |
          python -m compileall terraform/lambda terraform/test

  # Job 2: Check formatting and validity of Terraform configuration
  terraform:
    name: Validate Terraform
    runs-on: ubuntu-latest

    steps:
      # Checkout Terraform source code to the CI virtual machine
      - name: Checkout source
        uses: actions/checkout@v5

      # Set up Terraform with the correct project version
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.5.7"
          # Do not wrap Terraform output for clearer logs
          terraform_wrapper: false

      # Check if .tf files have the correct standard format
      # -check only reports errors, does not auto-edit files
      - name: Check Terraform formatting
        working-directory: terraform
        run: terraform fmt -check -recursive

      # Initialize Terraform to download providers, but do not connect to HCP Terraform backend
      # CI only checks configuration and does not create, modify, or delete AWS resources
      - name: Initialize Terraform without remote backend
        working-directory: terraform
        run: terraform init -backend=false

      # Check syntax, variables, resources, and references in Terraform
      - name: Validate Terraform configuration
        working-directory: terraform
        run: terraform validate

  # Job 3: Check JavaScript syntax of the Web Dashboard
  frontend:
    name: Check dashboard JavaScript
    runs-on: ubuntu-latest

    steps:
      # Checkout frontend source code to the CI virtual machine
      - name: Checkout source
        uses: actions/checkout@v5

      # Check script.js syntax without running the Dashboard in the browser
      - name: Check JavaScript syntax
        run: node --check terraform/web/script.js
```

**2.** Create Unit test for Lambda

You need to create a **tests** folder from the root of the project and then create a **conftest.py** file in this folder:

```python
import importlib.util
from pathlib import Path

# pyrefly: ignore [missing-import]
import pytest

# Determine the root directory of the project from the tests/conftest.py file location.
# parents[1] corresponds to the parent directory of the tests folder.
ROOT_DIR = Path(__file__).resolve().parents[1]


# Fixture that automatically runs before each test.
# Set up mock environment variables so boto3 does not use real AWS credentials
# and Lambda handlers have the necessary configuration when imported.
@pytest.fixture(autouse=True)
def aws_environment(monkeypatch):
    """Cấu hình môi trường giả phục vụ unit test Lambda."""
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")

    # Mock AWS resource values used during testing.
    monkeypatch.setenv("BUCKET_NAME", "test-cost-data-bucket")
    monkeypatch.setenv(
        "QUEUE_URL", "https://sqs.us-east-1.amazonaws.com/123456789012/events"
    )
    monkeypatch.setenv(
        "SNS_TOPIC_ARN",
        "arn:aws:sns:us-east-1:123456789012:cost-alerts",
    )

    # Configuration variables for the cost analysis logic.
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
    # Create the absolute path to the Lambda file to be tested.
    path = ROOT_DIR / relative_path

    # Create module information from the file path.
    spec = importlib.util.spec_from_file_location(module_name, path)

    # Create a new Python module and execute the source code in the handler.py file.
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Return the module for test files to call the function to be tested.
    return module
```

The **conftest.py** file provides the configuration and shared components for the entire unit testing process using pytest. The purpose of this file includes setting up a mock environment to ensure that Lambda functions use mock environment variables and AWS credentials when running tests. This keeps the test system completely isolated, avoiding accidental calls to the real AWS API that could incur costs or cause unwanted errors.

The file also provides the **load_lambda_module** utility, which helps load Lambda files independently. Since all Lambdas share the same filename **handler.py**, this utility allows importing them under distinct module names to avoid source code conflicts.

Next, we create the **test_analyzer.py** file:

```python
# Import helper function to load Lambda Analyzer directly from handler.py file.
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
    # Load Analyzer module to directly call the function to be tested.
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # Analyze mock cost data.
    result = analyzer.compute_total_and_top(sample_cost_data())

    # Expected total cost: 8.50 + 2.00 + 1.25 = 11.75 USD.
    assert result["total_cost"] == 11.75

    # The list of services must be sorted by cost in descending order.
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

    # The cost of 6 USD has not exceeded the 10 USD threshold and did not spike.
    severity, reasons = analyzer.classify_severity(total=6, avg=5)

    # No need to send an alert when the cost is within the normal range.
    assert severity == "INFO"
    assert reasons == []


def test_classify_severity_returns_warning_when_threshold_exceeded():
    """Kiểm tra chi phí vượt ngưỡng ngân sách được phân loại WARNING."""
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # The cost of 12 USD exceeds the 10 USD budget threshold,
    # but is not large enough to be considered a spike.
    severity, reasons = analyzer.classify_severity(total=12, avg=9)

    assert severity == "WARNING"
    assert "Budget threshold exceeded ($10.00)" in reasons


def test_classify_severity_returns_critical_for_cost_spike():
    """Kiểm tra chi phí tăng đột biến được phân loại CRITICAL."""
    analyzer = load_lambda_module(
        "analyzer_handler",
        "terraform/lambda/analyzer/handler.py",
    )

    # The cost of 20 USD is higher than 1.5 times the average of 5 USD,
    # therefore it is identified as a cost spike.
    severity, reasons = analyzer.classify_severity(total=20, avg=5)

    assert severity == "CRITICAL"

    # Verify the alert reason contains information about the cost spike.
    assert any("Cost spike detected" in reason for reason in reasons)
```

The **test_analyzer.py** file contains test cases dedicated to the Lambda Analyzer. Its task is to verify the cost calculation logic by ensuring the system correctly reads the mock data format, accurately accumulates the total daily cost, and correctly ranks the most expensive services.

This file also ensures the accuracy of the alert mechanism by thoroughly checking the severity classification conditions based on the budget threshold and cost spike relative to the historical average. This is especially important to prevent the risk of false alarms or missing actual cost overrun incidents.

Next, we create the **test_api.py** file:

```python
# Import helper function to load Lambda API directly from handler.py file.
from conftest import load_lambda_module


def test_parse_daily_returns_total_and_services():
    """
    Kiểm tra Lambda API đọc đúng dữ liệu Cost Explorer của một ngày,
    tính tổng chi phí và nhóm chi phí theo từng dịch vụ.
    """
    # Load Lambda API module to call the parse_daily function to be tested.
    api = load_lambda_module(
        "api_handler",
        "terraform/lambda/api/handler.py",
    )

    # Mock Cost Explorer data for 2026-07-15.
    # Do not call real Cost Explorer in unit tests.
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

    # Parse mock data, get date, total cost, and individual service costs.
    day, total, services = api.parse_daily(cost_data)

    # Verify the API gets the correct date from TimePeriod.
    assert day == "2026-07-15"

    # Verify total cost: 5.25 + 1.50 = 6.75 USD.
    assert total == 6.75

    # Verify costs are grouped correctly by AWS service.
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
    # Load Lambda API module.
    api = load_lambda_module(
        "api_handler",
        "terraform/lambda/api/handler.py",
    )

    # Create a sample response with HTTP status 200 and simple JSON data.
    response = api._response(200, {"status": "ok"})

    # Verify Lambda returns the correct HTTP status code.
    assert response["statusCode"] == 200

    # Verify the response is declared as JSON data.
    assert response["headers"]["Content-Type"] == "application/json"

    # Verify the body has been converted to a properly formatted JSON string.
    assert response["body"] == '{"status": "ok"}'
```

The **test_api.py** file focuses on testing the functionalities of the Lambda API. Its primary purpose is to test the data extraction logic, ensuring the API can accurately parse the mock raw data structure from Cost Explorer, extract the correct dates, accurately calculate total costs, and group costs by individual services.

This file also ensures the response format by checking whether the Lambda function generates the exact result structure required by API Gateway. This is crucial to ensure the Web Dashboard can read the data without formatting errors.

Next, we create the **test_collector.py** file:

```python
# MagicMock creates mock objects so unit tests do not call real AWS.
from unittest.mock import MagicMock

# Import helper function to load Lambda Collector directly from handler.py file.
from conftest import load_lambda_module


def test_get_cost_data_calls_cost_explorer():
    """
    Kiểm tra Collector gọi AWS Cost Explorer với đúng tham số
    để lấy chi phí theo ngày và theo từng dịch vụ.
    """
    # Load Lambda Collector module to be tested.
    collector = load_lambda_module(
        "collector_handler",
        "terraform/lambda/collector/handler.py",
    )

    # Replace real Cost Explorer client with mock.
    # Thus, the test does not need AWS credentials and does not call AWS API.
    collector.ce_client = MagicMock()
    collector.ce_client.get_cost_and_usage.return_value = {"ResultsByTime": []}

    # Call the function to get cost data for a one-day period.
    result = collector.get_cost_data("2026-07-01", "2026-07-02")

    # Verify Collector returns the expected data structure.
    assert result == {
        "ResultsByTime": [],
        "GroupDefinitions": [{"Type": "DIMENSION", "Key": "SERVICE"}],
    }

    # Verify Cost Explorer is called exactly once with the correct configuration.
    # Data is retrieved daily, using the UnblendedCost metric
    # and grouped by AWS service.
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

    # Replace real S3 client with mock to avoid writing files to AWS S3.
    collector.s3_client = MagicMock()

    # Save sample data with date 2026-07-15.
    key = collector.save_to_s3({"ResultsByTime": []}, "2026-07-15")

    # Verify S3 path is generated correctly according to the partition structure.
    assert key == "cost-data/year=2026/month=07/day=15/cost_2026-07-15.json"

    # Verify Collector performs one S3 put_object call.
    collector.s3_client.put_object.assert_called_once()

    # Get the parameters passed to the put_object function.
    call = collector.s3_client.put_object.call_args.kwargs

    # Verify data is written to the mock bucket configured in conftest.py.
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

    # Replace real SQS client with mock to avoid sending messages to AWS.
    collector.sqs_client = MagicMock()

    # Send sample event containing date, S3 file location, and total cost.
    collector.send_event_to_sqs(
        "2026-07-15",
        "cost-data/example.json",
        12.34,
    )

    # Verify Collector sends exactly one message to SQS.
    collector.sqs_client.send_message.assert_called_once()

    # Get the parameters of the send_message call.
    call = collector.sqs_client.send_message.call_args.kwargs

    # Verify the message is sent to the events queue.
    assert call["QueueUrl"].endswith("/events")

    # Verify the message content has the required data fields.
    assert '"date": "2026-07-15"' in call["MessageBody"]
    assert '"total_cost": 12.34' in call["MessageBody"]
```

The **test_collector.py** file tests the entire workflow of the Lambda Collector. Because this component interacts directly with AWS services, this file uses mocking techniques via **MagicMock** to avoid costs. The primary purpose is to test the Cost Explorer connection to ensure the AWS API call passes the correct configuration parameters.

The S3 storage logic check confirms that the analyzed data is correctly written to the desired Bucket and that the system generates an accurate file path.

Finally, ensuring the event-driven flow checks the message content sent to the SQS Queue to see if it contains all essential data keys so the Lambda Analyzer can receive and process it.

Next, you need to create the **requirements-dev.txt** file in the root directory of the project:

```text
boto3>=1.34,<2
pytest>=8,<10
ruff>=0.6,<1
```

This file is responsible for listing the Python libraries exclusively for development and testing. These libraries are not packaged into the actual AWS Lambda environment.

Then, proceed to create the **pyproject.toml** file:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]
```

This file helps standardize and optimize the CI/CD workflow. Specific functions include limiting the default test discovery scope to the tests folder to minimize latency. It also defines the target environment version as **Python 3.12** to ensure absolute consistency with the AWS Lambda system.

Finally, it enables core rule sets to control syntax errors and ensure source code integrity, while disabling the line length limit rule to provide flexibility when declaring complex data structures.

To continue, activate **venv** using the command line in the Terminal as follows:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install **dependencies** and run checks:

```bash
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
ruff check terraform/lambda tests
```

Automatically fix logic errors using the command:

```bash
ruff check terraform/lambda tests --fix
```

Automatically format the code:

```bash
ruff format terraform/lambda tests
```

While running the commands, a failure message might appear in the Terminal if your code has formatting errors or is out of sync. You can manually fix the errors and rerun the check commands. The expected result will look like the image below.

![CI/CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/ci_2.png)

After passing all checks, we proceed to edit the **python** Job in the **ci.yml** file:

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

The purpose of modifying the **python** Job is to upgrade the CI system from merely checking for basic errors to a comprehensive source code moderation filter. Previously, this Job only called a syntax checking command, but now we need to bring the Unit Test scripts and configuration tools into actual execution. This new Job will install the necessary tools via the **requirements-dev.txt** file. It will automatically run format checks and immediately flag errors, refusing to allow code merging if flaws are detected. At the same time, it automatically mocks and tests the entire system logic to ensure that new source code does not break old functionalities before deploying to AWS.

**3.** Terraform Plan CI

This step will automatically run a Terraform plan when you open a **Pull Request** into the main branch. First, we will proceed to check the HCP Terraform Workspace. Please go to your Workspace, select **General** under Settings, and confirm the execution mode is **Remote**.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_1.png)

Next, you need to create a Token for the **HCP Terraform API**. Access Account Settings, select Tokens, and click create a new Token.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_2.png)

Set a description and expiration for the Token, click create, and save this value immediately.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_3.png)

The next step is to save the Token in **GitHub Secrets**. Open your **GitHub repository** settings, navigate to **Secrets and variables** management, and create a new Secret for the repository.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_4.png)

Name the Secret and paste the newly created Token into the corresponding field.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_5.png)

Once configured, we update the **Terraform** Job in the **ci.yml** file:

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

Previously, the Terraform Job only stopped at checking for typos and basic syntax errors. When adding the test run command, the CI system will indicate exactly which AWS resources are about to be created, modified, or deleted. This helps the team easily spot destructive changes right from the proposal review stage.

Unlike the local initialization step, this step uses the Token to connect directly to **HCP Terraform**. Thus, the plan command can read the current state file, comparing the new source code with the actual infrastructure to provide an absolutely accurate assessment. The integration condition ensures this infrastructure simulation process is only triggered upon a code merge proposal, acting as a final mandatory test before actual implementation.

Now we will proceed to test by creating a new proposal. Create a new branch:

```bash
git checkout -b ci/terraform-plan
```

Next, push the workflows to the repository:

```bash
git add .github/workflows/ci.yml
git commit -m "Add Terraform plan to CI"
git push -u origin ci/terraform-plan
```

Then, open a merge proposal from the new branch to the main branch.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_6.png)

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_7.png)

At this point, the HCP Terraform Workspace does not have a value for the mandatory variable because this variable is defined in a hidden file not pushed to the network due to personal data. Therefore, you need to assign a value to this variable directly in the Workspace.

Go to the Workspace management page, open the Variables section, and add the email address.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_8.png)

The expected result in the **GitHub** workflow will show a completed status.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_9.png)

When everything is ready, scroll down and click the merge button to complete.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_10.png)

A successful merge will display a confirmation message.

![Terraform Plan CI](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformplan_11.png)

### Create CD Workflow

Because Terraform runs remotely on HCP Terraform, the GitHub system does not directly call AWS. The next step requires preparing a protected production environment so the system demands approval before executing the infrastructure apply command.

You need to create a production environment on GitHub by going to the repository, opening Settings, and choosing to create a new environment.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_1.png)

Enter the environment name as production and click configure.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_2.png)

In this environment, enable the required reviewers option and add accounts allowed to approve the process.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_3.png)

In the branch settings, restrict deployment to only the main branch.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_4.png)

Add the main branch and save the configuration.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_5.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_6.png)

Then confirm success and save the protection rules.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/terraformcd_7.png)

This setup will cause the deployment Job to always wait for approval before it can use the Secret or run the apply command.

Next, you will create an HCP Token specifically for the **CD** process. In the HCP Terraform dashboard, access your organization and select **Teams**.

At the owners team page, click on Token management.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_1.png)

Choose the option to create a new Token for the team.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_2.png)

Fill in the description, select the expiration, and save the newly created Token value.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_3.png)

Back in GitHub, go to the newly created production environment settings and add a new Secret.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_4.png)

Name the Secret, paste the Token value, and save it.

![HCP Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/hcptokencd_5.png)


Next, you need to create the **terraform-apply.yml** file in the workflows directory. Luồng công việc này chỉ chạy sau khi mã nguồn được gộp vào nhánh chính.

Nó sẽ chờ bạn phê duyệt ở môi trường production trước khi thực sự triển khai hạ tầng lên AWS.

```yaml
name: Terraform Apply

on:
  # Automatically run when Terraform changes are merged/pushed to the main branch
  push:
    branches: [main]
    paths:
      # Only run CD when there are Terraform infrastructure changes
      - "terraform/**"
      # Allow the workflow to run when this file itself is updated
      - ".github/workflows/terraform-apply.yml"

  # Allow running the workflow manually from GitHub Actions when needed
  workflow_dispatch:

# Workflow only needs read permissions for the source code from the repository
permissions:
  contents: read

# Prevent multiple terraform apply runs from executing concurrently on production
# New runs will be queued, do not cancel the in-progress apply run
concurrency:
  group: terraform-production
  cancel-in-progress: false

jobs:
  apply:
    name: Apply Terraform to production
    runs-on: ubuntu-latest
    environment: production

    env:
      # Tell Terraform the command is running in an automation environment
      TF_IN_AUTOMATION: "true"

      # Authentication token with HCP Terraform, fetched from GitHub Environment Secret
      # Token value is not displayed in GitHub Actions logs
      TF_TOKEN_app_terraform_io: ${{ secrets.TF_API_TOKEN }}

    steps:
      - name: Checkout source
        uses: actions/checkout@v5

      # Set up Terraform with the correct version used by the project
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.5.7"
          # Display Terraform logs directly to easily check for errors
          terraform_wrapper: false

      # Initialize Terraform and connect to HCP Terraform remote backend
      # HCP Terraform will manage state and perform remote runs
      - name: Initialize HCP Terraform
        working-directory: terraform
        run: terraform init -input=false

      # Apply existing Terraform configuration to the production environment
      - name: Apply Terraform
        working-directory: terraform
        run: terraform apply -input=false -auto-approve -no-color
```

The Terraform apply process will create a new plan and then execute it. This avoids applying an outdated plan after you have reviewed the proposal.

Now you proceed to create a branch and push the changes:

```bash
git checkout -b cd/terraform-apply
git add .github/workflows/terraform-apply.yml
git commit -m "Add protected Terraform apply workflow"
git push -u origin cd/terraform-apply
```

Then, open **Pull Request**, wait for the system to show all green checks, and click the merge button.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_1.png)

Right after merging, navigate to the **GitHub** Actions section to check the apply progress. The workflow will be in a waiting for review state.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_2.png)

Click on the **Review deployment**, select the production environment, and confirm approval.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_3.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_4.png)

Next, you can directly monitor the **HCP Terraform** dashboard to check the execution progress.

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_5.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_6.png)

![Terraform CD](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/merge_7.png)

On the first run, if the current infrastructure already matches the configuration state, the system will report no changes. Conversely, the deployment might create or update AWS resources and incur costs, so you must always read the logs carefully before approving.

The GitHub environment already supports a safe review workflow before granting access to secret variables for deployment.

Finally, we will set up a protection rule for the main branch. Protecting the branch helps prevent the infrastructure from undergoing unverified changes. All changes must go through a merge proposal, pass system checks, and be approved before merging into the main branch. This is extremely important because the merge process can automatically trigger the deployment workflow and alter AWS resources. This protection minimizes the risk of erroneous deployments or system disruption.

Access the branch settings in the repository and add a classic branch protection rule.

![Branch protection rule](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/branchprotectionrule_1.png)

Check the options requiring a merge proposal, mandatory passing of status checks, and requiring the branch to be up to date before merging.

![Branch protection rule](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/branchprotectionrule_3.png)

Scroll down and add the required checks, including checking dashboard syntax, running **Python** code tests, and validating **Terraform** configuration.

![Branch protection rule](/workshop-fcaj-intern/images/5-Workshop/5.8-CI-CD/branchprotectionrule_4.png)

Finally, save the changes. The system will request a re-check if the main branch has a newer update than the proposing branch. The standard procedure now will be creating a branch, pushing changes, opening a proposal, passing checks, merging into the main branch, and waiting for deployment approval.

We have completed the continuous integration and deployment section for the **CloudCost Insight** project. All changes are now automatically and strictly quality-checked via **GitHub Actions** before being merged.

When the merge process is complete, the system automatically updates the AWS infrastructure via HCP Terraform.

The combination with GitHub's protected environment ensures the deployment is always safe, consistent, and minimizes manual operations.

### Next Content

[Clean up](5-Workshop/5.9-Cleanup/)
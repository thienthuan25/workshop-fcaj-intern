---
title : "Prepare the Terraform Code"
date : 2024-01-01
weight : 3
chapter : false
pre : " <b> 5.2.3. </b> "
---

### Required Tools

In this workshop, we perform all command-line operations in the **WSL2** (Windows Subsystem for Linux) environment instead of using Windows **Command Prompt** (CMD) or **PowerShell**. There are several key reasons for this choice:

+ **A consistent Linux environment:** Most infrastructure tools such as **Terraform**, the **AWS CLI**, and deployment scripts are designed and optimized for Unix/Linux environments. WSL2 provides a real Linux environment running on Windows, eliminating differences in file paths, environment variables, and command-line behavior that often exist in CMD or PowerShell.
+ **Consistency with the production environment:** Most AWS servers and CI/CD pipelines run on Linux. Using WSL2 makes your development environment much closer to the production environment, reducing the risk of issues caused by operating system differences.
+ **Excellent support for command-line tools:** WSL2 fully supports Linux utilities such as **bash**, text-processing commands, and file management tools, making it much more convenient to write and execute scripts.
+ **Strong compatibility with development tools:** WSL2 integrates seamlessly with editors such as **Visual Studio Code**, allowing you to write code and execute commands within the same environment.

Overall, WSL2 provides a more consistent and stable experience when working with cloud infrastructure tools, especially **Terraform**.

For **macOS**, you simply need to open the Terminal, and the user experience is almost identical to working in the WSL environment on Windows.

Before you begin, make sure the following tools are installed:

+ **Terraform** version 1.5 or later to provision infrastructure using the Infrastructure as Code approach.
+ **AWS CLI** to interact with AWS services and perform testing from the command line.
+ **Python** version 3.12 or later to develop the Lambda functions.

You can verify that all required tools have been installed successfully by running the following commands:

```bash
terraform version
aws --version
python3 --version
```

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_1.png)

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_2.png)

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_3.png)

### Configure AWS Credentials for the CLI

In the terminal, configure your AWS credentials so that AWS CLI can authenticate and execute commands throughout the deployment and testing process:

```bash
aws configure
```

Enter the following information when prompted:

```
AWS Access Key ID       [None]: <ACCESS_KEY_ID>
AWS Secret Access Key   [None]: <SECRET_ACCESS_KEY>
Default region name     [None]: us-east-1
Default output format   [None]:
```

After completing the configuration, restrict access to the credentials file so that only the current user can read it:

```bash
chmod 600 ~/.aws/credentials
```

Verify that the credentials are working correctly:

```bash
aws sts get-caller-identity
```

### Configure the Terraform Environment

At the root directory of the project, create a new folder named `terraform`. This folder will contain Terraform files used to deploy AWS infrastructure.

Create a file named `version.tf` to specify the Terraform version, configure the connection to HCP Terraform, and define the AWS provider. Replace `TEN-TO-CHUC` with the name of your organization and replace `TEN-WORKSPACE` with the name of the workspace you created in HCP Terraform.

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

### Connect and Initialize Terraform

In the WSL2 terminal, navigate to the directory containing the Terraform files, then run the following command to authenticate Terraform CLI with HCP Terraform:

```bash
terraform login
```

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_4.png)

+ Open the URL displayed in the terminal:

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_5.png)

+ Enter a **Description** if you want to make the token easier to identify.
+ Select an expiration period for the API token.
+ Click **Generate token**.

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_6.png)

+ Copy newly created Token to Terminal:

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_7.png)

+ After logging in successfully, initialize Terraform to download providers and connect to the **Workspace**:

```bash
cd terraform
terraform init
```

![Code terraform](/workshop-fcaj-intern/images/5-Workshop/5.2-Prerequisite/5.2.3-Code-terraform/code_terraform_8.png)

After completing these steps, your working environment is fully configured and ready to deploy the **CloudCost Insight** system in the following sections.

### Preparing Git and Configuring `.gitignore`

Since this project is managed with **Git** and the source code will be pushed to **GitHub**, we need to configure Git to exclude files that should not be committed to the repository. This helps protect sensitive information and keeps the repository clean.

In the project's root directory, create a `.gitignore` file with the following content:

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

- The `.terraform/` directory: This is where Terraform stores the provider cache downloaded when running `terraform init`. Since this directory is large and can be recreated easily, it should not be committed to the repository.
- The `*.tfstate` and `*.tfstate.*` files: These are Terraform state files that may contain sensitive information. Because this project uses **HCP Terraform** to manage the remote state, the infrastructure state is already stored centrally on HCP Terraform, so there is no need to keep local state files in the repository.
- The `*.tfvars` files: These files contain actual variable values, such as the email address used for alert notifications, so they should not be committed to the repository to avoid exposing sensitive information. Only the template file, `*.tfvars.example`, should be included.

### Next Content

- [Provision Infrastructure with Terraform](5-Workshop/5.3-Infrastructure/)
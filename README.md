# Internship Report & Workshop Template

This repository contains the source code for an Internship Report (Báo cáo thực tập) and a Workshop template, built using **Hugo** and **Terraform** for AWS infrastructure.

## 🌟 Overview

The repository is divided into two main parts:

1. **Documentation Site (Hugo)**
   - A static website built with [Hugo](https://gohugo.io/) using a customized `hugo-theme-learn`.
   - Used for documenting the internship report, blog posts, events participated, and step-by-step workshop modules.
   - Content is written in Markdown and supports multiple languages (English and Vietnamese).
   - Connected to the **AWS Study Group**.

2. **Infrastructure as Code (Terraform & AWS)**
   - Located in the `terraform/` directory.
   - Contains Terraform configurations to deploy serverless AWS infrastructure.
   - Features include AWS Lambda functions (written in Python), S3 buckets, SQS queues, CloudWatch logs, and SNS topics for processing data and cost alerts.

## 📂 Repository Structure

- `content/`: Contains the Markdown files for the Hugo site, organized into sections like Blogs, Events, and Workshop modules.
- `config.toml`: The main configuration file for the Hugo site.
- `themes/` / `layouts/`: Customizations and templates for the Hugo theme.
- `terraform/`: Terraform `.tf` configurations and Lambda function source code (`terraform/lambda/`).
- `tests/`: Python test files for validating Lambda functions.
- `pyproject.toml` / `requirements-dev.txt`: Python project configuration and dependencies.

## 🛠️ Prerequisites

To work with this repository, you will need:
- [Hugo Extended](https://gohugo.io/installation/) (version 0.134.3 or higher recommended).
- [Terraform](https://developer.hashicorp.com/terraform/downloads) for provisioning AWS infrastructure.
- [Python 3.12](https://www.python.org/) for AWS Lambda functions and testing.
- [AWS CLI](https://aws.amazon.com/cli/) configured with appropriate credentials.

## 🚀 Getting Started

### Running the Documentation Site Locally

1. Ensure Hugo is installed on your machine.
2. Run the Hugo development server in the root directory:
   ```bash
   hugo server -D
   ```
3. Open your browser and navigate to `http://localhost:1313/` to view the site.

### Deploying the Infrastructure

1. Navigate to the Terraform directory:
   ```bash
   cd terraform
   ```
2. Initialize the Terraform workspace:
   ```bash
   terraform init
   ```
3. Review and apply the configuration (you will be prompted to confirm):
   ```bash
   terraform plan
   terraform apply
   ```

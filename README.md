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

## 🚀 Deployment & Usage

- **Documentation Site**: The Hugo site is automatically built and deployed via **GitHub Pages**. You can view the live site through the repository's GitHub Pages link.
- **Infrastructure**: The Terraform code and Lambda functions provided in this repository are part of the workshop modules. Participants are expected to write and deploy this code on their own AWS accounts following the workshop instructions.

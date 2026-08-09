---
title : "Deploy the Infrastructure"
date : 2024-01-01 
weight : 8
chapter : false
pre : " <b> 5.3.8 </b> "
---

Before deploying the infrastructure, we need to create one more file named `terraform/terraform.tfvars`.

In the first section, we created the `variables.tf` file to declare all input variables, such as the project name, deployment environment, and email address, together with their default values. The `terraform.tfvars` file is where you provide the actual values that will be used for your deployment. Keeping these values separate makes the Terraform code more flexible and reusable. If you want to share the project with someone else or update the email address or project name, you only need to modify the `terraform.tfvars` file without changing the infrastructure configuration in the other Terraform files. Terraform automatically detects and loads values from the `.tfvars` file during execution.

```hcl
# Required
aws_region          = "us-east-1" # AWS Region where the infrastructure will be deployed
environment         = "dev" # Deployment environment such as dev, test, or prod
project_name        = "[YOUR_PROJECT_NAME]"
alert_email         = "[EMAIL]" # Email address that will receive notifications
schedule_expression = "rate(1 day)" # Schedule expression for the automated task
```

After completing all of the files above, open a terminal, navigate to the project directory that contains the Terraform files, and run the following commands to deploy the infrastructure.

**1.** Preview the resources that Terraform will create.

```bash
terraform plan
```

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_1.png)

**2.** Deploy the infrastructure.

```bash
terraform apply
```

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_2.png)

- Type `yes` to confirm the deployment.

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_3.png)

**3.** After the deployment is complete, Terraform displays the output values that were defined in `outputs.tf`.

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_5.png)

**4.** Verify the deployed resources and confirm the email subscription.

After the deployment is complete, verify that the following resources have been created successfully in the AWS Management Console.

- S3 Bucket:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_6.png)

- SQS Queue:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_7.png)

- SNS Topic:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_8.png)

- EventBridge rule:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_9.png)

- Confirm the email subscription:

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_10.png)

Click `Confirm subscription`.

![Deploy Infrastructure](/workshop-fcaj-intern/images/5-Workshop/5.3-Infrastructure/5.3.8-Deploy-infrastructure/deploy_11.png)

### Next Content

- [Deploying Lambda Collector](5-Workshop/5.4-Deploy-Lambda)

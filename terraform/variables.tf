
# input variables
variable "aws_region" {
  description = "AWS region for infrastructure deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment (dev/test/prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name, used as a prefix for naming resources"
  type        = string
  default     = "cloudcost-insight"
}

variable "alert_email" {
  description = "Email address for receiving cost alert via SNS"
  type        = string

}

variable "schedule_expression" {
  description = "Scheduled expression for EventBridge"
  type        = string
  default     = "rate(1 day)"
}

variable "cost_threshold_usd" {
  description = "Cost threshold (USD) that triggers an alert"
  type        = number
  default     = 10
}

variable "spike_multiplier" {
  description = "Spike multiplier: if cost > historical average * this multiplier, it is considered an abnormal spike"
  type        = number
  default     = 1.5
}

variable "history_days" {
  description = "Number of historical days used to calculate the average cost (for spike detection)"
  type        = number
  default     = 7
}
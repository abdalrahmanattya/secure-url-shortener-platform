variable "aws_region" {
  description = "AWS region for the target platform."
  type        = string
  default     = "eu-west-1"
}

variable "project_name" {
  description = "Lowercase project identifier used in resource names."
  type        = string
  default     = "secure-url-shortener"

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,31}$", var.project_name))
    error_message = "project_name must be 3-32 lowercase letters, numbers, or hyphens and start with a letter."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "demo"

  validation {
    condition     = contains(["dev", "demo", "staging", "prod"], var.environment)
    error_message = "environment must be dev, demo, staging, or prod."
  }
}

variable "availability_zones" {
  description = "Exactly two AZs for the multi-AZ target. Leave empty to use the first two available AZs."
  type        = list(string)
  default     = []

  validation {
    condition     = length(var.availability_zones) == 0 || length(var.availability_zones) == 2
    error_message = "availability_zones must be empty or contain exactly two zones."
  }
}

variable "vpc_cidr" {
  description = "VPC IPv4 CIDR."
  type        = string
  default     = "10.40.0.0/16"
}

variable "container_image_digest" {
  description = "Immutable ECR image reference including @sha256 digest; mutable tags are rejected."
  type        = string
  default     = ""

  validation {
    condition     = var.container_image_digest == "" || can(regex("^[^@[:space:]]+@sha256:[0-9a-f]{64}$", var.container_image_digest))
    error_message = "container_image_digest must be an image@sha256:<64 lowercase hex> reference, or empty for a non-applied scaffold plan."
  }
}

variable "certificate_arn" {
  description = "ACM certificate ARN for the HTTPS listener. The syntactically valid placeholder is for credential-free validation only and must be replaced before apply."
  type        = string
  default     = "arn:aws:acm:eu-west-1:000000000000:certificate/00000000-0000-0000-0000-000000000000"

  validation {
    condition     = can(regex("^arn:aws:acm:[a-z0-9-]+:[0-9]{12}:certificate/[0-9a-f-]{36}$", var.certificate_arn))
    error_message = "certificate_arn must be a syntactically valid ACM certificate ARN."
  }
}

variable "github_repository" {
  description = "Exact GitHub owner/repository allowed to assume the deployment role."
  type        = string
  default     = "abdalrahmanattya/secure-url-shortener-platform"

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$", var.github_repository))
    error_message = "github_repository must be an exact owner/repository value."
  }
}

variable "github_environment" {
  description = "Required GitHub Actions environment name in the OIDC subject."
  type        = string
  default     = "demo"

  validation {
    condition     = can(regex("^[A-Za-z0-9_.-]{1,32}$", var.github_environment))
    error_message = "github_environment must be 1-32 simple characters."
  }
}

variable "enable_nat_gateway" {
  description = "Create one shared NAT gateway only for an explicitly approved external dependency; AWS runtime paths use private VPC endpoints by default."
  type        = bool
  default     = false
}

variable "enable_deletion_protection" {
  description = "Protect the Aurora cluster from accidental deletion. Keep true except for an explicitly approved demo destroy."
  type        = bool
  default     = true
}

variable "allow_demo_destroy" {
  description = "Explicit acknowledgement required before enabling deletion of the protected demo data plane."
  type        = bool
  default     = false
}

variable "db_backup_retention_days" {
  description = "Aurora automated backup retention."
  type        = number
  default     = 7

  validation {
    condition     = var.db_backup_retention_days >= 1 && var.db_backup_retention_days <= 35
    error_message = "db_backup_retention_days must be between 1 and 35."
  }
}

variable "db_min_capacity" {
  description = "Aurora Serverless v2 minimum ACU."
  type        = number
  default     = 0.5

  validation {
    condition     = var.db_min_capacity >= 0.5 && var.db_min_capacity <= 128
    error_message = "db_min_capacity must be between 0.5 and 128 ACUs."
  }
}

variable "db_max_capacity" {
  description = "Aurora Serverless v2 maximum ACU."
  type        = number
  default     = 2

  validation {
    condition     = var.db_max_capacity >= var.db_min_capacity && var.db_max_capacity <= 128
    error_message = "db_max_capacity must be at least db_min_capacity and no more than 128 ACUs."
  }
}

variable "ecs_cpu" {
  description = "Fargate task CPU units."
  type        = number
  default     = 512
}

variable "ecs_memory" {
  description = "Fargate task memory in MiB."
  type        = number
  default     = 1024
}

variable "ecs_desired_count" {
  description = "Initial ECS desired task count."
  type        = number
  default     = 2
}

variable "ecs_min_count" {
  description = "Minimum ECS autoscaling task count."
  type        = number
  default     = 2
}

variable "ecs_max_count" {
  description = "Maximum ECS autoscaling task count."
  type        = number
  default     = 6
}

variable "tags" {
  description = "Additional tags applied to managed resources."
  type        = map(string)
  default     = {}
}

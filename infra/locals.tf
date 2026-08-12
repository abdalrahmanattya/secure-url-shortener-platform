locals {
  name = "${var.project_name}-${var.environment}"

  azs = length(var.availability_zones) == 2 ? var.availability_zones : slice(data.aws_availability_zones.available.names, 0, 2)

  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Portfolio   = "secure-container-delivery"
    },
    var.tags,
  )

  public_subnets = {
    for index, az in local.azs : az => {
      cidr = cidrsubnet(var.vpc_cidr, 4, index)
      az   = az
    }
  }

  private_subnets = {
    for index, az in local.azs : az => {
      cidr = cidrsubnet(var.vpc_cidr, 4, index + 2)
      az   = az
    }
  }

  isolated_subnets = {
    for index, az in local.azs : az => {
      cidr = cidrsubnet(var.vpc_cidr, 4, index + 4)
      az   = az
    }
  }

  deployment_subject = "repo:${var.github_repository}:environment:${var.github_environment}"
  secret_arns        = [aws_secretsmanager_secret.database.arn, aws_secretsmanager_secret.application.arn]
}

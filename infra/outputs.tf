output "vpc_id" {
  description = "VPC identifier."
  value       = aws_vpc.this.id
}

output "alb_dns_name" {
  description = "ALB DNS name; public DNS is intentionally not managed here."
  value       = aws_lb.app.dns_name
}

output "ecr_repository_url" {
  description = "ECR repository URL for immutable image publication."
  value       = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster name."
  value       = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  description = "ECS service name."
  value       = aws_ecs_service.app.name
}

output "aurora_endpoint" {
  description = "Aurora writer endpoint; credentials are intentionally not output."
  value       = aws_rds_cluster.aurora.endpoint
}

output "database_secret_arn" {
  description = "Secrets Manager ARN containing generated database credentials."
  value       = aws_secretsmanager_secret.database.arn
}

output "application_secret_arn" {
  description = "Secrets Manager ARN containing the generated application secret."
  value       = aws_secretsmanager_secret.application.arn
}

output "github_deploy_role_arn" {
  description = "OIDC deployment role ARN for the exact GitHub repository/environment subject."
  value       = aws_iam_role.github_deploy.arn
}

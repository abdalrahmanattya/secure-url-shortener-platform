resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${local.name}"
  retention_in_days = 30
  kms_key_id        = aws_kms_key.platform.arn
  lifecycle { prevent_destroy = true }
}

resource "aws_cloudwatch_log_metric_filter" "redirect_errors" {
  name           = "${local.name}-application-errors"
  log_group_name = aws_cloudwatch_log_group.app.name
  pattern        = "{ $.status >= 500 }"
  metric_transformation {
    name      = "ApplicationErrors"
    namespace = "${var.project_name}/application"
    value     = "1"
  }
}

resource "aws_cloudwatch_dashboard" "platform" {
  dashboard_name = local.name
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "ECS service health"
          region = var.aws_region
          stat   = "Average"
          period = 300
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.app.name],
            ["AWS/ECS", "MemoryUtilization", "ClusterName", aws_ecs_cluster.this.name, "ServiceName", aws_ecs_service.app.name]
          ]
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "ALB request outcomes"
          region = var.aws_region
          stat   = "Sum"
          period = 300
          metrics = [
            ["AWS/ApplicationELB", "HTTPCode_ELB_5XX_Count", "LoadBalancer", aws_lb.app.arn_suffix],
            ["AWS/ApplicationELB", "RejectedConnectionCount", "LoadBalancer", aws_lb.app.arn_suffix]
          ]
        }
      }
    ]
  })
}

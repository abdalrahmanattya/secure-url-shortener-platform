resource "aws_cloudwatch_metric_alarm" "ecs_low_running_tasks" {
  alarm_name          = "${local.name}-ecs-low-running-tasks"
  alarm_description   = "Alert when the ECS service has fewer running tasks than desired."
  namespace           = "ECS/ContainerInsights"
  metric_name         = "RunningTaskCount"
  dimensions          = { ClusterName = aws_ecs_cluster.this.name, ServiceName = aws_ecs_service.app.name }
  statistic           = "Minimum"
  period              = 300
  evaluation_periods  = 2
  threshold           = var.ecs_min_count
  comparison_operator = "LessThanThreshold"
  treat_missing_data  = "breaching"
}

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${local.name}-alb-5xx"
  alarm_description   = "Alert on elevated ALB server-side errors."
  namespace           = "AWS/ApplicationELB"
  metric_name         = "HTTPCode_ELB_5XX_Count"
  dimensions          = { LoadBalancer = aws_lb.app.arn_suffix }
  statistic           = "Sum"
  period              = 300
  evaluation_periods  = 2
  threshold           = 5
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
}

resource "aws_cloudwatch_metric_alarm" "aurora_cpu" {
  alarm_name          = "${local.name}-aurora-cpu"
  alarm_description   = "Alert when Aurora CPU remains elevated."
  namespace           = "AWS/RDS"
  metric_name         = "CPUUtilization"
  dimensions          = { DBClusterIdentifier = aws_rds_cluster.aurora.cluster_identifier }
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 3
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
}

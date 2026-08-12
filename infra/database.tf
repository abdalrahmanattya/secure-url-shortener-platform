resource "aws_db_subnet_group" "aurora" {
  name       = "${local.name}-aurora"
  subnet_ids = [for subnet in aws_subnet.isolated : subnet.id]
  tags       = { Name = "${local.name}-aurora" }
}

resource "aws_rds_cluster" "aurora" {
  cluster_identifier              = "${local.name}-aurora"
  engine                          = "aurora-postgresql"
  engine_mode                     = "provisioned"
  engine_version                  = "16.4"
  database_name                   = "urlshortener"
  master_username                 = "urlshortener"
  master_password                 = random_password.database.result
  db_subnet_group_name            = aws_db_subnet_group.aurora.name
  vpc_security_group_ids          = [aws_security_group.database.id]
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.platform.arn
  backup_retention_period         = var.db_backup_retention_days
  preferred_backup_window         = "03:00-04:00"
  preferred_maintenance_window    = "sun:04:00-sun:05:00"
  deletion_protection             = var.enable_deletion_protection || !var.allow_demo_destroy
  skip_final_snapshot             = var.allow_demo_destroy && var.environment != "prod"
  final_snapshot_identifier       = var.allow_demo_destroy && var.environment != "prod" ? null : "${local.name}-final"
  copy_tags_to_snapshot           = true
  enabled_cloudwatch_logs_exports = ["postgresql"]

  serverlessv2_scaling_configuration {
    min_capacity = var.db_min_capacity
    max_capacity = var.db_max_capacity
  }

  lifecycle {
    prevent_destroy = true
    precondition {
      condition     = var.environment != "prod" || var.enable_deletion_protection
      error_message = "Production requires enable_deletion_protection=true."
    }
  }
  tags = { Name = "${local.name}-aurora" }
}

resource "aws_rds_cluster_instance" "aurora" {
  identifier                   = "${local.name}-aurora-1"
  cluster_identifier           = aws_rds_cluster.aurora.id
  instance_class               = "db.serverless"
  engine                       = aws_rds_cluster.aurora.engine
  engine_version               = aws_rds_cluster.aurora.engine_version
  db_subnet_group_name         = aws_db_subnet_group.aurora.name
  publicly_accessible          = false
  auto_minor_version_upgrade   = true
  performance_insights_enabled = true

  tags = { Name = "${local.name}-aurora-1" }
}

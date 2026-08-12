resource "random_password" "database" {
  length           = 32
  special          = true
  override_special = "-_@%+="
}

resource "random_password" "admin" {
  length           = 32
  special          = true
  override_special = "-_@%+="
}

resource "random_password" "owner" {
  length           = 32
  special          = true
  override_special = "-_@%+="
}

resource "aws_secretsmanager_secret" "database" {
  name                    = "${local.name}/database"
  description             = "Generated Aurora bootstrap credentials; values are never outputs"
  kms_key_id              = aws_kms_key.platform.arn
  recovery_window_in_days = 30
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql+asyncpg://urlshortener:${urlencode(random_password.database.result)}@${aws_rds_cluster.aurora.endpoint}:5432/urlshortener"
  })
}

resource "aws_secretsmanager_secret" "application" {
  name                    = "${local.name}/application"
  description             = "Generated application administration secret; value is never an output"
  kms_key_id              = aws_kms_key.platform.arn
  recovery_window_in_days = 30
}

resource "aws_secretsmanager_secret_version" "application" {
  secret_id = aws_secretsmanager_secret.application.id
  secret_string = jsonencode({
    OWNER_TOKENS = "owner:${random_password.owner.result}"
    ADMIN_TOKENS = "admin:${random_password.admin.result}"
  })
}

resource "aws_kms_key" "platform" {
  description             = "Encryption key for ${local.name} data and logs"
  enable_key_rotation     = true
  deletion_window_in_days = 30

  lifecycle {
    prevent_destroy = true
  }
  tags = { Name = "${local.name}-platform" }
}

resource "aws_kms_alias" "platform" {
  name          = "alias/${local.name}-platform"
  target_key_id = aws_kms_key.platform.key_id
}

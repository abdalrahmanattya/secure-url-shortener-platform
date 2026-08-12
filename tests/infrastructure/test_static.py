#!/usr/bin/env python3
"""Credential-free structural checks for the AWS Terraform target."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INFRA = ROOT / "infra"


def read(name: str) -> str:
    return (INFRA / name).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    versions = read("versions.tf")
    require('source  = "hashicorp/aws"' in versions, "AWS provider is declared")
    require('version = "~> 6.0"' in versions, "AWS provider is version constrained")
    require('source  = "hashicorp/random"' in versions, "random provider is declared")
    require('backend "s3" {}' in versions, "S3 backend is explicit and bootstrap-configured")

    all_hcl = "\n".join(path.read_text(encoding="utf-8") for path in INFRA.glob("*.tf"))
    required_blocks = (
        'resource "aws_vpc"',
        'resource "aws_lb"',
        'resource "aws_ecs_service"',
        'resource "aws_rds_cluster"',
        'resource "aws_wafv2_web_acl"',
        'resource "aws_ecr_repository"',
        'resource "aws_secretsmanager_secret"',
        'resource "aws_cloudwatch_dashboard"',
        'resource "aws_iam_role" "github_deploy"',
    )
    for block in required_blocks:
        require(block in all_hcl, f"required block present: {block}")

    require('image_tag_mutability = "IMMUTABLE"' in read("ecr.tf"), "ECR tags are immutable")
    require("scan_on_push = true" in read("ecr.tf"), "ECR scans on push")
    require("container_image_digest" in read("ecs.tf"), "ECS consumes digest input")
    require("latest" not in all_hcl.lower(), "Terraform does not use latest image tags")
    require("assign_public_ip = false" in read("ecs.tf"), "ECS tasks have no public IP")
    ecs = read("ecs.tf")
    require(
        '{ name = "ENVIRONMENT", value = var.environment }' in ecs,
        "ECS uses the application environment variable",
    )
    require(
        'name = "DATABASE_URL"' in ecs and ":DATABASE_URL::" in ecs,
        "DATABASE_URL uses a Secrets Manager JSON key",
    )
    require(
        'name = "OWNER_TOKENS"' in ecs and ":OWNER_TOKENS::" in ecs,
        "OWNER_TOKENS uses a Secrets Manager JSON key",
    )
    require(
        'name = "ADMIN_TOKENS"' in ecs and ":ADMIN_TOKENS::" in ecs,
        "ADMIN_TOKENS uses a Secrets Manager JSON key",
    )
    require(
        "APP_ENV" not in ecs and "DB_SECRET_ARN" not in ecs,
        "ECS does not use unsupported application variable names",
    )
    require(
        "/healthz" in ecs and "curl" not in ecs,
        "ECS health check uses the application health endpoint and Python",
    )
    secrets = read("secrets.tf")
    for key in ("DATABASE_URL", "OWNER_TOKENS", "ADMIN_TOKENS"):
        require(key in secrets, f"Secrets Manager JSON contains {key}")
    alb = read("alb.tf")
    require(
        'path                = "/healthz"' in alb,
        "ALB health check uses the application health endpoint",
    )
    require(
        'type = "redirect"' in alb and 'protocol    = "HTTPS"' in alb,
        "HTTP always redirects to HTTPS",
    )
    require(
        "fixed_response" not in alb and "count =" not in alb,
        "HTTPS is not an optional plaintext fallback",
    )
    security = read("security.tf")
    require('ip_protocol       = "tcp"' in security, "security groups use explicit TCP rules")
    require('ip_protocol       = "-1"' not in security, "no unrestricted security-group protocol")
    require(
        re.search(r"egress\s*\{[^}]*0\.0\.0\.0/0", security, re.DOTALL) is None,
        "no unrestricted security-group egress",
    )
    require(
        "referenced_security_group_id = aws_security_group.ecs.id" in security,
        "ALB/ECS and database/ECS SG references exist",
    )
    require("egress = []" in security, "database egress is explicitly empty")
    endpoints = read("endpoints.tf")
    require('vpc_endpoint_type   = "Interface"' in endpoints, "AWS interface endpoints are private")
    require('vpc_endpoint_type = "Gateway"' in endpoints, "S3 uses a gateway endpoint")
    require("aws_prefix_list.s3" in security, "S3 egress uses the AWS managed prefix list")
    require(
        re.search(r"from_port\s*=\s*5432", read("security.tf")) is not None,
        "database ingress is PostgreSQL",
    )
    require(
        "referenced_security_group_id = aws_security_group.ecs.id" in read("security.tf"),
        "database ingress is ECS-only",
    )
    require("deletion_protection" in read("database.tf"), "Aurora deletion protection is explicit")
    require("prevent_destroy = true" in read("database.tf"), "Aurora has an explicit destroy guard")
    require("random_password" in read("secrets.tf"), "secrets are generated")
    require("password" not in read("outputs.tf").lower(), "secret values are not outputs")
    require("token.actions.githubusercontent.com" in read("iam.tf"), "GitHub OIDC is configured")
    require("deployment_subject" in read("iam.tf"), "OIDC subject is constrained")
    require(
        "values   = [local.deployment_subject]" in read("iam.tf"),
        "OIDC trusts only the protected environment subject",
    )
    require(
        "deployment_ref" not in all_hcl and "github_ref" not in all_hcl,
        "OIDC has no branch/ref bypass",
    )
    require(
        'pattern        = "{ $.status >= 500 }"' in read("logging.tf"),
        "metric filter matches structured status logs",
    )
    require(
        "certificate/00000000-0000-0000-0000-000000000000" in read("variables.tf"),
        "certificate placeholder supports validation",
    )
    require(
        "encrypt        = true" in (ROOT / "infra/backend.hcl.example").read_text(encoding="utf-8"),
        "state backend encryption is explicit",
    )
    require("ELBSecurityPolicy-TLS13-1-2-2021-06" in read("alb.tf"), "HTTPS uses secure policy")
    require("AWSManagedRulesCommonRuleSet" in read("alb.tf"), "WAF managed rules are enabled")
    require("rate_based_statement" in read("alb.tf"), "WAF rate limiting is enabled")

    for path in INFRA.rglob("*"):
        if path.is_file() and path.suffix in {".tf", ".tfvars", ".hcl"}:
            content = path.read_text(encoding="utf-8")
            require(not re.search(r"AKIA[0-9A-Z]{16}", content), f"no AWS key in {path}")
            require("-----BEGIN" not in content, f"no private key in {path}")

    print("Infrastructure structural checks passed")


if __name__ == "__main__":
    main()

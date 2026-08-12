#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
infra_dir="${repo_root}/infra"

terraform -chdir="${infra_dir}" fmt -check -recursive
terraform -chdir="${infra_dir}" init -backend=false -input=false
terraform -chdir="${infra_dir}" validate
python3 "${repo_root}/tests/infrastructure/test_static.py"

if command -v tflint >/dev/null 2>&1; then
  tflint --chdir="${infra_dir}" --init
  tflint --chdir="${infra_dir}"
else
  echo "tflint not installed; configuration is present for the reviewed policy run." >&2
fi

if command -v checkov >/dev/null 2>&1; then
  checkov --directory "${infra_dir}" --config-file "${infra_dir}/.checkov.yml"
elif command -v tfsec >/dev/null 2>&1; then
  tfsec "${infra_dir}"
else
  echo "checkov/tfsec not installed; compatible policy configuration is present." >&2
fi

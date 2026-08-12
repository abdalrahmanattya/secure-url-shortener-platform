#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if command -v actionlint >/dev/null 2>&1; then
  actionlint "${repo_root}/.github/workflows"/*.yml
fi

if command -v ruby >/dev/null 2>&1; then
  ruby -ryaml -e 'ARGV.each { |path| YAML.parse_file(path); puts "YAML ok: #{path}" }' \
    "${repo_root}/.github/workflows"/*.yml
else
  echo "ruby is required for local workflow syntax checks" >&2
  exit 1
fi

while IFS= read -r action_reference; do
  sha="${action_reference##*@}"
  if [[ ! "${sha}" =~ ^[0-9a-f]{40}$ ]]; then
    echo "Unpinned GitHub Action: ${action_reference}" >&2
    exit 1
  fi
done < <(rg -o --glob '*.yml' --glob '*.yaml' 'uses: [^[:space:]]+' "${repo_root}/.github/workflows" | sed 's/.*uses: //')

echo "Workflow syntax and action pin checks passed"

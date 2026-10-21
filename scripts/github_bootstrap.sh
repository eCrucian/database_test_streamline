#!/usr/bin/env bash
# Cria o repositório no GitHub, sobe main e dev, cria os ambientes e protege as branches.
#
# Pré-requisito (uma vez):  gh auth login -s workflow
# Uso:                      scripts/github_bootstrap.sh [nome-do-repo] [private|public]
#
# Proteção de branch em repositório privado exige GitHub Pro/Team; no plano gratuito
# ela só funciona em repositório público (o script avisa e segue se não puder).
set -euo pipefail

repo_name="${1:-database_test_streamline}"
visibility="${2:-private}"

gh auth status >/dev/null

if ! git rev-parse --verify HEAD >/dev/null 2>&1; then
  git add -A
  git commit -m "chore: estrutura inicial do dbts"
fi

git branch -M main
gh repo create "$repo_name" "--${visibility}" --source . --remote origin --push

git switch -c dev
git push -u origin dev
git switch main

slug=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
gh api -X PUT "repos/${slug}/environments/dev" >/dev/null
gh api -X PUT "repos/${slug}/environments/production" >/dev/null

protect() {
  local branch="$1" body="$2"
  if ! gh api -X PUT "repos/${slug}/branches/${branch}/protection" --input - <<<"$body" >/dev/null; then
    echo "aviso: não foi possível proteger '${branch}' (plano do GitHub?)" >&2
  fi
}

# main: só via PR, com todos os checks verdes (inclusive integração), sem force push.
protect main '{
  "required_status_checks": {"strict": true, "contexts": ["lint", "sast", "unit", "integration"]},
  "enforce_admins": true,
  "required_pull_request_reviews": {"required_approving_review_count": 0},
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}'

# dev: exige lint, SAST e unitários; admin pode empurrar direto para agilizar.
protect dev '{
  "required_status_checks": {"strict": false, "contexts": ["lint", "sast", "unit"]},
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}'

gh repo set-default "$slug"
echo "pronto: https://github.com/${slug}"

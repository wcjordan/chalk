#!/usr/bin/env bash
set -euo pipefail
set -x

echo "DEBUG: pwd=$(pwd)"
echo "DEBUG: WORKSPACE=${WORKSPACE:-unset}"
ls -la
git rev-parse --is-inside-work-tree || echo "DEBUG: not inside a git work tree"
git status || echo "DEBUG: git status failed"

pip install --quiet pur

curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
    | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
    | tee /etc/apt/sources.list.d/github-cli.list > /dev/null
apt-get update -qq && apt-get install -y -qq gh

export GH_TOKEN="${GH_APP_PSW}"
gh auth setup-git

git config user.email "jenkins@minordomo"
git config user.name "Jenkins"

BRANCH="chore/bump-python-deps-$(date +%Y%m%d)"
git checkout -b "$BRANCH"

(cd server && pur -r requirements.txt && pur -r dev-requirements.txt)
(cd test_gen && pur -r requirements.txt && pur -r dev-requirements.txt)
(cd tests && pur --skip playwright -r requirements.txt)

if git diff --quiet; then
    echo "No Python dependency updates found."
    exit 0
fi

git add \
    server/requirements.txt \
    server/dev-requirements.txt \
    test_gen/requirements.txt \
    test_gen/dev-requirements.txt \
    tests/requirements.txt

git commit -m "chore: bump Python dependencies"
git push origin "$BRANCH"

gh pr create \
    --base main \
    --head "$BRANCH" \
    --title "chore: bump Python dependencies" \
    --body "Automated weekly bump of pinned Python dependency versions via \`pur\`."

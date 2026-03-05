#!/bin/bash
set -e

REGISTRY="ghcr.io"
REPO="manumnoha-sys/watch-dev"
IMAGE_NAME="watch-dev"
REGISTRY_IMAGE="${REGISTRY}/${REPO}:latest"

# Load token from file if not already in environment
if [ -z "${GITHUB_TOKEN}" ] && [ -f "${HOME}/.secrets/github_token" ]; then
    GITHUB_TOKEN="$(cat "${HOME}/.secrets/github_token")"
fi

if [ -z "${GITHUB_TOKEN}" ]; then
    echo "Error: GITHUB_TOKEN is not set."
    echo "Either export it or save it to ~/.secrets/github_token"
    exit 1
fi

# Login to GHCR
echo "${GITHUB_TOKEN}" | docker login "${REGISTRY}" -u manumnoha-sys --password-stdin

# Tag and push Docker image
echo "Tagging and pushing image to ${REGISTRY_IMAGE}..."
docker tag "${IMAGE_NAME}" "${REGISTRY_IMAGE}"
docker push "${REGISTRY_IMAGE}"

# Commit and push updated files
echo "Pushing updated files to GitHub..."
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "${REPO_ROOT}"
git add infra/
git diff --cached --quiet || git commit -m "infra: rebuild Docker image $(date +%Y-%m-%d)"
git remote set-url origin "https://manumnoha-sys:${GITHUB_TOKEN}@github.com/manumnoha-sys/smartwatch"
git push origin main
git remote set-url origin "https://github.com/manumnoha-sys/smartwatch"

echo ""
echo "Done! Image available at: ${REGISTRY_IMAGE}"

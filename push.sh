#!/bin/bash
set -e

REGISTRY="ghcr.io"
REPO="manumnoha-sys/watch-dev"
IMAGE_NAME="watch-dev"
REGISTRY_IMAGE="${REGISTRY}/${REPO}:latest"

# Require GITHUB_TOKEN env var
if [ -z "${GITHUB_TOKEN}" ]; then
    echo "Error: GITHUB_TOKEN is not set."
    echo "Create a token at https://github.com/settings/tokens with scopes: write:packages, read:packages"
    echo "Then run: export GITHUB_TOKEN=<your_token>"
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
cd "$(dirname "$0")"
git add Dockerfile run.sh
git commit -m "Rebuild for arm64: IntelliJ IDEA $(date +%Y-%m-%d)"
git push origin main

echo ""
echo "Done! Image available at: ${REGISTRY_IMAGE}"

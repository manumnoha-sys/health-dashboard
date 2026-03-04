#!/bin/bash
set -e

CONTAINER_NAME="watch-dev"
IMAGE_NAME="watch-dev"
PROJECTS_DIR="${HOME}/watch-projects"

# Create persistent dirs on host if they don't exist
mkdir -p "${PROJECTS_DIR}"
mkdir -p "${HOME}/.android-docker"
mkdir -p "${HOME}/.gradle-docker"

# Allow local X11 connections
if xhost &>/dev/null; then
    xhost +local:root > /dev/null
fi

# Remove old container if stopped
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    STATUS=$(docker inspect -f '{{.State.Status}}' "${CONTAINER_NAME}")
    if [ "${STATUS}" != "running" ]; then
        echo "Removing stopped container: ${CONTAINER_NAME}"
        docker rm "${CONTAINER_NAME}"
    else
        echo "Container '${CONTAINER_NAME}' is already running. Use into.sh to get a shell."
        exit 0
    fi
fi

echo "Starting container: ${CONTAINER_NAME}"

# KVM flags (optional — only add if /dev/kvm exists and kvm group is present)
KVM_FLAGS=()
if [ -e /dev/kvm ] && getent group kvm &>/dev/null; then
    KVM_GID=$(getent group kvm | cut -d: -f3)
    KVM_FLAGS=(--device /dev/kvm --group-add "${KVM_GID}")
    echo "KVM acceleration enabled (GID ${KVM_GID})"
else
    echo "KVM not available — emulator will run without hardware acceleration"
fi

docker run -d \
    --name "${CONTAINER_NAME}" \
    --network host \
    -e DISPLAY=:0 \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v "${PROJECTS_DIR}:/home/$(whoami)/projects" \
    -v "${HOME}/.android-docker:/home/$(whoami)/.android" \
    -v "${HOME}/.gradle-docker:/home/$(whoami)/.gradle" \
    "${KVM_FLAGS[@]}" \
    "${IMAGE_NAME}" \
    sleep infinity

echo "Container '${CONTAINER_NAME}' started."
echo "Run ./into.sh to get a shell, or run Android Studio with:"
echo "  docker exec -it ${CONTAINER_NAME} studio.sh"

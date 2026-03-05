#!/bin/bash
set -e

CONTAINER_NAME="watch-dev"

if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Container '${CONTAINER_NAME}' is not running. Start it with ./run.sh first."
    exit 1
fi

if xhost &>/dev/null; then
    xhost +local:root > /dev/null
fi

docker exec \
    -u "$(whoami)" \
    -e "DISPLAY=${DISPLAY}" \
    -it "${CONTAINER_NAME}" \
    bash

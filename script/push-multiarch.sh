#!/usr/bin/env bash
# Builds amd64 and arm64 images and pushes them. Needed when your computer
# (for example Apple Silicon) differs from the machine that runs the cluster.
set -euo pipefail
USER_NAME="${DOCKERHUB_USER:?set DOCKERHUB_USER}"
TAG="${TAG:-1.0}"
docker buildx inspect pft-builder >/dev/null 2>&1 || docker buildx create --name pft-builder --use
docker buildx use pft-builder
for pair in workout-service:pft-workout recommendation-service:pft-recommendation web-gateway:pft-gateway; do
  dir="${pair%%:*}"; image="${pair##*:}"
  docker buildx build --platform linux/amd64,linux/arm64 -t "$USER_NAME/$image:$TAG" --push "./$dir"
done

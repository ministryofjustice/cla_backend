#!/usr/bin/env bash
set -e

ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../helm_deploy/cla-backend/"

helm upgrade cla-backend \
$HELM_DIR \
--values ${HELM_DIR}/values-staging.yaml \
--install \
--set image.tag=$IMAGE_TAG

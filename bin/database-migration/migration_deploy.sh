#!/usr/bin/env bash
set -e
NAMESPACE=$1
ROOT=$(dirname "$0")
HELM_DIR="$ROOT/../../helm_deploy/cla-backend-migration/"

helm upgrade cla-backend-migration \
  $HELM_DIR \
  --namespace $NAMESPACE \
  --install \
  --force \
  --debug

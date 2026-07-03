#!/usr/bin/env bash
set -e

RELEASE_NAME=$(echo $BRANCH_NAME | sed 's/^feature[-/]//' | sed 's:^\w*\/::' | tr -s ' _/[]().' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-28 | sed 's/-$//')
APP_DEPLOYMENT_NAME="${RELEASE_NAME}-cla-backend-app"

echo "Attempting to delete release $RELEASE_NAME"

RELEASES=$(helm list --all)

echo "Current releases:"
echo "$RELEASES"

if [[ $RELEASES == *"$RELEASE_NAME"* ]]
then
  echo "Scaling down app deployment before deleting release"
  kubectl scale deployment "$APP_DEPLOYMENT_NAME" --replicas=0 --ignore-not-found=true

  echo "Waiting for app pods to stop"
  kubectl wait \
    --for=delete pod \
    -l "app=web,app.kubernetes.io/instance=$RELEASE_NAME" \
    --timeout=90s || true

  echo "Deleting release $RELEASE_NAME"
  helm delete "$RELEASE_NAME" --wait --timeout=3m
else
  echo "Release $RELEASE_NAME was not found"
fi

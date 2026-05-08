#!/usr/bin/env bash
set -e

RELEASE_NAME=$(echo $BRANCH_NAME | sed 's/^feature[-/]//' | sed 's:^\w*\/::' | tr -s ' _/[]().' '-' | tr '[:upper:]' '[:lower:]' | cut -c1-28 | sed 's/-$//')

echo "Attempting to delete release $RELEASE_NAME"

RELEASES=$(helm list --all)

echo "Current releases:"
echo "$RELEASES"

if [[ $RELEASES == *"$RELEASE_NAME"* ]]
then
  echo "Deleting release $RELEASE_NAME"
  helm delete $RELEASE_NAME
else
  echo "Release $RELEASE_NAME was not found"
fi

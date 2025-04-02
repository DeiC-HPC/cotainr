#!/bin/bash

ENCODED_TOKEN=$(echo -n "$GH_TOKEN" | base64)
TAGS=$(curl -s -H "Authorization: Bearer ${ENCODED_TOKEN}" \
  https://ghcr.io/v2/deic-hpc/cotainr/$1/$2/tags/list)
echo "TAGS: $TAGS"

## Check if TAGS is empty or null
if [[ -z "$TAGS" || "$TAGS" == "null" ]]; then
  echo "No tags found. Stopping."
  exit 1
else
  ## Check if the specific tag already exists
  if echo "$TAGS" | jq -e --arg TAG "$3" '.tags | index($TAG)'; then
    echo "Image with tag $3 exists."
    echo "container_tag=$3" >> $GITHUB_OUTPUT
  else
    echo "Image with tag $3 not found. Defaulting to main image."
    echo "container_tag=$3" >> $GITHUB_OUTPUT
  fi
fi
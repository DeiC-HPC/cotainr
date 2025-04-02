#!/bin/bash

curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: Bearer $GH_TOKEN" \
  https://api.github.com/repos/$1/actions/workflows/CI_push.yml/dispatches \
  -d '{"ref": '"$2"'}'

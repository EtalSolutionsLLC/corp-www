#!/usr/bin/env bash
set -euo pipefail

: "${READ_OPS_AND_SOPS:?Codespaces secret READ_OPS_AND_SOPS is missing}"
export GH_TOKEN="$READ_OPS_AND_SOPS"

ops_git() {
  git -c credential.helper= \
    -c 'credential.helper=!gh auth git-credential' "$@"
}

source=/workspaces/.ops-and-sops

if [ ! -d "$source/.git" ]; then
  ops_git clone --filter=blob:none --sparse \
    https://github.com/EtalSolutionsLLC/ops-and-sops.git "$source"
fi

ops_git -C "$source" sparse-checkout set ops/portmason

if [ ! -e /workspaces/portmason ] && [ ! -L /workspaces/portmason ]; then
  ln -s "$source/ops/portmason" /workspaces/portmason
fi

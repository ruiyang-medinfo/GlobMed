#!/usr/bin/env bash
# Fetch the exact external dependency used by the supplied training recipes.
set -euo pipefail
cd "$(dirname "$0")/.."
factory_commit=95ac3f2373b82662c1bd855c284d3379e6a763d3
if [ -e third_party/LlamaFactory ]; then
  test "$(git -C third_party/LlamaFactory rev-parse HEAD)" = "$factory_commit"
  test -z "$(git -C third_party/LlamaFactory status --porcelain)"
else
  mkdir -p third_party
  git clone https://github.com/hiyouga/LlamaFactory.git third_party/LlamaFactory
  git -C third_party/LlamaFactory checkout --detach "$factory_commit"
fi
printf 'LLaMA-Factory ready at %s\n' "$factory_commit"

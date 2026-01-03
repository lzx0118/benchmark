#!/usr/bin/env bash
set -euo pipefail

# Build X-Bench for all languages (bn fa hu id ms ur).
# Usage:
#   bash tools/build_all.sh

for lang in bn fa hu id ms ur; do
  echo "===================="
  echo "Building ${lang}"
  echo "===================="
  bash tools/build_one_lang.sh "${lang}"
done

echo "All done."

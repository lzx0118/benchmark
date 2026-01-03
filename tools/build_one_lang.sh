#!/usr/bin/env bash
set -euo pipefail

# Build X-Bench for one language.
# Usage:
#   bash tools/build_one_lang.sh bn
#
# NOTE:
# - You must first replace <PATH_TO_XBENCH_ROOT> in scripts/ with your local absolute path.
# - You must place OPUS raw files in the directories referenced by each script's BASE_DIR.

LANG="${1:-}"
if [[ -z "${LANG}" ]]; then
  echo "Usage: bash tools/build_one_lang.sh <lang>"
  echo "Supported: bn fa hu id ms ur"
  exit 1
fi

run() { echo "+ $*"; "$@"; }

case "${LANG}" in
  bn)
    run python scripts/bn/bn_Opensubtitles.py
    run python scripts/bn/bn_Opensubtitle_250.py
    run python scripts/bn/bn_TED.py
    run python scripts/bn/bn_TED_250.py
    run python scripts/bn/bn_QED.py
    run python scripts/bn/bn_QED_250.py
    run python scripts/bn/bn_Tanzil.py
    run python scripts/bn/bn_Tanzil_250.py
    run python scripts/bn/bn_wikimatrix.py
    run python scripts/bn/bn_wikimatrix_250.py
    run python scripts/bn/bn_merge.py
    ;;
  fa)
    run python scripts/fa/fa_TED.py
    run python scripts/fa/fa_TED_250.py
    run python scripts/fa/fa_QED.py
    run python scripts/fa/fa_QED_250.py
    run python scripts/fa/fa_Tanzil.py
    run python scripts/fa/fa_Tanzil_250.py
    run python scripts/fa/fa_wikimatrix.py
    run python scripts/fa/fa_wikimatrix_250.py
    run python scripts/fa/fa_TEP.py
    run python scripts/fa/fa_TEP_250.py
    run python scripts/fa/fa_merge.py
    ;;
  hu)
    run python scripts/hu/hu_opensubtitles.py
    run python scripts/hu/hu_opensubtitle_200.py
    run python scripts/hu/hu_TED.py
    run python scripts/hu/hu_TED_200.py
    run python scripts/hu/hu_QED.py
    run python scripts/hu/hu_QED_200.py
    run python scripts/hu/hu_wikimatrix.py
    run python scripts/hu/hu_wikimatrix_200.py
    run python scripts/hu/hu_Eurparl.py
    run python scripts/hu/hu_Europarl_200.py
    run python scripts/hu/hu_wmt_news.py
    run python scripts/hu/hu_wmt_200.py
    run python scripts/hu/hu_merge.py
    ;;
  id)
    run python scripts/id/id_Opensubtitle.py
    run python scripts/id/id_Opensubtitle_250.py
    run python scripts/id/id_TED.py
    run python scripts/id/id_TED_250.py
    run python scripts/id/id_QED.py
    run python scripts/id/id_QED_250.py
    run python scripts/id/id_Tanzil.py
    run python scripts/id/id_Tanzil_250.py
    run python scripts/id/id_wikimatrix.py
    run python scripts/id/id_wikimatrix_250.py
    run python scripts/id/id_merge.py
    ;;
  ms)
    run python scripts/ms/ms_opensubtitle.py
    run python scripts/ms/ms_opensubtitle_250.py
    run python scripts/ms/ms_TED.py
    run python scripts/ms/ms_TED_250.py
    run python scripts/ms/ms_QED.py
    run python scripts/ms/ms_QED_250.py
    run python scripts/ms/ms_Tanzil.py
    run python scripts/ms/ms_Tanzil_250.py
    run python scripts/ms/ms_wikimedia.py
    run python scripts/ms/ms_wikimedia_250.py
    run python scripts/ms/ms_merge.py
    ;;
  ur)
    run python scripts/ur/ur_opensubtitle.py
    run python scripts/ur/ur_opensubtitles_250.py
    run python scripts/ur/ur_TED.py
    run python scripts/ur/ur_TED_250.py
    run python scripts/ur/ur_QED.py
    run python scripts/ur/ur_QED_250.py
    run python scripts/ur/ur_Tanzil.py
    run python scripts/ur/ur_Tanzil_250.py
    run python scripts/ur/ur_wikimedia.py
    run python scripts/ur/ur_wikimedia_250.py
    run python scripts/ur/ur_merge.py
    ;;
  *)
    echo "Unsupported language: ${LANG}"
    echo "Supported: bn fa hu id ms ur"
    exit 1
    ;;
esac

echo "Done: ${LANG}"

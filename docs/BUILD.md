# Build X-Bench (from OPUS downloads)

This document explains how to reproduce the released `data/*_all_merged_clean.tsv` files from OPUS corpora.

> If you only want to use X-Bench as a test set, you can **skip this document** and directly use `data/*.tsv`.

---

## 0) Prerequisites

- Python 3.8+
- No third-party libraries are required for the construction scripts (pure Python I/O).
- Download the relevant OPUS corpora for your language pair(s).
  The OPUS entry pages are listed in the repository `README.md`.

### Expected file naming

Each corpus-specific script contains explicit `EN_FILE` and `{XX}_FILE` variables, e.g.:

- `OpenSubtitles.bn-en.en` and `OpenSubtitles.bn-en.bn`
- `TED2020.en-id.en` and `TED2020.en-id.id`

Please place the downloaded (or extracted) files in the directories indicated by `BASE_DIR` inside each script.
If your filenames differ, **rename them to match** the script variables.

### Configure the root path

All scripts use a placeholder:

`<PATH_TO_XBENCH_ROOT>`

Replace it globally before running any script:

```bash
grep -rl "<PATH_TO_XBENCH_ROOT>" scripts | xargs sed -i "s|<PATH_TO_XBENCH_ROOT>|/abs/path/to/X-Bench|g"
```

---

## 1) Per-language build commands

Below we list the commands in the intended order: (i) merge raw files -> `*.merged.tsv`,
(ii) sample -> `*.sampleXXX.tsv`, (iii) merge sampled files into `*_all_merged_clean.tsv`.

### bn (Bengali)

```bash
python scripts/bn/bn_Opensubtitles.py
python scripts/bn/bn_Opensubtitle_250.py

python scripts/bn/bn_TED.py
python scripts/bn/bn_TED_250.py

python scripts/bn/bn_QED.py
python scripts/bn/bn_QED_250.py

python scripts/bn/bn_Tanzil.py
python scripts/bn/bn_Tanzil_250.py

python scripts/bn/bn_wikimatrix.py
python scripts/bn/bn_wikimatrix_250.py

python scripts/bn/bn_merge.py
```

### fa (Persian)

```bash
python scripts/fa/fa_TED.py
python scripts/fa/fa_TED_250.py

python scripts/fa/fa_QED.py
python scripts/fa/fa_QED_250.py

python scripts/fa/fa_Tanzil.py
python scripts/fa/fa_Tanzil_250.py

python scripts/fa/fa_wikimatrix.py
python scripts/fa/fa_wikimatrix_250.py

python scripts/fa/fa_TEP.py
python scripts/fa/fa_TEP_250.py

python scripts/fa/fa_merge.py
```

### hu (Hungarian)

Note: this subset additionally uses Europarl and WMT-News, and sampling budgets are 200 in the provided scripts.

```bash
python scripts/hu/hu_opensubtitles.py
python scripts/hu/hu_opensubtitle_200.py

python scripts/hu/hu_TED.py
python scripts/hu/hu_TED_200.py

python scripts/hu/hu_QED.py
python scripts/hu/hu_QED_200.py

python scripts/hu/hu_wikimatrix.py
python scripts/hu/hu_wikimatrix_200.py

python scripts/hu/hu_Eurparl.py
python scripts/hu/hu_Europarl_200.py

python scripts/hu/hu_wmt_news.py
python scripts/hu/hu_wmt_200.py

python scripts/hu/hu_merge.py
```

### id (Indonesian)

```bash
python scripts/id/id_Opensubtitle.py
python scripts/id/id_Opensubtitle_250.py

python scripts/id/id_TED.py
python scripts/id/id_TED_250.py

python scripts/id/id_QED.py
python scripts/id/id_QED_250.py

python scripts/id/id_Tanzil.py
python scripts/id/id_Tanzil_250.py

python scripts/id/id_wikimatrix.py
python scripts/id/id_wikimatrix_250.py

python scripts/id/id_merge.py
```

### ms (Malay)

```bash
python scripts/ms/ms_opensubtitle.py
python scripts/ms/ms_opensubtitle_250.py

python scripts/ms/ms_TED.py
python scripts/ms/ms_TED_250.py

python scripts/ms/ms_QED.py
python scripts/ms/ms_QED_250.py

python scripts/ms/ms_Tanzil.py
python scripts/ms/ms_Tanzil_250.py

python scripts/ms/ms_wikimedia.py
python scripts/ms/ms_wikimedia_250.py

python scripts/ms/ms_merge.py
```

### ur (Urdu)

```bash
python scripts/ur/ur_opensubtitle.py
python scripts/ur/ur_opensubtitles_250.py

python scripts/ur/ur_TED.py
python scripts/ur/ur_TED_250.py

python scripts/ur/ur_QED.py
python scripts/ur/ur_QED_250.py

python scripts/ur/ur_Tanzil.py
python scripts/ur/ur_Tanzil_250.py

python scripts/ur/ur_wikimedia.py
python scripts/ur/ur_wikimedia_250.py

python scripts/ur/ur_merge.py
```

---

## 2) Copy final outputs into `data/`

The merge scripts write the final TSV under their `BASE_DIR`. After building, copy them into `data/`:

- `bn_all_merged_clean.tsv`
- `fa_all_merged_clean.tsv`
- `hu_all_merged_clean.tsv`
- `id_all_merged_clean.tsv`
- `ms_all_merged_clean.tsv`
- `ur_all_merged_clean.tsv`

You can then run:

```bash
python tools/check_tsv.py data/bn_all_merged_clean.tsv
```

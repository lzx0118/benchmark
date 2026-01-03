# X-Bench: Cross-domain Low-resource MT Test Sets (xx↔en)

X-Bench is a **multi-domain test benchmark** for evaluating **low-resource machine translation** under **domain shift**.
It is constructed by sampling parallel sentence pairs from multiple OPUS corpora, covering diverse domains such as movies/TV, talks, education, religion, encyclopedia, government, and news.

This repository contains:
- **Released test sets** in `data/` (TSV, columns: `id`, `en`, `xx`)
- **Dataset construction scripts** in `scripts/` (per-language, per-corpus)
- Minimal helper tools in `tools/` for sanity checks and convenience exports

> **What you can do immediately:** use the released TSVs in `data/` as test sets.  
> **What you can reproduce:** rebuild the TSVs from OPUS downloads using the scripts in `scripts/` (see `docs/BUILD.md`).

---

## Languages and sizes

We release six language subsets (total **6060** sentence pairs):

- `hu` (Hungarian): 1186
- `ms` (Malay): 1075
- `ur` (Urdu): 841
- `bn` (Bengali): 892
- `fa` (Persian): 911
- `id` (Indonesian): 1155

Released files:
- `data/bn_all_merged_clean.tsv`
- `data/fa_all_merged_clean.tsv`
- `data/hu_all_merged_clean.tsv`
- `data/id_all_merged_clean.tsv`
- `data/ms_all_merged_clean.tsv`
- `data/ur_all_merged_clean.tsv`

---

## Source corpora (OPUS entry pages) and domain mapping

| Corpus | Domain | OPUS entry page |
|---|---|---|
| OpenSubtitles | movies/TV | [OPUS page](https://opus.nlpl.eu/OpenSubtitles/corpus/version/OpenSubtitles) |
| TED2020 | talks | [OPUS page](https://opus.nlpl.eu/TED2020/corpus/version/TED2020) |
| QED | education | [OPUS page](https://opus.nlpl.eu/QED/corpus/version/QED) |
| Tanzil | religion | [OPUS page](https://opus.nlpl.eu/Tanzil/corpus/version/Tanzil) |
| Wikimedia | encyclopedia | [OPUS page](https://opus.nlpl.eu/wikimedia/corpus/version/wikimedia) |
| WikiMatrix | encyclopedia | [OPUS page](https://opus.nlpl.eu/WikiMatrix/corpus/version/WikiMatrix) |
| Europarl | government | [OPUS page](https://opus.nlpl.eu/Europarl/corpus/version/Europarl) |
| WMT-News | news | [OPUS page](https://opus.nlpl.eu/WMT-News/corpus/version/WMT-News) |
| TEP | movies/TV | [OPUS page](https://opus.nlpl.eu/TEP/corpus/version/TEP) |

Domains correspond to:
- **movies/TV**: OpenSubtitles, TEP
- **talks**: TED2020
- **education**: QED
- **religion**: Tanzil
- **encyclopedia**: Wikimedia, WikiMatrix
- **government**: Europarl
- **news**: WMT-News

---

## Composition by language

Checkmarks indicate which source datasets are included for each language subset.

| Lang | OpenSubs | TED2020 | QED | Tanzil | Wikimedia | WikiMatrix | Europarl | WMT-News | TEP | Size |
|------|----------|---------|-----|--------|----------|-----------|---------|----------|-----|------|
| hu   | ✓        | ✓       | ✓   |        |          | ✓         | ✓       | ✓        |     | 1186 |
| ms   | ✓        | ✓       | ✓   | ✓      | ✓        |           |         |          |     | 1075 |
| ur   | ✓        | ✓       | ✓   | ✓      | ✓        |           |         |          |     | 841  |
| bn   | ✓        | ✓       | ✓   | ✓      |          | ✓         |         |          |     | 892  |
| fa   |          | ✓       | ✓   | ✓      |          | ✓         |         |          | ✓   | 911  |
| id   | ✓        | ✓       | ✓   | ✓      |          | ✓         |         |          |     | 1155 |
| **Total** |    |         |     |        |          |           |         |          |     | **6060** |

---

## Data format

All released test sets are TSV files with the following columns:
- `id`: integer index starting from 1
- `en`: English sentence
- `xx`: source-language sentence (language-specific column: `bn/fa/hu/id/ms/ur`)

> Note: Domain labels are implicitly determined by the source corpus during construction; the released TSVs are the final merged test sets.

---

## Quick sanity check

```bash
python tools/check_tsv.py data/bn_all_merged_clean.tsv
```

Extract the source side as a plain text file:

```bash
python tools/extract_monolingual.py --input data/bn_all_merged_clean.tsv --col bn --output bn.src.txt
```

---

## Reproduce construction from OPUS downloads

See **docs/BUILD.md** for step-by-step instructions. In brief, each language follows:

1) For each corpus: merge the raw OPUS `*.en` + `*.xx` files into a `*.merged.tsv`  
2) Sample a fixed budget from each corpus into `*.sampleXXX.tsv` (typically 250; hu uses 200 for some corpora)  
3) Merge the sampled corpora into the final `*_all_merged_clean.tsv`

### Configure paths

All scripts contain a placeholder root path:

- `<PATH_TO_XBENCH_ROOT>`

Replace it globally (example on Linux/macOS):

```bash
grep -rl "<PATH_TO_XBENCH_ROOT>" scripts | xargs sed -i "s|<PATH_TO_XBENCH_ROOT>|/abs/path/to/X-Bench|g"
```

Then follow the per-language instructions in `docs/BUILD.md`.


### Optional: one-command build helpers

After replacing `<PATH_TO_XBENCH_ROOT>` in `scripts/`, you can run:

```bash
bash tools/build_one_lang.sh bn
# or build all:
bash tools/build_all.sh
```

---

## License and redistribution note

X-Bench is derived from multiple OPUS corpora. This repository releases:
- **small-scale curated test TSVs**, and
- **construction scripts**.

Please ensure that your use and redistribution comply with the licenses/terms of the original corpora.

---

## Citation

If you use X-Bench in your research, please cite the accompanying paper (to be added) and OPUS.
A `CITATION.cff` file is included for convenience.

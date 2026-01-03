#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extract monolingual text from a parallel TSV.

Input TSV format (header required): id<TAB>en<TAB>xx
Output: one sentence per line (xx side by default).

Example:
  python tools/extract_monolingual.py --input data/bn_all_merged_clean.tsv --lang_col bn --output bn.txt
"""

import argparse
import csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to parallel TSV with header.")
    ap.add_argument("--lang_col", required=True, help="Target language column name, e.g., bn/fa/hu/id/ms/ur.")
    ap.add_argument("--output", required=True, help="Output TXT path (one sentence per line).")
    args = ap.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        if args.lang_col not in reader.fieldnames:
            raise ValueError(f"lang_col={args.lang_col} not found. columns={reader.fieldnames}")
        with open(args.output, "w", encoding="utf-8") as out:
            n=0
            for row in reader:
                out.write((row[args.lang_col] or "").replace("\n"," ").strip() + "\n")
                n += 1
    print(f"[OK] Wrote {n} lines -> {args.output}")

if __name__ == "__main__":
    main()

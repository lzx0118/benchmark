#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Sanity-check X-Bench TSV files.

Checks:
- header has id/en/<lang>
- no empty sentences
- basic length stats
"""

import argparse
import csv
import statistics

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--lang", required=True, help="language code, e.g., bn/fa/hu/id/ms/ur")
    args = ap.parse_args()

    lens_en=[]
    lens_x=[]
    n=0
    with open(args.input, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        exp = {"id","en",args.lang}
        if set(reader.fieldnames) != exp:
            raise ValueError(f"Unexpected header: {reader.fieldnames} (expected exactly {sorted(exp)})")
        for row in reader:
            n += 1
            en=row["en"].strip()
            xx=row[args.lang].strip()
            if not en or not xx:
                raise ValueError(f"Empty sentence at row {n}")
            lens_en.append(len(en.split()))
            lens_x.append(len(xx.split()))
    def stats(arr):
        return {"n":len(arr),"min":min(arr),"max":max(arr),"mean":round(statistics.mean(arr),2),"median":statistics.median(arr)}
    print(f"[OK] {args.input}")
    print("EN:", stats(lens_en))
    print(f"{args.lang.upper()}:", stats(lens_x))

if __name__ == "__main__":
    main()

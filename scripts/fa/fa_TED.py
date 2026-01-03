#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).



import os

# === 修改成你自己的路径 ===
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/fa\TED"
EN_FILE  = os.path.join(BASE_DIR, "TED2020.en-fa.en")
FA_FILE  = os.path.join(BASE_DIR, "TED2020.en-fa.fa")
OUT_FILE = os.path.join(BASE_DIR, "TED.en-fa.merged.tsv")

def merge_parallel(en_path, fa_path, out_path):
    with open(en_path, "r", encoding="utf-8") as f_en, \
         open(fa_path, "r", encoding="utf-8") as f_fa, \
         open(out_path, "w", encoding="utf-8", newline="\n") as fout:

        # 写表头，如果不想要可以注释掉下一行
        fout.write("id\ten\tfa\n")

        count = 0
        for idx, (en_line, fa_line) in enumerate(zip(f_en, f_fa), start=1):
            en_line = en_line.rstrip("\n\r")
            fa_line = fa_line.rstrip("\n\r")

            fout.write(f"{idx}\t{en_line}\t{fa_line}\n")
            count += 1

        # 检查两边行数是否一致
        extra_en = f_en.readline()
        extra_fa = f_fa.readline()
        if extra_en or extra_fa:
            print("警告：en 和 fa 文件行数不一致，请检查！")
        print(f"已合并 {count} 行，输出到: {out_path}")

if __name__ == "__main__":
    merge_parallel(EN_FILE, FA_FILE, OUT_FILE)
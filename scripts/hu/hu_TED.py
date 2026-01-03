#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""


文件路径按你截图里的来写。
"""

import os

# === 修改成你自己的路径 ===
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/hu\TED"
EN_FILE  = os.path.join(BASE_DIR, "TED2020.en-hu.en")
HU_FILE  = os.path.join(BASE_DIR, "TED2020.en-hu.hu")
OUT_FILE = os.path.join(BASE_DIR, "TED2020.en-hu.merged.tsv")

def merge_parallel(en_path, hu_path, out_path):
    with open(en_path, "r", encoding="utf-8") as f_en, \
         open(hu_path, "r", encoding="utf-8") as f_hu, \
         open(out_path, "w", encoding="utf-8", newline="\n") as fout:

        # 写表头，如果不想要可以注释掉下一行
        fout.write("id\ten\thu\n")

        count = 0
        for idx, (en_line, hu_line) in enumerate(zip(f_en, f_hu), start=1):
            en_line = en_line.rstrip("\n\r")
            hu_line = hu_line.rstrip("\n\r")

            fout.write(f"{idx}\t{en_line}\t{hu_line}\n")
            count += 1

        # 检查两边行数是否一致
        extra_en = f_en.readline()
        extra_hu = f_hu.readline()
        if extra_en or extra_hu:
            print("警告：en 和 hu 文件行数不一致，请检查！")
        print(f"已合并 {count} 行，输出到: {out_path}")

if __name__ == "__main__":
    merge_parallel(EN_FILE, HU_FILE, OUT_FILE)
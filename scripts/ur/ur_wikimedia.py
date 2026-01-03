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
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/ur\wikimedia"
EN_FILE  = os.path.join(BASE_DIR, "wikimedia.en-ur.en")
UR_FILE  = os.path.join(BASE_DIR, "wikimedia.en-ur.ur")
OUT_FILE = os.path.join(BASE_DIR, "wikimedia.en-ur.merged.tsv")

def merge_parallel(en_path, ur_path, out_path):
    with open(en_path, "r", encoding="utf-8") as f_en, \
         open(ur_path, "r", encoding="utf-8") as f_ur, \
         open(out_path, "w", encoding="utf-8", newline="\n") as fout:

        # 写表头，如果不想要可以注释掉下一行
        fout.write("id\ten\tur\n")

        count = 0
        for idx, (en_line, ur_line) in enumerate(zip(f_en, f_ur), start=1):
            en_line = en_line.rstrip("\n\r")
            ur_line = ur_line.rstrip("\n\r")

            fout.write(f"{idx}\t{en_line}\t{ur_line}\n")
            count += 1

        # 检查两边行数是否一致
        extra_en = f_en.readline()
        extra_ur = f_ur.readline()
        if extra_en or extra_ur:
            print("警告：en 和 ur 文件行数不一致，请检查！")
        print(f"已合并 {count} 行，输出到: {out_path}")

if __name__ == "__main__":
    merge_parallel(EN_FILE, UR_FILE, OUT_FILE)
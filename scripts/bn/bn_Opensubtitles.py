# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


文件路径按你截图里的来写。
"""

import os

# === 修改成你自己的路径 ===
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/bn\Opensubtitle"
EN_FILE  = os.path.join(BASE_DIR, "OpenSubtitles.bn-en.en")
BN_FILE  = os.path.join(BASE_DIR, "OpenSubtitles.bn-en.bn")
OUT_FILE = os.path.join(BASE_DIR, "OpenSubtitles.bn-en.merged.tsv")

def merge_parallel(en_path, bn_path, out_path):
    with open(en_path, "r", encoding="utf-8") as f_en, \
         open(bn_path, "r", encoding="utf-8") as f_bn, \
         open(out_path, "w", encoding="utf-8", newline="\n") as fout:

        # 写表头，如果不想要可以注释掉下一行
        fout.write("id\ten\tbn\n")

        count = 0
        for idx, (en_line, bn_line) in enumerate(zip(f_en, f_bn), start=1):
            en_line = en_line.rstrip("\n\r")
            bn_line = bn_line.rstrip("\n\r")

            fout.write(f"{idx}\t{en_line}\t{bn_line}\n")
            count += 1

        # 检查两边行数是否一致
        extra_en = f_en.readline()
        extra_bn = f_bn.readline()
        if extra_en or extra_bn:
            print("警告：en 和 bn 文件行数不一致，请检查！")
        print(f"已合并 {count} 行，输出到: {out_path}")

if __name__ == "__main__":
    merge_parallel(EN_FILE, BN_FILE, OUT_FILE)
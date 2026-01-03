#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
合并多个 hu 的 sample TSV，并做进一步清洗：

1. 合并以下文件（根据需要修改 FILES 列表）：
   - Europarl.en-hu.sample200
   - OpenSubtitles.en-hu.sample200
   - QED.en-hu.sample200
   - TED.en-hu.sample200
   - WMT-News.en-hu.sample200
   - WikiMatrix.en-hu.sample200

2. 只看 hu 列，若 hu 的词数 < 6（按空格分词）则丢弃该行。

3. 对 en 和 hu 句子：
   - 去掉首尾的空括号、引号、破折号等无用字符（而不是删除整句）
   - 压缩多余空格

4. 重新编号 id，从 1 开始，输出为 hu_all_merged_clean.tsv
"""

import os
import csv
import re

# ==== 路径 & 文件名，根据你的实际目录调整 ====
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/hu\all_new"

FILES = [
    "Europarl.hu.sample200.tsv",      # 如果真实文件带 .tsv，需要写成 "Europarl.en-hu.sample200.tsv"
    "OpenSubtitles.en-hu.sample200.tsv",
    "QED.en-hu.sample200.tsv",
    "TED.en-hu.sample200.tsv",
    "WMT-News.en-hu.sample200.tsv",
    "WikiMatrix.en-hu.sample200.tsv",
]

# 输出文件
OUTPUT_TSV = os.path.join(BASE_DIR, "hu_all_merged_clean.tsv")

# 认为 en 在第 2 列（索引 1），hu 在最后一列
EN_COL_IDX = 1
HU_COL_IDX = -1

# hu 最小词数（小于这个就丢弃）
HU_MIN_TOKENS = 8


def clean_sentence(text: str) -> str:
    """
    清洗句子：
    - strip 两端空白
    - 去掉开头/结尾的括号、引号、破折号等无用字符（可按需要增减）
    - 去掉孤立的空括号 "()" "[]" "{}"
    - 压缩多个空格为一个
    """
    if not text:
        return ""

    s = text.strip()

    # 去除孤立的空括号
    s = s.replace("()", "").replace("[]", "").replace("{}", "")

    # 去除开头/结尾的杂字符：括号、引号、破折号等
    # 可以按需要把正则里的符号加多一点或删减
    s = re.sub(r'^[\s\(\)\[\]\{\}"“”\'«»„‚…\-–—]+', '', s)
    s = re.sub(r'[\s\(\)\[\]\{\}"“”\'«»„‚…\-–—]+$', '', s)

    # 再压缩多余空格
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def is_header(row):
    """
    简单判断这一行是不是表头：如果第一列包含 'id' 字样，就认为是表头。
    """
    if not row:
        return False
    first = row[0].strip().lower()
    return first == "id" or first.startswith("#")


def merge_and_clean():
    merged_rows = []

    for fname in FILES:
        path = os.path.join(BASE_DIR, fname)
        if not os.path.exists(path):
            # 尝试补 .tsv 后缀
            if os.path.exists(path + ".tsv"):
                path = path + ".tsv"
            else:
                print(f"⚠ 找不到文件：{path}，跳过")
                continue

        print(f"读取文件: {path}")
        with open(path, "r", encoding="utf-8") as fin:
            reader = csv.reader(fin, delimiter="\t")

            first_row = next(reader, None)
            if first_row is None:
                continue

            # 跳过表头
            if not is_header(first_row):
                # 第一行就是数据，需要处理
                rows_iter = [first_row] + list(reader)
            else:
                rows_iter = list(reader)

            for row in rows_iter:
                if not row:
                    continue

                # 防御：如果行太短，跳过
                if len(row) <= max(EN_COL_IDX if EN_COL_IDX >= 0 else 0,
                                   len(row) + HU_COL_IDX):
                    continue

                # 定位 en / hu 字段
                en = row[EN_COL_IDX]
                hu = row[HU_COL_IDX]

                # 清洗 en / hu
                en_clean = clean_sentence(en)
                hu_clean = clean_sentence(hu)

                # 按 hu 词数过滤
                if not hu_clean:
                    continue
                hu_tokens = hu_clean.split()
                if len(hu_tokens) < HU_MIN_TOKENS:
                    continue

                # 把清洗后的句子放回 row 中
                row[EN_COL_IDX] = en_clean
                row[HU_COL_IDX] = hu_clean

                merged_rows.append(row)

    # 重新编号 id，从 1 开始
    print(f"合并后，符合条件的句子总数：{len(merged_rows)}")
    with open(OUTPUT_TSV, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "hu"])

        for new_id, row in enumerate(merged_rows, start=1):
            en = row[EN_COL_IDX]
            hu = row[HU_COL_IDX]
            writer.writerow([new_id, en, hu])

    print(f"已写出到: {OUTPUT_TSV}")


if __name__ == "__main__":
    merge_and_clean()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
从合并后的 OpenSubtitles.en-ms.merged.tsv 中，按条件抽取最多 200 句：
- 使用 ms 列过滤：
  - 词数 >= 8
  - 句子不重复
  - 拉丁字母比例 > 80%（粗略保证是马来语 / 英文一类的 Latin 文本）
"""

import os
import csv
import random
import string

# === 路径按你的实际情况修改 ===
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/ms\Tanzil"  # 自己改成 ms 的目录
INPUT_TSV  = os.path.join(BASE_DIR, "Tanzil.en-ms.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "Tanzil.en-ms.sample250.tsv")

MAX_LINES   = 10000   # 只看前 10000 行（不含表头）
SAMPLE_SIZE = 250     # 最多抽 200 句
MIN_TOKENS  = 8       # 至少 8 个词

# 允许的 Latin 字母集合（大小写）
LATIN_LETTERS = set(string.ascii_letters)


def latin_ratio(text: str) -> float:
    """
    计算文本中 Latin 字母所占比例（只统计字母，忽略空格和标点）。
    用来粗略过滤掉非 Latin 的奇怪内容。
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    latin = [c for c in letters if c in LATIN_LETTERS]
    return len(latin) / len(letters)


def process_line(row, candidates, seen_ms):
    """
    处理单行：row = [id, en, ms]
    符合条件则加入 candidates。
    """
    if len(row) < 3:
        return

    orig_id, en, ms = row[0], row[1], row[2]
    ms = ms.strip()
    if not ms:
        return

    # 词数过滤
    tokens = ms.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 去重（同一个 ms 句子只保留一次）
    if ms in seen_ms:
        return

    # Latin 字母比例过滤（>= 0.8，防止混入太多非文本符号）
    ratio = latin_ratio(ms)
    if ratio < 1:
        return

    seen_ms.add(ms)
    candidates.append((orig_id, en, ms))


def sample_from_merged(input_tsv: str, output_tsv: str):
    candidates = []
    seen_ms = set()

    with open(input_tsv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin, delimiter="\t")

        # 处理表头：如果第一列是 "id" 就跳过
        first_row = next(reader, None)
        if first_row is None:
            print("输入文件为空。")
            return

        if not first_row[0].lower().startswith("id"):
            # 没表头，把第一行当数据
            process_line(first_row, candidates, seen_ms)

        # 继续读剩下的行
        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_ms)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # 写出结果
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "ms"])
        for new_id, (orig_id, en, ms) in enumerate(sampled, start=1):
            writer.writerow([new_id, en, ms])

    print(f"候选句子数量：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_from_merged(INPUT_TSV, OUTPUT_TSV)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
从合并后的 QED.en-fa.merged.tsv 的前若干行中，按条件抽取最多 250 句：
- 使用 fa 列过滤：
  - 词数 > 7（至少 8 个词）
  - 句子不重复
  - 波斯语/阿拉伯字母比例 > 80%（大致保证是 fa）
"""

import os
import csv
import random

# === 路径按你的实际情况修改 ===
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/fa\Tanzil"  # 自己改
INPUT_TSV  = os.path.join(BASE_DIR, "Tanzil.en-fa.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "Tanzil.en-fa.sample250.tsv")

MAX_LINES    = 2000   # 只看前 1000 行（不含表头）
SAMPLE_SIZE  = 250    # 最多抽 250 句
MIN_TOKENS   = 8      # 词数 > 7 => 至少 8 个词
MIN_FA_RATIO = 1   # 波斯语字符占全部字母的比例 > 80%


def fa_char_ratio(text: str) -> float:
    """
    计算文本中“波斯语/阿拉伯字母”的比例（只统计字母，忽略空格和标点）。
    波斯语主要使用阿拉伯字母：Unicode 大致范围 U+0600 ~ U+06FF
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0

    fa_letters = [c for c in letters if '\u0600' <= c <= '\u06FF']
    return len(fa_letters) / len(letters)


def process_line(row, candidates, seen_fa):
    """
    处理单行：row = [id, en, fa]
    符合条件则加入 candidates。
    """
    if len(row) < 3:
        return

    orig_id, en, fa = row[0], row[1], row[2]
    fa = fa.strip()
    if not fa:
        return

    # 词数过滤
    tokens = fa.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 去重（同一个 fa 句子只保留一次）
    if fa in seen_fa:
        return

    # 波斯语字符比例过滤
    ratio = fa_char_ratio(fa)
    if ratio < MIN_FA_RATIO:
        return

    seen_fa.add(fa)
    candidates.append((orig_id, en, fa))


def sample_from_merged(input_tsv: str, output_tsv: str):
    candidates = []
    seen_fa = set()

    with open(input_tsv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin, delimiter="\t")

        # 处理表头：如果第一列是 "id" 就跳过
        first_row = next(reader, None)
        if first_row is None:
            print("输入文件为空。")
            return

        if not first_row[0].lower().startswith("id"):
            # 没表头，把第一行当数据
            process_line(first_row, candidates, seen_fa)

        # 继续读剩下的行
        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_fa)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # 写出结果
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "fa"])
        for new_id, (orig_id, en, fa) in enumerate(sampled, start=1):
            writer.writerow([new_id, en, fa])

    print(f"候选句子数量：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_from_merged(INPUT_TSV, OUTPUT_TSV)
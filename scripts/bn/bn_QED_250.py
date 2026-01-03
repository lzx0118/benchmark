#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
从合并后的 QED.en-bn.merged.tsv 的前若干行中，按条件抽取最多 200 句：
- 使用 bn 列过滤：
  - 词数 > 7（至少 8 个词）
  - 句子不重复
  - 孟加拉语字符比例 > 80%（大致保证是 bn）
"""

import os
import csv
import random

# === 路径按你的实际情况修改 ===
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/bn\QED"  # 自己改
INPUT_TSV  = os.path.join(BASE_DIR, "QED.bn-en.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "QED.en-bn.sample250.tsv")

MAX_LINES   = 2000   # 只看前 10000 行（不含表头）
SAMPLE_SIZE = 350     # 最多抽 200 句
MIN_TOKENS  = 8       # 词数 > 7 => 至少 8 个词
MIN_BN_RATIO = 1   # 孟加拉文字符占全部字母的比例 > 80%


def bn_char_ratio(text: str) -> float:
    """
    计算文本中“孟加拉语字符”的比例（只统计字母，忽略空格和标点）。
    粗略判断是不是孟加拉语句子。
    孟加拉文 Unicode 范围：U+0980 ~ U+09FF
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0

    bn_letters = [c for c in letters if '\u0980' <= c <= '\u09FF']
    return len(bn_letters) / len(letters)


def process_line(row, candidates, seen_bn):
    """
    处理单行：row = [id, en, bn]
    符合条件则加入 candidates。
    """
    if len(row) < 3:
        return

    orig_id, en, bn = row[0], row[1], row[2]
    bn = bn.strip()
    if not bn:
        return

    # 词数过滤
    tokens = bn.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 去重（同一个 bn 句子只保留一次）
    if bn in seen_bn:
        return

    # 孟加拉语字符比例过滤
    ratio = bn_char_ratio(bn)
    if ratio < MIN_BN_RATIO:
        return

    seen_bn.add(bn)
    candidates.append((orig_id, en, bn))


def sample_from_merged(input_tsv: str, output_tsv: str):
    candidates = []
    seen_bn = set()

    with open(input_tsv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin, delimiter="\t")

        # 处理表头：如果第一列是 "id" 就跳过
        first_row = next(reader, None)
        if first_row is None:
            print("输入文件为空。")
            return

        if not first_row[0].lower().startswith("id"):
            # 没表头，把第一行当数据
            process_line(first_row, candidates, seen_bn)

        # 继续读剩下的行
        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_bn)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # 写出结果
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "bn"])
        for new_id, (orig_id, en, bn) in enumerate(sampled, start=1):
            writer.writerow([new_id, en, bn])

    print(f"候选句子数量：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_from_merged(INPUT_TSV, OUTPUT_TSV)
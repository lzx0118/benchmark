#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
从合并后的 QED.en-hu.merged.tsv 的前 1000 句中，按条件抽取最多 250 句：
- 使用 hu 列过滤：
  - 词数 > 7（至少 8 个词）
  - 句子不重复
  - 匈牙利重音字母比例 > 2%（大致保证是 hu）
"""

import os
import csv
import random

# === 路径按你的实际情况修改 ===
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/hu\WMT-news"
INPUT_TSV  = os.path.join(BASE_DIR, "WMT-News.en-hu.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "WMT-News.en-hu.sample200.tsv")

MAX_LINES         = 1000   # 只看前 1000 行（不含表头）
SAMPLE_SIZE       = 200    # 最多抽 250 句
MIN_TOKENS        = 8      # 词数 > 7 => 至少 8 个词
MIN_HU_SPEC_RATIO = 0.02   # 匈牙利重音字母占全部字母的比例 > 2%


# 匈牙利语中特有的重音字母
HU_ACCENTED = set("áéíóöőúüűÁÉÍÓÖŐÚÜŰ")


def hu_specific_ratio(text: str) -> float:
    """
    计算文本中“匈牙利重音字母”的比例（只统计字母，忽略空格和标点）。
    用来粗略判断是不是匈牙利语句子。
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    hu_spec = [c for c in letters if c in HU_ACCENTED]
    return len(hu_spec) / len(letters)


def process_line(row, candidates, seen_hu):
    """
    处理单行：row = [id, en, hu]
    符合条件则加入 candidates。
    """
    if len(row) < 3:
        return

    orig_id, en, hu = row[0], row[1], row[2]
    hu = hu.strip()
    if not hu:
        return

    # 词数过滤
    tokens = hu.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 去重（同一个 hu 句子只保留一次）
    if hu in seen_hu:
        return

    # 匈牙利重音字母比例过滤
    ratio = hu_specific_ratio(hu)
    if ratio < MIN_HU_SPEC_RATIO:
        return

    seen_hu.add(hu)
    candidates.append((orig_id, en, hu))


def sample_from_merged(input_tsv: str, output_tsv: str):
    candidates = []
    seen_hu = set()

    with open(input_tsv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin, delimiter="\t")

        # 处理表头：如果第一列是 "id" 就跳过
        first_row = next(reader, None)
        if first_row is None:
            print("输入文件为空。")
            return

        if not first_row[0].lower().startswith("id"):
            # 没表头，把第一行当数据
            process_line(first_row, candidates, seen_hu)

        # 继续读剩下的行
        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_hu)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # 写出结果
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "hu"])
        for new_id, (orig_id, en, hu) in enumerate(sampled, start=1):
            writer.writerow([new_id, en, hu])

    print(f"候选句子数量：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_from_merged(INPUT_TSV, OUTPUT_TSV)
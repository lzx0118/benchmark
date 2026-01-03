#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
从合并后的 QED.en-id.merged.tsv 的前若干行中，按条件抽取最多 250 句：
- 使用 id 列过滤：
  - 词数 > 7（至少 8 个词）
  - 句子不重复
  - “基本拉丁字母”比例 > 80%（大致保证是印尼语 / 英文字母书写的句子）
"""

import os
import csv
import random

# === 路径按你的实际情况修改 ===
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/id\wikimatrix"          # 自己改成 id 的目录
INPUT_TSV  = os.path.join(BASE_DIR, "WikiMatrix.en-id.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "WikiMatrix.en-id.sample250.tsv")

MAX_LINES    = 10000   # 只看前 1000 行（不含表头）
SAMPLE_SIZE  = 250    # 最多抽 250 句
MIN_TOKENS   = 8      # 词数 > 7 => 至少 8 个词
MIN_ID_RATIO = 1   # 基本拉丁字母占全部字母的比例 > 80%


def id_char_ratio(text: str) -> float:
    """
    粗略计算文本中“基本拉丁字母”的比例（只统计字母，忽略空格和标点）。
    这里不能像 bn 那样用独特的脚本范围，只是过滤掉太多奇怪字符的句子。

    基本拉丁字母 Unicode 范围：
      - 'A' ~ 'Z' (U+0041 ~ U+005A)
      - 'a' ~ 'z' (U+0061 ~ U+007A)
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0

    latin_letters = [
        c for c in letters
        if ('A' <= c <= 'Z') or ('a' <= c <= 'z')
    ]
    return len(latin_letters) / len(letters)


def process_line(row, candidates, seen_id):
    """
    处理单行：row = [id, en, id_text]
    符合条件则加入 candidates。
    """
    if len(row) < 3:
        return

    orig_id, en, id_text = row[0], row[1], row[2]
    id_text = id_text.strip()
    if not id_text:
        return

    # 词数过滤
    tokens = id_text.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 去重（同一个 id 句子只保留一次）
    if id_text in seen_id:
        return

    # 字母比例过滤（去掉包含太多奇怪符号的噪声句子）
    ratio = id_char_ratio(id_text)
    if ratio < MIN_ID_RATIO:
        return

    seen_id.add(id_text)
    candidates.append((orig_id, en, id_text))


def sample_from_merged(input_tsv: str, output_tsv: str):
    candidates = []
    seen_id = set()

    with open(input_tsv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin, delimiter="\t")

        # 处理表头：如果第一列是 "id" 就跳过
        first_row = next(reader, None)
        if first_row is None:
            print("输入文件为空。")
            return

        if not first_row[0].lower().startswith("id"):
            # 没表头，把第一行当数据
            process_line(first_row, candidates, seen_id)

        # 继续读剩下的行
        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_id)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # 写出结果
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "id"])  # 表头：id, en, id
        for new_id, (orig_id, en, id_text) in enumerate(sampled, start=1):
            writer.writerow([new_id, en, id_text])

    print(f"候选句子数量：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_from_merged(INPUT_TSV, OUTPUT_TSV)
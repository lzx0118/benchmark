#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
从合并后的 OpenSubtitles.en-ur.merged.tsv 中，按条件抽取最多 250 句：
- 使用 ur 列过滤：
  - 词数 >= 8
  - 句子不重复
  - 阿拉伯/乌尔都字符比例 > 80%（粗略保证主要是 Urdu 文本）
"""

import os
import csv
import random

# === 路径按你的实际情况修改 ===
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/ur\Tanzil"  # 自己改成 ur 的目录
INPUT_TSV  = os.path.join(BASE_DIR, "Tanzil.en-ur.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "Tanzil.en-ur.sample250.tsv")

MAX_LINES   = 10000   # 只看前 10000 行（不含表头）
SAMPLE_SIZE = 280     # 最多抽 250 句
MIN_TOKENS  = 8       # 至少 8 个词


def is_urdu_char(ch: str) -> bool:
    """判断一个字符是否在阿拉伯/乌尔都相关的 Unicode 段里。"""
    code = ord(ch)
    # 基本阿拉伯文块
    if 0x0600 <= code <= 0x06FF:
        return True
    # 阿拉伯补充
    if 0x0750 <= code <= 0x077F:
        return True
    # 阿拉伯呈现形式-A
    if 0xFB50 <= code <= 0xFDFF:
        return True
    # 阿拉伯呈现形式-B
    if 0xFE70 <= code <= 0xFEFF:
        return True
    return False


def urdu_ratio(text: str) -> float:
    """
    计算文本中“看起来像乌尔都/阿拉伯”的字符比例（只统计字母类字符）。
    用来粗略过滤掉非 Urdu 的奇怪内容。
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    ur = [c for c in letters if is_urdu_char(c)]
    return len(ur) / len(letters)


def process_line(row, candidates, seen_ur):
    """
    处理单行：row = [id, en, ur]
    符合条件则加入 candidates。
    """
    if len(row) < 3:
        return

    orig_id, en, ur = row[0], row[1], row[2]
    ur = ur.strip()
    if not ur:
        return

    # 词数过滤
    tokens = ur.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 去重（同一个 ur 句子只保留一次）
    if ur in seen_ur:
        return

    # Urdu 字符比例过滤（>= 0.8，防止混入太多拉丁或其它脚本）
    ratio = urdu_ratio(ur)
    if ratio < 1:
        return

    seen_ur.add(ur)
    candidates.append((orig_id, en, ur))


def sample_from_merged(input_tsv: str, output_tsv: str):
    candidates = []
    seen_ur = set()

    with open(input_tsv, "r", encoding="utf-8") as fin:
        reader = csv.reader(fin, delimiter="\t")

        # 处理表头：如果第一列是 "id" 就跳过
        first_row = next(reader, None)
        if first_row is None:
            print("输入文件为空。")
            return

        if not first_row[0].lower().startswith("id"):
            # 没表头，把第一行当数据
            process_line(first_row, candidates, seen_ur)

        # 继续读剩下的行
        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_ur)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # 写出结果
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "en", "ur"])
        for new_id, (orig_id, en, ur) in enumerate(sampled, start=1):
            writer.writerow([new_id, en, ur])

    print(f"候选句子数量：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_from_merged(INPUT_TSV, OUTPUT_TSV)
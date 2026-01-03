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
BASE_DIR   = r"<PATH_TO_XBENCH_ROOT>/hu\wikimatrix"
INPUT_TSV  = os.path.join(BASE_DIR, "WikiMatrix.en-hu.merged.tsv")
OUTPUT_TSV = os.path.join(BASE_DIR, "WikiMatrix.en-hu.sample200.tsv")

MAX_LINES         = 100000   # 只看前 1000 条（不含表头）
SAMPLE_SIZE       = 200    # 最多抽 200 句
MIN_TOKENS        = 8      # 词数下限
MIN_HU_SPEC_RATIO = 0.02   # 匈牙利重音字母占所有字母的比例下限

# 匈牙利语特有重音字母
HU_ACCENTED = set("áéíóöőúüűÁÉÍÓÖŐÚÜŰ")


# ========= 工具函数 =========
def hu_specific_ratio(text: str) -> float:
    """计算文本中匈牙利重音字母比例，用于粗过滤“不是 hu 语言”的句子。"""
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    hu_spec = [c for c in letters if c in HU_ACCENTED]
    return len(hu_spec) / len(letters)


def has_foreign_like_word(text: str) -> bool:
    """
    判断一句话中是否存在“疑似外语长单词”：
      - token 中不含匈牙利重音字母；
      - 且 token 长度 >= 4；
    一旦出现这样的 token，就认为句子可能混入了其它语言的词，返回 True。
    """
    for raw_tok in text.split():
        tok = raw_tok.strip(".,!?;:()[]{}\"'“”‘’-–—／/\\")  # 简单剥掉标点
        if not tok:
            continue

        # 有匈牙利重音字母 -> 明显是匈牙利词，安全
        if any(ch in HU_ACCENTED for ch in tok):
            continue

        # 全是数字或混杂数字 -> 不要，但算“外语嫌疑词”
        letters = [c for c in tok if c.isalpha()]
        if not letters:
            # 纯数字/符号，这里也可以直接判为外语嫌疑，看你是否要保留带很多数字的句子
            return True

        # 长度 <= 3 且无重音：允许（如 van, nem, meg, stb.）
        if len(letters) <= 3:
            continue

        # 长度 >= 4 且无重音：大概率是英文之类的外语单词 -> 认为有外语
        return True

    return False


def process_line(row, candidates, seen_hu):
    """
    处理 TSV 中的一行 row = [id, en, hu]，
    符合所有条件就把 (orig_id, hu) 加到候选列表。
    """
    if len(row) < 3:
        return

    orig_id, en, hu = row[0], row[1], row[2]
    hu = hu.strip()
    if not hu:
        return

    # 1) 词数过滤
    tokens = hu.split()
    if len(tokens) < MIN_TOKENS:
        return

    # 2) 去重
    if hu in seen_hu:
        return

    # 3) 匈牙利重音比例过滤
    ratio = hu_specific_ratio(hu)
    if ratio < MIN_HU_SPEC_RATIO:
        return

    # 4) 检查是否含有“疑似外语长单词”
    if has_foreign_like_word(hu):
        return

    seen_hu.add(hu)
    candidates.append((orig_id, hu))


def sample_hu_only(input_tsv: str, output_tsv: str):
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
            # 没有表头，把第一行当数据
            process_line(first_row, candidates, seen_hu)

        for i, row in enumerate(reader, start=1):
            if i > MAX_LINES:
                break
            process_line(row, candidates, seen_hu)

    # 随机抽样
    random.seed(42)
    random.shuffle(candidates)
    sampled = candidates[:SAMPLE_SIZE]

    # ===== 写出文件：id + hu 两列 =====
    with open(output_tsv, "w", encoding="utf-8", newline="\n") as fout:
        writer = csv.writer(fout, delimiter="\t")
        writer.writerow(["id", "hu"])
        for new_id, (_, hu) in enumerate(sampled, start=1):
            writer.writerow([new_id, hu])

    print(f"候选句子数量（全部过滤后）：{len(candidates)}")
    print(f"实际抽取：{len(sampled)} 句")
    print(f"已写入：{output_tsv}")


if __name__ == "__main__":
    sample_hu_only(INPUT_TSV, OUTPUT_TSV)
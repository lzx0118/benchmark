#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
合并 bn 方向的多个 TSV（en-bn），去重 & 清洗 & 过滤句长 + 数字比例。

示例输入文件（按需要改成你自己的名字）：
- <PATH_TO_XBENCH_ROOT>/bn/all_new/OpenSubtitles.en-bn.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/bn/all_new/QED.en-bn.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/bn/all_new/Tanzil.en-bn.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/bn/all_new/TED.en-bn.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/bn/all_new/wikimedia.sample250.tsv

输出：
- <PATH_TO_XBENCH_ROOT>/bn/all_new/bn_all_merged_clean.tsv

输出列顺序：
id <TAB> en <TAB> bn

过滤规则：
- en / bn 句长（按空格分词）在 [8, 55] 之间
- 删除数字含量过高的句子（en 或 bn 任意一侧，数字 / (字母+数字) > 0.5 即删除）
- 清洗 en / bn 句首的编号（如 "1.", "(2)", "[3]", "4、" 等）
- 删除非法符号 / emoji
- 删除句中省略号（"…" 或连续的多个 "."）
"""

import csv
import os
import re
from typing import List, Tuple

# ===== 根据你机器上的实际路径改这里 =====
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/bn/all_new"

INPUT_FILES: List[str] = [
    os.path.join(BASE_DIR, "OpenSubtitles.en-bn.sample250.tsv"),
    os.path.join(BASE_DIR, "QED.en-bn.sample250.tsv"),
    os.path.join(BASE_DIR, "Tanzil.en-bn.sample250.tsv"),
    os.path.join(BASE_DIR, "TED.en-bn.sample250.tsv"),
    os.path.join(BASE_DIR, "wikimedia.sample250.tsv"),
]

OUTPUT_FILE = os.path.join(BASE_DIR, "bn_all_merged_clean.tsv")

# 句长 & 数字比例阈值
MIN_WORDS = 8
MAX_WORDS = 45
MAX_DIGIT_RATIO = 0.3  # 数字 / (字母+数字) > 0.5 就删


# ----------------- 文本清洗相关函数 -----------------

def is_emoji(ch: str) -> bool:
    """粗略判断一个字符是否为 emoji"""
    cp = ord(ch)
    if (
        0x1F300 <= cp <= 0x1F5FF
        or 0x1F600 <= cp <= 0x1F64F
        or 0x1F680 <= cp <= 0x1F6FF
        or 0x1F900 <= cp <= 0x1F9FF
        or 0x2600 <= cp <= 0x26FF
        or 0x2700 <= cp <= 0x27BF
    ):
        return True
    return False


def remove_leading_numbering(text: str) -> str:
    """
    去掉句首的“编号”前缀，比如：
    - "1. xxx"
    - "2) xxx"
    - "(3) xxx"
    - "[4] xxx"
    - "5、xxx"
    - "1.2. xxx"
    """
    text = re.sub(
        r'^\s*(?:[\(\[\{]?\d+(?:\.\d+)*[\)\]\}\.\)\-、:]+)\s*',
        '',
        text
    )
    return text


def clean_text(text: str) -> str:
    """去编号、首尾垃圾符号、非法字符、emoji、句中省略号、空白折叠"""
    if text is None:
        return ""

    text = text.strip()

    # 1) 删除句首编号
    text = remove_leading_numbering(text)

    # 2) 去掉首尾的一些“无用符号”（括号、引号、破折号、点点点等）
    #    加上孟加拉常见句号 "।"
    text = re.sub(r'^[\s\-\–\—\·\•\(\)\[\]\{\}"“”‘’\'`…·।!?？！,.;:·]+', '', text)
    text = re.sub(r'[\s\-\–\—\·\•\(\)\[\]\{\}"“”‘’\'`…·।!?？！,.;:·]+$', '', text)

    # 3) 删除控制字符（保留正常可见字符）
    text = ''.join(ch for ch in text if (ord(ch) >= 32 and ord(ch) != 127))

    # 4) 删除 emoji
    text = ''.join(ch for ch in text if not is_emoji(ch))

    # 5) 删除句中省略号：
    #    - Unicode 省略号 “…” 全部删
    #    - 连续三个及以上的点号 "..." "...." 等也删掉
    text = text.replace("…", "")
    text = re.sub(r'\.{3,}', '', text)

    # 6) 压缩空白
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def count_words(text: str) -> int:
    """按空格统计单词数"""
    if not text:
        return 0
    return len(text.split())


def digit_ratio(text: str) -> float:
    """
    数字占比：digits / (letters+digits)
    若 letters+digits 为 0，则返回 0.
    """
    if not text:
        return 0.0
    digits = 0
    alnum = 0
    for ch in text:
        if ch.isdigit():
            digits += 1
            alnum += 1
        elif ch.isalpha():
            alnum += 1
    if alnum == 0:
        return 0.0
    return digits / float(alnum)


def detect_en_bn_indices(header: List[str]) -> Tuple[int, int]:
    """从表头自动检测 en/bn 列索引"""
    lower = [h.lower().strip() for h in header]
    en_idx = None
    bn_idx = None
    for i, name in enumerate(lower):
        if name == "en":
            en_idx = i
        elif name == "bn":
            bn_idx = i
    if en_idx is not None and bn_idx is not None:
        return en_idx, bn_idx
    # 找不到就默认最后两列
    if len(header) >= 2:
        return len(header) - 2, len(header) - 1
    raise ValueError("无法从表头中识别 en / bn 列，请检查输入 TSV 的列名。")


# ----------------- 主流程 -----------------

def main():
    seen_pairs = set()   # (en_lower, bn_lower)
    rows_out = []
    next_id = 1
    header_written = False

    for path in INPUT_FILES:
        if not os.path.isfile(path):
            print(f"[WARN] 找不到文件: {path}，跳过。")
            continue

        print(f"[INFO] 读取: {path}")
        with open(path, "r", encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t")

            first_row = True
            en_idx = None
            bn_idx = None

            for row in reader:
                if not row:
                    continue

                # 处理表头
                if first_row:
                    first_row = False
                    try:
                        en_idx, bn_idx = detect_en_bn_indices(row)
                    except Exception as e:
                        print(f"[WARN] {path} 自动检测表头失败: {e}")
                        en_idx, bn_idx = len(row) - 2, len(row) - 1

                    if not header_written:
                        rows_out.append(["id", "en", "bn"])
                        header_written = True
                    continue

                if en_idx >= len(row) or bn_idx >= len(row):
                    continue

                en_raw = row[en_idx]
                bn_raw = row[bn_idx]

                en_clean = clean_text(en_raw)
                bn_clean = clean_text(bn_raw)

                # 空行直接跳过
                if not en_clean or not bn_clean:
                    continue

                # 句长过滤
                en_len = count_words(en_clean)
                bn_len = count_words(bn_clean)
                if (
                    en_len < MIN_WORDS or en_len > MAX_WORDS or
                    bn_len < MIN_WORDS or bn_len > MAX_WORDS
                ):
                    continue

                # 数字比例过滤
                if (
                    digit_ratio(en_clean) > MAX_DIGIT_RATIO or
                    digit_ratio(bn_clean) > MAX_DIGIT_RATIO
                ):
                    continue

                key = (en_clean.lower(), bn_clean.lower())
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)

                rows_out.append([str(next_id), en_clean, bn_clean])
                next_id += 1

    final_rows = len(rows_out) - 1  # 去掉表头
    print(f"[INFO] 最终保留句对数：{final_rows}")
    print(f"[INFO] 写出到: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out, delimiter="\t")
        writer.writerows(rows_out)


if __name__ == "__main__":
    main()
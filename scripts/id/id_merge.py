#!/usr/bin/env python
# -*- coding: utf-8 -*-
# NOTE (for GitHub release):
# - This script was originally written with absolute Windows paths (e.g., D:/All_test/...).
# - Please replace <PATH_TO_XBENCH_ROOT> with your local dataset root before running.
# - Only standard Python libraries are required (csv/os/re/random/...).


"""
合并 id 方向的多个 TSV（en-id），去重 & 清洗 & 过滤句长。

输入文件（示例）：
- <PATH_TO_XBENCH_ROOT>/id/all/OpenSubtitles.en-id.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/id/all/QED.en-id.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/id/all/Tanzil.en-id.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/id/all/TED.en-id.sample250.tsv
- <PATH_TO_XBENCH_ROOT>/id/all/WikiMatrix.en-id.sample250.tsv

输出：
- <PATH_TO_XBENCH_ROOT>/id/all/id_all_merged_clean.tsv

输出列顺序：
id <TAB> en <TAB> id_text   （id_text 为印尼语句子，避免和编号 id 混淆）
"""

import csv
import os
import re
from typing import List, Tuple

# ======= 按你机器上的实际路径改这里即可 =======
BASE_DIR = r"<PATH_TO_XBENCH_ROOT>/id/all_new"

INPUT_FILES: List[str] = [
    os.path.join(BASE_DIR, "OpenSubtitles.en-id.sample250.tsv"),
    os.path.join(BASE_DIR, "QED.en-id.sample250.tsv"),
    os.path.join(BASE_DIR, "Tanzil.en-id.sample250.tsv"),
    os.path.join(BASE_DIR, "TED.en-id.sample250.tsv"),
    os.path.join(BASE_DIR, "WikiMatrix.en-id.sample250.tsv"),
]

OUTPUT_FILE = os.path.join(BASE_DIR, "id_all_merged_clean.tsv")

# 英文 / id 句子词数阈值
MIN_WORDS = 8
MAX_WORDS = 55


def clean_text(text: str) -> str:
    """对句子做轻量清洗：首尾垃圾符号、控制字符、空白折叠。"""
    if text is None:
        return ""

    text = text.strip()

    # 去掉首尾的一些“无用符号”（括号、引号、破折号、点点点等）
    text = re.sub(r'^[\s\-\–\—\·\•\(\)\[\]\{\}"“”‘’\'`…·。？！?!,.;:·]+', '', text)
    text = re.sub(r'[\s\-\–\—\·\•\(\)\[\]\{\}"“”‘’\'`…·。？！?!,.;:·]+$', '', text)

    # 去掉控制字符
    text = ''.join(ch for ch in text if (ord(ch) >= 32 and ord(ch) != 127))

    # 把连续空白压成一个空格
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def count_words(text: str) -> int:
    """按空格简单统计单词数（id 也直接按空格粗略计数）。"""
    if not text:
        return 0
    return len(text.split())


def detect_en_id_indices(header: List[str]) -> Tuple[int, int]:
    """
    从表头里找 'en' / 'id' 两列的位置。
    如果没找到，就默认最后两列（倒数第二是 en，最后一列是 id_text）。
    注意：输入文件里通常叫 'id'，这里同时兼容 'id' 和 'id_text'。
    """
    lower = [h.lower().strip() for h in header]

    en_idx = None
    id_idx = None
    for i, name in enumerate(lower):
        if name == "en":
            en_idx = i
        elif name in ("id", "id_text"):
            id_idx = i

    if en_idx is not None and id_idx is not None:
        return en_idx, id_idx

    # 找不到就默认最后两列
    if len(header) >= 2:
        return len(header) - 2, len(header) - 1

    raise ValueError("无法从表头中识别 en / id(id_text) 列，请检查输入 TSV 的列名。")


def main():
    seen_pairs = set()  # 去重：(en_lower, id_lower)
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
            id_idx = None

            for row in reader:
                if not row:
                    continue

                if first_row:
                    first_row = False
                    # 第一行当表头，尝试检测 en/id 列
                    try:
                        en_idx, id_idx = detect_en_id_indices(row)
                    except Exception as e:
                        print(f"[WARN] {path} 自动检测表头失败: {e}")
                        # 当成无表头文件处理：默认最后两列
                        en_idx, id_idx = len(row) - 2, len(row) - 1

                    if not header_written:
                        rows_out.append(["id", "en", "id_text"])
                        header_written = True
                    continue

                if en_idx >= len(row) or id_idx >= len(row):
                    continue

                en_raw = row[en_idx]
                id_raw = row[id_idx]

                en_clean = clean_text(en_raw)
                id_clean = clean_text(id_raw)

                if not en_clean or not id_clean:
                    continue

                en_len = count_words(en_clean)
                id_len = count_words(id_clean)

                # 过滤过短或过长
                if (
                    en_len < MIN_WORDS or en_len > MAX_WORDS or
                    id_len < MIN_WORDS or id_len > MAX_WORDS
                ):
                    continue

                key = (en_clean.lower(), id_clean.lower())
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)

                rows_out.append([str(next_id), en_clean, id_clean])
                next_id += 1

    print(f"[INFO] 写出 {len(rows_out) - 1} 行数据到: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.writer(f_out, delimiter="\t")
        writer.writerows(rows_out)


if __name__ == "__main__":
    main()
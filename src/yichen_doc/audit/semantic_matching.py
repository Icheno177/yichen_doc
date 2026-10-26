"""Conservative lexical candidates plus material-conflict tripwires."""
from __future__ import annotations

from collections import Counter
import re
from difflib import SequenceMatcher

from .schemas import normalize

NEGATIONS = ("不", "未", "无", "没有", "不得", "不能", "禁止", "低于", "下降", "减少", "未披露", "不等于",
             "not", "never", "no ", "without", "declined", "decreased", "fell")
DIRECTIONS = {
    "up": ("增长", "上升", "提高", "增加", "扩大", "提升", "改善", "grew", "increased", "rose", "improved"),
    "down": ("下降", "下滑", "降低", "减少", "收缩", "恶化", "低于", "fell", "decreased", "declined", "reduced"),
}


def compact(text: str) -> str:
    return re.sub(r"[\W_]+", "", text, flags=re.UNICODE).lower()


def numbers(text: str) -> list[str]:
    return [re.sub(r"\s+", "", x).replace(",", "") for x in re.findall(
        r"(?<!\w)[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?\s*(?:%|％|pp|bp|亿元|万元|万|亿|元|美元|欧元|年|月|天|次|席位)?", text, re.I
    )]


def conflict_signals(source: str, target: str) -> list[str]:
    findings = []
    a_num, b_num = numbers(source), numbers(target)
    # A target paragraph may legitimately contain extra numbers around a
    # retained source sentence. Flag a numeric conflict only when both sides
    # expose the same number of numeric tokens and their values/units differ;
    # count differences remain subject to reviewer mapping instead of being
    # escalated to a contradiction by an unrelated extra figure.
    if a_num and b_num and len(a_num) == len(b_num) and Counter(a_num) != Counter(b_num):
        findings.append(f"数字或单位不同: source={a_num}; target={b_num}")
    a_neg = any(x in source for x in NEGATIONS)
    b_neg = any(x in target for x in NEGATIONS)
    if a_neg != b_neg:
        findings.append("否定/条件词变化，可能造成结论反转")
    for label, terms in DIRECTIONS.items():
        other = "down" if label == "up" else "up"
        if any(x in source for x in terms) and any(x in target for x in DIRECTIONS[other]):
            findings.append("变化方向词冲突")
            break
    return findings


def lexical_similarity(a: str, b: str) -> float:
    x, y = compact(a), compact(b)
    if not x or not y:
        return 0.0
    if x in y or y in x:
        return min(len(x), len(y)) / max(len(x), len(y))
    if len(x) < 2 or len(y) < 2:
        return SequenceMatcher(None, x, y, autojunk=False).ratio()
    ax = Counter(x[i:i+2] for i in range(len(x)-1))
    by = Counter(y[i:i+2] for i in range(len(y)-1))
    inter = sum((ax & by).values())
    dice = 2 * inter / (sum(ax.values()) + sum(by.values()))
    seq = SequenceMatcher(None, x, y, autojunk=False).ratio()
    return max(dice, seq)

"""
사주 + 별자리 + 혈액형을 기반으로 MBTI를 예측한다.
과학적 근거 없음. 순수 엔터테인먼트 용도.
"""
from __future__ import annotations

from typing import Optional


# 오행 → MBTI 축 경향 매핑
_OHAENG_MBTI = {
    "목": {"E": 10, "N": 15, "F": 10, "P": 10},
    "화": {"E": 20, "N": 10, "F": 5,  "P": 15},
    "토": {"I": 5,  "S": 15, "F": 10, "J": 15},
    "금": {"I": 10, "S": 10, "T": 20, "J": 15},
    "수": {"I": 15, "N": 15, "T": 10, "P": 10},
}

# 별자리 원소 → MBTI 축 경향
_ELEMENT_MBTI = {
    "불":  {"E": 15, "N": 10, "T": 5,  "P": 10},
    "흙":  {"I": 5,  "S": 15, "T": 10, "J": 15},
    "바람": {"E": 10, "N": 15, "F": 5,  "P": 10},
    "물":  {"I": 15, "S": 5,  "F": 15, "J": 5},
}

# 혈액형 → MBTI 축 경향
_BLOOD_MBTI = {
    "A":  {"I": 10, "S": 10, "F": 10, "J": 15},
    "B":  {"E": 10, "N": 10, "T": 5,  "P": 15},
    "O":  {"E": 15, "S": 10, "T": 10, "J": 5},
    "AB": {"I": 10, "N": 15, "T": 15, "P": 5},
}

_AXES = [("E", "I"), ("S", "N"), ("T", "F"), ("J", "P")]


def predict_mbti(
    ohaeng_counts: dict,
    zodiac_element: Optional[str] = None,
    blood_type: Optional[str] = None,
) -> dict:
    """종합 분석을 기반으로 MBTI를 예측한다."""
    scores = {letter: 0 for pair in _AXES for letter in pair}

    # 오행 기여 (가장 큰 비중)
    for oh, count in ohaeng_counts.items():
        if oh in _OHAENG_MBTI:
            for letter, weight in _OHAENG_MBTI[oh].items():
                scores[letter] += weight * count

    # 별자리 원소 기여
    if zodiac_element and zodiac_element in _ELEMENT_MBTI:
        for letter, weight in _ELEMENT_MBTI[zodiac_element].items():
            scores[letter] += weight

    # 혈액형 기여
    if blood_type:
        bt = blood_type.upper()
        if bt in _BLOOD_MBTI:
            for letter, weight in _BLOOD_MBTI[bt].items():
                scores[letter] += weight

    # 각 축에서 승자 결정 + 비율 계산
    mbti_type = ""
    axis_scores = {}
    for a, b in _AXES:
        total = scores[a] + scores[b]
        if total == 0:
            total = 1
        a_pct = round(scores[a] / total * 100)
        b_pct = 100 - a_pct
        mbti_type += a if scores[a] >= scores[b] else b
        axis_scores[f"{a}_{b}"] = {a: a_pct, b: b_pct}

    return {
        "type": mbti_type,
        "scores": axis_scores,
    }

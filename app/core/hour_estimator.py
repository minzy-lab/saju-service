"""
태어난 시간을 모를 때 간단한 퀴즈로 시주를 추정한다.
전통 명리학의 성향-시주 상관관계를 참고한 매핑.
"""

from app.data.constants import HOUR_LABELS

# 퀴즈 답변 → 시간대 가중치 매핑
# 각 답변이 특정 시간대(지지 인덱스 0~11)에 점수를 부여

_SIBLING_WEIGHTS = {
    "외동":  {0: 2, 5: 2, 6: 3, 11: 2},
    "첫째":  {2: 3, 3: 2, 4: 2, 8: 2},
    "중간":  {1: 2, 6: 2, 7: 3, 9: 2},
    "막내":  {0: 2, 1: 3, 10: 2, 11: 2},
}

_CHRONOTYPE_WEIGHTS = {
    "아침형":    {2: 3, 3: 3, 4: 2, 5: 2},
    "저녁형":    {9: 2, 10: 3, 11: 3, 0: 2},
    "둘 다 아님": {6: 2, 7: 3, 8: 2, 1: 2},
}

_IMPRESSION_WEIGHTS = {
    "차가움":  {0: 3, 8: 2, 9: 2, 11: 2},
    "따뜻함":  {3: 2, 5: 2, 6: 3, 7: 2},
    "활발함":  {2: 2, 4: 3, 5: 2, 10: 2},
    "조용함":  {1: 3, 7: 2, 9: 2, 11: 2},
}

_DECISION_WEIGHTS = {
    "즉흥적":       {2: 2, 5: 3, 6: 2, 10: 2},
    "신중함":       {1: 2, 7: 2, 9: 3, 11: 2},
    "상황에 따라 다름": {0: 2, 3: 2, 4: 2, 8: 2},
}

# 대표 시간 (각 지지의 중간 시각)
_JIJI_REPRESENTATIVE_HOUR = {
    0: 0, 1: 2, 2: 4, 3: 6, 4: 8, 5: 10,
    6: 12, 7: 14, 8: 16, 9: 18, 10: 20, 11: 22,
}


def estimate_birth_hour(
    sibling_order: str,
    morning_or_night: str,
    first_impression: str,
    decision_style: str,
) -> list[dict]:
    """퀴즈 답변을 기반으로 가장 가능성 높은 시간대를 추정한다."""
    scores = {i: 0 for i in range(12)}

    weight_maps = [
        (_SIBLING_WEIGHTS, sibling_order),
        (_CHRONOTYPE_WEIGHTS, morning_or_night),
        (_IMPRESSION_WEIGHTS, first_impression),
        (_DECISION_WEIGHTS, decision_style),
    ]

    for mapping, answer in weight_maps:
        if answer in mapping:
            for jiji_idx, weight in mapping[answer].items():
                scores[jiji_idx] += weight

    # 점수 높은 순으로 정렬, 상위 3개
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_3 = sorted_scores[:3]

    max_score = top_3[0][1] if top_3 else 1

    results = []
    for jiji_idx, score in top_3:
        if score == 0:
            continue
        ratio = score / max_score
        if ratio >= 0.8:
            confidence = "높음"
        elif ratio >= 0.5:
            confidence = "보통"
        else:
            confidence = "낮음"

        results.append({
            "hour": _JIJI_REPRESENTATIVE_HOUR[jiji_idx],
            "label": HOUR_LABELS[jiji_idx],
            "confidence": confidence,
        })

    return results

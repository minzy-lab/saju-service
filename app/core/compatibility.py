from app.core.saju import calculate_saju
from app.core.ohaeng import analyze_ohaeng
from app.core.zodiac import analyze_zodiac
from app.core.blood_type import get_blood_type_compatibility
from app.core.chinese_zodiac import analyze_chinese_zodiac

# 별자리 원소 궁합 점수
_ELEMENT_COMPAT = {
    ("불", "불"): 80,
    ("불", "흙"): 55,
    ("불", "바람"): 90,
    ("불", "물"): 50,
    ("흙", "흙"): 75,
    ("흙", "바람"): 55,
    ("흙", "물"): 85,
    ("바람", "바람"): 80,
    ("바람", "물"): 60,
    ("물", "물"): 75,
}

# 오행 상생/상극
_OHAENG_COMPAT = {
    ("목", "화"): 90,  # 상생
    ("화", "토"): 90,
    ("토", "금"): 90,
    ("금", "수"): 90,
    ("수", "목"): 90,
    ("목", "토"): 40,  # 상극
    ("토", "수"): 40,
    ("수", "화"): 40,
    ("화", "금"): 40,
    ("금", "목"): 40,
    ("목", "목"): 70,  # 동일
    ("화", "화"): 70,
    ("토", "토"): 70,
    ("금", "금"): 70,
    ("수", "수"): 70,
}


def _get_element_score(e1: str, e2: str) -> int:
    key = (e1, e2) if (e1, e2) in _ELEMENT_COMPAT else (e2, e1)
    return _ELEMENT_COMPAT.get(key, 65)


def _get_ohaeng_score(oh1: str, oh2: str) -> int:
    key = (oh1, oh2) if (oh1, oh2) in _OHAENG_COMPAT else (oh2, oh1)
    return _OHAENG_COMPAT.get(key, 65)


def analyze_compatibility(
    person1: dict,
    person2: dict,
) -> dict:
    """두 사람의 종합 궁합을 분석한다."""
    # 사주 분석
    saju1 = calculate_saju(person1["year"], person1["month"], person1["day"], person1["hour"])
    saju2 = calculate_saju(person2["year"], person2["month"], person2["day"], person2["hour"])
    ohaeng1 = analyze_ohaeng(saju1)
    ohaeng2 = analyze_ohaeng(saju2)

    # 별자리 분석
    zodiac1 = analyze_zodiac(person1["month"], person1["day"])
    zodiac2 = analyze_zodiac(person2["month"], person2["day"])

    # 사주 궁합 (일간 오행 비교)
    saju_score = _get_ohaeng_score(ohaeng1["my_ohaeng"], ohaeng2["my_ohaeng"])

    # 별자리 궁합 (원소 비교)
    zodiac_score = _get_element_score(zodiac1["element"], zodiac2["element"])

    # 혈액형 궁합
    bt1 = person1.get("blood_type")
    bt2 = person2.get("blood_type")
    if bt1 and bt2:
        bt_compat = get_blood_type_compatibility(bt1, bt2)
        bt_score = bt_compat["score"]
        bt_comment = bt_compat["comment"]
    else:
        bt_score = None
        bt_comment = "혈액형 정보 없음"

    # 띠 궁합
    cz1 = analyze_chinese_zodiac(person1["year"], person1["month"], person1["day"])
    cz2 = analyze_chinese_zodiac(person2["year"], person2["month"], person2["day"])
    animal_compat = 75  # 기본값
    if cz2["animal"] in cz1["compatible"]:
        animal_compat = 90
    elif cz2["animal"] in cz1["incompatible"]:
        animal_compat = 45

    # 종합 점수 (가중 평균)
    scores = [saju_score, zodiac_score, animal_compat]
    weights = [35, 30, 15]
    if bt_score is not None:
        scores.append(bt_score)
        weights.append(20)

    total = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

    return {
        "score": round(total),
        "details": {
            "saju_compatibility": {
                "score": saju_score,
                "comment": f"{ohaeng1['my_ohaeng']}(金) × {ohaeng2['my_ohaeng']}(金) 오행 궁합",
            },
            "zodiac_compatibility": {
                "score": zodiac_score,
                "comment": f"{zodiac1['sign']} × {zodiac2['sign']} ({zodiac1['element']} × {zodiac2['element']})",
            },
            "chinese_zodiac_compatibility": {
                "score": animal_compat,
                "comment": f"{cz1['animal']}띠 × {cz2['animal']}띠",
            },
            "blood_type_compatibility": {
                "score": bt_score,
                "comment": bt_comment,
            },
        },
    }

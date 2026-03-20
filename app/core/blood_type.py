from app.data.blood_type_data import BLOOD_TYPE_INFO, BLOOD_TYPE_COMPATIBILITY


def analyze_blood_type(blood_type: str) -> dict:
    """혈액형 성격 분석 결과를 반환한다."""
    bt = blood_type.upper()
    if bt not in BLOOD_TYPE_INFO:
        return None

    info = BLOOD_TYPE_INFO[bt]
    return {
        "type": bt,
        "traits": info["traits"],
        "strengths": info["strengths"],
        "weaknesses": info["weaknesses"],
        "love_style": info["love_style"],
        "personality": info["personality"],
    }


def get_blood_type_compatibility(type1: str, type2: str) -> dict:
    """두 혈액형의 궁합을 반환한다."""
    t1, t2 = type1.upper(), type2.upper()
    key = (t1, t2) if (t1, t2) in BLOOD_TYPE_COMPATIBILITY else (t2, t1)
    return BLOOD_TYPE_COMPATIBILITY.get(key, {"score": 50, "comment": "데이터 없음"})

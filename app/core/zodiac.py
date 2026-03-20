from app.data.zodiac_data import ZODIAC_DATES, ZODIAC_INFO


def get_zodiac_sign(month: int, day: int) -> str:
    """생월일로 별자리를 판별한다."""
    for name, sm, sd, em, ed in ZODIAC_DATES:
        if sm <= em:
            if (month == sm and day >= sd) or (month == em and day <= ed):
                return name
            if sm < month < em:
                return name
        else:
            # 염소자리처럼 연도를 넘기는 경우
            if (month == sm and day >= sd) or (month == em and day <= ed):
                return name
            if month > sm or month < em:
                return name
    return "물고기자리"


def analyze_zodiac(month: int, day: int) -> dict:
    """별자리 분석 결과를 반환한다."""
    sign = get_zodiac_sign(month, day)
    info = ZODIAC_INFO[sign]

    return {
        "sign": sign,
        "element": info["element"],
        "ruling_planet": info["ruling_planet"],
        "keywords": info["keywords"],
        "personality": info["personality"],
    }

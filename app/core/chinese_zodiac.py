from app.data.constants import JIJI_ANIMAL
from app.data.chinese_zodiac_data import CHINESE_ZODIAC_INFO


def get_chinese_zodiac(year: int, month: int, day: int) -> str:
    """절기 기준 띠 동물을 반환한다."""
    # 입춘 이전이면 전년도 띠
    if month < 2 or (month == 2 and day < 4):
        year -= 1
    jiji_idx = (year - 4) % 12
    return JIJI_ANIMAL[jiji_idx]


def analyze_chinese_zodiac(year: int, month: int, day: int) -> dict:
    """띠 운세 분석 결과를 반환한다."""
    animal = get_chinese_zodiac(year, month, day)
    info = CHINESE_ZODIAC_INFO[animal]

    return {
        "animal": animal,
        "traits": info["traits"],
        "personality": info["personality"],
        "compatible": info["compatible"],
        "incompatible": info["incompatible"],
        "fortune_2026": info["fortune_2026"],
    }

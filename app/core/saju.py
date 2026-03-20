from datetime import datetime

from app.data.constants import (
    CHEONGAN,
    JIJI,
    JIJI_ANIMAL,
    WOLJU_CHEONGAN_BASE,
    SIJU_CHEONGAN_BASE,
    HOUR_TO_JIJI,
    JEOLGI_BOUNDARIES,
)


def _get_saju_year(year: int, month: int, day: int) -> int:
    """절기 기준 사주 연도. 입춘(약 2/4) 이전이면 전년도."""
    if month < 2 or (month == 2 and day < 4):
        return year - 1
    return year


def _get_saju_month(month: int, day: int) -> int:
    """절기 기준 사주 월(1~12, 인월=1)."""
    for i, (m, d) in enumerate(JEOLGI_BOUNDARIES):
        next_idx = (i + 1) % 12
        next_m, next_d = JEOLGI_BOUNDARIES[next_idx]

        if next_m > m:
            if (month == m and day >= d) or (m < month < next_m) or (month == next_m and day < next_d):
                return i + 1
        else:
            if (month == m and day >= d) or (month > m) or (month < next_m) or (month == next_m and day < next_d):
                return i + 1

    return 12


def calc_year_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """년주(年柱) 계산."""
    saju_year = _get_saju_year(year, month, day)
    cheongan_idx = (saju_year - 4) % 10
    jiji_idx = (saju_year - 4) % 12
    return CHEONGAN[cheongan_idx], JIJI[jiji_idx]


def calc_month_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """월주(月柱) 계산."""
    year_gan, _ = calc_year_pillar(year, month, day)
    saju_month = _get_saju_month(month, day)

    jiji_idx = (saju_month + 1) % 12
    base = WOLJU_CHEONGAN_BASE[year_gan]
    cheongan_idx = (base + saju_month - 1) % 10

    return CHEONGAN[cheongan_idx], JIJI[jiji_idx]


def calc_day_pillar(year: int, month: int, day: int) -> tuple[str, str]:
    """일주(日柱) 계산. 1900-01-01 = 경자(庚子)일 기준."""
    base_date = datetime(1900, 1, 1)
    target_date = datetime(year, month, day)
    diff_days = (target_date - base_date).days

    cheongan_idx = (diff_days + 6) % 10  # 경=6
    jiji_idx = diff_days % 12

    return CHEONGAN[cheongan_idx], JIJI[jiji_idx]


def calc_hour_pillar(year: int, month: int, day: int, hour: int) -> tuple[str, str]:
    """시주(時柱) 계산."""
    day_gan, _ = calc_day_pillar(year, month, day)

    jiji_idx = HOUR_TO_JIJI.get(hour, 0)
    base = SIJU_CHEONGAN_BASE[day_gan]
    cheongan_idx = (base + jiji_idx) % 10

    return CHEONGAN[cheongan_idx], JIJI[jiji_idx]


def get_animal(year: int, month: int, day: int) -> str:
    """띠 동물 반환."""
    saju_year = _get_saju_year(year, month, day)
    jiji_idx = (saju_year - 4) % 12
    return JIJI_ANIMAL[jiji_idx]


def calculate_saju(year: int, month: int, day: int, hour: int) -> dict:
    """사주팔자 전체 계산."""
    year_gan, year_ji = calc_year_pillar(year, month, day)
    month_gan, month_ji = calc_month_pillar(year, month, day)
    day_gan, day_ji = calc_day_pillar(year, month, day)
    hour_gan, hour_ji = calc_hour_pillar(year, month, day, hour)

    return {
        "year_pillar": {"cheongan": year_gan, "jiji": year_ji},
        "month_pillar": {"cheongan": month_gan, "jiji": month_ji},
        "day_pillar": {"cheongan": day_gan, "jiji": day_ji},
        "hour_pillar": {"cheongan": hour_gan, "jiji": hour_ji},
        "animal": get_animal(year, month, day),
    }

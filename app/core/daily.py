"""오늘의 사주 기반 데일리 추천 모듈."""

from __future__ import annotations

from datetime import datetime, date
from typing import Optional

from app.core.saju import calc_day_pillar, calculate_saju
from app.core.ohaeng import analyze_ohaeng
from app.data.constants import CHEONGAN_OHAENG, JIJI_OHAENG, CHEONGAN_UMYANG


# ── 오행 상생 / 상극 ──

# 상생: A가 B를 생한다 (A → B)
SANGSAENG = {"목": "화", "화": "토", "토": "금", "금": "수", "수": "목"}

# 나를 생해주는 오행 (인성)
SAENG_ME = {"목": "수", "화": "목", "토": "화", "금": "토", "수": "금"}

# 상극: A가 B를 극한다
SANGGEUK = {"목": "토", "화": "금", "토": "수", "금": "목", "수": "화"}

# 나를 극하는 오행
GEUK_ME = {"목": "금", "화": "수", "토": "목", "금": "화", "수": "토"}


# ── 오행별 연관 데이터 ──

OHAENG_COLORS = {
    "목": ["초록", "연두", "청록"],
    "화": ["빨강", "주황", "분홍"],
    "토": ["노랑", "베이지", "갈색"],
    "금": ["흰색", "은색", "금색"],
    "수": ["검정", "남색", "파랑"],
}

OHAENG_DIRECTIONS = {
    "목": "동쪽",
    "화": "남쪽",
    "토": "중앙",
    "금": "서쪽",
    "수": "북쪽",
}

OHAENG_FOODS = {
    "목": ["샐러드", "나물 반찬", "비타민이 풍부한 과일", "녹즙", "봄나물"],
    "화": ["매콤한 떡볶이", "불고기", "바비큐", "따뜻한 차", "볶음 요리"],
    "토": ["고구마", "호박죽", "곡물빵", "꿀물", "단호박 라떼"],
    "금": ["삼계탕", "매운 음식", "생강차", "배", "도라지차"],
    "수": ["해산물", "미역국", "수박", "아이스 아메리카노", "회"],
}

OHAENG_ACTIVITIES = {
    "목": ["새로운 프로젝트 시작", "독서", "식물 가꾸기", "산책", "계획 세우기", "아이디어 정리"],
    "화": ["운동", "사람 만나기", "프레젠테이션", "SNS 활동", "요리", "창작 활동"],
    "토": ["집 정리", "저축/재테크", "맛집 탐방", "안정적인 루틴", "가족과 시간 보내기"],
    "금": ["중요한 결정", "마무리 작업", "정리정돈", "다이어트 시작", "불필요한 것 정리"],
    "수": ["명상", "일기 쓰기", "공부", "자기 성찰", "음악 감상", "목욕/반신욕"],
}

OHAENG_CAUTION = {
    "목": "급하게 결정하지 마세요. 충동적인 소비를 조심하세요.",
    "화": "감정적으로 대응하지 마세요. 과로에 주의하세요.",
    "토": "우유부단함을 조심하세요. 남의 일에 너무 신경 쓰지 마세요.",
    "금": "고집을 부리면 손해를 볼 수 있어요. 유연하게 대처하세요.",
    "수": "걱정을 너무 많이 하지 마세요. 혼자 끙끙 앓지 말고 표현하세요.",
}

OHAENG_NUMBERS = {
    "목": [3, 8],
    "화": [2, 7],
    "토": [5, 10],
    "금": [4, 9],
    "수": [1, 6],
}

# ── 오행 관계별 오늘의 에너지 해석 ──

_ENERGY_DESCRIPTIONS = {
    "생아": "오늘은 나를 도와주는 에너지가 흐르는 날이에요! 힘이 충전되고 안정감을 느낄 수 있어요.",
    "아생": "오늘은 내 에너지를 나누는 날이에요. 다른 사람을 돕거나 가르치는 일에 보람을 느낄 수 있어요.",
    "극아": "오늘은 도전적인 에너지가 있는 날이에요. 긴장감이 오히려 성장의 동력이 될 수 있어요.",
    "아극": "오늘은 적극적으로 밀고 나갈 수 있는 날이에요. 결단력이 빛나는 하루가 될 거예요.",
    "비견": "오늘은 나와 비슷한 에너지가 흐르는 날이에요. 자신감이 높아지고 주체적인 하루를 보낼 수 있어요.",
}


def _get_energy_relation(my_ohaeng: str, today_ohaeng: str) -> str:
    """내 오행과 오늘의 오행 관계를 판별."""
    if my_ohaeng == today_ohaeng:
        return "비견"
    if SAENG_ME[my_ohaeng] == today_ohaeng:
        return "생아"  # 오늘이 나를 생함
    if SANGSAENG[my_ohaeng] == today_ohaeng:
        return "아생"  # 내가 오늘을 생함
    if GEUK_ME[my_ohaeng] == today_ohaeng:
        return "극아"  # 오늘이 나를 극함
    if SANGGEUK[my_ohaeng] == today_ohaeng:
        return "아극"  # 내가 오늘을 극함
    return "비견"


def _calc_daily_luck_score(relation: str, my_ohaeng: str, today_ohaeng: str, weakest: str) -> int:
    """오늘의 운세 점수 (0~100)."""
    base = {"생아": 90, "비견": 75, "아극": 70, "아생": 60, "극아": 45}
    score = base.get(relation, 65)

    # 약한 오행이 보충되면 보너스
    if today_ohaeng == SAENG_ME.get(weakest):
        score = min(score + 10, 100)

    return score


def get_daily_recommendation(
    year: int, month: int, day: int, hour: int,
    today: date | None = None,
) -> dict:
    """사주 기반 오늘의 추천을 생성한다."""
    if today is None:
        today = date.today()

    # 사용자 사주 분석
    saju = calculate_saju(year, month, day, hour)
    ohaeng = analyze_ohaeng(saju)
    my_ohaeng = ohaeng["my_ohaeng"]
    weakest = ohaeng["weakest"]

    # 오늘의 일주
    today_gan, today_ji = calc_day_pillar(today.year, today.month, today.day)
    today_ohaeng = CHEONGAN_OHAENG[today_gan]
    today_umyang = CHEONGAN_UMYANG[today_gan]

    # 나와 오늘의 관계
    relation = _get_energy_relation(my_ohaeng, today_ohaeng)
    energy_desc = _ENERGY_DESCRIPTIONS[relation]
    luck_score = _calc_daily_luck_score(relation, my_ohaeng, today_ohaeng, weakest)

    # 추천 오행: 나를 생해주는 오행 우선, 약한 오행 보충
    beneficial = SAENG_ME[my_ohaeng]

    # 추천 컬러 (나를 생해주는 오행의 색상)
    lucky_colors = OHAENG_COLORS[beneficial]

    # 추천 음식
    lucky_foods = OHAENG_FOODS[beneficial]

    # 추천 활동
    # 관계에 따라 다른 활동 추천
    if relation in ("생아", "비견"):
        lucky_activities = OHAENG_ACTIVITIES[my_ohaeng][:3]
    elif relation == "아극":
        lucky_activities = OHAENG_ACTIVITIES[today_ohaeng][:3]
    else:
        lucky_activities = OHAENG_ACTIVITIES[beneficial][:3]

    # 추천 방향
    lucky_direction = OHAENG_DIRECTIONS[beneficial]

    # 추천 숫자
    lucky_numbers = OHAENG_NUMBERS[beneficial]

    # 주의사항
    caution_ohaeng = GEUK_ME[my_ohaeng]
    caution = OHAENG_CAUTION[caution_ohaeng]

    # 오늘의 한마디
    tips = _get_daily_tip(relation, my_ohaeng, today_ohaeng)

    return {
        "date": today.isoformat(),
        "today_pillar": {
            "cheongan": today_gan,
            "jiji": today_ji,
            "ohaeng": today_ohaeng,
            "umyang": today_umyang,
        },
        "my_ohaeng": my_ohaeng,
        "weakest_ohaeng": weakest,
        "relation": relation,
        "energy_description": energy_desc,
        "luck_score": luck_score,
        "recommendations": {
            "colors": lucky_colors,
            "foods": lucky_foods,
            "activities": lucky_activities,
            "direction": lucky_direction,
            "numbers": lucky_numbers,
        },
        "caution": caution,
        "daily_tip": tips,
        "saju": saju,
        "ohaeng": ohaeng,
    }


def _get_daily_tip(relation: str, my_ohaeng: str, today_ohaeng: str) -> str:
    """오행 관계에 따른 오늘의 팁."""
    tips = {
        ("생아", "목"): "오늘은 수(水)의 에너지가 당신을 감싸주는 날. 물 많이 마시고, 여유로운 하루를 즐기세요.",
        ("생아", "화"): "오늘은 목(木)의 에너지가 당신의 열정을 키워주는 날. 새로운 아이디어에 불을 붙여보세요!",
        ("생아", "토"): "오늘은 화(火)의 에너지가 당신을 따뜻하게 해주는 날. 소중한 사람과 함께하면 더 좋아요.",
        ("생아", "금"): "오늘은 토(土)의 에너지가 당신을 받쳐주는 날. 안정적인 환경에서 큰 성과를 낼 수 있어요.",
        ("생아", "수"): "오늘은 금(金)의 에너지가 당신에게 맑은 기운을 주는 날. 머리가 맑고 판단력이 좋아요.",

        ("극아", "목"): "금(金)의 에너지가 강한 날이에요. 너무 무리하지 말고 유연하게 대처하세요.",
        ("극아", "화"): "수(水)의 에너지가 강한 날이에요. 감정 조절에 신경 쓰고, 차분하게 행동하세요.",
        ("극아", "토"): "목(木)의 에너지가 강한 날이에요. 변화에 유연하게 대응하면 좋은 결과가 있을 거예요.",
        ("극아", "금"): "화(火)의 에너지가 강한 날이에요. 열정적인 사람들 사이에서 배울 점을 찾아보세요.",
        ("극아", "수"): "토(土)의 에너지가 강한 날이에요. 현실적인 문제에 집중하면 해결의 실마리가 보여요.",

        ("아극", "목"): "당신의 에너지가 강한 날! 밀고 나가되, 상대방 입장도 한번 더 생각해보세요.",
        ("아극", "화"): "당신의 열정이 빛나는 날! 적극적으로 행동하되 감정 컨트롤은 필수예요.",
        ("아극", "토"): "당신의 안정감이 힘을 발휘하는 날! 주도적으로 일을 이끌어가세요.",
        ("아극", "금"): "당신의 결단력이 빛나는 날! 과감한 선택이 좋은 결과를 가져올 거예요.",
        ("아극", "수"): "당신의 지혜가 빛나는 날! 분석력을 발휘해서 문제를 해결해보세요.",

        ("아생", "목"): "당신의 에너지가 밖으로 나가는 날이에요. 베푸는 만큼 돌아오니 아끼지 마세요.",
        ("아생", "화"): "열정을 나누는 날이에요. 후배나 동료를 도와주면 보람찬 하루가 될 거예요.",
        ("아생", "토"): "안정의 에너지를 나누는 날. 주변을 챙기되, 자신의 에너지도 꼭 보충하세요.",
        ("아생", "금"): "정리하고 정돈하는 에너지를 나누는 날. 환경을 깔끔하게 하면 마음도 가벼워져요.",
        ("아생", "수"): "지혜를 나누는 날이에요. 조언이 필요한 사람에게 좋은 말을 해주세요.",

        ("비견", "목"): "같은 목(木) 에너지가 겹치는 날! 자신감이 넘치지만, 고집은 살짝 내려놓으세요.",
        ("비견", "화"): "같은 화(火) 에너지가 겹치는 날! 열정이 배가 되지만, 번아웃 주의하세요.",
        ("비견", "토"): "같은 토(土) 에너지가 겹치는 날! 안정감이 극대화되지만, 새로운 시도도 해보세요.",
        ("비견", "금"): "같은 금(金) 에너지가 겹치는 날! 집중력이 최고지만, 완벽주의는 잠시 내려놓으세요.",
        ("비견", "수"): "같은 수(水) 에너지가 겹치는 날! 깊은 생각이 가능하지만, 행동으로 옮기는 것도 중요해요.",
    }

    return tips.get((relation, my_ohaeng), _ENERGY_DESCRIPTIONS.get(relation, ""))

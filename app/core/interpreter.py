import os
import json

from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────
# 오행별 성격/운세 템플릿
# ──────────────────────────────────────────
_OHAENG_PERSONALITY = {
    "목": "성장과 창조의 에너지를 가진 당신은 새로운 것을 시작하는 데 탁월하고, 정의감이 강하며 리더십이 있습니다.",
    "화": "열정과 표현력이 넘치는 당신은 사람들 사이에서 빛나는 존재이며, 감정이 풍부하고 직관력이 뛰어납니다.",
    "토": "안정감과 신뢰를 주는 당신은 주변 사람들의 중심이 되며, 꾸준하고 책임감 있는 성격의 소유자입니다.",
    "금": "결단력과 집중력이 뛰어난 당신은 목표를 향해 흔들림 없이 나아가며, 원칙과 질서를 중시합니다.",
    "수": "깊은 사고력과 지혜를 가진 당신은 상황을 꿰뚫어보는 통찰력이 있으며, 유연하게 적응하는 능력이 탁월합니다.",
}

_OHAENG_FORTUNE = {
    "목": "2026년은 당신의 아이디어와 창의력이 빛을 발하는 해입니다. 새로운 프로젝트나 학습을 시작하기에 최적의 시기이며, 봄과 여름에 특히 좋은 기회가 찾아옵니다.",
    "화": "2026년은 인간관계와 표현력이 빛나는 해입니다. 그동안 쌓아온 능력을 보여줄 기회가 오며, 주변의 인정을 받는 시기가 됩니다.",
    "토": "2026년은 안정과 결실의 해입니다. 꾸준히 노력해온 일에서 성과가 나타나고, 부동산이나 자산 관련 좋은 소식이 있을 수 있습니다.",
    "금": "2026년은 변화와 도전의 해입니다. 기존의 틀을 깨고 새로운 방향을 모색하면 좋은 결과가 따릅니다. 하반기에 특히 운이 상승합니다.",
    "수": "2026년은 내면 성장과 지혜가 깊어지는 해입니다. 공부나 자기계발에 투자하면 큰 수확이 있으며, 직관을 믿고 행동하면 좋은 결과를 얻습니다.",
}

_OHAENG_LOVE = {
    "목": "연애에서 성장을 추구하는 타입입니다. 서로 발전시켜줄 수 있는 파트너에게 끌리며, 자유로우면서도 깊은 유대감을 원합니다.",
    "화": "연애에서 열정적이고 로맨틱한 타입입니다. 감정 표현이 풍부하고 상대방을 즐겁게 해주지만, 가끔 감정 기복이 있을 수 있어요.",
    "토": "연애에서 안정과 신뢰를 중시하는 타입입니다. 한번 마음을 주면 끝까지 함께하며, 가정적이고 헌신적인 파트너입니다.",
    "금": "연애에서 진지하고 신중한 타입입니다. 쉽게 마음을 열지 않지만, 한번 빠지면 깊고 강한 사랑을 합니다.",
    "수": "연애에서 감성적이고 직관적인 타입입니다. 상대방의 마음을 잘 읽고 공감해주며, 정서적 교감을 가장 중요하게 여깁니다.",
}

_OHAENG_CAREER = {
    "목": "창의적인 분야, 교육, 스타트업, 기획 등에서 능력을 발휘합니다. 새로운 것을 만들어내는 직업이 잘 맞습니다.",
    "화": "엔터테인먼트, 마케팅, 디자인, 영업 등 사람을 만나고 표현하는 분야에서 빛납니다. 무대 위의 사람이 될 수 있어요.",
    "토": "경영, 부동산, 금융, 공무원 등 안정적이고 체계적인 분야에서 능력을 발휘합니다. 조직의 중심 역할을 잘합니다.",
    "금": "법률, IT, 엔지니어링, 연구직 등 정밀함과 논리가 필요한 분야에 적합합니다. 전문가로서의 길이 잘 맞습니다.",
    "수": "학문, 예술, 상담, 철학 등 깊이 있는 사고가 필요한 분야에서 능력을 발휘합니다. 통찰력으로 문제를 해결하는 역할이 잘 맞아요.",
}

_OHAENG_ADVICE = {
    "목": "올해는 시작의 용기를 가지세요. 머릿속 아이디어를 실행으로 옮기면 기대 이상의 결과가 따라옵니다.",
    "화": "올해는 감정 조절이 핵심입니다. 열정을 유지하되, 중요한 결정은 한 템포 쉬고 내려보세요.",
    "토": "올해는 기존의 것을 굳건히 지키는 것이 답입니다. 급한 변화보다 꾸준함이 최고의 전략이에요.",
    "금": "올해는 유연함을 연습하세요. 완벽하지 않아도 괜찮다는 마음가짐이 오히려 더 좋은 결과를 만들어줍니다.",
    "수": "올해는 직감을 믿으세요. 논리적으로 설명이 안 되더라도 마음이 끌리는 방향이 정답일 확률이 높습니다.",
}

# 별자리 원소별 보충 성격
_ELEMENT_TRAIT = {
    "불": "겉으로는 활발하고 에너지가 넘치는 모습을 보여주며",
    "흙": "겉으로는 듬직하고 믿음직한 인상을 주며",
    "바람": "겉으로는 유쾌하고 소통을 잘하는 사교적인 모습이며",
    "물": "겉으로는 조용하고 깊이 있는 분위기를 풍기며",
}


def _build_local_interpretation(analysis: dict) -> dict:
    """사전 정의된 템플릿으로 종합 해석을 생성한다."""
    ohaeng = analysis.get("ohaeng", {})
    zodiac = analysis.get("zodiac", {})
    blood = analysis.get("blood_type", {})
    mbti = analysis.get("predicted_mbti", {})
    chinese = analysis.get("chinese_zodiac", {})

    my_oh = ohaeng.get("my_ohaeng", "목")
    sign = zodiac.get("sign", "")
    element = zodiac.get("element", "")
    bt = blood.get("type", "")
    mbti_type = mbti.get("type", "")
    animal = chinese.get("animal", "")

    # 한줄 요약
    parts = [f"{my_oh}({my_oh}) 기운의 {sign}"]
    if bt:
        parts.append(f"{bt}형")
    if animal:
        parts.append(f"{animal}띠")
    summary = ", ".join(parts)

    # 성격
    base_personality = _OHAENG_PERSONALITY.get(my_oh, "")
    element_trait = _ELEMENT_TRAIT.get(element, "")
    personality = f"{element_trait}, {base_personality}"
    if bt and blood.get("personality"):
        personality += f" {blood['personality']}"
    if mbti_type:
        personality += f" MBTI로 보면 {mbti_type} 타입에 가깝습니다."

    # 운세
    fortune = _OHAENG_FORTUNE.get(my_oh, "")
    if chinese.get("fortune_2026"):
        fortune += f" {chinese['fortune_2026']}"

    # 연애
    love = _OHAENG_LOVE.get(my_oh, "")
    if bt and blood.get("love_style"):
        love += f" {blood['love_style']}"

    # 직업
    career = _OHAENG_CAREER.get(my_oh, "")

    # 조언
    advice = _OHAENG_ADVICE.get(my_oh, "")

    return {
        "summary": summary,
        "personality": personality,
        "fortune_2026": fortune,
        "love": love,
        "career": career,
        "advice": advice,
    }


def _build_local_compatibility_summary(compat_result: dict) -> str:
    """사전 정의된 템플릿으로 궁합 해석을 생성한다."""
    score = compat_result.get("score", 50)
    details = compat_result.get("details", {})

    if score >= 85:
        tone = "아주 잘 맞는 환상의 궁합이에요!"
    elif score >= 70:
        tone = "꽤 좋은 궁합이에요! 서로에게 긍정적인 영향을 줄 수 있는 관계입니다."
    elif score >= 55:
        tone = "보통의 궁합이지만, 서로 노력하면 충분히 좋은 관계를 만들 수 있어요."
    else:
        tone = "성격 차이가 있지만, 오히려 서로 부족한 부분을 채워줄 수 있는 관계예요."

    parts = [tone]

    saju = details.get("saju_compatibility", {})
    if saju.get("comment"):
        parts.append(f"사주 오행으로 보면 {saju['comment']}입니다.")

    zodiac = details.get("zodiac_compatibility", {})
    if zodiac.get("comment"):
        parts.append(f"별자리로 보면 {zodiac['comment']} 조합이에요.")

    bt = details.get("blood_type_compatibility", {})
    if bt.get("score") and bt.get("comment"):
        parts.append(f"혈액형은 {bt['comment']}.")

    return " ".join(parts)


async def interpret_full(analysis: dict) -> dict:
    """무료 로컬 템플릿 해석."""
    return _build_local_interpretation(analysis)


async def interpret_full_ai(analysis: dict) -> dict:
    """유료 AI 상세 해석 (Claude API)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}

    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key)

        prompt = f"""당신은 사주/운세/성격 분석 전문가입니다.
아래 분석 결과를 종합해서 한 사람의 운명을 재미있고 친근한 말투로 해석해주세요.
일반적인 해석이 아니라, 이 사람만의 고유한 조합을 깊이 있게 분석해주세요.

## 분석 데이터
{json.dumps(analysis, ensure_ascii=False, indent=2)}

## 해석 형식 (JSON)
아래 형식으로 JSON만 반환해주세요. 다른 텍스트 없이 순수 JSON만 출력하세요.
{{
  "summary": "한줄 요약 (30자 이내)",
  "personality": "종합 성격 분석 (사주 오행 + 별자리 + 혈액형 + MBTI를 엮어서 5~6문장, 깊이 있게)",
  "fortune_2026": "2026년 운세 (월별 흐름 포함, 3~4문장)",
  "love": "연애운/이상형 분석 (구체적으로 3~4문장)",
  "career": "직업/진로 적성 (구체적 직업군 추천 포함, 3~4문장)",
  "advice": "올해 핵심 조언 (2~3문장, 구체적 행동 제안)"
}}

주의사항:
- 반드시 위 JSON 형식으로만 답변
- 친근하고 긍정적인 톤 유지
- 각 모듈의 결과를 자연스럽게 엮어서 이 사람만의 고유한 해석 제공
- 혈액형이나 MBTI 데이터가 없으면 있는 데이터만으로 해석"""

        message = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        text = message.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


async def interpret_compatibility(person1_analysis: dict, person2_analysis: dict, compat_result: dict) -> str:
    """궁합 해석. Claude API 가능하면 사용, 아니면 로컬 템플릿."""
    api_key = os.getenv("ANTHROPIC_API_KEY")

    if api_key:
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=api_key)

            prompt = f"""당신은 궁합 분석 전문가입니다.
두 사람의 분석 결과와 궁합 점수를 보고, 재미있고 친근한 말투로 궁합 해석을 해주세요.

## 1번째 사람
{json.dumps(person1_analysis, ensure_ascii=False, indent=2)}

## 2번째 사람
{json.dumps(person2_analysis, ensure_ascii=False, indent=2)}

## 궁합 분석 결과
{json.dumps(compat_result, ensure_ascii=False, indent=2)}

3~5문장으로 종합 궁합 해석을 해주세요. 친근하고 긍정적인 톤으로."""

            message = await client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text.strip()
        except Exception:
            pass

    # API 실패 → 로컬 템플릿
    return _build_local_compatibility_summary(compat_result)

import os
import json

import anthropic
from dotenv import load_dotenv

load_dotenv()


async def interpret_full(analysis: dict) -> dict:
    """모든 분석 결과를 Claude API로 종합 해석한다."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {"error": "ANTHROPIC_API_KEY가 설정되지 않았습니다."}

    client = anthropic.AsyncAnthropic(api_key=api_key)

    prompt = f"""당신은 사주/운세/성격 분석 전문가입니다.
아래 분석 결과를 종합해서 한 사람의 운명을 재미있고 친근한 말투로 해석해주세요.

## 분석 데이터
{json.dumps(analysis, ensure_ascii=False, indent=2)}

## 해석 형식 (JSON)
아래 형식으로 JSON만 반환해주세요. 다른 텍스트 없이 순수 JSON만 출력하세요.
{{
  "summary": "한줄 요약 (30자 이내)",
  "personality": "종합 성격 분석 (사주 오행 + 별자리 + 혈액형 + MBTI를 엮어서 3~4문장)",
  "fortune_2026": "2026년 운세 (사주 기반 2~3문장)",
  "love": "연애운/이상형 분석 (2~3문장)",
  "career": "직업/진로 적성 (2~3문장)",
  "advice": "올해 핵심 조언 한마디 (1~2문장)"
}}

주의사항:
- 반드시 위 JSON 형식으로만 답변
- 친근하고 긍정적인 톤 유지
- 각 모듈의 결과를 자연스럽게 연결해서 해석
- 혈액형이나 MBTI 데이터가 없으면 있는 데이터만으로 해석"""

    message = await client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        text = message.content[0].text.strip()
        # JSON 블록 추출
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        return json.loads(text)
    except (json.JSONDecodeError, IndexError):
        return {"raw_response": message.content[0].text}


async def interpret_compatibility(person1_analysis: dict, person2_analysis: dict, compat_result: dict) -> str:
    """궁합 분석 결과를 AI로 해석한다."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return "ANTHROPIC_API_KEY가 설정되지 않았습니다."

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

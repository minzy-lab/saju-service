from fastapi import APIRouter

from app.models.schemas import AnalyzeRequest, EstimateHourRequest, CompatibilityRequest
from app.core.saju import calculate_saju
from app.core.ohaeng import analyze_ohaeng
from app.core.zodiac import analyze_zodiac
from app.core.blood_type import analyze_blood_type
from app.core.chinese_zodiac import analyze_chinese_zodiac
from app.core.mbti_predictor import predict_mbti
from app.core.hour_estimator import estimate_birth_hour
from app.core.compatibility import analyze_compatibility
from app.core.interpreter import interpret_full, interpret_compatibility

router = APIRouter(prefix="/api")


def _build_analysis(req: AnalyzeRequest) -> dict:
    """공통 분석 로직."""
    saju = calculate_saju(req.year, req.month, req.day, req.hour)
    ohaeng = analyze_ohaeng(saju)
    zodiac = analyze_zodiac(req.month, req.day)
    chinese_zodiac = analyze_chinese_zodiac(req.year, req.month, req.day)

    blood = None
    if req.blood_type:
        blood = analyze_blood_type(req.blood_type)

    mbti = predict_mbti(
        ohaeng_counts=ohaeng["counts"],
        zodiac_element=zodiac["element"],
        blood_type=req.blood_type,
    )

    result = {
        "saju": saju,
        "ohaeng": ohaeng,
        "zodiac": zodiac,
        "chinese_zodiac": chinese_zodiac,
        "predicted_mbti": mbti,
    }

    if blood:
        result["blood_type"] = blood

    return result


@router.post("/analyze")
async def analyze(req: AnalyzeRequest):
    """전체 모듈 분석 (AI 해석 제외)."""
    return _build_analysis(req)


@router.post("/analyze/full")
async def analyze_full(req: AnalyzeRequest):
    """전체 분석 + AI 종합 해석."""
    analysis = _build_analysis(req)
    interpretation = await interpret_full(analysis)
    analysis["interpretation"] = interpretation
    return analysis


@router.post("/saju")
async def saju_only(req: AnalyzeRequest):
    """사주팔자 + 오행만 분석."""
    saju = calculate_saju(req.year, req.month, req.day, req.hour)
    ohaeng = analyze_ohaeng(saju)
    return {"saju": saju, "ohaeng": ohaeng}


@router.post("/zodiac")
async def zodiac_only(req: AnalyzeRequest):
    """별자리만 분석."""
    return analyze_zodiac(req.month, req.day)


@router.post("/blood-type")
async def blood_type_only(req: AnalyzeRequest):
    """혈액형 성격만 분석."""
    if not req.blood_type:
        return {"error": "blood_type 필드가 필요합니다."}
    return analyze_blood_type(req.blood_type)


@router.post("/estimate-hour")
async def estimate_hour(req: EstimateHourRequest):
    """시주 추정 퀴즈."""
    results = estimate_birth_hour(
        sibling_order=req.quiz.sibling_order,
        morning_or_night=req.quiz.morning_or_night,
        first_impression=req.quiz.first_impression,
        decision_style=req.quiz.decision_style,
    )
    return {"estimated_hours": results}


@router.post("/compatibility")
async def compatibility(req: CompatibilityRequest):
    """두 사람 궁합 분석."""
    p1 = req.person1.model_dump()
    p2 = req.person2.model_dump()

    compat = analyze_compatibility(p1, p2)

    # AI 해석 추가
    analysis1 = _build_analysis(req.person1)
    analysis2 = _build_analysis(req.person2)
    summary = await interpret_compatibility(analysis1, analysis2, compat)
    compat["summary"] = summary

    return compat

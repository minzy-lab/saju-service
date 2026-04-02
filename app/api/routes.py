import uuid

from fastapi import APIRouter, Request, Depends

from app.dependencies import require_login
from app.models.schemas import (
    AnalyzeRequest, EstimateHourRequest, CompatibilityRequest,
    PaymentOrderRequest, PaymentConfirmRequest,
)
from app.core.payment import create_order, confirm_payment, get_order, PRICE, TOSS_CLIENT_KEY
from app.core.saju import calculate_saju
from app.core.ohaeng import analyze_ohaeng
from app.core.zodiac import analyze_zodiac
from app.core.blood_type import analyze_blood_type
from app.core.chinese_zodiac import analyze_chinese_zodiac
from app.core.mbti_predictor import predict_mbti
from app.core.hour_estimator import estimate_birth_hour
from app.core.compatibility import analyze_compatibility
from app.core.interpreter import interpret_full, interpret_full_ai, interpret_compatibility
from app.core.daily import get_daily_recommendation

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
    """전체 모듈 분석 + 무료 로컬 해석."""
    analysis = _build_analysis(req)
    analysis["interpretation"] = await interpret_full(analysis)
    return analysis


@router.post("/analyze/full")
async def analyze_full(req: AnalyzeRequest, request: Request, user: dict = Depends(require_login)):
    """전체 분석 + AI 상세 해석 (유료, 로그인 필요)."""
    analysis = _build_analysis(req)
    interpretation = await interpret_full_ai(analysis)
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


@router.post("/daily")
async def daily(req: AnalyzeRequest):
    """사주 기반 오늘의 추천."""
    return get_daily_recommendation(req.year, req.month, req.day, req.hour)


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


# ── 결제 ──

@router.post("/payment/order")
async def payment_order(req: PaymentOrderRequest, request: Request, user: dict = Depends(require_login)):
    """주문 생성 (로그인 필요)."""
    order_id = f"saju_{uuid.uuid4().hex[:12]}"
    body = req.model_dump()
    order = create_order(order_id, PRICE, body)
    return {
        "orderId": order["order_id"],
        "amount": order["amount"],
        "clientKey": TOSS_CLIENT_KEY,
    }


@router.post("/payment/confirm")
async def payment_confirm(req: PaymentConfirmRequest, request: Request, user: dict = Depends(require_login)):
    """결제 승인 (로그인 필요)."""
    result = await confirm_payment(req.payment_key, req.order_id, req.amount)
    if result.get("error"):
        return {"success": False, "error": result["error"]}

    # 승인 성공 → 주문에 저장된 분석 데이터로 AI 해석
    order = get_order(req.order_id)
    if order:
        body = order["analysis_body"]
        analyze_req = AnalyzeRequest(**body)
        analysis = _build_analysis(analyze_req)
        interpretation = await interpret_full_ai(analysis)
        order["status"] = "INTERPRETED"
        return {"success": True, "interpretation": interpretation}

    return {"success": True, "interpretation": None}

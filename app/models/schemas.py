from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100, description="출생 연도")
    month: int = Field(..., ge=1, le=12, description="출생 월")
    day: int = Field(..., ge=1, le=31, description="출생 일")
    hour: int = Field(..., ge=0, le=23, description="출생 시 (0~23)")
    blood_type: Optional[str] = Field(None, pattern="^(A|B|O|AB)$", description="혈액형 (선택)")


class QuizAnswers(BaseModel):
    sibling_order: str = Field(..., description="형제 순서: 외동/첫째/중간/막내")
    morning_or_night: str = Field(..., description="아침형/저녁형/둘 다 아님")
    first_impression: str = Field(..., description="첫인상: 차가움/따뜻함/활발함/조용함")
    decision_style: str = Field(..., description="의사결정: 즉흥적/신중함/상황에 따라 다름")


class EstimateHourRequest(BaseModel):
    year: int = Field(..., ge=1900, le=2100)
    month: int = Field(..., ge=1, le=12)
    day: int = Field(..., ge=1, le=31)
    quiz: QuizAnswers


class CompatibilityRequest(BaseModel):
    person1: AnalyzeRequest
    person2: AnalyzeRequest

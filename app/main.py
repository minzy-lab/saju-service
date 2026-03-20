from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="운명 API (Unmyeong API)",
    description="샤머니즘 총집합 — 사주, 별자리, 혈액형, MBTI, 띠를 한번에 분석하고 AI가 종합 해석",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}

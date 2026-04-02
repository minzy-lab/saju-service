from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="운명 API (Unmyeong API)",
    description="샤머니즘 총집합 — 사주, 별자리, 혈액형, MBTI, 띠를 한번에 분석하고 AI가 종합 해석",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/compatibility")
async def compatibility_page(request: Request):
    return templates.TemplateResponse("compatibility.html", {"request": request})


@app.get("/payment/success")
async def payment_success_page(request: Request):
    return templates.TemplateResponse("payment_success.html", {"request": request})


@app.get("/payment/fail")
async def payment_fail_page(request: Request):
    return templates.TemplateResponse("payment_fail.html", {"request": request})

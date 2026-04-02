import os
from pathlib import Path
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import router
from app.api.auth import router as auth_router
from app.db import init_db
from app.dependencies import get_current_user

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="운명 API (Unmyeong API)",
    description="샤머니즘 총집합 — 사주, 별자리, 혈액형, MBTI, 띠를 한번에 분석하고 AI가 종합 해석",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "change-me-in-production"),
    max_age=60 * 60 * 24 * 7,
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

app.include_router(router)
app.include_router(auth_router)


def _template(request: Request, name: str, ctx: dict = None):
    context = {"request": request, "user": get_current_user(request)}
    if ctx:
        context.update(ctx)
    return templates.TemplateResponse(name, context)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def index(request: Request):
    return _template(request, "index.html")


@app.get("/daily")
async def daily_page(request: Request):
    return _template(request, "daily.html")


@app.get("/compatibility")
async def compatibility_page(request: Request):
    return _template(request, "compatibility.html")


@app.get("/login")
async def login_page(request: Request):
    if get_current_user(request):
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/")
    return _template(request, "login.html")


@app.get("/payment/success")
async def payment_success_page(request: Request):
    return _template(request, "payment_success.html")


@app.get("/payment/fail")
async def payment_fail_page(request: Request):
    return _template(request, "payment_fail.html")

from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db
from app.models.user import User
from app.core.kakao import get_authorize_url, get_access_token, get_user_info, kakao_logout

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login")
async def login(request: Request):
    redirect_uri = str(request.url_for("kakao_callback"))
    authorize_url = get_authorize_url(redirect_uri)
    return RedirectResponse(url=authorize_url)


@router.get("/kakao/callback", name="kakao_callback")
async def kakao_callback(
    request: Request,
    code: str,
    db: AsyncSession = Depends(get_db),
):
    redirect_uri = str(request.url_for("kakao_callback"))

    # 1. 인가 코드 → 액세스 토큰
    token_data = await get_access_token(code, redirect_uri)
    access_token = token_data.get("access_token")
    if not access_token:
        return RedirectResponse(url="/?error=login_failed")

    # 2. 사용자 정보 조회
    user_info = await get_user_info(access_token)
    kakao_id = str(user_info["id"])
    kakao_account = user_info.get("kakao_account", {})
    profile = kakao_account.get("profile", {})

    nickname = profile.get("nickname")
    profile_image = profile.get("profile_image_url")
    email = kakao_account.get("email")

    # 3. DB upsert
    result = await db.execute(select(User).where(User.kakao_id == kakao_id))
    user = result.scalar_one_or_none()

    if user:
        user.nickname = nickname
        user.profile_image = profile_image
        if email:
            user.email = email
    else:
        user = User(
            kakao_id=kakao_id,
            nickname=nickname,
            profile_image=profile_image,
            email=email,
        )
        db.add(user)

    await db.commit()
    await db.refresh(user)

    # 4. 세션 설정
    request.session["user_id"] = user.id
    request.session["nickname"] = user.nickname
    request.session["profile_image"] = user.profile_image
    request.session["kakao_access_token"] = access_token

    return RedirectResponse(url="/", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    kakao_token = request.session.get("kakao_access_token")
    if kakao_token:
        await kakao_logout(kakao_token)

    request.session.clear()
    return RedirectResponse(url="/", status_code=302)

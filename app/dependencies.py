from typing import Optional

from fastapi import Request, HTTPException


def get_current_user(request: Request) -> Optional[dict]:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return {
        "id": user_id,
        "nickname": request.session.get("nickname"),
        "profile_image": request.session.get("profile_image"),
    }


def require_login(request: Request) -> dict:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    return user

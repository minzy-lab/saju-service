import os

from dotenv import load_dotenv
import httpx

load_dotenv()

KAKAO_REST_API_KEY = os.getenv("KAKAO_REST_API_KEY")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
KAKAO_AUTH_URL = "https://kauth.kakao.com/oauth/authorize"
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_INFO_URL = "https://kapi.kakao.com/v2/user/me"
KAKAO_LOGOUT_URL = "https://kapi.kakao.com/v1/user/logout"


def get_authorize_url(redirect_uri: str) -> str:
    return (
        f"{KAKAO_AUTH_URL}"
        f"?client_id={KAKAO_REST_API_KEY}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )


async def get_access_token(code: str, redirect_uri: str) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.post(
            KAKAO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_REST_API_KEY,
                "client_secret": KAKAO_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "code": code,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    return res.json()


async def get_user_info(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        res = await client.get(
            KAKAO_USER_INFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    return res.json()


async def kakao_logout(access_token: str) -> None:
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                KAKAO_LOGOUT_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )
    except Exception:
        pass

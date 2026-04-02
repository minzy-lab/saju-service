from __future__ import annotations

import os
import base64
from datetime import datetime
from typing import Dict, Optional

import httpx
from dotenv import load_dotenv

load_dotenv()

# 인메모리 주문 저장소
_orders: Dict[str, dict] = {}

TOSS_SECRET_KEY = os.getenv("TOSS_SECRET_KEY", "test_gsk_docs_OaPz8L5KdmQXkzRz3y47BMw6")
TOSS_CLIENT_KEY = os.getenv("TOSS_CLIENT_KEY", "test_gck_docs_Ovk5rk1EwkEbP0W43n07xlzm")
CONFIRM_URL = "https://api.tosspayments.com/v1/payments/confirm"

PRICE = 1000  # 상세 풀이 가격 (원)


def create_order(order_id: str, amount: int, analysis_body: dict) -> dict:
    """주문 생성."""
    order = {
        "order_id": order_id,
        "amount": amount,
        "status": "PENDING",
        "analysis_body": analysis_body,
        "created_at": datetime.now().isoformat(),
    }
    _orders[order_id] = order
    return order


def get_order(order_id: str) -> Optional[dict]:
    """주문 조회."""
    return _orders.get(order_id)


async def confirm_payment(payment_key: str, order_id: str, amount: int) -> dict:
    """토스페이먼츠 결제 승인 API 호출."""
    order = _orders.get(order_id)
    if not order:
        return {"error": "주문을 찾을 수 없습니다."}
    if order["amount"] != amount:
        return {"error": "결제 금액이 일치하지 않습니다."}

    # Basic 인증: 시크릿키 + ":" → Base64
    auth = base64.b64encode(f"{TOSS_SECRET_KEY}:".encode()).decode()

    async with httpx.AsyncClient() as client:
        res = await client.post(
            CONFIRM_URL,
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
            },
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount,
            },
        )

    if res.status_code == 200:
        order["status"] = "PAID"
        order["payment_key"] = payment_key
        return {"success": True, "data": res.json()}
    else:
        return {"error": res.json().get("message", "결제 승인에 실패했습니다."), "code": res.json().get("code", "")}

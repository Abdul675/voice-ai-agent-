# backend/services/vapi.py

import httpx
from backend.config import settings


VAPI_BASE_URL = "https://api.vapi.ai"


async def trigger_outbound_call(
    phone_number: str,
    variables: dict,
) -> dict:
    """
    Triggers an outbound call via Vapi API.
    Returns the Vapi call object.
    """

    payload = {
        "assistantId": settings.VAPI_ASSISTANT_ID,
        "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": phone_number,
        },
        "assistantOverrides": {
            "variableValues": variables,
        },
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{VAPI_BASE_URL}/call",
            headers={
                "Authorization": f"Bearer {settings.VAPI_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=30.0,
        )

    if response.status_code not in (200, 201):
        raise Exception(
            f"Vapi API error {response.status_code}: {response.text}"
        )

    return response.json()
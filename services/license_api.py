import httpx

from config import API_KEY, API_URL


async def call_api(reg_number: str) -> list:
    params = {"key": API_KEY, "regNumber": reg_number}

    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(API_URL, params=params, timeout=10)

    if response.status_code != 200:
        return []

    return response.json().get("records") or []

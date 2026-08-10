import httpx

from config import API_KEY, API_URL


class LicenseApiError(Exception):
    pass


async def call_api(reg_number: str) -> list:
    params = {"key": API_KEY, "regNumber": reg_number}

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(API_URL, params=params, timeout=10)
    except httpx.HTTPError as e:
        raise LicenseApiError(str(e)) from e

    if response.status_code != 200:
        raise LicenseApiError(f"HTTP {response.status_code}")

    return response.json().get("records") or []

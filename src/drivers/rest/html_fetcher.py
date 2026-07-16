import httpx


async def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/137 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "Cache-Control": "no-cache",
    }

    async with httpx.AsyncClient(
        follow_redirects=True,
        headers=headers,
        timeout=30
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

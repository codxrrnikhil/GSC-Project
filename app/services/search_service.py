"""Search with SearchAPI.io, then crawl the top organic result URLs."""

import asyncio
import os
from typing import Any

import requests
from dotenv import load_dotenv

from app.services.crawler_service import CrawlerService

load_dotenv()

SEARCHAPI_ENDPOINT = "https://www.searchapi.io/api/v1/search"


def _require_api_key() -> str:
    key = os.getenv("SEARCHAPI_API_KEY")
    if not key:
        raise RuntimeError(
            "SEARCHAPI_API_KEY is not set. Add it to your environment or .env file."
        )
    return key


def _fetch_top_organic_results(query: str) -> list[dict[str, Any]]:
    response = requests.get(
        SEARCHAPI_ENDPOINT,
        params={
            "engine": "google",
            "q": query,
            "api_key": _require_api_key(),
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    organic = payload.get("organic_results") or []
    return list(organic[:10])


def _organic_urls(organic: list[dict[str, Any]]) -> list[str]:
    urls: list[str] = []
    for item in organic:
        link = item.get("link")
        if isinstance(link, str) and link.strip():
            urls.append(link.strip())
    return urls


async def search_and_crawl(query: str) -> list[dict]:
    if not isinstance(query, str) or not query.strip():
        raise ValueError("query must be a non-empty string.")

    organic = await asyncio.to_thread(_fetch_top_organic_results, query.strip())
    urls = _organic_urls(organic)

    crawler = CrawlerService()
    return await crawler.crawl(urls)

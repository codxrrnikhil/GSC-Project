import logging

import requests
from fastapi import APIRouter, HTTPException, status

from app.schemas.crawler import (
    CrawlRequest,
    CrawlResponse,
    SearchCrawlRequest,
    SearchCrawlResponse,
)
from app.services.crawler_service import CrawlerService
from app.services.search_service import search_and_crawl

logger = logging.getLogger(__name__)

router = APIRouter(tags=["crawler"])


@router.get("/crawler-health")
async def crawler_health():
    return {"status": "Crawler Ready"}


@router.post(
    "/crawl",
    response_model=CrawlResponse,
    responses={
        400: {"description": "Invalid input"},
        500: {"description": "Crawl failed"},
    },
)
async def crawl_urls(body: CrawlRequest):
    try:
        crawler = CrawlerService()
        results = await crawler.crawl(body.urls)
        return CrawlResponse(results=results)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("crawl failed for urls=%s", body.urls)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "code": "crawl_failed"},
        ) from e


@router.post(
    "/search-crawl",
    response_model=SearchCrawlResponse,
    responses={
        400: {"description": "Invalid query"},
        502: {"description": "Search API error"},
        503: {"description": "Search API not configured"},
        500: {"description": "Unexpected error"},
    },
)
async def search_crawl(body: SearchCrawlRequest):
    try:
        results = await search_and_crawl(body.query)
        return SearchCrawlResponse(results=results)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(e), "code": "invalid_query"},
        ) from e
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"error": str(e), "code": "searchapi_config"},
        ) from e
    except requests.RequestException as e:
        logger.exception("SearchAPI request failed for query=%s", body.query)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": str(e), "code": "searchapi_request"},
        ) from e
    except Exception as e:
        logger.exception("search-crawl failed for query=%s", body.query)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "code": "search_crawl_failed"},
        ) from e

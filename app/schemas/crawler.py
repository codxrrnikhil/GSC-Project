from typing import Any

from pydantic import BaseModel, Field


class CrawlRequest(BaseModel):
    urls: list[str] = Field(..., min_length=1)


class SearchCrawlRequest(BaseModel):
    query: str = Field(..., min_length=1)


class CrawlResponse(BaseModel):
    results: list[dict[str, Any]]


class SearchCrawlResponse(BaseModel):
    results: list[dict[str, Any]]

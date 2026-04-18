import requests
try:
    from scrapy.selector import Selector
except ImportError:  # pragma: no cover - optional dependency at runtime
    Selector = None


def crawl_static_page(url: str) -> dict:
    response = requests.get(url, timeout=20)
    response.raise_for_status()

    title = ""
    meta_description = ""
    if Selector is not None:
        selector = Selector(text=response.text)
        title = (selector.css("title::text").get() or "").strip()
        meta_description = (
            selector.css("meta[name='description']::attr(content)").get() or ""
        ).strip()

    return {
        "url": url,
        "status": "success",
        "title": title,
        "meta_description": meta_description,
        "html": response.text[:2000],
        "error": None,
    }


def crawl_static(urls: list[str]) -> list[dict]:
    results: list[dict] = []
    for url in urls:
        try:
            results.append(crawl_static_page(url))
        except Exception as exc:
            results.append(
                {
                    "url": url,
                    "status": "failed",
                    "title": None,
                    "meta_description": None,
                    "html": None,
                    "error": str(exc),
                }
            )
    return results

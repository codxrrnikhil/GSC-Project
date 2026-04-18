import asyncio

from playwright.async_api import async_playwright


class CrawlerService:
    _BLOCKED_RESOURCE_TYPES = frozenset({"image", "font", "media"})
    _CONTEXT_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    def __init__(self, max_concurrency: int = 3, timeout: int = 10000):
        self.max_concurrency = max_concurrency
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.browser = None
        self.playwright = None

    @staticmethod
    async def _block_heavy_resources(route):
        if route.request.resource_type in CrawlerService._BLOCKED_RESOURCE_TYPES:
            await route.abort()
        else:
            await route.continue_()

    async def init_browser(self):
        if self.browser is not None:
            return
        pw = await async_playwright().start()
        try:
            self.browser = await pw.chromium.launch(headless=True)
            self.playwright = pw
        except Exception:
            await pw.stop()
            raise

    async def close_browser(self):
        if self.browser is not None:
            try:
                await self.browser.close()
            finally:
                self.browser = None
        if self.playwright is not None:
            try:
                await self.playwright.stop()
            finally:
                self.playwright = None

    async def fetch_page(self, url: str):
        async with self.semaphore:
            if self.browser is None:
                return {
                    "url": url,
                    "status": "failed",
                    "html": None,
                    "title": None,
                    "meta_description": None,
                    "error": "Browser is not initialized. Call init_browser() first.",
                }

            last_error: BaseException | None = None
            for _ in range(2):
                context = None
                page = None
                try:
                    context = await self.browser.new_context(
                        user_agent=self._CONTEXT_USER_AGENT
                    )
                    page = await context.new_page()
                    await page.route("**/*", self._block_heavy_resources)
                    await page.goto(
                        url,
                        timeout=self.timeout,
                        wait_until="domcontentloaded",
                    )

                    html = await page.content()
                    title = await page.title()
                    meta = None
                    try:
                        meta = await page.locator(
                            "meta[name='description']"
                        ).get_attribute("content")
                    except Exception:
                        meta = None

                    meta_description = meta if meta is not None else ""
                    html_preview = (html or "")[:2000]

                    return {
                        "url": url,
                        "status": "success",
                        "html": html_preview,
                        "title": title,
                        "meta_description": meta_description,
                        "error": None,
                    }
                except Exception as e:
                    last_error = e
                finally:
                    if page is not None:
                        try:
                            await page.close()
                        except Exception:
                            pass
                    if context is not None:
                        try:
                            await context.close()
                        except Exception:
                            pass

            return self._failed_response(
                url,
                last_error if last_error is not None else "Unknown error after retries",
            )

    @staticmethod
    def _failed_response(url: str, error: BaseException | str) -> dict:
        message = str(error) if isinstance(error, BaseException) else error
        return {
            "url": url,
            "status": "failed",
            "html": None,
            "title": None,
            "meta_description": None,
            "error": message,
        }

    async def crawl(self, urls: list[str]) -> list[dict]:
        await self.init_browser()
        try:
            tasks = [asyncio.create_task(self.fetch_page(url)) for url in urls]
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)
            normalized: list[dict] = []
            for url, item in zip(urls, raw_results):
                if isinstance(item, BaseException):
                    normalized.append(self._failed_response(url, item))
                else:
                    normalized.append(item)
            return normalized
        finally:
            await self.close_browser()

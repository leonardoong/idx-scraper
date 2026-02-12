from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from config import PAGE_SIZE, MAYORITY_STAKEHOLDER_KEYWORD


def fetch_api(url: str, page: int):
    with Stealth().use_sync(sync_playwright()) as p:
        browser = p.chromium.launch(
            headless=False,     # CRITICAL
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36"
        )

        page.goto("https://idx.co.id", wait_until="domcontentloaded")
        print("WAITING FOR 2 SECONDS")
        page.wait_for_timeout(2000)

        response = page.request.get(
            url,
            params={
                "keywords": MAYORITY_STAKEHOLDER_KEYWORD,
                "indexFrom": page,
                "pageSize": PAGE_SIZE,
                "lang": "id"
            }
        )

        data = response.json()
        browser.close()
        return data

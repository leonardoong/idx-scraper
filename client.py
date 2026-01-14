import requests
import urllib.parse
from config import HEADERS, PAGE_SIZE, MAYORITY_STAKEHOLDER_KEYWORD

def fetch_api(url: str, page:int):
    params = {
        "keywords": MAYORITY_STAKEHOLDER_KEYWORD,
        "pageNumber": page,
        "pageSize": PAGE_SIZE,
        "lang": "id",
    }

    url = f"{url}?{urllib.parse.urlencode(params)}"
    print(f"Fetching page {page} from {url}")
    print(f"Fetching page headers {HEADERS}")
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    return resp.json()
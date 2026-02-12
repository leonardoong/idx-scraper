import hashlib
from client import fetch_api
from config import IDX_ANNOUNCEMENT_URL
from pdf import downloader, parser
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from config import PAGE_SIZE, MAYORITY_STAKEHOLDER_KEYWORD
from repositories.pdf_repo import PdfRepository
from repositories.stock_movement import StockMovementRepository


def sha256_file(input_string: str) -> str:
    """
    Generates a SHA-256 hash for the given input string.
    """
    encoded_string = input_string.encode('utf-8')
    hash_object = hashlib.sha256(encoded_string)
    hex_digest = hash_object.hexdigest()
    return hex_digest


def main():
    # scrape idx
    # data = fetch_api(IDX_ANNOUNCEMENT_URL, 0)
    # print("response data === ", json.dumps(data, indent=2, ensure_ascii=False))

    pdf_repo = PdfRepository()
    stock_repo = StockMovementRepository()

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
            IDX_ANNOUNCEMENT_URL,
            params={
                "keywords": MAYORITY_STAKEHOLDER_KEYWORD,
                "indexFrom": page,
                "pageSize": PAGE_SIZE,
                "lang": "id"
            }
        )

        data = response.json()
        for item in data.get("Items", []):
            itemID = item.get("Id")
            print(f"Processing item ID: {itemID}")
            for attach in item.get("Attachments", []):
                if attach.get("IsAttachment") == 1:
                    url = attach.get("FullSavePath")
                    sha_url = sha256_file(url)
                    print(
                        f"Found attachment URL for item {itemID}: {url} & sha256: {sha_url}")
                    if not pdf_repo.pdf_exists(sha_url):
                        print(f"Downloading and parsing PDF for item {itemID}")
                        file_path = downloader.download_pdf_via_browser(
                            page, url)
                        print(f"Downloaded PDF to: {file_path}")

                        # # Save PDF record
                        publish_date = item.get("PublishDate")
                        file_name = file_path.split("/")[-1]
                        print(
                            f"Saving PDF record for URL: {url} {file_name} {publish_date}")
                        pdf_repo.insert_pdf(
                            url, file_name, file_path, sha_url, publish_date)

        browser.close()

    # Save stock movement records
    file_paths = pdf_repo.get_all_unparsed_pdf_paths()
    for pdf_id, file_path in file_paths:
        print(f"Parsing PDF file: {pdf_id} {file_path}")
        results = parser.parse_ownership_pdf(file_path)

        for _, groups in results["moving_stocks"].items():
            for owners in groups:
                for row in owners:
                    stock_repo.save_stock_movements(pdf_id, row)

        for _, groups in results["moving_owner_perc"].items():
            for owners in groups:
                for row in owners:
                    stock_repo.save_stock_movements_owner(pdf_id, row)


if __name__ == "__main__":
    main()

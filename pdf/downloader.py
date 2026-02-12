import os
from config import PDF_SAVE_PATH


def download_pdf_via_browser(page, pdf_url):
    os.makedirs(PDF_SAVE_PATH, exist_ok=True)

    filename = os.path.basename(pdf_url)
    local_path = os.path.join(PDF_SAVE_PATH, filename)

    if os.path.exists(local_path):
        return local_path

    cookies = page.context.cookies()
    cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

    headers = {
        "User-Agent": page.evaluate("() => navigator.userAgent"),
        "Accept": "application/pdf,*/*",
        "Referer": "https://www.idx.co.id/",
        "Cookie": cookie_header
    }

    r = page.request.get(pdf_url, headers=headers, timeout=30_000)
    if not r.ok:
        raise Exception(f"Download failed {r.status}: {pdf_url}")

    with open(local_path, "wb") as f:
        f.write(r.body())

    print("Saved:", local_path)
    return local_path

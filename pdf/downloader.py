import os
import requests
from config import PDF_SAVE_PATH

def download_pdf(url):
    os.makedirs(PDF_SAVE_PATH, exist_ok=True)
    filename = os.path.basename(url)
    local_path = os.path.join(PDF_SAVE_PATH, filename)

    if not os.path.exists(local_path):
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)

    return local_path
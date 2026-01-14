import os

IDX_ANNOUNCEMENT_URL = "https://www.idx.co.id/primary/NewsAnnouncement/GetAllAnnouncement"
MAYORITY_STAKEHOLDER_KEYWORD = "Pemegang Saham di atas 5%"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
    "Referer": "https://www.idx.co.id/id/berita/pengumuman/",
}

PAGE_SIZE = 10
PDF_SAVE_PATH = "./data/pdfs"

# polling & timing
POLL_INTERVAL = 3600  # 1 hour

# DB
DATABASE_URL = "postgresql://psql:psql@localhost:5432/idx"

from client import fetch_api
from pdf.downloader import download_pdf
from pdf.parser import parse_ownership_pdf
from repository import OwnershipRepository
from config import IDX_ANNOUNCEMENT_URL
# from notifier.whatsapp import send_message

def process_page(page):
    data = fetch_api(IDX_ANNOUNCEMENT_URL, page)
    announcements = data.get("Items", [])

    for item in announcements:
        ann_id = item["Id"]
        repo = OwnershipRepository()

        if repo.announcement_exists(ann_id):
            continue

        publish_date = item.get("PublishDate")
        title = item.get("Title", "").strip()

        for attach in item.get("PdfPath") or []:
            url = attach.get("FullSavePath")
            if not url:
                continue

            file_path = download_pdf(url)
            records = parse_ownership_pdf(file_path)

            # save
            repo.save_announcement(ann_id, publish_date, title, file_path)
            repo.save_ownership_records(records)

            # notify
            # send_message(f"New ownership: {title} - {file_path}")

    return data["PageCount"]
from .base import BaseRepository


class PdfRepository(BaseRepository):

    def pdf_exists(self, pdf_url):
        sql = """
        SELECT 1 FROM pdf_files WHERE sha256 = %s
        """
        return self.execute(sql, (pdf_url,), fetchone=True)

    def insert_pdf(self, pdf_url, file_name, file_path, sha256, publish_date):
        sql = """
        INSERT INTO pdf_files (pdf_url, file_name, file_path, sha256, publish_date, downloaded_at)
        VALUES (%s, %s, %s, %s, %s, now())
        RETURNING id
        """
        return self.execute(sql, (pdf_url, file_name, file_path, sha256, publish_date))

    def get_all_unparsed_pdf_paths(self):
        sql = """
        SELECT id, file_path
        FROM pdf_files
        WHERE parsed = false
        ORDER BY publish_date DESC
        """
        return self.execute(sql, fetchall=True)

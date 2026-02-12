from .base import BaseRepository
import re
from decimal import Decimal


def parse_bigint(val):
    """
    Converts '3,200,142,830' → 3200142830
    Converts '' or None → None
    """
    if not val:
        return None

    # remove commas, spaces, non-numeric except minus
    clean = re.sub(r"[^\d\-]", "", val)

    if clean == "" or clean == "-":
        return None

    return int(clean)


def parse_numeric(val):
    """
    Converts '41.10' → Decimal('41.10')
    Converts '0' → Decimal('0')
    """
    if not val:
        return None

    clean = val.replace(",", "").strip()

    try:
        return Decimal(clean)
    except:
        return None


class StockMovementRepository(BaseRepository):

    def save_stock_movements(self, pdf_id, row):
        sql = """
        INSERT INTO idx_stock_movement (
            pdf_id,
            kode_saham,
            nama_emiten,
            nama_pemegang_rekening_efek,
            pemegang_saham,
            jumlah_sebelum,
            jumlah_sesudah,
            perubahan,
            persen_sebelum,
            persen_sesudah,
            type
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'stock_movement')
        """
        print(f"Executing SQL for row: {row}")
        self.execute(sql, (
            pdf_id,
            row["kode_saham"],
            row["nama_emiten"],
            row["nama_pemegang_rekening_efek"],
            row["nama_pemegang_saham"],
            parse_bigint(row["jumlah_saham_sebelum"]),
            parse_bigint(row["jumlah_saham_sesudah"]),
            parse_bigint(row["perubahan"]),
            parse_numeric(row["persentase_kepemilikan_sebelum"]),
            parse_numeric(row["persentase_kepemilikan_sesudah"]),
        ))

    def save_stock_movements_owner(self, pdf_id, row):
        sql = """
        INSERT INTO idx_stock_movement (
            pdf_id,
            kode_saham,
            nama_emiten,
            nama_pemegang_rekening_efek,
            pemegang_saham,
            perubahan,
            persen_sebelum,
            persen_sesudah,
            type
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,'owner_percentage')
        """

        self.execute(sql, (
            pdf_id,
            row["kode_saham"],
            row["nama_emiten"],
            row["nama_pemegang_rekening_efek"],
            row["nama_pemegang_saham"],
            parse_bigint(row["perubahan"]),
            parse_numeric(row["persentase_kepemilikan_sebelum"]),
            parse_numeric(row["persentase_kepemilikan_sesudah"]),
        ))

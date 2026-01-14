import pdfplumber
import os
from collections import defaultdict

COLUMNS = {
    "kode_saham" : (30, 42),
    "nama_emiten" : (42, 110),
    "nama_pemegang_rekening_efek" : (110, 182),
    "nama_pemegang_saham" : (183, 256),
    "nama_rekening_efek" : (256, 329),
    "status": (544,546),
    "jumlah_saham_sebelum": (547,575),
    "saham_gabungan_sebelum" : (575,609),
    "persentase_kepemilikan_sebelum" : (645,654),
    "jumlah_saham_sesudah" : (654, 673),
    "saham_gabungan_sesudah" : (673, 706),
    "persentase_kepemilikan_sesudah" : (706, 751),
    "perubahan":(751, 768),
}

def parse_ownership_pdf(folder: str):
    """
    Extract ownership >5% info from PDF.
    This is a stub you can implement with pdfplumber.
    """
    results = defaultdict(list)

    for pdf_path in scan_pdf_folder(folder):
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.page_number != 10:
                    continue
                moving_stocks = parse_page(page)
                results = results | moving_stocks

    return results

def group_chars_by_line(chars, y_tolerance=3):
    lines = defaultdict(list)

    for ch in chars:
        key = round(ch["top"] / y_tolerance) * y_tolerance
        lines[key].append(ch)

    return lines

def is_blue(color) -> bool:
    """
    color example:
    (0, 0, 1)
    (0.0, 0.24, 0.72)
    """
    if not color or not isinstance(color, (list, tuple)):
        return False

    r, g, b = color
    return b > 0.6 and r < 0.4 and g < 0.4

def scan_pdf_folder(folder: str):
    res = [
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.lower().endswith(".pdf")
    ]
    print(res)
    return res

def slice_row(row_chars):
    result = {k: "" for k in COLUMNS}

    for c in row_chars:
        for col, (xmin, xmax) in COLUMNS.items():
            if xmin <= c["x0"] < xmax:
                result[col] += c["text"]
                break

    return {k: v.strip() for k, v in result.items()}

def stock_group_by_name_and_owner(stock_name: str, stock_owner: str):
    return stock_name + "_" + stock_owner

def stock_group_name(s : str):
    return s.split("_")[0]

def parse_page(page):
    tables = page.extract_tables()
    for table in tables:
        print(table)


    moving_stocks = defaultdict(list)
    # store moving stocks group by stock name and owner
    moving_stocks_key = set()
    stock_owner_group = defaultdict(list)

    chars = page.chars
    lines = group_chars_by_line(chars)

    line_no = 1
    for k, line_chars in lines.items():
        if k <= 30:
            continue
        line_chars.sort(key=lambda c: c["x0"])

        result = slice_row(line_chars)
        if not result.get('kode_saham'):
            print(result)
            continue
        key = stock_group_by_name_and_owner(result.get('kode_saham'), result.get('nama_pemegang_saham'))
        stock_owner_group[key].append(result)

        if result.get('perubahan') != '0':
            moving_stocks_key.add(key)
        elif result.get('persentase_kepemilikan_sebelum') != result.get('persentase_kepemilikan_sesudah'):
            moving_stocks_key.add(key)

        line_no += 1

    for msk in moving_stocks_key:
        # print(f"{msk}")
        moving_stocks[stock_group_name(msk)].append(stock_owner_group[msk])
    return moving_stocks

def compact_char(c):
    return {
        "text": c.get("text"),
        "x0": round(c.get("x0", 0), 2),
        "x1": round(c.get("x1", 0), 2),
        "top": round(c.get("top", 0), 2),
        "bottom": round(c.get("bottom", 0), 2),
    }

import pdfplumber
from pathlib import Path
from collections import defaultdict

COLUMNS = {
    "kode_saham": (30, 42),
    "nama_emiten": (42, 110),
    "nama_pemegang_rekening_efek": (110, 182),
    "nama_pemegang_saham": (183, 256),
    "nama_rekening_efek": (256, 329),
    "status": (544, 546),
    "jumlah_saham_sebelum": (547, 575),
    "saham_gabungan_sebelum": (575, 609),
    "persentase_kepemilikan_sebelum": (645, 654),
    "jumlah_saham_sesudah": (654, 673),
    "saham_gabungan_sesudah": (673, 706),
    "persentase_kepemilikan_sesudah": (706, 751),
    "perubahan": (751, 768),
}


def parse_ownership_pdf(file_path: str):
    """
    Extract ownership >5% info from PDF.
    This is a stub you can implement with pdfplumber.
    """
    results = {
        "moving_stocks": defaultdict(list),
        "moving_owner_perc": defaultdict(list),
    }

    # for pdf_path in scan_pdf_folder(folder):
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            if page.page_number == 1:
                continue
            page_result = parse_page(page)

            for stock, rows in page_result["moving_stocks"].items():
                results["moving_stocks"][stock].extend(rows)

            for stock, rows in page_result["moving_owner_perc"].items():
                results["moving_owner_perc"][stock].extend(rows)

    print_results(results)
    return results


def print_results(results):
    print("\n📈 MOVING STOCKS")
    for stock, groups in results["moving_stocks"].items():
        print(f"\n{stock}")
        for owners in groups:
            for row in owners:
                print(
                    f"  {row['nama_rekening_efek']}  {row['jumlah_saham_sebelum']} → {row['jumlah_saham_sesudah']} "
                    f"(Δ {row['perubahan']})"
                )

    print("\n📊 OWNER % CHANGES")
    for stock, groups in results["moving_owner_perc"].items():
        print(f"\n{stock.split('_')[0]}")
        for owners in groups:
            for row in owners:
                print(
                    f"{row['nama_rekening_efek']}  {row['persentase_kepemilikan_sebelum']}% → "
                    f"{row['persentase_kepemilikan_sesudah']}%"
                )


def group_chars_by_line(chars, y_tolerance=3):
    lines = defaultdict(list)

    for ch in chars:
        key = round(ch["top"] / y_tolerance) * y_tolerance
        lines[key].append(ch)

    return lines


def scan_pdf_folder(folder: str):
    folder_path = Path(folder)
    res = list(folder_path.glob("*.pdf"))
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


def stock_group_by_name_and_owner(*parts):
    return "_".join(
        str(p).strip()
        for p in parts
        if p is not None and str(p).strip() != ""
    )


def stock_group_name(s: str):
    return s.split("_")[0]


def parse_page(page):
    # tables = page.extract_tables()

    moving_stocks = defaultdict(list)
    moving_owner_perc = defaultdict(list)
    # store moving stocks group by stock name and owner
    moving_stocks_key = set()
    moving_owner_perc_key = set()
    stock_owner_group = defaultdict(list)
    stock_owner_perc_group = defaultdict(list)

    chars = page.chars
    lines = group_chars_by_line(chars)

    line_no = 1
    for k, line_chars in lines.items():
        if k <= 30:
            continue
        line_chars.sort(key=lambda c: c["x0"])

        result = slice_row(line_chars)

        if not result.get('kode_saham'):
            continue
        elif result.get('kode_saham').__len__() != 4:
            continue
        elif not result.get('perubahan'):
            continue

        key = stock_group_by_name_and_owner(result.get(
            'kode_saham'), result.get('nama_rekening_efek'))
        owner_perc_key = stock_group_by_name_and_owner(result.get(
            'kode_saham'), result.get('nama_rekening_efek'), result.get('nama_pemegang_rekening_efek'))

        stock_owner_group[key].append(result)

        if result.get('perubahan') != '0':
            moving_stocks_key.add(key)
        elif result.get('persentase_kepemilikan_sebelum') != result.get('persentase_kepemilikan_sesudah'):
            moving_owner_perc_key.add(owner_perc_key)
            stock_owner_perc_group[owner_perc_key].append(result)

        line_no += 1

    for msk in moving_stocks_key:
        moving_stocks[stock_group_name(msk)].append(stock_owner_group[msk])

    for mopk in moving_owner_perc_key:
        moving_owner_perc[mopk].append(
            stock_owner_perc_group[mopk])
    return {
        "moving_stocks": moving_stocks,
        "moving_owner_perc": moving_owner_perc
    }


def compact_char(c):
    return {
        "text": c.get("text"),
        "x0": round(c.get("x0", 0), 2),
        "x1": round(c.get("x1", 0), 2),
        "top": round(c.get("top", 0), 2),
        "bottom": round(c.get("bottom", 0), 2),
    }

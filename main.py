from scraper import process_page
from pdf import parser

def main():
    res = parser.parse_ownership_pdf('./files')
    # print(res)


    # page = 1
    # while True:
    #     total_pages = process_page(page)
    #     if page >= total_pages:
    #         break
    #     page += 1

if __name__ == "__main__":
    main()
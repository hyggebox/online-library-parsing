import argparse
import os
import urllib3
import requests

from bs4 import BeautifulSoup

from helpers import (check_for_redirect, download_book,
                     download_cover, parse_book_page)


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser(
        description="Скрипт скачивает книги с сайта tululu.org"
    )
    parser.add_argument("start_id", help="Начальный id",
                        type=int, nargs="?", default=1)
    parser.add_argument("end_id", help="Конечный id",
                        type=int, nargs="?", default=10)

    args = parser.parse_args()

    books_dir_name = "books"
    img_dir_name = "images"
    os.makedirs(books_dir_name, exist_ok=True)
    os.makedirs(img_dir_name, exist_ok=True)

    for book_id in range(args.start_id, args.end_id+1):
        book_url = f"https://tululu.org/b{book_id}"
        try:
            bs4_response = requests.get(book_url)
            bs4_response.raise_for_status()
            check_for_redirect(bs4_response)
            soup = BeautifulSoup(bs4_response.text, "lxml")

            parsed_book = parse_book_page(soup, book_url)
            download_book(book_id, books_dir_name, parsed_book["title"])
            book_cover = parsed_book["cover_url"]
            if book_cover:
                download_cover(book_cover, img_dir_name)
        except requests.HTTPError:
            pass
        except requests.exceptions.ConnectionError as error:
            print(error)

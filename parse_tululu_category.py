import argparse
import json
import os
import urllib3
import re

import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from helpers import (check_for_redirect, create_description,download_book,
                     download_cover, parse_book_page)


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    category_url = "http://tululu.org/l55/"
    endpoint = "https://tululu.org"
    num_pages = 4

    bs4_response = requests.get(category_url)
    bs4_response.raise_for_status()
    soup = BeautifulSoup(bs4_response.text, "lxml")
    last_page = int(soup.select_one(".center .npage:last-child").text) + 1

    parser = argparse.ArgumentParser(
        description='Скрипт скачивает книги с сайта tululu.org'
    )
    parser.add_argument("--start_page", help='Скачивать начиная со стр.',
                        type=int, default=1)
    parser.add_argument("--end_page", help='Скачивать до стр. (не включая)',
                        type=int, default=last_page)
    args = parser.parse_args()

    books_description = {}
    for page in range(args.start_page-1, args.end_page-1):
        books_dir_name = "books"
        img_dir_name = "images"
        os.makedirs(books_dir_name, exist_ok=True)
        os.makedirs(img_dir_name, exist_ok=True)

        bs4_response = requests.get(urljoin(category_url, str(page+1)))
        bs4_response.raise_for_status()
        soup = BeautifulSoup(bs4_response.text, "lxml")

        book_cards = soup.select(".d_book .bookimage a")
        for book_card in book_cards:
            book_path = book_card["href"]
            book_url = urljoin(endpoint, book_path)
            book_id = re.sub("[^0-9]", "", book_path)

            try:
                bs4_response = requests.get(book_url)
                bs4_response.raise_for_status()
                check_for_redirect(bs4_response)
                soup = BeautifulSoup(bs4_response.text, "lxml")

                parsed_book = parse_book_page(soup, book_url)
                book_path = download_book(book_id, books_dir_name,
                                          parsed_book["title"])
                book_cover = parsed_book["cover_url"]
                if book_cover:
                    img_path = download_cover(book_cover, img_dir_name)
                books_description[book_id] = create_description(parsed_book,
                                                                img_path,
                                                                book_path)
            except requests.HTTPError:
                pass
            except requests.exceptions.ConnectionError as error:
                print(error)

    with open("books_description.json", "w", encoding="utf8") as file:
        json.dump(books_description, file, ensure_ascii=False, indent=4)


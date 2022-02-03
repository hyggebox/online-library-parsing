import argparse
import io
import json
import os
import re
import urllib3
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from helpers import (check_for_redirect, create_description,download_book,
                     download_cover, parse_book_page)


def get_last_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")
    last_page = int(soup.select_one(".center .npage:last-child").text) + 1
    return last_page


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    category_url = "http://tululu.org/l55/"
    endpoint = "https://tululu.org"
    last_page = get_last_page(category_url)

    parser = argparse.ArgumentParser(
        description="Скрипт скачивает книги с сайта tululu.org"
    )
    parser.add_argument("-s", "--start_page", help="Скачивать начиная со стр.",
                        type=int, default=1)
    parser.add_argument("-e", "--end_page", help="Скачивать до стр. (не включая)",
                        type=int, default=last_page)
    parser.add_argument("--skip_imgs", action="store_true",
                        help="Не скачивать картинки")
    parser.add_argument("--skip_txt", action="store_true",
                        help="Не скачивать книги")
    parser.add_argument("-d", "--dest_folder", default="",
                        help="Путь к каталогу с результатами парсинга")
    parser.add_argument("-j", "--json_path", default="",
                        help="Путь к *.json файлу с результатами")
    args = parser.parse_args()

    dest_folder = args.dest_folder
    books_dir_path = os.path.join(dest_folder, "books")
    img_dir_path = os.path.join(dest_folder, "images")

    os.makedirs(books_dir_path, exist_ok=True)
    os.makedirs(img_dir_path, exist_ok=True)

    books_description = {}
    for page in range(args.start_page-1, args.end_page-1):
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
                book_path = download_book(book_id, books_dir_path,
                                          parsed_book["title"]) if not args.skip_txt else None
                book_cover = parsed_book["cover_url"]
                img_path = download_cover(book_cover,
                                          img_dir_path) if book_cover and not args.skip_imgs else None
                books_description[book_id] = create_description(parsed_book,
                                                                img_path,
                                                                book_path)
            except requests.HTTPError:
                pass
            except requests.exceptions.ConnectionError as error:
                print(error)

    json_path = os.path.join(args.json_path or dest_folder, "description.json")

    if os.path.isfile(json_path):
        with io.open(json_path, encoding="utf-8") as file:
            existing_description = json.load(file)
        books_description.update(existing_description)

    with open(json_path, "w", encoding="utf8") as file:
        json.dump(books_description, file, ensure_ascii=False, indent=4)


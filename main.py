import requests

import argparse
import os
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


def check_for_redirect(response):
    for resp in response.history:
        if resp.status_code == 302:
            raise requests.HTTPError


def download_book(book_id, dir_name, book_title):
    endpoint = "https://tululu.org/txt.php"
    payload = {"id": book_id}
    response = requests.get(endpoint, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    filename = "{}.{}.txt".format(book_id, book_title)
    safe_filename = sanitize_filename(filename)
    with open(os.path.join(dir_name, safe_filename), "wt", encoding='utf-8') as file:
        file.write(response.text)


def parse_book_page(soup, book_url):
    book_h1 = soup.select_one("#content h1").text
    book_title, book_author = book_h1.split("::")
    cover_src = soup.select_one(".bookimage img")
    img_url = urljoin(book_url, cover_src["src"]) if cover_src else None
    comments = soup.select(".texts .black")
    genres = soup.select(".d_book > a")
    return {
        "book_title": book_title.strip(),
        "cover_url": img_url,
        "comments": [comment.text for comment in comments],
        "genres": [genre.text for genre in genres]
    }


def download_cover(url, dir_name):
    response = requests.get(url)
    response.raise_for_status()
    img_name = urlsplit(unquote(url)).path.split("/")[-1]
    with open(os.path.join(dir_name, img_name), "wb") as file:
        file.write(response.content)


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    parser = argparse.ArgumentParser(
        description='Скрипт скачивает книги с сайта tululu.org'
    )
    parser.add_argument("start_id", help='Начальный id',
                        type=int, nargs='?', default=1)
    parser.add_argument("end_id", help='Конечный id',
                        type=int, nargs='?', default=10)
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
            soup = BeautifulSoup(bs4_response.text, 'lxml')

            parsed_book = parse_book_page(soup, book_url)
            download_book(book_id, books_dir_name, parsed_book['book_title'])
            download_cover(parsed_book['cover_url'], img_dir_name)
        except requests.HTTPError:
            pass
        except requests.exceptions.ConnectionError as error:
            print(error)
        except requests.exceptions.MissingSchema:
            pass

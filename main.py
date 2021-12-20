import requests

import argparse
import os
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_book(book_id, dir_name):
    endpoint = "https://tululu.org/txt.php"
    payload = {"id": book_id}
    response = requests.get(endpoint, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    book_url = f"https://tululu.org/b{book_id}"
    bs4_response = requests.get(book_url)
    bs4_response.raise_for_status()
    check_for_redirect(bs4_response)
    soup = BeautifulSoup(bs4_response.text, 'lxml')
    parsed_book = parse_book_page(soup, book_url)

    download_cover(parsed_book['cover_url'], img_dir_name)

    filename = "{}.{}.txt".format(book_id, parsed_book['book_title'])
    safe_filename = sanitize_filename(filename)
    with open(os.path.join(dir_name, safe_filename), "wt", encoding='utf-8') as file:
        file.write(response.text)
    return parsed_book


def parse_book_page(soup, book_url):
    return {
        "book_title": get_book_title(soup),
        "cover_url": get_book_covers(book_url, soup),
        "comments": fetch_comments(soup),
        "genres": fetch_genres(soup)
    }


def download_cover(url, dir_name):
    response = requests.get(url)
    response.raise_for_status()
    img_name = urlsplit(unquote(url)).path.split("/")[-1]
    with open(os.path.join(dir_name, img_name), "wb") as file:
        file.write(response.content)


def fetch_comments(soup):
    comments = soup.select(".texts .black")
    return [comment.text for comment in comments]


def fetch_genres(soup):
    genres = soup.select(".d_book > a")
    return [genre.text for genre in genres]


def get_book_title(soup):
    book_h1 = soup.select_one("#content h1").text
    book_title, book_author = book_h1.split("::")
    return book_title.strip()


def get_book_covers(book_url, soup):
    cover_src = soup.select_one(".bookimage img")
    if cover_src:
        img_url = urljoin(book_url, cover_src["src"])
        return img_url


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
        try:
            download_book(book_id, books_dir_name)
        except requests.HTTPError:
            pass
        except requests.exceptions.ConnectionError as error:
            print(error)

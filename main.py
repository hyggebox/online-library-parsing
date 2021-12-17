import requests

import os
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit, unquote


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_book(book_id, dir_name='books'):
    endpoint = "https://tululu.org/txt.php"
    payload = {"id": book_id}
    response = requests.get(endpoint, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    book_url = f"https://tululu.org/b{book_id}"
    bs4_response = requests.get(book_url)
    soup = BeautifulSoup(bs4_response.text, 'lxml')

    book_title = get_book_title(soup)
    cover_url = get_book_covers(book_url, soup)

    download_cover(cover_url)

    filename = "{}.{}.txt".format(book_id, book_title)
    safe_filename = sanitize_filename(filename)
    with open(os.path.join(dir_name, safe_filename), "wt") as file:
        file.write(response.text)


def download_cover(url, dir_name='images'):
    response = requests.get(url)
    img_name = unquote(str(urlsplit(url).path.split("/")[-1]))
    with open(os.path.join(dir_name, img_name), "wb") as file:
        file.write(response.content)


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
    books_dir_name = "books"
    img_dir_name = "images"
    os.makedirs(books_dir_name, exist_ok=True)
    os.makedirs(img_dir_name, exist_ok=True)

    for book_id in range(11):
        try:
            download_book(book_id, dir_name=books_dir_name)
        except requests.HTTPError:
            pass
        except requests.exceptions.ConnectionError as error:
            print(error)

import os

import requests

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
    book_path = os.path.join(dir_name, safe_filename)
    with open(book_path, "wt", encoding='utf-8') as file:
        file.write(response.text)
    return safe_filename


def download_cover(url, dir_name):
    response = requests.get(url)
    response.raise_for_status()
    img_name = urlsplit(unquote(url)).path.split("/")[-1]
    img_path = os.path.join(dir_name, img_name)
    with open(img_path, "wb") as file:
        file.write(response.content)
    return img_name


def parse_book_page(soup, book_url):
    book_h1 = soup.select_one("#content h1").text
    book_title, book_author = book_h1.split("::")
    cover_src = soup.select_one(".bookimage img")
    img_url = urljoin(book_url, cover_src["src"]) if cover_src else None
    comments = soup.select(".texts .black")
    genres = soup.select(".d_book > a")
    return {
        "title": book_title.strip(),
        "author": book_author.strip(),
        "cover_url": img_url,
        "comments": [comment.text for comment in comments],
        "genres": [genre.text for genre in genres]
    }

import requests

import os
import urllib3

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(book_id, folder='books'):
    endpoint = "https://tululu.org/txt.php"
    payload = {
        "id": book_id
    }
    response = requests.get(endpoint, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)

    book_url = f"https://tululu.org/b{book_id}"
    book_title = get_book_title(book_url)
    filename = "{}.{}.txt".format(book_id, book_title)
    safe_filename = sanitize_filename(filename)
    with open(os.path.join(folder, safe_filename), "wt") as file:
        file.write(response.text)


def get_book_title(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    book_h1 = soup.select_one("#content h1").text
    book_title, book_author = book_h1.split("::")
    return book_title.strip()


if __name__ == "__main__":
    dir_name = "books"
    os.makedirs(dir_name, exist_ok=True)

    for book_id in range(11):
        try:
            download_txt(book_id, folder=dir_name)
        except requests.HTTPError:
            pass
        except requests.exceptions.ConnectionError as error:
            print(error)

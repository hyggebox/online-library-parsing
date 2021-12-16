import requests

import os
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


if __name__ == "__main__":
    dir_name = "books"
    os.makedirs(dir_name, exist_ok=True)

    for book_id in range(1, 11):
        endpoint = "https://tululu.org/txt.php"
        payload = {
            "id": book_id
        }
        filename = f"book_{book_id}.txt"
        response = requests.get(endpoint, params=payload, verify=False)
        response.raise_for_status()
        with open(os.path.join(dir_name, filename), "wt") as file:
            file.write(response.text)

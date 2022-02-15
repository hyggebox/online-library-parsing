import io
import json
import os

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell
from more_itertools import chunked


def reload_site():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")

    with io.open("description.json", encoding="utf-8") as file:
        books_description = json.load(file)

    books_ids = [book_id for book_id, book_description in books_description.items()]
    books_groups = list(chunked(books_ids, 20))

    for page_num in range(len(books_groups)):
        books_group = books_groups[page_num]
        books = {book_id: books_description[book_id] for book_id in books_group}
        rendered_page = template.render(
            books=books,
        )

        with open(os.path.join("pages", f"index{page_num}.html"), "w",
                  encoding="utf8") as file:
            file.write(rendered_page)


def main():
    os.makedirs("pages", exist_ok=True)
    reload_site()
    server = Server()
    server.watch("template.html", reload_site)
    server.serve(default_filename="pages/index0.html")


if __name__ == "__main__":
    main()



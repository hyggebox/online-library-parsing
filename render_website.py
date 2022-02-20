import argparse
import io
import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def reload_site(args):
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")

    json_path = os.path.join(args.json_path, "description.json")
    with io.open(json_path, encoding="utf-8") as file:
        books_description = json.load(file)

    books_per_page = 20
    books_ids = [book_id for book_id, book_description in books_description.items()]
    books_groups = list(chunked(books_ids, books_per_page))
    pages_num = len(books_groups)

    for page_num in range(pages_num):
        books_group = books_groups[page_num]
        books = {book_id: books_description[book_id] for book_id in books_group}
        rendered_page = template.render(
            books=books,
            pages_num=pages_num,
            current_page=page_num
        )
        with open(os.path.join("pages", f"index{page_num}.html"), "w",
                  encoding="utf8") as file:
            file.write(rendered_page)


def get_args():
    parser = argparse.ArgumentParser(
        description="Сайт с библиотекой книг"
    )
    parser.add_argument("-j", "--json_path", default="",
                        help="Путь к *.json файлу с результатами парсинга")
    return parser.parse_args()


def main():
    args = get_args()
    os.makedirs("pages", exist_ok=True)
    reload_site(args)
    server = Server()
    server.watch("template.html", lambda: reload_site(args))
    server.serve(default_filename="pages/index0.html")


if __name__ == "__main__":
    main()



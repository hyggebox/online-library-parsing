import io
import json

from http.server import HTTPServer, SimpleHTTPRequestHandler
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell


def reload_site():
    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")

    with io.open("description.json", encoding="utf-8") as file:
        books_description = json.load(file)

    rendered_page = template.render(
        books=books_description,
    )
    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)


reload_site()
server = Server()
server.watch('template.html', reload_site)
server.serve(root='.')



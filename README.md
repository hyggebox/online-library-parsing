# Парсер книг с сайта tululu.org

Скрипт парсит и скачивает электронные книги с обложками и названиями 
с сайта [tululu.org](https://tululu.org/). 

- Книги скачиваются в формате .txt в папку `texts/` 
- Обложки книг -- в папку `images/`
- Описание книг сохраняется в файл `description.json` в следующем виде:

```json
{
  "18944": {
    "title": "90х60х90",
    "author": "Берендеев Кирилл",
    "img_src": "images\\nopic.gif",
    "book_path": "books\\18944.90х60х90.txt",
    "comments": [
      "Ни фантастики, ни фэнтези, обычный детектив..."
    ],
    "genres": [
      "Научная фантастика"
    ]
  }
}
```

## Установка

- Скачайте код из репозитория
- Python3 должен быть уже установлен. Используйте `pip` (или `pip3`, если есть 
конфликт с Python2) для установки зависимостей:

```shell
pip install -r requirements.txt
```

## Скачать книги по id

- Запустите скрипт командой `python` (`python3`, если есть конфликт с Python2):

```shell
python main.py
```

- По умолчанию скачиваются книги с первыми 10 id (при наличии книги на сайте).
Задайте собственный диапазон id книг для парсинга при запуске скрипта. 
Например, чтобы скачать книги c id с 100 по 150:
```shell
python main.py 100 150
```

## Скачать книги из категории "Научная фантастика"
Скрипт скачивает книги из раздела [Научная фантастика](http://tululu.org/l55/).

Скрипт запускается командой:

```shell
python parse_tululu_category.py
```

По умолчанию скачиваются все книги из категории. Доступны следующие опциональные аргументы:
- `-s/--start_page` — номер страницы, с которой начать скачивание книг
- `-e/--end_page` — по какую страницу скачивать книги (исключая данную страницу)
- `-d/--dest_folder` — путь к каталогу с результатами парсинга: картинкам, книгам, JSON.
- `--skip_imgs` — не скачивать картинки
- `--skip_txt` — не скачивать книги
- `-j/--json_path` — указать свой путь к *.json файлу с результатами

Например:
```shell
python parse_tululu_category.py -s 10 -e 25 --skip_imgs -d books
```

## Запустить сайт со скачанными книгами
Запустите сайт командой:
```shell
python render_website.py
```
Если для *.json файла с результатами парсинга вы указывали свой путь, 
укажите его также при запуске скрипта:
```shell
python render_website.py results
```


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на 
сайте [Devman](https://dvmn.org).
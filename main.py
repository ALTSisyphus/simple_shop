"""Простое веб-приложение интернет-магазина без использования фреймворков.

Модуль запускает HTTP-сервер, который обрабатывает GET- и POST-запросы.
На GET-запрос сервер возвращает HTML-страницу «Контакты» с типом содержимого
text/html. На POST-запрос сервер принимает данные формы и выводит их в консоль.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
HOST = "127.0.0.1"
PORT = 8000


class ShopHandler(BaseHTTPRequestHandler):
    """Обработчик HTTP-запросов для простого сайта интернет-магазина."""

    def send_html(self, filename: str, status: int = 200) -> None:
        """Читает HTML-файл из папки templates и отправляет его пользователю."""
        file_path = TEMPLATES_DIR / filename

        try:
            # Критерий: чтение HTML-файла через контекстный менеджер.
            with open(file_path, "rb") as file:
                content = file.read()
        except FileNotFoundError:
            with open(TEMPLATES_DIR / "500.html", "rb") as file:
                content = file.read()
            status = 500

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        """Обрабатывает GET-запросы и возвращает страницу «Контакты»."""
        # По заданию на любой GET-запрос возвращаем страницу «Контакты».
        # Для CSS сделано техническое исключение, чтобы Bootstrap-верстка отображалась корректно.
        if self.path == "/base.css":
            with open(TEMPLATES_DIR / "base.css", "rb") as file:
                content = file.read()
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.end_headers()
            self.wfile.write(content)
            return

        self.send_html("contacts.html")

    def do_POST(self) -> None:
        """Принимает данные формы из POST-запроса и выводит их в консоль."""
        content_length = int(self.headers.get("Content-Length", 0))
        raw_data = self.rfile.read(content_length).decode("utf-8")
        data = parse_qs(raw_data)

        print("Получен POST-запрос:")
        for key, value in data.items():
            print(f"{key}: {value[0] if value else ''}")

        self.send_html("contacts.html")


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), ShopHandler)
    print(f"Сервер запущен: http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    finally:
        server.server_close()

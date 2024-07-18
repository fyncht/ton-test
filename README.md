# TON Blockchain Parser

## Описание
Мини парсер блокчейна ТОН, который сохраняет адреса из транзакций в базу данных, обрабатывает смарт-контракты и выгружает данные в JSON.

## Установка

1. Клонируйте репозиторий:
    ```bash
    git clone <repository_url>
    cd ton_parser
    ```

2. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```

3. Нужно настроить базу данных в `ton_parser/settings.py`.

## Использование

1. Запустите парсер и воркер:
    ```bash
    python manage.py start_parsing
    ```

2. Экспорт данных в JSON:
    ```bash
    python blockchain/export.py
    ```

## Структура проекта
- `main.py` - основной файл для запуска парсера и воркера.
- `blockchain/parser.py` - парсер блокчейна.
- `blockchain/worker.py` - воркер для обработки адресов.
- `blockchain/export.py` - экспорт данных в JSON.
- `blockchain/models.py` - модели базы данных.
- `blockchain/admin.py` - административный интерфейс для модели Address.
- `ton_parser/settings.py` - настройки Django.
- `ton_parser/urls.py` - маршруты URL для проекта.

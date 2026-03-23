"""setup_db.py — Инициализация базы данных и создание ресурсов при первом запуске."""
import os
import sqlite3

DB_PATH = "shoe_store.db"
SQL_PATH = "database.sql"
PLACEHOLDER_PATH = os.path.join("assets", "picture.png")


def initialize_database():
    """Создаёт БД и заполняет тестовыми данными, если таблицы ещё не существуют."""
    _create_placeholder_image()

    if not os.path.exists(SQL_PATH):
        print(f"[WARN] Файл {SQL_PATH} не найден. База данных не создана.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='products'"
        ).fetchone()
        if tables:
            return

        with open(SQL_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()

        conn.executescript(sql_script)
        conn.commit()
        print("[INFO] База данных успешно создана и заполнена тестовыми данными.")
    finally:
        conn.close()


def _create_placeholder_image():
    """Создаёт изображение-заглушку, если оно отсутствует."""
    if os.path.exists(PLACEHOLDER_PATH):
        return
    os.makedirs("assets", exist_ok=True)
    try:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (300, 200), color="#CCCCCC")
        draw = ImageDraw.Draw(img)
        draw.rectangle([10, 10, 289, 189], outline="#999999", width=2)
        draw.text((150, 100), "Нет фото", fill="#666666", anchor="mm")
        img.save(PLACEHOLDER_PATH)
    except ImportError:
        _write_minimal_png(PLACEHOLDER_PATH)


def _write_minimal_png(path):
    """Записывает минимальный серый PNG 1x1 если PIL недоступен."""
    import base64
    minimal_png = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    with open(path, "wb") as f:
        f.write(minimal_png)

"""database.py — Слой доступа к данным (паттерн Singleton)."""
import sqlite3

DB_PATH = "shoe_store.db"


class Database:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conn = None
        return cls._instance


    def get_connection(self) -> sqlite3.Connection:
        """Возвращает активное соединение, создавая его при необходимости."""
        if self._conn is None:
            self._conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
        return self._conn


    def get_user_by_credentials(self, login: str, password: str):
        """Возвращает запись пользователя или None при неверных данных."""
        cursor = self.get_connection().execute(
            """SELECT u.id, u.login, u.full_name, r.name AS role
               FROM users u
               JOIN roles r ON u.role_id = r.id
               WHERE u.login = ? AND u.password = ?""",
            (login, password),
        )
        return cursor.fetchone()


    def get_categories(self):
        cursor = self.get_connection().execute("SELECT id, name FROM categories ORDER BY name")
        return cursor.fetchall()

    def get_manufacturers(self):
        cursor = self.get_connection().execute("SELECT id, name FROM manufacturers ORDER BY name")
        return cursor.fetchall()

    def get_suppliers(self):
        cursor = self.get_connection().execute("SELECT id, name FROM suppliers ORDER BY name")
        return cursor.fetchall()

    def get_or_create_supplier(self, name: str) -> int:
        """Возвращает id поставщика по имени, создавая запись при необходимости."""
        conn = self.get_connection()
        row = conn.execute("SELECT id FROM suppliers WHERE LOWER(name) = LOWER(?)", (name,)).fetchone()
        if row:
            return row["id"]
        cursor = conn.execute("INSERT INTO suppliers (name) VALUES (?)", (name,))
        conn.commit()
        return cursor.lastrowid


    def get_all_products(self):
        """Возвращает все товары с раскрытыми внешними ключами."""
        cursor = self.get_connection().execute(
            """SELECT p.id, p.name, c.name AS category, p.description,
                      m.name AS manufacturer, s.name AS supplier,
                      p.price, p.unit, p.stock_quantity, p.discount, p.image_path
               FROM products p
               JOIN categories   c ON p.category_id     = c.id
               JOIN manufacturers m ON p.manufacturer_id = m.id
               JOIN suppliers     s ON p.supplier_id     = s.id
               ORDER BY p.id"""
        )
        return cursor.fetchall()

    def get_product_by_id(self, product_id: int):
        cursor = self.get_connection().execute(
            """SELECT id, name, category_id, description, manufacturer_id,
                      supplier_id, price, unit, stock_quantity, discount, image_path
               FROM products WHERE id = ?""",
            (product_id,),
        )
        return cursor.fetchone()

    def add_product(self, name, category_id, description, manufacturer_id,
                    supplier_id, price, unit, stock_quantity, discount, image_path):
        conn = self.get_connection()
        conn.execute(
            """INSERT INTO products
               (name, category_id, description, manufacturer_id, supplier_id,
                price, unit, stock_quantity, discount, image_path)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, category_id, description, manufacturer_id, supplier_id,
             price, unit, stock_quantity, discount, image_path),
        )
        conn.commit()

    def update_product(self, product_id, name, category_id, description, manufacturer_id,
                       supplier_id, price, unit, stock_quantity, discount, image_path):
        conn = self.get_connection()
        conn.execute(
            """UPDATE products SET name=?, category_id=?, description=?,
               manufacturer_id=?, supplier_id=?, price=?, unit=?,
               stock_quantity=?, discount=?, image_path=?
               WHERE id=?""",
            (name, category_id, description, manufacturer_id, supplier_id,
             price, unit, stock_quantity, discount, image_path, product_id),
        )
        conn.commit()

    def delete_product(self, product_id: int):
        conn = self.get_connection()
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()

    def is_product_in_orders(self, product_id: int) -> bool:
        """Проверяет, задействован ли товар хотя бы в одном заказе."""
        cursor = self.get_connection().execute(
            "SELECT COUNT(*) FROM order_items WHERE product_id = ?", (product_id,)
        )
        return cursor.fetchone()[0] > 0

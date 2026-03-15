PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    login     TEXT NOT NULL UNIQUE,
    password  TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role_id   INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE IF NOT EXISTS categories (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS manufacturers (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS suppliers (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS products (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL,
    category_id    INTEGER NOT NULL,
    description    TEXT,
    manufacturer_id INTEGER NOT NULL,
    supplier_id    INTEGER NOT NULL,
    price          REAL    NOT NULL CHECK(price >= 0),
    unit           TEXT    NOT NULL DEFAULT 'шт',
    stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK(stock_quantity >= 0),
    discount       REAL    NOT NULL DEFAULT 0 CHECK(discount >= 0 AND discount <= 100),
    image_path     TEXT,
    FOREIGN KEY (category_id)     REFERENCES categories(id),
    FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(id),
    FOREIGN KEY (supplier_id)     REFERENCES suppliers(id)
);

CREATE TABLE IF NOT EXISTS order_statuses (
    id   INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS orders (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    article         TEXT NOT NULL,
    status_id       INTEGER NOT NULL,
    pickup_address  TEXT,
    order_date      TEXT,
    delivery_date   TEXT,
    FOREIGN KEY (status_id) REFERENCES order_statuses(id)
);

CREATE TABLE IF NOT EXISTS order_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id   INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity   INTEGER NOT NULL DEFAULT 1,
    FOREIGN KEY (order_id)   REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Роли
INSERT INTO roles (id, name) VALUES (1, 'admin'), (2, 'manager'), (3, 'client');

-- Пользователи (логин / пароль)
INSERT INTO users (login, password, full_name, role_id) VALUES
    ('admin',    'admin',   'Администратов Иван Иванович',  1),
    ('manager1', 'manager', 'Менеджеров Пётр Петрович',     2),
    ('client1',  'client',  'Клиентов Сергей Сергеевич',    3);

-- Категории
INSERT INTO categories (name) VALUES
    ('Кроссовки'), ('Туфли'), ('Сапоги'), ('Ботинки'), ('Сандалии');

-- Производители
INSERT INTO manufacturers (name) VALUES
    ('Nike'), ('Adidas'), ('Puma'), ('Ecco'), ('Clarks');

-- Поставщики
INSERT INTO suppliers (name) VALUES
    ('ООО СпортТрейд'), ('ИП Башмаков'), ('ООО ОбувьОптПлюс');

-- Статусы заказов
INSERT INTO order_statuses (id, name) VALUES
    (1, 'Новый'), (2, 'В обработке'), (3, 'Выдан'), (4, 'Отменён');

-- Товары (некоторые со скидкой > 15%, некоторые с нулевым остатком для тестирования)
INSERT INTO products (name, category_id, description, manufacturer_id, supplier_id,
                      price, unit, stock_quantity, discount, image_path) VALUES
    ('Nike Air Max 270',    1, 'Лёгкие кроссовки с воздушной подушкой Max Air',       1, 1, 8990.00,  'шт', 15, 0,  NULL),
    ('Adidas Ultraboost 22',1, 'Кроссовки для бега с адаптивной подошвой Boost',       2, 1, 12490.00, 'шт',  8, 10, NULL),
    ('Puma RS-X',           1, 'Ретро-кроссовки с объёмной многослойной подошвой',     3, 2, 6990.00,  'шт',  0, 0,  NULL),
    ('Ecco Soft 7',         2, 'Классические кожаные туфли с анатомической стелькой',  4, 2, 9990.00,  'шт',  5, 20, NULL),
    ('Clarks Desert Boot',  4, 'Замшевые ботинки в стиле casual',                      5, 3, 7490.00,  'шт', 12, 5,  NULL),
    ('Nike Blazer Mid 77',  1, 'Высокие кроссовки в стиле ретро 1977 года',            1, 1, 7990.00,  'шт',  0, 0,  NULL),
    ('Adidas Stan Smith',   2, 'Культовые белые туфли-кеды из натуральной кожи',       2, 3, 5990.00,  'шт', 20, 15, NULL),
    ('Ecco Biom C',         4, 'Ботинки с улучшенной анатомической стелькой Biom',     4, 2, 14990.00, 'шт',  3, 25, NULL),
    ('Puma Suede Classic',  1, 'Культовые замшевые кроссовки с логотипом формstrip',   3, 1, 5490.00,  'шт',  7, 0,  NULL),
    ('Clarks Wallabee',     4, 'Мокасины из натуральной кожи ручной работы',           5, 3, 8490.00,  'шт', 10, 18, NULL);

-- Заказы
INSERT INTO orders (article, status_id, pickup_address, order_date, delivery_date) VALUES
    ('ORD-2024-001', 1, 'ул. Ленина, д. 10',   '2024-01-15', '2024-01-20'),
    ('ORD-2024-002', 3, 'пр. Мира, д. 25',     '2024-01-16', '2024-01-22');

-- Товары в заказах (id=3 и id=6 нельзя будет удалить — тест ограничения)
INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 3, 2), (2, 6, 1);

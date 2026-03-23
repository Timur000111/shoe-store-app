"""views/products.py — Экран списка товаров с ролевым доступом."""
import os
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

FONT = "Times New Roman"
COLOR_BG = "#FFFFFF"
COLOR_SECONDARY = "#7FFF00"
COLOR_ACCENT = "#00FA9A"
COLOR_DISCOUNT_HIGH = "#2E8B57"   # скидка > 15 %
COLOR_NO_STOCK = "#ADD8E6"        # нет на складе
COLOR_LOGOUT_BTN = "#FF6B6B"

ROLE_LABELS = {"admin": "Администратор", "manager": "Менеджер",
               "client": "Клиент", "guest": "Гость"}

COLUMNS = ("id", "name", "category", "manufacturer", "supplier",
           "price", "final_price", "unit", "stock", "discount")
COL_LABELS = {
    "id": "ID", "name": "Наименование", "category": "Категория",
    "manufacturer": "Производитель", "supplier": "Поставщик",
    "price": "Цена (осн.)", "final_price": "Цена (итог.)",
    "unit": "Ед.изм.", "stock": "Остаток", "discount": "Скидка %",
}
COL_WIDTHS = {
    "id": 40, "name": 190, "category": 100, "manufacturer": 100,
    "supplier": 130, "price": 95, "final_price": 95,
    "unit": 60, "stock": 70, "discount": 70,
}


class ProductsFrame(tk.Frame):
    def __init__(self, parent, app, user: dict):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app
        self.user = user
        self.role = user.get("role", "guest")
        self.db = Database()

        self._search_var = tk.StringVar()
        self._supplier_var = tk.StringVar(value="Все поставщики")
        self._search_var.trace_add("write", lambda *_: self._apply_filters())
        self._supplier_var.trace_add("write", lambda *_: self._apply_filters())

        self._sort_ascending = True
        self._sort_by_stock = False

        self._edit_window = None

        self._thumb_cache: dict = {}

        self._build_ui()
        self._load_products()

    def _build_ui(self):
        self.app.title("Список товаров — Магазин обуви")
        self._build_top_bar()

        if self.role in ("manager", "admin"):
            self._build_toolbar()

        if self.role == "admin":
            self._build_admin_bar()

        self._build_table()
        self._build_legend()

    def _build_top_bar(self):
        bar = tk.Frame(self, bg=COLOR_SECONDARY, pady=8)
        bar.pack(fill=tk.X)

        tk.Label(bar, text="🥿  Магазин обуви", font=(FONT, 14, "bold"),
                 bg=COLOR_SECONDARY).pack(side=tk.LEFT, padx=12)

        tk.Button(bar, text="Выход", font=(FONT, 10), bg=COLOR_LOGOUT_BTN,
                  fg="white", cursor="hand2", command=self._on_logout).pack(side=tk.RIGHT, padx=10)

        role_text = ROLE_LABELS.get(self.role, self.role)
        full_name = self.user.get("full_name", "Гость")
        tk.Label(bar, text=f"{full_name}  |  {role_text}",
                 font=(FONT, 11), bg=COLOR_SECONDARY).pack(side=tk.RIGHT, padx=10)

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=COLOR_BG, pady=6)
        bar.pack(fill=tk.X, padx=12)

        tk.Label(bar, text="Поиск:", font=(FONT, 11), bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Entry(bar, textvariable=self._search_var, font=(FONT, 11), width=28).pack(
            side=tk.LEFT, padx=(4, 16))

        tk.Label(bar, text="Поставщик:", font=(FONT, 11), bg=COLOR_BG).pack(side=tk.LEFT)
        supplier_names = ["Все поставщики"] + [s["name"] for s in self.db.get_suppliers()]
        ttk.Combobox(bar, textvariable=self._supplier_var, values=supplier_names,
                     state="readonly", font=(FONT, 11), width=22).pack(side=tk.LEFT, padx=(4, 16))

        tk.Label(bar, text="Сортировка по остатку:", font=(FONT, 11), bg=COLOR_BG).pack(side=tk.LEFT)
        tk.Button(bar, text="↑", font=(FONT, 11), bg=COLOR_ACCENT, cursor="hand2",
                  command=lambda: self._set_sort(True)).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="↓", font=(FONT, 11), bg=COLOR_ACCENT, cursor="hand2",
                  command=lambda: self._set_sort(False)).pack(side=tk.LEFT, padx=2)
        tk.Button(bar, text="✕ Сброс", font=(FONT, 10), bg="#DDDDDD", cursor="hand2",
                  command=self._reset_sort).pack(side=tk.LEFT, padx=6)

    def _build_admin_bar(self):
        bar = tk.Frame(self, bg=COLOR_BG, pady=4)
        bar.pack(fill=tk.X, padx=12)

        tk.Button(bar, text="+ Добавить товар", font=(FONT, 11, "bold"),
                  bg=COLOR_SECONDARY, cursor="hand2",
                  command=self._open_add_form).pack(side=tk.LEFT)
        tk.Button(bar, text="🗑  Удалить товар", font=(FONT, 11),
                  bg=COLOR_LOGOUT_BTN, fg="white", cursor="hand2",
                  command=self._delete_selected).pack(side=tk.LEFT, padx=10)

    def _build_table(self):
        wrapper = tk.Frame(self)
        wrapper.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        self.tree = ttk.Treeview(
            wrapper, columns=COLUMNS, show="tree headings", selectmode="browse"
        )
        self.tree.column("#0", width=90, anchor="center", stretch=False)
        self.tree.heading("#0", text="Фото")

        for col in COLUMNS:
            self.tree.heading(col, text=COL_LABELS[col])
            self.tree.column(col, width=COL_WIDTHS[col], anchor="center")

        self.tree.tag_configure("discount_high", background=COLOR_DISCOUNT_HIGH, foreground="white")
        self.tree.tag_configure("no_stock", background=COLOR_NO_STOCK)
        self.tree.tag_configure("normal", background=COLOR_BG)

        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(wrapper, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        wrapper.grid_rowconfigure(0, weight=1)
        wrapper.grid_columnconfigure(0, weight=1)

        # Двойной клик по строке (только администратор)
        if self.role == "admin":
            self.tree.bind("<Double-1>", self._on_row_double_click)

    def _build_legend(self):
        """Легенда цветовой разметки строк."""
        bar = tk.Frame(self, bg=COLOR_BG)
        bar.pack(fill=tk.X, padx=12, pady=(0, 6))

        tk.Label(bar, text="■", fg=COLOR_DISCOUNT_HIGH, bg=COLOR_BG, font=(FONT, 13)).pack(side=tk.LEFT)
        tk.Label(bar, text=" Скидка > 15%   ", bg=COLOR_BG, font=(FONT, 10)).pack(side=tk.LEFT)
        tk.Label(bar, text="■", fg=COLOR_NO_STOCK, bg=COLOR_BG, font=(FONT, 13)).pack(side=tk.LEFT)
        tk.Label(bar, text=" Нет на складе", bg=COLOR_BG, font=(FONT, 10)).pack(side=tk.LEFT)


    def _load_products(self):
        self._all_products = [dict(row) for row in self.db.get_all_products()]
        self._thumb_cache.clear()
        self._preload_thumbnails()
        self._apply_filters()

    def _preload_thumbnails(self):
        try:
            from PIL import Image, ImageTk
            placeholder = "assets/picture.png"
            for p in self._all_products:
                img_path = p.get("image_path")
                path = img_path if (img_path and os.path.exists(img_path)) else placeholder
                try:
                    img = Image.open(path)
                    img.thumbnail((80, 54))
                    self._thumb_cache[p["id"]] = ImageTk.PhotoImage(img)
                except Exception:
                    self._thumb_cache[p["id"]] = None
        except ImportError:
            pass

    def _apply_filters(self):
        products = list(self._all_products)

        if self.role in ("manager", "admin"):
            search = self._search_var.get().strip().lower()
            if search:
                products = [
                    p for p in products
                    if any(
                        search in str(p.get(field, "")).lower()
                        for field in ("name", "category", "description",
                                      "manufacturer", "supplier", "unit")
                    )
                ]

            supplier = self._supplier_var.get()
            if supplier and supplier != "Все поставщики":
                products = [p for p in products if p.get("supplier") == supplier]

        if self._sort_by_stock:
            products.sort(key=lambda p: p.get("stock_quantity", 0), reverse=not self._sort_ascending)

        self._refresh_tree(products)

    def _refresh_tree(self, products: list):
        """Перерисовывает строки таблицы."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for p in products:
            price = p.get("price", 0.0)
            discount = p.get("discount", 0.0)
            stock = p.get("stock_quantity", 0)

            if discount > 0:
                final = price * (1 - discount / 100)
                price_str = f"{price:.2f} р."
                final_str = f"{final:.2f} р."
            else:
                price_str = f"{price:.2f} р."
                final_str = "—"

            values = (
                p["id"], p["name"], p.get("category", ""),
                p.get("manufacturer", ""), p.get("supplier", ""),
                price_str, final_str,
                p.get("unit", ""), stock, f"{discount:.0f}%",
            )

            
            if discount > 15:
                tag = "discount_high"
            elif stock == 0:
                tag = "no_stock"
            else:
                tag = "normal"

            thumbnail = self._thumb_cache.get(p["id"])
            self.tree.insert(
                "", "end", iid=str(p["id"]),
                image=thumbnail if thumbnail else "",
                values=values, tags=(tag,),
            )

    def _set_sort(self, ascending: bool):
        self._sort_by_stock = True
        self._sort_ascending = ascending
        self._apply_filters()

    def _reset_sort(self):
        self._sort_by_stock = False
        self._apply_filters()

    def _on_logout(self):
        self.app.show_login()

    def _on_row_double_click(self, _event):
        item = self.tree.focus()
        if item:
            self._open_edit_form(int(item))

    def _open_add_form(self):
        if self._is_edit_window_open():
            return
        from views.product_form import ProductFormWindow
        self._edit_window = ProductFormWindow(
            self.app, self.db, product_id=None, on_save=self._load_products
        )

    def _open_edit_form(self, product_id: int):
        if self._is_edit_window_open():
            return
        from views.product_form import ProductFormWindow
        self._edit_window = ProductFormWindow(
            self.app, self.db, product_id=product_id, on_save=self._load_products
        )

    def _is_edit_window_open(self) -> bool:
        """Проверяет, открыто ли уже окно редактирования."""
        if self._edit_window and self._edit_window.winfo_exists():
            messagebox.showwarning(
                "Предупреждение",
                "Форма редактирования уже открыта.\n"
                "Закройте её перед открытием новой.",
            )
            self._edit_window.focus()
            return True
        return False

    def _delete_selected(self):
        item = self.tree.focus()
        if not item:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления в таблице.")
            return

        product_id = int(item)
        product = self.db.get_product_by_id(product_id)
        if not product:
            return

        if self.db.is_product_in_orders(product_id):
            messagebox.showerror(
                "Удаление невозможно",
                f"Товар «{product['name']}» включён в один или несколько заказов.\n"
                "Удаление товаров, задействованных в заказах, запрещено.\n\n"
                "Сначала удалите или измените соответствующие заказы.",
            )
            return

        confirmed = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы собираетесь безвозвратно удалить товар:\n\n"
            f"  «{product['name']}»\n\n"
            "Это действие нельзя отменить. Продолжить?",
            icon="warning",
        )
        if not confirmed:
            return

        img_path = product["image_path"]
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
            except OSError:
                pass

        self.db.delete_product(product_id)
        messagebox.showinfo("Удалено", f"Товар «{product['name']}» успешно удалён.")
        self._load_products()

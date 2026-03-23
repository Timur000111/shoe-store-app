"""views/product_form.py — Модальное окно добавления / редактирования товара."""
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from database import Database

FONT = "Times New Roman"
COLOR_BG = "#FFFFFF"
COLOR_SECONDARY = "#7FFF00"
COLOR_ACCENT = "#00FA9A"
COLOR_BTN_CANCEL = "#FF6B6B"

IMAGES_DIR = os.path.join("assets", "products")
PLACEHOLDER = os.path.join("assets", "picture.png")
IMG_MAX_W = 300
IMG_MAX_H = 200


class ProductFormWindow(tk.Toplevel):

    def __init__(self, parent, db: Database, product_id, on_save):
        super().__init__(parent)
        self.db = db
        self.product_id = product_id
        self.on_save = on_save
        self._new_image_path = None    
        self._old_image_path = None   

        title = "Редактирование товара" if product_id else "Добавление товара"
        self.title(title)
        self.geometry("720x680")
        self.configure(bg=COLOR_BG)
        self.resizable(False, True)
        self.grab_set()    

        os.makedirs(IMAGES_DIR, exist_ok=True)
        self._build_ui()

        if product_id:
            self._fill_from_db()

    def _build_ui(self):
        canvas = tk.Canvas(self, bg=COLOR_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._form = tk.Frame(canvas, bg=COLOR_BG)
        self._form.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._form, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Заголовок формы
        title_text = "Редактирование товара" if self.product_id else "Добавление товара"
        tk.Label(self._form, text=title_text, font=(FONT, 16, "bold"), bg=COLOR_BG).pack(pady=(16, 10))

        # ID 
        if self.product_id:
            self._add_row_entry("ID товара:", tk.StringVar(value=str(self.product_id)),
                                readonly=True, store_as="_id_var")

        # Фото товара
        self._add_image_section()

        # Текстовые поля
        self._name_var = tk.StringVar()
        self._add_row_entry("Наименование: *", self._name_var)

        # Категория 
        cats = self.db.get_categories()
        self._cat_map = {c["name"]: c["id"] for c in cats}
        self._cat_var = tk.StringVar()
        self._add_row_combo("Категория: *", self._cat_var, list(self._cat_map.keys()))

        # Описание 
        self._add_row_textbox("Описание:")

        # Производитель 
        mans = self.db.get_manufacturers()
        self._man_map = {m["name"]: m["id"] for m in mans}
        self._man_var = tk.StringVar()
        self._add_row_combo("Производитель: *", self._man_var, list(self._man_map.keys()))

        # Поставщик
        sup_names = [s["name"] for s in self.db.get_suppliers()]
        self._sup_var = tk.StringVar()
        self._add_row_combo("Поставщик: *", self._sup_var, sup_names, readonly=False)

        # Числовые поля
        self._price_var = tk.StringVar()
        self._add_row_entry("Цена (руб.): *", self._price_var)

        self._unit_var = tk.StringVar(value="шт")
        self._add_row_entry("Единица изм.: *", self._unit_var)

        self._stock_var = tk.StringVar(value="0")
        self._add_row_entry("Кол-во на складе: *", self._stock_var)

        self._discount_var = tk.StringVar(value="0")
        self._add_row_entry("Скидка (%): *", self._discount_var)

        # Кнопки «Сохранить» / «Отмена»
        btn_bar = tk.Frame(self._form, bg=COLOR_BG)
        btn_bar.pack(pady=20)
        tk.Button(btn_bar, text="Сохранить", font=(FONT, 12, "bold"),
                  bg=COLOR_ACCENT, width=14, cursor="hand2",
                  command=self._on_save).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_bar, text="Отмена", font=(FONT, 12),
                  bg=COLOR_BTN_CANCEL, fg="white", width=14, cursor="hand2",
                  command=self.destroy).pack(side=tk.LEFT, padx=10)


    def _add_row_entry(self, label: str, var: tk.StringVar,
                       readonly: bool = False, store_as: str = None):
        row = tk.Frame(self._form, bg=COLOR_BG)
        row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(row, text=label, font=(FONT, 11), bg=COLOR_BG,
                 width=20, anchor="w").pack(side=tk.LEFT)
        state = "readonly" if readonly else "normal"
        entry = tk.Entry(row, textvariable=var, font=(FONT, 11), width=36, state=state)
        entry.pack(side=tk.LEFT)
        if store_as:
            setattr(self, store_as, var)

    def _add_row_combo(self, label: str, var: tk.StringVar,
                       values: list, readonly: bool = True):
        row = tk.Frame(self._form, bg=COLOR_BG)
        row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(row, text=label, font=(FONT, 11), bg=COLOR_BG,
                 width=20, anchor="w").pack(side=tk.LEFT)
        state = "readonly" if readonly else "normal"
        ttk.Combobox(row, textvariable=var, values=values,
                     state=state, font=(FONT, 11), width=34).pack(side=tk.LEFT)

    def _add_row_textbox(self, label: str):
        row = tk.Frame(self._form, bg=COLOR_BG)
        row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(row, text=label, font=(FONT, 11), bg=COLOR_BG,
                 width=20, anchor="nw").pack(side=tk.LEFT, pady=(3, 0))
        self._desc_text = tk.Text(row, font=(FONT, 11), width=36, height=3,
                                  wrap="word")
        self._desc_text.pack(side=tk.LEFT)

    def _add_image_section(self):
        row = tk.Frame(self._form, bg=COLOR_BG)
        row.pack(fill=tk.X, padx=20, pady=3)
        tk.Label(row, text="Фото товара:", font=(FONT, 11), bg=COLOR_BG,
                 width=20, anchor="w").pack(side=tk.LEFT)
        self._img_label = tk.Label(row, bg=COLOR_BG, relief="sunken", width=12, height=4)
        self._img_label.pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(row, text="Выбрать фото", font=(FONT, 10),
                  bg=COLOR_SECONDARY, cursor="hand2",
                  command=self._choose_image).pack(side=tk.LEFT)
        self._refresh_image_preview(None)

    def _fill_from_db(self):
        product = self.db.get_product_by_id(self.product_id)
        if not product:
            messagebox.showerror("Ошибка", "Товар не найден в базе данных.")
            self.destroy()
            return

        self._name_var.set(product["name"])
        self._desc_text.insert("1.0", product["description"] or "")
        self._price_var.set(str(product["price"]))
        self._unit_var.set(product["unit"])
        self._stock_var.set(str(product["stock_quantity"]))
        self._discount_var.set(str(product["discount"]))

        for name, cid in self._cat_map.items():
            if cid == product["category_id"]:
                self._cat_var.set(name)
                break
        for name, mid in self._man_map.items():
            if mid == product["manufacturer_id"]:
                self._man_var.set(name)
                break

        suppliers = self.db.get_suppliers()
        for s in suppliers:
            if s["id"] == product["supplier_id"]:
                self._sup_var.set(s["name"])
                break

        self._old_image_path = product["image_path"]
        self._new_image_path = product["image_path"]
        self._refresh_image_preview(product["image_path"])


    def _choose_image(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение товара",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"),
                       ("Все файлы", "*.*")],
        )
        if not path:
            return
        try:
            from PIL import Image
            img = Image.open(path).resize((IMG_MAX_W, IMG_MAX_H))
            filename = os.path.basename(path)
            dest = os.path.join(IMAGES_DIR, filename)
            img.save(dest)
            self._new_image_path = dest
            self._refresh_image_preview(dest)
        except ImportError:
            dest = os.path.join(IMAGES_DIR, os.path.basename(path))
            shutil.copy2(path, dest)
            self._new_image_path = dest
            self._refresh_image_preview(dest)
        except Exception as exc:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить изображение:\n{exc}")

    def _refresh_image_preview(self, image_path):
        try:
            from PIL import Image, ImageTk
            path = image_path if (image_path and os.path.exists(image_path)) else PLACEHOLDER
            img = Image.open(path)
            img.thumbnail((96, 64))
            self._preview_photo = ImageTk.PhotoImage(img)
            self._img_label.configure(image=self._preview_photo, text="")
        except Exception:
            self._img_label.configure(image="", text="[нет фото]", font=(FONT, 9))


    def _validate(self) -> list:
        """Возвращает список ошибок. Пустой список — форма валидна."""
        errors = []

        if not self._name_var.get().strip():
            errors.append("• Наименование товара обязательно для заполнения.")

        if not self._cat_var.get():
            errors.append("• Выберите категорию товара из выпадающего списка.")

        if not self._man_var.get():
            errors.append("• Выберите производителя из выпадающего списка.")

        if not self._sup_var.get().strip():
            errors.append("• Укажите поставщика товара.")

        if not self._unit_var.get().strip():
            errors.append("• Укажите единицу измерения (например: шт, пара).")

        try:
            price = float(self._price_var.get())
            if price < 0:
                errors.append("• Цена не может быть отрицательной.")
        except ValueError:
            errors.append("• Цена должна быть числом (например: 1990.50).")

        try:
            stock = int(self._stock_var.get())
            if stock < 0:
                errors.append("• Количество на складе не может быть отрицательным.")
        except ValueError:
            errors.append("• Количество на складе должно быть целым числом.")

        try:
            discount = float(self._discount_var.get())
            if not (0 <= discount <= 100):
                errors.append("• Скидка должна быть от 0 до 100 процентов.")
        except ValueError:
            errors.append("• Скидка должна быть числом от 0 до 100.")

        return errors

    def _on_save(self):
        errors = self._validate()
        if errors:
            messagebox.showerror(
                "Ошибки заполнения формы",
                "Обнаружены ошибки:\n\n" + "\n".join(errors) +
                "\n\nИсправьте ошибки и повторите попытку.",
            )
            return

        name = self._name_var.get().strip()
        category_id = self._cat_map[self._cat_var.get()]
        description = self._desc_text.get("1.0", "end-1c").strip()
        manufacturer_id = self._man_map[self._man_var.get()]
        supplier_id = self.db.get_or_create_supplier(self._sup_var.get().strip())
        price = float(self._price_var.get())
        unit = self._unit_var.get().strip()
        stock_quantity = int(self._stock_var.get())
        discount = float(self._discount_var.get())
        image_path = self._new_image_path

        if self.product_id:
            if self._old_image_path and self._old_image_path != image_path:
                if os.path.exists(self._old_image_path):
                    try:
                        os.remove(self._old_image_path)
                    except OSError:
                        pass

            self.db.update_product(
                self.product_id, name, category_id, description,
                manufacturer_id, supplier_id, price, unit,
                stock_quantity, discount, image_path,
            )
            messagebox.showinfo("Сохранено", f"Товар «{name}» успешно обновлён.")
        else:
            self.db.add_product(
                name, category_id, description, manufacturer_id, supplier_id,
                price, unit, stock_quantity, discount, image_path,
            )
            messagebox.showinfo("Добавлено", f"Товар «{name}» успешно добавлен.")

        self.on_save()
        self.destroy()

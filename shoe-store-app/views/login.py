"""views/login.py — Экран авторизации."""
import tkinter as tk
from tkinter import messagebox
from database import Database

FONT = "Times New Roman"
COLOR_BG = "#FFFFFF"
COLOR_SECONDARY = "#7FFF00"
COLOR_ACCENT = "#00FA9A"


class LoginFrame(tk.Frame):
    """Первый экран, который видит пользователь при запуске."""

    def __init__(self, parent, app):
        super().__init__(parent, bg=COLOR_BG)
        self.app = app
        self.db = Database()
        self.app.title("Вход — Магазин обуви")
        self._build_ui()

    def _build_ui(self):
        # Центральный контейнер
        center = tk.Frame(self, bg=COLOR_BG, bd=1, relief=tk.FLAT)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Логотип компании (файл assets/logo.png должен быть в папке приложения)
        try:
            from PIL import Image, ImageTk
            logo_img = Image.open("assets/logo.png").resize((220, 88))
            self._logo = ImageTk.PhotoImage(logo_img)
            tk.Label(center, image=self._logo, bg=COLOR_BG).pack(pady=(0, 16))
        except Exception:
            tk.Label(center, text="🥿  Магазин обуви", font=(FONT, 22, "bold"), bg=COLOR_BG).pack(pady=(0, 16))

        tk.Label(center, text="Вход в систему", font=(FONT, 17, "bold"), bg=COLOR_BG).pack(pady=(0, 20))

        # Поле «Логин»
        tk.Label(center, text="Логин:", font=(FONT, 12), bg=COLOR_BG, anchor="w").pack(fill=tk.X)
        self._login_var = tk.StringVar()
        login_entry = tk.Entry(center, textvariable=self._login_var, font=(FONT, 12), width=30)
        login_entry.pack(pady=(2, 10))
        login_entry.focus_set()

        # Поле «Пароль»
        tk.Label(center, text="Пароль:", font=(FONT, 12), bg=COLOR_BG, anchor="w").pack(fill=tk.X)
        self._password_var = tk.StringVar()
        tk.Entry(center, textvariable=self._password_var, show="*", font=(FONT, 12), width=30).pack(pady=(2, 20))

        # Кнопка «Войти»
        tk.Button(
            center, text="Войти", font=(FONT, 12, "bold"),
            bg=COLOR_ACCENT, fg="black", width=20,
            cursor="hand2", command=self._on_login,
        ).pack(pady=(0, 8))

        # Кнопка «Войти как гость»
        tk.Button(
            center, text="Войти как гость", font=(FONT, 11),
            bg=COLOR_SECONDARY, fg="black", width=20,
            cursor="hand2", command=self._on_guest,
        ).pack()

        # Подсказка с тестовыми учётными данными
        hint = "Тест: admin/admin · manager1/manager · client1/client"
        tk.Label(center, text=hint, font=(FONT, 9), bg=COLOR_BG, fg="#888888").pack(pady=(14, 0))

        # Enter → войти
        self.app.bind("<Return>", lambda _e: self._on_login())

    def _on_login(self):
        login = self._login_var.get().strip()
        password = self._password_var.get().strip()

        if not login or not password:
            messagebox.showerror(
                "Ошибка",
                "Необходимо заполнить оба поля:\n"
                "  • Логин\n"
                "  • Пароль\n\n"
                "Пожалуйста, введите данные и повторите попытку.",
            )
            return

        user_row = self.db.get_user_by_credentials(login, password)
        if user_row:
            self.app.show_products(dict(user_row))
        else:
            messagebox.showerror(
                "Ошибка авторизации",
                "Неверный логин или пароль.\n\n"
                "Проверьте введённые данные и попробуйте снова.",
            )

    def _on_guest(self):
        self.app.show_products({"id": None, "login": "guest", "full_name": "Гость", "role": "guest"})

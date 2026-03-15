"""main.py — Точка входа. Создаёт главное окно и управляет переключением экранов."""
import tkinter as tk
from setup_db import initialize_database

FONT_NAME = "Times New Roman"
COLOR_BG = "#FFFFFF"


class App(tk.Tk):
    """Главное окно приложения (единственный экземпляр Tk)."""

    def __init__(self):
        super().__init__()
        self.title("Магазин обуви")
        self.geometry("1280x750")
        self.minsize(960, 600)
        self.configure(bg=COLOR_BG)
        self.current_frame = None

        # Иконка приложения (файл поместить в assets/icon.ico)
        try:
            self.iconbitmap("assets/icon.ico")
        except Exception:
            pass

        initialize_database()
        self.show_login()

    # ------------------------------------------------------------------
    # Навигация между экранами
    # ------------------------------------------------------------------

    def show_login(self):
        """Переходит на экран авторизации."""
        from views.login import LoginFrame
        self._switch_frame(LoginFrame)

    def show_products(self, user: dict):
        """Переходит на экран товаров для указанного пользователя."""
        from views.products import ProductsFrame
        self._switch_frame(ProductsFrame, user=user)

    def _switch_frame(self, frame_class, **kwargs):
        if self.current_frame is not None:
            self.current_frame.destroy()
        self.current_frame = frame_class(self, app=self, **kwargs)
        self.current_frame.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()

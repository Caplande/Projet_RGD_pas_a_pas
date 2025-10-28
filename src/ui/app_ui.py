from tkinter import ttk
from ui.menu import build_menu
from ui.pages.accueil import AccueilPage


class AppUI:
    def __init__(self, context):
        self.context = context
        self.root = context.root
        self._setup_ui()

    def _setup_ui(self):
        self.context.menu = build_menu(self.root, self.context)

        frame = ttk.Frame(self.root)
        frame.pack(fill="both", expand=True)
        self.context.current_page = AccueilPage(frame, self.context)


if __name__ == '__main__':
    pass

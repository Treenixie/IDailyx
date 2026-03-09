import customtkinter as ctk
from functools import partial
from tkinter import messagebox

from core.storage import save_ideas
from ui.dialogs import IdeaDialog


class MainWindow(ctk.CTk):
    def __init__(self, idea_manager, data_file: str):
        super().__init__()

        self.title("IDailyx")
        self.geometry("1400x800")
        self.minsize(1100, 650)

        self.idea_manager = idea_manager
        self.data_file = data_file
        self.ideas = self.idea_manager.get_all()
        self.selected_idea = None

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color="#16181d")

        self._build_layout()
        self._fill_idea_list()

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.top_bar = ctk.CTkFrame(self, corner_radius=16, fg_color="#1d2128")
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=12, pady=(12, 6))

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=16, fg_color="#1d2128")
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(6, 12))
        self.sidebar.grid_propagate(False)

        self.center_panel = ctk.CTkFrame(self, corner_radius=16, fg_color="#1d2128")
        self.center_panel.grid(row=1, column=1, sticky="nsew", padx=6, pady=(6, 12))

        self.details_panel = ctk.CTkFrame(self, corner_radius=16, fg_color="#1d2128")
        self.details_panel.grid(row=1, column=2, sticky="nsew", padx=(6, 12), pady=(6, 12))

        self._build_top_bar()
        self._build_sidebar()
        self._build_center_panel()
        self._build_details_panel()

    def _build_top_bar(self):
        self.top_bar.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self.top_bar,
            text="IDailyx",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=16, pady=14, sticky="w")

        self.search_entry = ctk.CTkEntry(
            self.top_bar,
            placeholder_text="Поиск идей..."
        )
        self.search_entry.grid(row=0, column=1, padx=10, pady=14, sticky="ew")

        self.new_button = ctk.CTkButton(
            self.top_bar,
            text="+ Новая идея",
            command=self.open_add_dialog
        )
        self.new_button.grid(row=0, column=2, padx=10, pady=14)

        self.random_button = ctk.CTkButton(self.top_bar, text="Случайная идея")
        self.random_button.grid(row=0, column=3, padx=(0, 16), pady=14)

    def _build_sidebar(self):
        title = ctk.CTkLabel(
            self.sidebar,
            text="Жанры",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", padx=16, pady=(16, 8))

        categories = [
            "Все идеи",
            "Шутеры",
            "Платформеры",
            "Головоломки",
            "Хорроры",
            "Рогалики",
            "Приключения",
            "Стратегии",
            "Симуляторы",
            "Мультиплеер",
            "Неотсортированные",
            "Избранное",
        ]

        for category in categories:
            button = ctk.CTkButton(
                self.sidebar,
                text=category,
                anchor="w",
                fg_color="#242936",
                hover_color="#2d3442"
            )
            button.pack(fill="x", padx=12, pady=4)

    def _build_center_panel(self):
        title = ctk.CTkLabel(
            self.center_panel,
            text="Список идей",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(anchor="w", padx=16, pady=(16, 8))

        self.idea_listbox = ctk.CTkScrollableFrame(self.center_panel, fg_color="transparent")
        self.idea_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_details_panel(self):
        self.details_title = ctk.CTkLabel(
            self.details_panel,
            text="Выбери идею",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.details_title.pack(anchor="w", padx=16, pady=(16, 8))

        self.details_buttons_frame = ctk.CTkFrame(self.details_panel, fg_color="transparent")
        self.details_buttons_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.edit_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="Редактировать",
            command=self.open_edit_dialog,
            state="disabled"
        )
        self.edit_button.pack(side="left", padx=(0, 8))

        self.delete_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="Удалить",
            fg_color="#8B3A3A",
            hover_color="#A04444",
            command=self.delete_selected_idea,
            state="disabled"
        )
        self.delete_button.pack(side="left")

        self.details_text = ctk.CTkTextbox(self.details_panel, wrap="word")
        self.details_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.details_text.insert("1.0", "Здесь будут показаны подробности выбранной идеи.")
        self.details_text.configure(state="disabled")

    def _fill_idea_list(self):
        for widget in self.idea_listbox.winfo_children():
            widget.destroy()

        self.ideas = self.idea_manager.get_all()

        if not self.ideas:
            empty_label = ctk.CTkLabel(
                self.idea_listbox,
                text="Идей пока нет. Добавь первую через кнопку «+ Новая идея».",
                text_color="#aeb7c5"
            )
            empty_label.pack(anchor="w", padx=8, pady=8)
            return

        for idea in self.ideas:
            card = ctk.CTkFrame(self.idea_listbox, corner_radius=14, fg_color="#242936")
            card.pack(fill="x", padx=4, pady=6)

            title = ctk.CTkLabel(
                card,
                text=idea["title"],
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title.pack(anchor="w", padx=12, pady=(10, 2))

            subtitle = ctk.CTkLabel(
                card,
                text=f'{idea["genre"]} • {idea["status"]} • {idea["readiness"]}',
                text_color="#aeb7c5"
            )
            subtitle.pack(anchor="w", padx=12, pady=2)

            hook = ctk.CTkLabel(
                card,
                text=idea["hook"],
                wraplength=500,
                justify="left"
            )
            hook.pack(anchor="w", padx=12, pady=(2, 10))

            click_handler = partial(self._handle_idea_click, idea)

            card.bind("<Button-1>", click_handler)
            title.bind("<Button-1>", click_handler)
            subtitle.bind("<Button-1>", click_handler)
            hook.bind("<Button-1>", click_handler)

    def _handle_idea_click(self, idea: dict, event=None):
        self.show_idea_details(idea)

    def show_idea_details(self, idea: dict):
        self.selected_idea = idea
        self.details_title.configure(text=idea["title"])
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")

        details = (
            f'Ключевая фишка: {idea["hook"]}\n\n'
            f'Описание: {idea["short_description"]}\n\n'
            f'Жанр: {idea["genre"]}\n'
            f'Механика: {idea["mechanic"]}\n'
            f'Масштаб: {idea["scale"]}\n'
            f'Перспектива: {idea["perspective"]}\n'
            f'Платформа: {idea["platform"]}\n'
            f'Проработка: {idea["readiness"]}\n'
            f'Статус: {idea["status"]}\n'
            f'Теги: {", ".join(idea["tags"]) if idea["tags"] else "Нет"}\n'
            f'Избранное: {"Да" if idea["favorite"] else "Нет"}\n'
            f'Дата создания: {idea["created_at"]}\n'
            f'Дата изменения: {idea["updated_at"]}\n\n'
            f'Заметки:\n{idea["notes"]}'
        )

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", details)
        self.details_text.configure(state="disabled")

    def clear_details(self):
        self.selected_idea = None
        self.details_title.configure(text="Выбери идею")
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "Здесь будут показаны подробности выбранной идеи.")
        self.details_text.configure(state="disabled")

    def open_add_dialog(self):
        IdeaDialog(self, self.handle_add_idea)

    def handle_add_idea(self, idea_data: dict):
        new_idea = self.idea_manager.add_idea(idea_data)
        save_ideas(self.data_file, self.idea_manager.get_all())

        self._fill_idea_list()
        self.show_idea_details(new_idea)

    def open_edit_dialog(self):
        if self.selected_idea is None:
            messagebox.showwarning("Предупреждение", "Сначала выбери идею.")
            return

        IdeaDialog(self, self.handle_edit_idea, idea=self.selected_idea)

    def handle_edit_idea(self, updated_data: dict):
        if self.selected_idea is None:
            return

        updated_idea = self.idea_manager.update_idea(self.selected_idea["id"], updated_data)
        if updated_idea is None:
            messagebox.showerror("Ошибка", "Не удалось обновить идею.")
            return

        save_ideas(self.data_file, self.idea_manager.get_all())
        self._fill_idea_list()
        self.show_idea_details(updated_idea)

    def delete_selected_idea(self):
        if self.selected_idea is None:
            messagebox.showwarning("Предупреждение", "Сначала выбери идею.")
            return

        confirm = messagebox.askyesno(
            "Удаление идеи",
            f'Удалить идею "{self.selected_idea["title"]}"?'
        )

        if not confirm:
            return

        was_deleted = self.idea_manager.delete_idea(self.selected_idea["id"])
        if not was_deleted:
            messagebox.showerror("Ошибка", "Не удалось удалить идею.")
            return

        save_ideas(self.data_file, self.idea_manager.get_all())
        self._fill_idea_list()
        self.clear_details()
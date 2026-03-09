import customtkinter as ctk
from functools import partial
from tkinter import messagebox

from core.constants import STATUS_OPTIONS, READINESS_OPTIONS, MECHANICS
from core.storage import save_ideas
from ui.dialogs import IdeaDialog
from ui.styles import (
    APP_BG,
    PANEL_BG,
    CARD_BG,
    CARD_BORDER,
    TEXT_SECONDARY,
    ACCENT,
    ACCENT_HOVER,
    DANGER,
    DANGER_HOVER,
    FAVORITE,
    FAVORITE_HOVER,
    get_status_color,
    get_sidebar_button_colors,
)


class MainWindow(ctk.CTk):
    def __init__(self, idea_manager, data_file: str):
        super().__init__()

        self.title("IDailyx")
        self.geometry("1450x860")
        self.minsize(1180, 700)

        self.idea_manager = idea_manager
        self.data_file = data_file
        self.selected_idea = None
        self.filtered_ideas = []
        self.current_sidebar_filter = "Все идеи"
        self.sidebar_buttons = {}

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.configure(fg_color=APP_BG)

        self._build_layout()
        self._update_sidebar_button_styles()
        self.apply_filters()

    def _build_layout(self):
        self.grid_columnconfigure(0, minsize=220)
        self.grid_columnconfigure(1, weight=1, uniform="content_columns")
        self.grid_columnconfigure(2, weight=1, uniform="content_columns")
        self.grid_rowconfigure(1, weight=1)

        self.top_bar = ctk.CTkFrame(self, corner_radius=16, fg_color=PANEL_BG)
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=12, pady=(12, 6))

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=16, fg_color=PANEL_BG)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(6, 12))
        self.sidebar.grid_propagate(False)

        self.center_panel = ctk.CTkFrame(self, corner_radius=16, fg_color=PANEL_BG)
        self.center_panel.grid(row=1, column=1, sticky="nsew", padx=6, pady=(6, 12))

        self.details_panel = ctk.CTkFrame(self, corner_radius=16, fg_color=PANEL_BG)
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
        title_label.grid(row=0, column=0, padx=16, pady=(14, 8), sticky="w")

        self.search_entry = ctk.CTkEntry(
            self.top_bar,
            placeholder_text="Поиск идей..."
        )
        self.search_entry.grid(row=0, column=1, padx=10, pady=(14, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        self.new_button = ctk.CTkButton(
            self.top_bar,
            text="+ Новая идея",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=self.open_add_dialog
        )
        self.new_button.grid(row=0, column=2, padx=10, pady=(14, 8))

        self.random_button = ctk.CTkButton(
            self.top_bar,
            text="Случайная идея",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=self.show_random_idea
        )
        self.random_button.grid(row=0, column=3, padx=(0, 16), pady=(14, 8))

        filters_frame = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        filters_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=16, pady=(0, 14))

        self.status_menu = ctk.CTkOptionMenu(
            filters_frame,
            values=["Все статусы"] + STATUS_OPTIONS,
            command=self._on_filter_change,
            width=170,
            fg_color=ACCENT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER
        )
        self.status_menu.pack(side="left", padx=(0, 8))
        self.status_menu.set("Все статусы")

        self.readiness_menu = ctk.CTkOptionMenu(
            filters_frame,
            values=["Вся проработка"] + READINESS_OPTIONS,
            command=self._on_filter_change,
            width=190,
            fg_color=ACCENT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER
        )
        self.readiness_menu.pack(side="left", padx=(0, 8))
        self.readiness_menu.set("Вся проработка")

        self.mechanic_menu = ctk.CTkOptionMenu(
            filters_frame,
            values=["Все механики"] + MECHANICS,
            command=self._on_filter_change,
            width=210,
            fg_color=ACCENT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER
        )
        self.mechanic_menu.pack(side="left", padx=(0, 8))
        self.mechanic_menu.set("Все механики")

        self.sort_menu = ctk.CTkOptionMenu(
            filters_frame,
            values=[
                "Сначала новые",
                "Сначала старые",
                "Недавно изменённые",
                "По названию (А-Я)",
                "По названию (Я-А)",
            ],
            command=self._on_filter_change,
            width=190,
            fg_color=ACCENT,
            button_color=ACCENT,
            button_hover_color=ACCENT_HOVER
        )
        self.sort_menu.pack(side="right")
        self.sort_menu.set("Сначала новые")

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
                command=partial(self.set_sidebar_filter, category)
            )
            button.pack(fill="x", padx=12, pady=4)
            self.sidebar_buttons[category] = button

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

        self.status_badge = ctk.CTkLabel(
            self.details_panel,
            text="",
            fg_color=CARD_BORDER,
            corner_radius=8,
            padx=10,
            pady=4
        )
        self.status_badge.pack(anchor="w", padx=16, pady=(0, 10))

        self.details_buttons_frame = ctk.CTkFrame(self.details_panel, fg_color="transparent")
        self.details_buttons_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.details_buttons_frame.grid_columnconfigure(0, weight=1, uniform="details_buttons")
        self.details_buttons_frame.grid_columnconfigure(1, weight=1, uniform="details_buttons")
        self.details_buttons_frame.grid_columnconfigure(2, weight=1, uniform="details_buttons")

        self.edit_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="Редактировать",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=self.open_edit_dialog,
            state="disabled"
        )
        self.edit_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.delete_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="Удалить",
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            command=self.delete_selected_idea,
            state="disabled"
        )
        self.delete_button.grid(row=0, column=1, sticky="ew", padx=(0, 8))

        self.favorite_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="☆ В избранное",
            fg_color=FAVORITE,
            hover_color=FAVORITE_HOVER,
            command=self.toggle_selected_favorite,
            state="disabled"
        )
        self.favorite_button.grid(row=0, column=2, sticky="ew")

        self.details_text = ctk.CTkTextbox(self.details_panel, wrap="word")
        self.details_text.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self.details_text.insert("1.0", "Здесь будут показаны подробности выбранной идеи.")
        self.details_text.configure(state="disabled")

    def _fill_idea_list(self, ideas: list[dict]):
        for widget in self.idea_listbox.winfo_children():
            widget.destroy()

        if not ideas:
            empty_label = ctk.CTkLabel(
                self.idea_listbox,
                text="Ничего не найдено. Попробуй изменить поиск или фильтры.",
                text_color=TEXT_SECONDARY
            )
            empty_label.pack(anchor="w", padx=8, pady=8)
            return

        for idea in ideas:
            status_color = get_status_color(idea["status"])

            card = ctk.CTkFrame(
                self.idea_listbox,
                corner_radius=14,
                fg_color=CARD_BG,
                border_width=1,
                border_color=status_color
            )
            card.pack(fill="x", padx=4, pady=6)

            title_text = f'★ {idea["title"]}' if idea["favorite"] else idea["title"]

            title = ctk.CTkLabel(
                card,
                text=title_text,
                font=ctk.CTkFont(size=16, weight="bold")
            )
            title.pack(anchor="w", padx=12, pady=(10, 2))

            subtitle = ctk.CTkLabel(
                card,
                text=f'{idea["genre"]} • {idea["status"]} • {idea["readiness"]}',
                text_color=status_color
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

    def _on_search_change(self, event=None):
        self.apply_filters()

    def _on_filter_change(self, _value=None):
        self.apply_filters()

    def set_sidebar_filter(self, category: str):
        self.current_sidebar_filter = category
        self._update_sidebar_button_styles()
        self.apply_filters()

    def _update_sidebar_button_styles(self):
        for category, button in self.sidebar_buttons.items():
            fg_color, hover_color = get_sidebar_button_colors(category == self.current_sidebar_filter)
            button.configure(fg_color=fg_color, hover_color=hover_color)

    def _update_favorite_button_state(self):
        if self.selected_idea is None:
            self.favorite_button.configure(state="disabled", text="☆ В избранное")
            return

        if self.selected_idea["favorite"]:
            self.favorite_button.configure(state="normal", text="★ Убрать из избранного")
        else:
            self.favorite_button.configure(state="normal", text="☆ В избранное")

    def apply_filters(self):
        query = self.search_entry.get().strip()

        genre = None
        favorites_only = False

        if self.current_sidebar_filter == "Избранное":
            favorites_only = True
        elif self.current_sidebar_filter != "Все идеи":
            genre = self.current_sidebar_filter

        status = self.status_menu.get()
        if status == "Все статусы":
            status = None

        readiness = self.readiness_menu.get()
        if readiness == "Вся проработка":
            readiness = None

        mechanic = self.mechanic_menu.get()
        if mechanic == "Все механики" or mechanic == "Не выбрано":
            mechanic = None

        filtered = self.idea_manager.filter_ideas(
            query=query,
            genre=genre,
            status=status,
            readiness=readiness,
            mechanic=mechanic,
            favorites_only=favorites_only,
        )

        filtered = self.idea_manager.sort_ideas(filtered, self.sort_menu.get())
        self.filtered_ideas = filtered

        self._fill_idea_list(filtered)

        if self.selected_idea is not None:
            visible_ids = {idea["id"] for idea in filtered}

            if self.selected_idea["id"] not in visible_ids:
                self.clear_details()
            else:
                updated_selected = self.idea_manager.get_by_id(self.selected_idea["id"])
                if updated_selected is not None:
                    self.show_idea_details(updated_selected)

    def show_idea_details(self, idea: dict):
        self.selected_idea = idea
        self.details_title.configure(text=idea["title"])
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self._update_favorite_button_state()

        status_color = get_status_color(idea["status"])
        self.status_badge.configure(text=f'Статус: {idea["status"]}', fg_color=status_color)

        details = (
            f'Ключевая фишка: {idea["hook"]}\n\n'
            f'Описание: {idea["short_description"]}\n\n'
            f'Жанр: {idea["genre"]}\n'
            f'Механика: {idea["mechanic"]}\n'
            f'Масштаб: {idea["scale"]}\n'
            f'Перспектива: {idea["perspective"]}\n'
            f'Платформа: {idea["platform"]}\n'
            f'Проработка: {idea["readiness"]}\n'
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
        self._update_favorite_button_state()
        self.status_badge.configure(text="", fg_color=CARD_BORDER)

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", "Здесь будут показаны подробности выбранной идеи.")
        self.details_text.configure(state="disabled")

    def open_add_dialog(self):
        IdeaDialog(self, self.handle_add_idea)

    def handle_add_idea(self, idea_data: dict):
        new_idea = self.idea_manager.add_idea(idea_data)
        save_ideas(self.data_file, self.idea_manager.get_all())

        self.apply_filters()
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
        self.apply_filters()
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
        self.apply_filters()
        self.clear_details()

    def toggle_selected_favorite(self):
        if self.selected_idea is None:
            messagebox.showwarning("Предупреждение", "Сначала выбери идею.")
            return

        was_toggled = self.idea_manager.toggle_favorite(self.selected_idea["id"])
        if not was_toggled:
            messagebox.showerror("Ошибка", "Не удалось изменить избранное.")
            return

        save_ideas(self.data_file, self.idea_manager.get_all())

        updated_idea = self.idea_manager.get_by_id(self.selected_idea["id"])
        self.apply_filters()

        if updated_idea is not None:
            visible_ids = {idea["id"] for idea in self.filtered_ideas}

            if updated_idea["id"] in visible_ids:
                self.show_idea_details(updated_idea)
            else:
                self.clear_details()

    def show_random_idea(self):
        random_idea = self.idea_manager.get_random_idea(self.filtered_ideas)

        if random_idea is None:
            messagebox.showinfo("Случайная идея", "Нет идей для выбора.")
            return

        self.show_idea_details(random_idea)
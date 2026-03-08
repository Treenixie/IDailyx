import customtkinter as ctk
from tkinter import messagebox

from core.constants import (
    GENRES,
    MECHANICS,
    SCALES,
    PERSPECTIVES,
    PLATFORMS,
    READINESS_OPTIONS,
    STATUS_OPTIONS,
)


class IdeaDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save):
        super().__init__(master)

        self.on_save = on_save

        self.title("Новая идея")
        self.geometry("720x760")
        self.minsize(620, 600)
        self.configure(fg_color="#16181d")

        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkScrollableFrame(
            self,
            corner_radius=16,
            fg_color="#1d2128"
        )
        self.container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self._build_form()
        self.after(100, lambda: self.title_entry.focus())

    def _build_form(self):
        title_label = ctk.CTkLabel(
            self.container,
            text="Новая идея",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        title_label.pack(anchor="w", padx=12, pady=(12, 16))

        self.title_entry = self._create_entry("Название")
        self.hook_entry = self._create_entry("Ключевая фишка")

        self.short_description_text = self._create_textbox(
            "Краткое описание",
            height=120
        )

        self.genre_menu = self._create_option_menu("Жанр", GENRES, "Неотсортированные")
        self.mechanic_menu = self._create_option_menu("Основная механика", MECHANICS, "Не выбрано")
        self.scale_menu = self._create_option_menu("Масштаб", SCALES, "Не выбрано")
        self.perspective_menu = self._create_option_menu("Перспектива", PERSPECTIVES, "Не выбрано")
        self.platform_menu = self._create_option_menu("Платформа", PLATFORMS, "Не выбрано")
        self.readiness_menu = self._create_option_menu("Проработка", READINESS_OPTIONS, "черновая идея")
        self.status_menu = self._create_option_menu("Статус", STATUS_OPTIONS, "новая")

        self.tags_entry = self._create_entry("Теги через запятую")

        self.notes_text = self._create_textbox(
            "Заметки",
            height=140
        )

        self.favorite_var = ctk.BooleanVar(value=False)
        self.favorite_checkbox = ctk.CTkCheckBox(
            self.container,
            text="Добавить в избранное",
            variable=self.favorite_var
        )
        self.favorite_checkbox.pack(anchor="w", padx=12, pady=(8, 16))

        buttons_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=12, pady=(0, 16))

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Сохранить",
            command=self._save
        )
        save_button.pack(side="left", padx=(0, 10))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            fg_color="#3a3f4b",
            hover_color="#4a5160",
            command=self.destroy
        )
        cancel_button.pack(side="left")

    def _create_entry(self, label_text: str):
        label = ctk.CTkLabel(self.container, text=label_text)
        label.pack(anchor="w", padx=12, pady=(8, 4))

        entry = ctk.CTkEntry(self.container)
        entry.pack(fill="x", padx=12, pady=(0, 8))

        return entry

    def _create_textbox(self, label_text: str, height: int = 100):
        label = ctk.CTkLabel(self.container, text=label_text)
        label.pack(anchor="w", padx=12, pady=(8, 4))

        textbox = ctk.CTkTextbox(self.container, height=height)
        textbox.pack(fill="x", padx=12, pady=(0, 8))

        return textbox

    def _create_option_menu(self, label_text: str, values: list[str], default_value: str):
        label = ctk.CTkLabel(self.container, text=label_text)
        label.pack(anchor="w", padx=12, pady=(8, 4))

        menu = ctk.CTkOptionMenu(self.container, values=values)
        menu.pack(fill="x", padx=12, pady=(0, 8))
        menu.set(default_value)

        return menu

    def _save(self):
        title = self.title_entry.get().strip()

        if not title:
            messagebox.showerror("Ошибка", "Введите название идеи.")
            return

        tags_raw = self.tags_entry.get().strip()
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()]

        idea_data = {
            "title": title,
            "hook": self.hook_entry.get().strip(),
            "short_description": self.short_description_text.get("1.0", "end").strip(),
            "genre": self.genre_menu.get(),
            "mechanic": self.mechanic_menu.get(),
            "scale": self.scale_menu.get(),
            "perspective": self.perspective_menu.get(),
            "platform": self.platform_menu.get(),
            "readiness": self.readiness_menu.get(),
            "status": self.status_menu.get(),
            "tags": tags,
            "notes": self.notes_text.get("1.0", "end").strip(),
            "favorite": self.favorite_var.get(),
        }

        self.on_save(idea_data)
        self.destroy()
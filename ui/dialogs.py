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
from ui.styles import (
    APP_BG,
    PANEL_BG,
    INPUT_BG,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    ACCENT,
    ACCENT_HOVER,
    BUTTON_NEUTRAL,
    BUTTON_NEUTRAL_HOVER,
    CARD_BORDER,
    LINE_COLOR,
    ui_font,
)


class IdeaDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save, idea=None):
        super().__init__(master)

        self.on_save = on_save
        self.idea = idea
        self.is_edit_mode = idea is not None

        self.title("Редактирование идеи" if self.is_edit_mode else "Новая идея")
        self.geometry("720x760")
        self.minsize(620, 600)
        self.configure(fg_color=APP_BG)

        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkScrollableFrame(
            self,
            corner_radius=18,
            fg_color=PANEL_BG
        )
        self.container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self._build_form()

        if self.is_edit_mode:
            self._fill_form()

        self.after(100, lambda: self.title_entry.focus())

    def _build_form(self):
        title_label = ctk.CTkLabel(
            self.container,
            text="Редактирование идеи" if self.is_edit_mode else "Новая идея",
            text_color=TEXT_PRIMARY,
            font=ui_font(22, "bold")
        )
        title_label.pack(anchor="w", padx=12, pady=(12, 6))

        divider = ctk.CTkFrame(self.container, height=1, fg_color=LINE_COLOR)
        divider.pack(fill="x", padx=12, pady=(0, 14))

        self.title_entry = self._create_entry("Название")

        self.short_description_text = self._create_textbox(
            "Описание",
            height=140
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
            variable=self.favorite_var,
            text_color=TEXT_PRIMARY,
            font=ui_font(13)
        )
        self.favorite_checkbox.pack(anchor="w", padx=12, pady=(8, 16))

        buttons_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=12, pady=(0, 16))

        save_button = ctk.CTkButton(
            buttons_frame,
            text="Сохранить",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=APP_BG,
            font=ui_font(13, "bold"),
            command=self._save
        )
        save_button.pack(side="left", padx=(0, 10))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            fg_color=BUTTON_NEUTRAL,
            hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            font=ui_font(13, "bold"),
            command=self.destroy
        )
        cancel_button.pack(side="left")

    def _bind_text_widget_shortcuts(self, widget):
        widget.bind("<Control-a>", self._select_all)
        widget.bind("<Control-A>", self._select_all)
        widget.bind("<Control-c>", self._copy_selection)
        widget.bind("<Control-C>", self._copy_selection)
        widget.bind("<Control-v>", self._paste_selection)
        widget.bind("<Control-V>", self._paste_selection)
        widget.bind("<Control-x>", self._cut_selection)
        widget.bind("<Control-X>", self._cut_selection)

    def _copy_selection(self, event):
        event.widget.event_generate("<<Copy>>")
        return "break"

    def _paste_selection(self, event):
        event.widget.event_generate("<<Paste>>")
        return "break"

    def _cut_selection(self, event):
        event.widget.event_generate("<<Cut>>")
        return "break"

    def _select_all(self, event):
        widget = event.widget

        if hasattr(widget, "tag_add"):
            try:
                widget.tag_add("sel", "1.0", "end")
                widget.mark_set("insert", "1.0")
                widget.see("insert")
            except Exception:
                pass
        elif hasattr(widget, "select_range"):
            try:
                widget.select_range(0, "end")
                widget.icursor("end")
            except Exception:
                pass

        return "break"

    def _fill_form(self):
        self.title_entry.insert(0, self.idea["title"])
        self.short_description_text.insert("1.0", self.idea.get("short_description", ""))

        self.genre_menu.set(self.idea["genre"])
        self.mechanic_menu.set(self.idea["mechanic"])
        self.scale_menu.set(self.idea["scale"])
        self.perspective_menu.set(self.idea["perspective"])
        self.platform_menu.set(self.idea["platform"])
        self.readiness_menu.set(self.idea["readiness"])
        self.status_menu.set(self.idea["status"])

        self.tags_entry.insert(0, ", ".join(self.idea["tags"]))
        self.notes_text.insert("1.0", self.idea["notes"])
        self.favorite_var.set(self.idea["favorite"])

    def _create_entry(self, label_text: str):
        label = ctk.CTkLabel(
            self.container,
            text=label_text,
            text_color=TEXT_SECONDARY,
            font=ui_font(13, "bold")
        )
        label.pack(anchor="w", padx=12, pady=(8, 4))

        entry = ctk.CTkEntry(
            self.container,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            border_color=CARD_BORDER,
            font=ui_font(14)
        )
        entry.pack(fill="x", padx=12, pady=(0, 8))
        self._bind_text_widget_shortcuts(entry)

        return entry

    def _create_textbox(self, label_text: str, height: int = 100):
        label = ctk.CTkLabel(
            self.container,
            text=label_text,
            text_color=TEXT_SECONDARY,
            font=ui_font(13, "bold")
        )
        label.pack(anchor="w", padx=12, pady=(8, 4))

        textbox = ctk.CTkTextbox(
            self.container,
            height=height,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=CARD_BORDER,
            font=ui_font(14)
        )
        textbox.pack(fill="x", padx=12, pady=(0, 8))
        self._bind_text_widget_shortcuts(textbox)

        return textbox

    def _create_option_menu(self, label_text: str, values: list[str], default_value: str):
        label = ctk.CTkLabel(
            self.container,
            text=label_text,
            text_color=TEXT_SECONDARY,
            font=ui_font(13, "bold")
        )
        label.pack(anchor="w", padx=12, pady=(8, 4))

        menu = ctk.CTkOptionMenu(
            self.container,
            values=values,
            fg_color=BUTTON_NEUTRAL,
            button_color=BUTTON_NEUTRAL,
            button_hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            font=ui_font(13),
            dropdown_font=ui_font(13)
        )
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
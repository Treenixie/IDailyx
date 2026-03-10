from tkinter import messagebox

import tkinter as tk
import customtkinter as ctk

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
from ui.window_utils import apply_window_icon


class IdeaDialog(ctk.CTkToplevel):
    def __init__(self, master, on_save, idea=None):
        super().__init__(master)

        self.on_save = on_save
        self.idea = idea
        self.is_edit_mode = idea is not None
        self.context_widget = None

        self.text_context_menu = tk.Menu(self, tearoff=0)
        self.text_context_menu.add_command(label="Отменить", command=self._context_undo)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="Вырезать", command=self._context_cut)
        self.text_context_menu.add_command(label="Копировать", command=self._context_copy)
        self.text_context_menu.add_command(label="Вставить", command=self._context_paste)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="Выделить всё", command=self._context_select_all)

        self.title("Редактирование идеи" if self.is_edit_mode else "Новая идея")
        self.geometry("720x760")
        self.minsize(620, 600)
        self.configure(fg_color=APP_BG)

        self.transient(master)
        self.grab_set()
        self.after(50, lambda: apply_window_icon(self))

        self._setup_global_shortcuts()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.container = ctk.CTkScrollableFrame(
            self,
            corner_radius=18,
            fg_color=PANEL_BG,
        )
        self.container.grid(row=0, column=0, sticky="nsew", padx=16, pady=16)

        self._build_form()

        if self.is_edit_mode:
            self._fill_form()

        self.after(100, lambda: self.title_entry.focus())

    def _setup_global_shortcuts(self):
        self.bind_all("<Control-KeyPress>", self._handle_global_ctrl_shortcuts, add="+")
        self.bind_all("<Button-3>", self._show_text_context_menu, add="+")

    def _is_text_input_widget(self, widget) -> bool:
        if widget is None:
            return False
        return isinstance(widget, (tk.Entry, tk.Text)) or widget.winfo_class() in {"Entry", "Text"}

    def _get_focused_text_widget(self, event=None):
        widget = self.focus_get()
        if self._is_text_input_widget(widget):
            return widget

        if event is not None and self._is_text_input_widget(event.widget):
            return event.widget

        return None

    def _handle_global_ctrl_shortcuts(self, event):
        widget = self._get_focused_text_widget(event)
        if widget is None:
            return

        key = event.keysym.lower()

        if key == "a":
            self._select_all_widget(widget)
            return "break"
        if key == "c":
            self._copy_widget_selection(widget)
            return "break"
        if key == "x":
            self._cut_widget_selection(widget)
            return "break"
        if key == "v":
            self._paste_into_widget(widget)
            return "break"
        if key == "z":
            self._undo_widget(widget)
            return "break"

    def _select_all_widget(self, widget):
        try:
            if isinstance(widget, tk.Text):
                widget.tag_add("sel", "1.0", "end-1c")
                widget.mark_set("insert", "1.0")
                widget.see("insert")
            elif isinstance(widget, tk.Entry):
                widget.select_range(0, "end")
                widget.icursor("end")
        except Exception:
            pass

    def _copy_widget_selection(self, widget):
        try:
            text = ""
            if isinstance(widget, tk.Text):
                if widget.tag_ranges("sel"):
                    text = widget.get("sel.first", "sel.last")
            elif isinstance(widget, tk.Entry):
                if widget.selection_present():
                    text = widget.selection_get()

            if text:
                self.clipboard_clear()
                self.clipboard_append(text)
        except Exception:
            pass

    def _cut_widget_selection(self, widget):
        try:
            self._copy_widget_selection(widget)

            if isinstance(widget, tk.Text):
                if widget.tag_ranges("sel"):
                    widget.delete("sel.first", "sel.last")
            elif isinstance(widget, tk.Entry):
                if widget.selection_present():
                    start = widget.index("sel.first")
                    end = widget.index("sel.last")
                    widget.delete(start, end)
        except Exception:
            pass

    def _paste_into_widget(self, widget):
        try:
            text = self.clipboard_get()
        except Exception:
            return

        try:
            if isinstance(widget, tk.Text):
                if widget.tag_ranges("sel"):
                    widget.delete("sel.first", "sel.last")
                widget.insert("insert", text)
            elif isinstance(widget, tk.Entry):
                if widget.selection_present():
                    start = widget.index("sel.first")
                    end = widget.index("sel.last")
                    widget.delete(start, end)
                widget.insert("insert", text)
        except Exception:
            pass

    def _undo_widget(self, widget):
        try:
            if isinstance(widget, tk.Text):
                widget.edit_undo()
            elif isinstance(widget, tk.Entry):
                widget.event_generate("<<Undo>>")
        except Exception:
            pass

    def _show_text_context_menu(self, event):
        widget = event.widget
        if not self._is_text_input_widget(widget):
            return

        self.context_widget = widget
        try:
            self.text_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.text_context_menu.grab_release()

    def _context_undo(self):
        if self.context_widget is not None:
            self._undo_widget(self.context_widget)

    def _context_copy(self):
        if self.context_widget is not None:
            self._copy_widget_selection(self.context_widget)

    def _context_cut(self):
        if self.context_widget is not None:
            self._cut_widget_selection(self.context_widget)

    def _context_paste(self):
        if self.context_widget is not None:
            self._paste_into_widget(self.context_widget)

    def _context_select_all(self):
        if self.context_widget is not None:
            self._select_all_widget(self.context_widget)

    def _build_form(self):
        title_label = ctk.CTkLabel(
            self.container,
            text="Редактирование идеи" if self.is_edit_mode else "Новая идея",
            text_color=TEXT_PRIMARY,
            font=ui_font(22, "bold"),
        )
        title_label.pack(anchor="w", padx=12, pady=(12, 6))

        divider = ctk.CTkFrame(self.container, height=1, fg_color=LINE_COLOR)
        divider.pack(fill="x", padx=12, pady=(0, 14))

        self.title_entry = self._create_entry("Название")
        self.short_description_text = self._create_textbox("Описание", height=140)

        self.genre_menu = self._create_option_menu("Жанр", GENRES, "Неотсортированные")
        self.mechanic_menu = self._create_option_menu("Основная механика", MECHANICS, "Не выбрано")
        self.scale_menu = self._create_option_menu("Масштаб", SCALES, "Не выбрано")
        self.perspective_menu = self._create_option_menu("Перспектива", PERSPECTIVES, "Не выбрано")
        self.platform_menu = self._create_option_menu("Платформа", PLATFORMS, "Не выбрано")
        self.readiness_menu = self._create_option_menu("Проработка", READINESS_OPTIONS, "черновая идея")
        self.status_menu = self._create_option_menu("Статус", STATUS_OPTIONS, "новая")

        self.tags_entry = self._create_entry("Теги через запятую")
        self.notes_text = self._create_textbox("Заметки", height=140)

        self.favorite_var = ctk.BooleanVar(value=False)
        self.favorite_checkbox = ctk.CTkCheckBox(
            self.container,
            text="Добавить в избранное",
            variable=self.favorite_var,
            text_color=TEXT_PRIMARY,
            font=ui_font(13),
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
            font=ui_font(13),
            command=self._save,
        )
        save_button.pack(side="left", padx=(0, 10))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Отмена",
            fg_color=BUTTON_NEUTRAL,
            hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            font=ui_font(13),
            command=self.destroy,
        )
        cancel_button.pack(side="left")

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
            font=ui_font(13, "bold"),
        )
        label.pack(anchor="w", padx=12, pady=(8, 4))

        entry = ctk.CTkEntry(
            self.container,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            border_color=CARD_BORDER,
            font=ui_font(14),
        )
        entry.pack(fill="x", padx=12, pady=(0, 8))

        try:
            entry._entry.configure(undo=True)
        except Exception:
            pass

        return entry

    def _create_textbox(self, label_text: str, height: int = 100):
        label = ctk.CTkLabel(
            self.container,
            text=label_text,
            text_color=TEXT_SECONDARY,
            font=ui_font(13, "bold"),
        )
        label.pack(anchor="w", padx=12, pady=(8, 4))

        textbox = ctk.CTkTextbox(
            self.container,
            height=height,
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            border_width=1,
            border_color=CARD_BORDER,
            font=ui_font(14),
            undo=True,
        )
        textbox.pack(fill="x", padx=12, pady=(0, 8))

        try:
            textbox._textbox.configure(undo=True, autoseparators=True, maxundo=-1)
        except Exception:
            pass

        return textbox

    def _create_option_menu(self, label_text: str, values: list[str], default_value: str):
        label = ctk.CTkLabel(
            self.container,
            text=label_text,
            text_color=TEXT_SECONDARY,
            font=ui_font(13, "bold"),
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
            dropdown_font=ui_font(13),
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
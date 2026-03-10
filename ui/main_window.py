from functools import partial
from tkinter import filedialog, messagebox

import tkinter as tk
import customtkinter as ctk
from PIL import Image

from core.constants import STATUS_OPTIONS, READINESS_OPTIONS, MECHANICS
from core.paths import get_asset_path
from core.storage import save_ideas
from ui.dialogs import IdeaDialog
from ui.window_utils import apply_window_icon
from ui.styles import (
    APP_BG,
    PANEL_BG,
    CARD_BG,
    INPUT_BG,
    CARD_BORDER,
    LINE_COLOR,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    ACCENT,
    ACCENT_HOVER,
    DANGER,
    DANGER_HOVER,
    BUTTON_NEUTRAL,
    BUTTON_NEUTRAL_HOVER,
    get_status_color,
    get_sidebar_button_colors,
    ui_font,
)

FAVORITES_LABEL = "★ Избранное"


class MainWindow(ctk.CTk):
    def __init__(self, idea_manager, data_file: str):
        super().__init__()

        self.section_title_font = ui_font(18, "bold")
        self.button_font = ui_font(13)

        self.idea_manager = idea_manager
        self.data_file = data_file
        self.selected_idea = None
        self.filtered_ideas = []
        self.current_sidebar_filter = "Все идеи"
        self.sidebar_buttons = {}

        self.logo_image = None
        self.context_widget = None

        self.text_context_menu = tk.Menu(self, tearoff=0)
        self.text_context_menu.add_command(label="Отменить", command=self._context_undo)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="Вырезать", command=self._context_cut)
        self.text_context_menu.add_command(label="Копировать", command=self._context_copy)
        self.text_context_menu.add_command(label="Вставить", command=self._context_paste)
        self.text_context_menu.add_separator()
        self.text_context_menu.add_command(label="Выделить всё", command=self._context_select_all)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("IDailyx")
        self.geometry("1450x860")
        self.minsize(1180, 700)
        self.configure(fg_color=APP_BG)

        self._load_brand_assets()
        self._build_layout()
        self.after(50, lambda: apply_window_icon(self))
        self._setup_global_shortcuts()
        self._setup_mousewheel_support()
        self._update_sidebar_button_styles()
        self._update_status_filter_style()
        self.apply_filters()

    def _load_brand_assets(self):
        logo_path = get_asset_path("logo.png")
        if logo_path:
            try:
                pil_logo = Image.open(logo_path)
                logo_width, logo_height = pil_logo.size

                target_height = 80
                target_width = max(1, int(logo_width * (target_height / logo_height)))

                self.logo_image = ctk.CTkImage(
                    light_image=pil_logo,
                    dark_image=pil_logo,
                    size=(target_width, target_height),
                )
            except Exception:
                self.logo_image = None

    def _build_layout(self):
        self.grid_columnconfigure(0, minsize=220, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, minsize=390, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.top_bar = ctk.CTkFrame(self, corner_radius=18, fg_color=PANEL_BG)
        self.top_bar.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=12, pady=(12, 6))

        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=18, fg_color=PANEL_BG)
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(12, 6), pady=(6, 12))
        self.sidebar.grid_propagate(False)

        self.center_panel = ctk.CTkFrame(self, corner_radius=18, fg_color=PANEL_BG)
        self.center_panel.grid(row=1, column=1, sticky="nsew", padx=6, pady=(6, 12))

        self.details_panel = ctk.CTkFrame(self, width=390, corner_radius=18, fg_color=PANEL_BG)
        self.details_panel.grid(row=1, column=2, sticky="nsew", padx=(6, 12), pady=(6, 12))
        self.details_panel.grid_propagate(False)

        self._build_top_bar()
        self._build_sidebar()
        self._build_center_panel()
        self._build_details_panel()

    def _build_top_bar(self):
        self.top_bar.grid_columnconfigure(0, weight=0)
        self.top_bar.grid_columnconfigure(1, weight=1)
        self.top_bar.grid_columnconfigure(2, weight=0)

        if self.logo_image is not None:
            logo_label = ctk.CTkLabel(self.top_bar, text="", image=self.logo_image)
        else:
            logo_label = ctk.CTkLabel(
                self.top_bar,
                text="IDailyx",
                text_color=TEXT_PRIMARY,
                font=ui_font(30, "bold"),
            )

        logo_label.grid(row=0, column=0, rowspan=2, padx=(16, 14), pady=14, sticky="n")

        center_block = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        center_block.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(0, 12), pady=14)
        center_block.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            center_block,
            placeholder_text="Поиск идей...",
            fg_color=INPUT_BG,
            text_color=TEXT_PRIMARY,
            placeholder_text_color=TEXT_MUTED,
            border_color=CARD_BORDER,
            height=36,
            font=ui_font(14),
        )
        self.search_entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.search_entry.bind("<KeyRelease>", self._on_search_change)

        try:
            self.search_entry._entry.configure(undo=True)
        except Exception:
            pass

        filters_left = ctk.CTkFrame(center_block, fg_color="transparent")
        filters_left.grid(row=1, column=0, sticky="w")

        self.status_menu = ctk.CTkOptionMenu(
            filters_left,
            values=["Все статусы"] + STATUS_OPTIONS,
            command=self._on_filter_change,
            width=170,
            height=34,
            fg_color=BUTTON_NEUTRAL,
            button_color=BUTTON_NEUTRAL,
            button_hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            dropdown_fg_color=PANEL_BG,
            dropdown_hover_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            font=self.button_font,
            dropdown_font=self.button_font,
        )
        self.status_menu.pack(side="left", padx=(0, 8))
        self.status_menu.set("Все статусы")

        self.readiness_menu = ctk.CTkOptionMenu(
            filters_left,
            values=["Вся проработка"] + READINESS_OPTIONS,
            command=self._on_filter_change,
            width=190,
            height=34,
            fg_color=BUTTON_NEUTRAL,
            button_color=BUTTON_NEUTRAL,
            button_hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            dropdown_fg_color=PANEL_BG,
            dropdown_hover_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            font=self.button_font,
            dropdown_font=self.button_font,
        )
        self.readiness_menu.pack(side="left", padx=(0, 8))
        self.readiness_menu.set("Вся проработка")

        self.mechanic_menu = ctk.CTkOptionMenu(
            filters_left,
            values=["Все механики"] + MECHANICS,
            command=self._on_filter_change,
            width=210,
            height=34,
            fg_color=BUTTON_NEUTRAL,
            button_color=BUTTON_NEUTRAL,
            button_hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            dropdown_fg_color=PANEL_BG,
            dropdown_hover_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            font=self.button_font,
            dropdown_font=self.button_font,
        )
        self.mechanic_menu.pack(side="left")
        self.mechanic_menu.set("Все механики")

        right_block = ctk.CTkFrame(self.top_bar, fg_color="transparent")
        right_block.grid(row=0, column=2, rowspan=2, sticky="ne", padx=(0, 16), pady=14)

        actions_row = ctk.CTkFrame(right_block, fg_color="transparent")
        actions_row.pack(anchor="e", pady=(0, 10))

        self.new_button = ctk.CTkButton(
            actions_row,
            text="+ Новая идея",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=APP_BG,
            width=140,
            height=34,
            font=self.button_font,
            command=self.open_add_dialog,
        )
        self.new_button.pack(side="left", padx=(0, 8))

        self.random_button = ctk.CTkButton(
            actions_row,
            text="Случайная идея",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=APP_BG,
            width=140,
            height=34,
            font=self.button_font,
            command=self.show_random_idea,
        )
        self.random_button.pack(side="left", padx=(0, 8))

        self.export_button = ctk.CTkButton(
            actions_row,
            text="Экспорт .txt",
            fg_color=BUTTON_NEUTRAL,
            hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            width=140,
            height=34,
            font=self.button_font,
            command=self.export_filtered_ideas,
        )
        self.export_button.pack(side="left")

        filters_right = ctk.CTkFrame(right_block, fg_color="transparent")
        filters_right.pack(anchor="e")

        self.reset_filters_button = ctk.CTkButton(
            filters_right,
            text="Сбросить фильтры",
            fg_color=BUTTON_NEUTRAL,
            hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            width=150,
            height=34,
            font=self.button_font,
            command=self.reset_filters,
        )
        self.reset_filters_button.pack(side="left", padx=(0, 8))

        self.sort_menu = ctk.CTkOptionMenu(
            filters_right,
            values=[
                "Сначала новые",
                "Сначала старые",
                "Недавно изменённые",
                "По названию (А-Я)",
                "По названию (Я-А)",
            ],
            command=self._on_filter_change,
            width=190,
            height=34,
            fg_color=BUTTON_NEUTRAL,
            button_color=BUTTON_NEUTRAL,
            button_hover_color=BUTTON_NEUTRAL_HOVER,
            text_color=APP_BG,
            dropdown_fg_color=PANEL_BG,
            dropdown_hover_color=CARD_BG,
            dropdown_text_color=TEXT_PRIMARY,
            font=self.button_font,
            dropdown_font=self.button_font,
        )
        self.sort_menu.pack(side="left")
        self.sort_menu.set("Сначала новые")

    def _build_sidebar(self):
        title = ctk.CTkLabel(
            self.sidebar,
            text="Жанры",
            text_color=TEXT_PRIMARY,
            font=self.section_title_font,
            anchor="w",
            justify="left",
        )
        title.pack(fill="x", padx=20, pady=(16, 6))

        divider = ctk.CTkFrame(self.sidebar, height=1, fg_color=LINE_COLOR)
        divider.pack(fill="x", padx=20, pady=(0, 12))

        top_categories = [
            FAVORITES_LABEL,
            "Неотсортированные",
            "Все идеи",
        ]

        other_categories = [
            "Платформеры",
            "Шутеры",
            "Головоломки",
            "Хорроры",
            "Рогалики",
            "Приключения",
            "Стратегии",
            "Симуляторы",
            "Мультиплеер",
        ]

        ctk.CTkFrame(self.sidebar, height=4, fg_color="transparent").pack(fill="x", padx=12, pady=(0, 2))

        for category in top_categories:
            button = ctk.CTkButton(
                self.sidebar,
                text=category,
                anchor="w",
                text_color=TEXT_PRIMARY,
                text_color_disabled=TEXT_MUTED,
                font=self.button_font,
                command=partial(self.set_sidebar_filter, category),
            )
            button.pack(fill="x", padx=12, pady=4)
            self.sidebar_buttons[category] = button

        ctk.CTkFrame(self.sidebar, height=14, fg_color="transparent").pack(fill="x", padx=12, pady=(4, 6))

        for category in other_categories:
            button = ctk.CTkButton(
                self.sidebar,
                text=category,
                anchor="w",
                text_color=TEXT_PRIMARY,
                text_color_disabled=TEXT_MUTED,
                font=self.button_font,
                command=partial(self.set_sidebar_filter, category),
            )
            button.pack(fill="x", padx=12, pady=4)
            self.sidebar_buttons[category] = button

    def _build_center_panel(self):
        title = ctk.CTkLabel(
            self.center_panel,
            text="Архив идей",
            text_color=TEXT_PRIMARY,
            font=self.section_title_font,
            anchor="w",
            justify="left",
        )
        title.pack(fill="x", padx=28, pady=(16, 6))

        divider = ctk.CTkFrame(self.center_panel, height=1, fg_color=LINE_COLOR)
        divider.pack(fill="x", padx=28, pady=(0, 12))

        ctk.CTkFrame(self.center_panel, height=4, fg_color="transparent").pack(fill="x", padx=12, pady=(0, 2))

        self.idea_listbox = ctk.CTkScrollableFrame(self.center_panel, fg_color="transparent")
        self.idea_listbox.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_details_panel(self):
        self.details_header = ctk.CTkFrame(self.details_panel, fg_color="transparent")
        self.details_header.pack(fill="x", padx=16, pady=(16, 6))

        self.details_header.grid_columnconfigure(0, weight=1)
        self.details_header.grid_columnconfigure(1, weight=0)

        self.details_title = ctk.CTkLabel(
            self.details_header,
            text="Карточка идеи",
            text_color=TEXT_PRIMARY,
            font=self.section_title_font,
            anchor="w",
            justify="left",
        )
        self.details_title.grid(row=0, column=0, sticky="w")

        self.favorite_button = ctk.CTkButton(
            self.details_header,
            text="☆",
            width=38,
            height=38,
            corner_radius=10,
            fg_color=INPUT_BG,
            hover_color=CARD_BG,
            border_width=2,
            border_color=ACCENT,
            text_color=ACCENT,
            font=ui_font(18, "bold"),
            command=self.toggle_selected_favorite,
            state="disabled",
        )
        self.favorite_button.grid(row=0, column=1, sticky="e")

        divider = ctk.CTkFrame(self.details_panel, height=1, fg_color=LINE_COLOR)
        divider.pack(fill="x", padx=16, pady=(0, 12))

        self.details_buttons_frame = ctk.CTkFrame(self.details_panel, fg_color="transparent")
        self.details_buttons_frame.pack(fill="x", padx=12, pady=(0, 8))

        self.details_buttons_frame.grid_columnconfigure(0, weight=1)
        self.details_buttons_frame.grid_columnconfigure(1, weight=1)

        self.edit_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="Редактировать",
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color=APP_BG,
            text_color_disabled="#6F6258",
            font=self.button_font,
            command=self.open_edit_dialog,
            state="disabled",
        )
        self.edit_button.grid(row=0, column=0, sticky="ew", padx=(0, 8))

        self.delete_button = ctk.CTkButton(
            self.details_buttons_frame,
            text="Удалить",
            fg_color=DANGER,
            hover_color=DANGER_HOVER,
            text_color=APP_BG,
            text_color_disabled="#6F6258",
            font=self.button_font,
            command=self.delete_selected_idea,
            state="disabled",
        )
        self.delete_button.grid(row=0, column=1, sticky="ew")

        self.details_content = ctk.CTkScrollableFrame(
            self.details_panel,
            fg_color=INPUT_BG,
            corner_radius=12,
        )
        self.details_content.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self._hide_favorite_button()
        self._show_empty_details_state()

    def _setup_global_shortcuts(self):
        self.bind_all("<Control-KeyPress>", self._handle_global_ctrl_shortcuts, add="+")
        self.bind_all("<Button-3>", self._show_text_context_menu, add="+")

    def _setup_mousewheel_support(self):
        self.bind_all("<MouseWheel>", self._on_global_mousewheel, add="+")
        self.bind_all("<Button-4>", self._on_global_mousewheel_linux_up, add="+")
        self.bind_all("<Button-5>", self._on_global_mousewheel_linux_down, add="+")

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

    def _get_scroll_canvas_under_pointer(self):
        widget = self.winfo_containing(self.winfo_pointerx(), self.winfo_pointery())
        if widget is None:
            return None

        candidates = [self.idea_listbox, self.details_content]

        current = widget
        while current is not None:
            for frame in candidates:
                if current == frame:
                    canvas = getattr(frame, "_parent_canvas", None) or getattr(frame, "_canvas", None)
                    if canvas is not None:
                        return canvas
            current = current.master

        return None

    def _on_global_mousewheel(self, event):
        canvas = self._get_scroll_canvas_under_pointer()
        if canvas is None:
            return

        if event.delta > 0:
            canvas.yview_scroll(-1, "units")
        elif event.delta < 0:
            canvas.yview_scroll(1, "units")

        return "break"

    def _on_global_mousewheel_linux_up(self, event):
        canvas = self._get_scroll_canvas_under_pointer()
        if canvas is None:
            return
        canvas.yview_scroll(-1, "units")
        return "break"

    def _on_global_mousewheel_linux_down(self, event):
        canvas = self._get_scroll_canvas_under_pointer()
        if canvas is None:
            return
        canvas.yview_scroll(1, "units")
        return "break"

    def _fill_idea_list(self, ideas: list[dict]):
        for widget in self.idea_listbox.winfo_children():
            widget.destroy()

        if not ideas:
            empty_label = ctk.CTkLabel(
                self.idea_listbox,
                text="Ничего не найдено.\nИзмени поиск или сбрось фильтры.",
                text_color=TEXT_MUTED,
                justify="left",
                anchor="w",
                font=ui_font(14),
            )
            empty_label.pack(fill="x", padx=8, pady=8)
            return

        self.update_idletasks()
        preview_wrap = max(520, self.idea_listbox.winfo_width() - 40)

        for idea in ideas:
            status_color = get_status_color(idea["status"])

            card = ctk.CTkFrame(
                self.idea_listbox,
                corner_radius=18,
                fg_color=CARD_BG,
                border_width=1,
                border_color=status_color,
            )
            card.pack(fill="x", padx=4, pady=6)

            title_text = f'★ {idea["title"]}' if idea["favorite"] else idea["title"]

            title = ctk.CTkLabel(
                card,
                text=title_text,
                text_color=status_color,
                font=ui_font(18, "bold"),
                justify="left",
                anchor="w",
            )
            title.pack(fill="x", padx=12, pady=(10, 2))

            subtitle = ctk.CTkLabel(
                card,
                text=f'{idea["genre"]} • {idea["status"]} • {idea["readiness"]}',
                text_color=TEXT_SECONDARY,
                font=ui_font(12, "bold"),
                justify="left",
                anchor="w",
            )
            subtitle.pack(fill="x", padx=12, pady=(0, 2))

            description_preview = idea.get("short_description", "").strip() or "Без описания"

            preview = ctk.CTkLabel(
                card,
                text=description_preview,
                text_color=TEXT_PRIMARY,
                wraplength=preview_wrap,
                justify="left",
                anchor="w",
                font=ui_font(13),
            )
            preview.pack(fill="x", padx=12, pady=(2, 10))

            click_handler = partial(self._handle_idea_click, idea)

            card.bind("<Button-1>", click_handler)
            title.bind("<Button-1>", click_handler)
            subtitle.bind("<Button-1>", click_handler)
            preview.bind("<Button-1>", click_handler)

    def _handle_idea_click(self, idea: dict, event=None):
        self.show_idea_details(idea)

    def _on_search_change(self, event=None):
        self.apply_filters()

    def _on_filter_change(self, _value=None):
        self._update_status_filter_style()
        self.apply_filters()

    def _update_status_filter_style(self):
        current_status = self.status_menu.get()

        if current_status == "Все статусы":
            self.status_menu.configure(
                fg_color=BUTTON_NEUTRAL,
                button_color=BUTTON_NEUTRAL,
                button_hover_color=BUTTON_NEUTRAL_HOVER,
                text_color=APP_BG,
            )
        else:
            status_color = get_status_color(current_status)
            self.status_menu.configure(
                fg_color=status_color,
                button_color=status_color,
                button_hover_color=status_color,
                text_color=APP_BG,
            )

    def set_sidebar_filter(self, category: str):
        self.current_sidebar_filter = category
        self._update_sidebar_button_styles()
        self.apply_filters()

    def _update_sidebar_button_styles(self):
        for category, button in self.sidebar_buttons.items():
            fg_color, hover_color = get_sidebar_button_colors(category == self.current_sidebar_filter)
            button.configure(fg_color=fg_color, hover_color=hover_color)

    def _show_favorite_button(self):
        self.favorite_button.grid()
        self.favorite_button.configure(state="normal")

    def _hide_favorite_button(self):
        self.favorite_button.grid_remove()
        self.favorite_button.configure(state="disabled")

    def _update_favorite_button_state(self):
        if self.selected_idea is None:
            self.favorite_button.configure(
                state="disabled",
                text="☆",
                fg_color=INPUT_BG,
                border_color=ACCENT,
                text_color=ACCENT,
            )
            return

        if self.selected_idea["favorite"]:
            self.favorite_button.configure(
                state="normal",
                text="★",
                fg_color=ACCENT,
                hover_color=ACCENT_HOVER,
                border_color=ACCENT,
                text_color=APP_BG,
            )
        else:
            self.favorite_button.configure(
                state="normal",
                text="☆",
                fg_color=INPUT_BG,
                hover_color=CARD_BG,
                border_color=ACCENT,
                text_color=ACCENT,
            )

    def _clear_details_content(self):
        for widget in self.details_content.winfo_children():
            widget.destroy()

    def _show_empty_details_state(self):
        self._clear_details_content()
        placeholder = ctk.CTkLabel(
            self.details_content,
            text="Здесь будут показаны подробности выбранной идеи.",
            text_color=TEXT_PRIMARY,
            justify="left",
            anchor="w",
            wraplength=320,
            font=ui_font(14),
        )
        placeholder.pack(fill="x", padx=10, pady=8)

    def _add_section_title(self, parent, text: str):
        label = ctk.CTkLabel(
            parent,
            text=text,
            text_color=TEXT_PRIMARY,
            font=self.section_title_font,
            justify="left",
            anchor="w",
        )
        label.pack(fill="x", padx=8, pady=(8, 3))

    def _add_divider(self, parent):
        divider = ctk.CTkFrame(parent, height=1, fg_color=LINE_COLOR)
        divider.pack(fill="x", padx=8, pady=(4, 4))

    def _add_two_column_row(self, parent, left_text: str, right_text: str):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=0)

        row.grid_columnconfigure(0, minsize=96)
        row.grid_columnconfigure(1, weight=1)

        left_label = ctk.CTkLabel(
            row,
            text=left_text,
            text_color=TEXT_SECONDARY,
            anchor="w",
            justify="left",
            font=ui_font(13, "bold"),
        )
        left_label.grid(row=0, column=0, sticky="w", pady=0)

        right_label = ctk.CTkLabel(
            row,
            text=right_text,
            text_color=TEXT_PRIMARY,
            anchor="w",
            justify="left",
            wraplength=170,
            font=ui_font(13),
        )
        right_label.grid(row=0, column=1, sticky="w", padx=(6, 0), pady=0)

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_menu.set("Все статусы")
        self.readiness_menu.set("Вся проработка")
        self.mechanic_menu.set("Все механики")
        self.sort_menu.set("Сначала новые")
        self.current_sidebar_filter = "Все идеи"
        self._update_sidebar_button_styles()
        self._update_status_filter_style()
        self.apply_filters()

    def apply_filters(self):
        query = self.search_entry.get().strip()

        genre = None
        favorites_only = False

        if self.current_sidebar_filter == FAVORITES_LABEL:
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

        status_color = get_status_color(idea["status"])
        self.details_title.configure(
            text=idea["title"],
            text_color=status_color,
            font=self.section_title_font,
        )

        self._show_favorite_button()
        self._update_favorite_button_state()

        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")

        self._clear_details_content()
        self.update_idletasks()
        text_wrap = max(280, self.details_content.winfo_width() - 40)

        self._add_section_title(self.details_content, "Описание")
        description = ctk.CTkLabel(
            self.details_content,
            text=idea.get("short_description", "").strip() or "—",
            text_color=TEXT_PRIMARY,
            justify="left",
            anchor="w",
            wraplength=text_wrap,
            font=ui_font(14),
        )
        description.pack(fill="x", padx=8, pady=(0, 4))

        self._add_divider(self.details_content)

        self._add_section_title(self.details_content, "Параметры")
        self._add_two_column_row(self.details_content, "Жанр", idea["genre"])
        self._add_two_column_row(self.details_content, "Статус", idea["status"])
        self._add_two_column_row(self.details_content, "Механика", idea["mechanic"])
        self._add_two_column_row(self.details_content, "Масштаб", idea["scale"])
        self._add_two_column_row(self.details_content, "Перспектива", idea["perspective"])
        self._add_two_column_row(self.details_content, "Платформа", idea["platform"])
        self._add_two_column_row(self.details_content, "Проработка", idea["readiness"])
        self._add_two_column_row(
            self.details_content,
            "Теги",
            ", ".join(idea["tags"]) if idea["tags"] else "Нет",
        )
        self._add_two_column_row(
            self.details_content,
            "Избранное",
            "Да" if idea["favorite"] else "Нет",
        )

        self._add_divider(self.details_content)

        self._add_section_title(self.details_content, "Служебное")
        self._add_two_column_row(self.details_content, "Дата создания", idea["created_at"])
        self._add_two_column_row(self.details_content, "Дата изменения", idea["updated_at"])

        self._add_divider(self.details_content)

        self._add_section_title(self.details_content, "Заметки")
        notes = ctk.CTkLabel(
            self.details_content,
            text=idea["notes"] or "—",
            text_color=TEXT_PRIMARY,
            justify="left",
            anchor="w",
            wraplength=text_wrap,
            font=ui_font(14),
        )
        notes.pack(fill="x", padx=8, pady=(0, 4))

    def clear_details(self):
        self.selected_idea = None
        self.details_title.configure(
            text="Карточка идеи",
            text_color=TEXT_PRIMARY,
            font=self.section_title_font,
        )
        self.edit_button.configure(state="disabled")
        self.delete_button.configure(state="disabled")
        self._hide_favorite_button()
        self._update_favorite_button_state()
        self._show_empty_details_state()

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
            f'Удалить идею "{self.selected_idea["title"]}"?',
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

    def export_filtered_ideas(self):
        if not self.filtered_ideas:
            messagebox.showwarning("Экспорт", "Нет идей для экспорта.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Сохранить экспорт идей",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile="idailyx_export.txt",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("IDailyx — экспорт идей\n")
                file.write("=" * 40 + "\n\n")

                for index, idea in enumerate(self.filtered_ideas, start=1):
                    file.write(f"{index}. {idea['title']}\n")
                    file.write(f"   Описание: {idea.get('short_description', '').strip() or '—'}\n")
                    file.write(f"   Жанр: {idea['genre']}\n")
                    file.write(f"   Статус: {idea['status']}\n")
                    file.write(f"   Механика: {idea['mechanic']}\n")
                    file.write(f"   Масштаб: {idea['scale']}\n")
                    file.write(f"   Перспектива: {idea['perspective']}\n")
                    file.write(f"   Платформа: {idea['platform']}\n")
                    file.write(f"   Проработка: {idea['readiness']}\n")
                    file.write(f"   Теги: {', '.join(idea['tags']) if idea['tags'] else 'Нет'}\n")
                    file.write(f"   Избранное: {'Да' if idea['favorite'] else 'Нет'}\n")
                    file.write(f"   Дата создания: {idea['created_at']}\n")
                    file.write(f"   Дата изменения: {idea['updated_at']}\n")
                    file.write(f"   Заметки: {idea['notes'] if idea['notes'] else 'Нет'}\n")
                    file.write("\n" + "-" * 40 + "\n\n")

            messagebox.showinfo("Экспорт", "Идеи успешно экспортированы в .txt")
        except OSError as error:
            messagebox.showerror("Ошибка экспорта", f"Не удалось сохранить файл:\n{error}")
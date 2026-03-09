import customtkinter as ctk

FONT_FAMILY = "Segoe UI"


def ui_font(size: int = 14, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


APP_BG = "#1F1A17"
PANEL_BG = "#2B2420"
CARD_BG = "#342D28"
INPUT_BG = "#3A332D"
CARD_BORDER = "#5C4F45"
LINE_COLOR = "#53463D"

TEXT_PRIMARY = "#F3E8D8"
TEXT_SECONDARY = "#D9C6AE"
TEXT_MUTED = "#A7937D"

ACCENT = "#D39A63"
ACCENT_HOVER = "#E0AC7B"

BUTTON_NEUTRAL = "#91A4A0"
BUTTON_NEUTRAL_HOVER = "#A2B4B0"

DANGER = "#C28770"
DANGER_HOVER = "#D39881"

FAVORITE = "#D39A63"
FAVORITE_HOVER = "#E0AC7B"

SIDEBAR_BUTTON = "#342D28"
SIDEBAR_BUTTON_HOVER = "#3E3630"
SIDEBAR_ACTIVE = "#4A4038"
SIDEBAR_ACTIVE_HOVER = "#584B41"

STATUS_COLORS = {
    "новая": "#F3E8D8",
    "в работе": "#D39A63",
    "заморожена": "#9FB5C1",
    "завершена": "#97B27A",
}


def get_status_color(status: str) -> str:
    return STATUS_COLORS.get(status, TEXT_MUTED)


def get_status_text_color(status: str) -> str:
    return APP_BG


def get_sidebar_button_colors(is_active: bool) -> tuple[str, str]:
    if is_active:
        return SIDEBAR_ACTIVE, SIDEBAR_ACTIVE_HOVER
    return SIDEBAR_BUTTON, SIDEBAR_BUTTON_HOVER
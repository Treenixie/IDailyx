import customtkinter as ctk

FONT_FAMILY = "Segoe UI"


def ui_font(size: int = 14, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family=FONT_FAMILY, size=size, weight=weight)


# База интерфейса: перевод из тёплого коричневого в тёмный серо-синий
APP_BG = "#1C2128"
PANEL_BG = "#242B34"
CARD_BG = "#2B333D"
INPUT_BG = "#313A45"
CARD_BORDER = "#4A5866"
LINE_COLOR = "#42505D"

# Текст: мягкий тёплый светлый, как на референсе
TEXT_PRIMARY = "#F3DFC2"
TEXT_SECONDARY = "#D7C1A2"
TEXT_MUTED = "#A9967D"

# Основные акцентные кнопки: оранжевый
ACCENT = "#D88E57"
ACCENT_HOVER = "#E39D6A"

# Нейтральные фильтры и селекты: светло-голубой
BUTTON_NEUTRAL = "#A9CDD6"
BUTTON_NEUTRAL_HOVER = "#B8D9E1"

# Опасные действия: красный
DANGER = "#D46A57"
DANGER_HOVER = "#DF7A68"

# Избранное можно оставить в оранжевой гамме
FAVORITE = "#D88E57"
FAVORITE_HOVER = "#E39D6A"

# Кнопки в боковой панели
SIDEBAR_BUTTON = "#313844"
SIDEBAR_BUTTON_HOVER = "#39424E"
SIDEBAR_ACTIVE = "#4B5866"
SIDEBAR_ACTIVE_HOVER = "#596878"

# Цвета статусов
STATUS_COLORS = {
    "новая": "#F3DFC2",
    "в работе": "#D88E57",
    "заморожена": "#8FC6D4",
    "завершена": "#8FAE73",
}


def get_status_color(status: str) -> str:
    return STATUS_COLORS.get(status, TEXT_MUTED)


def get_status_text_color(status: str) -> str:
    return APP_BG


def get_sidebar_button_colors(is_active: bool) -> tuple[str, str]:
    if is_active:
        return SIDEBAR_ACTIVE, SIDEBAR_ACTIVE_HOVER
    return SIDEBAR_BUTTON, SIDEBAR_BUTTON_HOVER
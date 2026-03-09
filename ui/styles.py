APP_BG = "#16181d"
PANEL_BG = "#1d2128"
CARD_BG = "#242936"
CARD_BORDER = "#2f3645"

TEXT_PRIMARY = "#f3f4f6"
TEXT_SECONDARY = "#aeb7c5"
TEXT_MUTED = "#8b95a7"

ACCENT = "#2f6db2"
ACCENT_HOVER = "#3c7ccc"

DANGER = "#8B3A3A"
DANGER_HOVER = "#A04444"

FAVORITE = "#8A6A1F"
FAVORITE_HOVER = "#A68028"

BUTTON_NEUTRAL = "#3a3f4b"
BUTTON_NEUTRAL_HOVER = "#4a5160"

SIDEBAR_BUTTON = "#242936"
SIDEBAR_BUTTON_HOVER = "#2d3442"

STATUS_COLORS = {
    "новая": "#3B82F6",
    "в работе": "#22C55E",
    "заморожена": "#F59E0B",
    "завершена": "#A855F7",
}


def get_status_color(status: str) -> str:
    return STATUS_COLORS.get(status, TEXT_MUTED)


def get_sidebar_button_colors(is_active: bool) -> tuple[str, str]:
    if is_active:
        return ACCENT, ACCENT_HOVER
    return SIDEBAR_BUTTON, SIDEBAR_BUTTON_HOVER
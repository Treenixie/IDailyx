import os
import ctypes
import tkinter as tk

from PIL import Image, ImageTk

from core.paths import get_asset_path


DEFAULT_APP_ID = "Treenixie.IDailyx"


def set_app_user_model_id(app_id: str = DEFAULT_APP_ID):
    if os.name != "nt":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def apply_windows_dark_title_bar(window):
    if os.name != "nt":
        return

    try:
        window.update_idletasks()
        hwnd = window.winfo_id()
    except Exception:
        return

    value = ctypes.c_int(1)

    for attribute in (20, 19):
        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd,
                attribute,
                ctypes.byref(value),
                ctypes.sizeof(value),
            )
            break
        except Exception:
            continue


def _apply_iconbitmap(window):
    icon_ico_path = get_asset_path("icon.ico")
    if not icon_ico_path:
        return

    try:
        window.iconbitmap(icon_ico_path)
    except Exception:
        try:
            window.iconbitmap(default=icon_ico_path)
        except Exception:
            pass


def _apply_iconphoto(window):
    icon_png_path = get_asset_path("icon.png")
    if not icon_png_path:
        return

    try:
        pil_image = Image.open(icon_png_path)
        photo = ImageTk.PhotoImage(pil_image)

        # Сохраняем ссылку, чтобы иконка не исчезла из-за сборщика мусора
        window._idailyx_icon_photo = photo

        window.iconphoto(True, photo)
    except Exception:
        pass


def _apply_icon_once(window, app_id: str):
    if os.name != "nt":
        return

    set_app_user_model_id(app_id)

    try:
        window.update_idletasks()
    except Exception:
        pass

    _apply_iconbitmap(window)
    _apply_iconphoto(window)
    apply_windows_dark_title_bar(window)


def apply_window_icon(window, app_id: str = DEFAULT_APP_ID):
    if os.name != "nt":
        return

    # Первый проход
    _apply_icon_once(window, app_id)

    # Повторяем позже, потому что CustomTkinter любит
    # поверх нашей иконки снова воткнуть свою синюю дефолтную.
    try:
        window.after(100, lambda: _apply_icon_once(window, app_id))
        window.after(300, lambda: _apply_icon_once(window, app_id))
    except Exception:
        pass
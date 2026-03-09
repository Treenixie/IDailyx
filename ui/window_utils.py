import os
import ctypes
from typing import Iterable

from PIL import Image, ImageTk


DEFAULT_APP_ID = "Treenixie.IDailyx"


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_asset_path(filename: str) -> str | None:
    root = get_project_root()
    candidates = [
        os.path.join(root, "assets", filename),
        os.path.join(root, filename),
    ]

    for path in candidates:
        if os.path.exists(path):
            return path

    return None


def set_app_user_model_id(app_id: str = DEFAULT_APP_ID):
    if os.name != "nt":
        return

    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception as exc:
        print(f"[IDailyx] AppUserModelID error: {exc}")


def _iter_icon_candidates(filenames: Iterable[str]) -> list[str]:
    result: list[str] = []

    for filename in filenames:
        path = get_asset_path(filename)
        if path and path not in result:
            result.append(path)

    return result


def apply_window_icon(window, delay_ms: int = 0):
    icon_candidates = _iter_icon_candidates(("icon.ico", "icon.png", "logo.png"))

    if not icon_candidates:
        print("[IDailyx] Icon file not found")
        return

    if os.name == "nt":
        set_app_user_model_id()

    if hasattr(window, "_iconbitmap_method_called"):
        try:
            window._iconbitmap_method_called = True
        except Exception:
            pass

    for icon_path in icon_candidates:
        try:
            pil_icon = Image.open(icon_path)
            window._window_icon_photo = ImageTk.PhotoImage(pil_icon)
            window.iconphoto(True, window._window_icon_photo)
            break
        except Exception as exc:
            print(f"[IDailyx] iconphoto error for {os.path.basename(icon_path)}: {exc}")
    else:
        window._window_icon_photo = None

    if os.name != "nt":
        return

    icon_ico_path = get_asset_path("icon.ico")
    if not icon_ico_path:
        print("[IDailyx] icon.ico not found for Windows title bar")
        return

    def _apply_iconbitmap():
        try:

            window.iconbitmap(icon_ico_path)
        except Exception as first_error:
            try:

                window.iconbitmap(default=icon_ico_path)
            except Exception as second_error:
                print(
                    "[IDailyx] iconbitmap error: "
                    f"{first_error}; fallback error: {second_error}"
                )

    delays = [
        max(delay_ms, 250),
        max(delay_ms, 500),
        max(delay_ms, 900),
    ]

    for ms in delays:
        try:
            window.after(ms, _apply_iconbitmap)
        except Exception as exc:
            print(f"[IDailyx] after({ms}) icon apply error: {exc}")
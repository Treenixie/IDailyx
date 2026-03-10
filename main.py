import os
import sys
from pathlib import Path

from core.idea_manager import IdeaManager
from core.storage import load_ideas, ensure_data_file
from core.paths import (
    get_ideas_file_path,
    get_legacy_ideas_file_path,
    get_old_appdata_ideas_file_path,
)


DATA_FILE = str(get_ideas_file_path())


def configure_tk_environment():
    if getattr(sys, "frozen", False):
        return

    tcl_root = Path(sys.base_prefix) / "tcl"

    if not tcl_root.is_dir():
        os.environ.pop("TCL_LIBRARY", None)
        os.environ.pop("TK_LIBRARY", None)
        return

    tcl_dir = None
    tk_dir = None

    for folder in tcl_root.iterdir():
        if not folder.is_dir():
            continue

        if folder.name.startswith("tcl8"):
            tcl_dir = folder
        elif folder.name.startswith("tk8"):
            tk_dir = folder

    if tcl_dir is not None:
        os.environ["TCL_LIBRARY"] = str(tcl_dir)
    else:
        os.environ.pop("TCL_LIBRARY", None)

    if tk_dir is not None:
        os.environ["TK_LIBRARY"] = str(tk_dir)
    else:
        os.environ.pop("TK_LIBRARY", None)


def migrate_ideas_file() -> None:
    current_file = get_ideas_file_path()

    if current_file.exists():
        return

    current_file.parent.mkdir(parents=True, exist_ok=True)

    migration_sources = [
        get_old_appdata_ideas_file_path(),
        get_legacy_ideas_file_path(),
    ]

    for source_file in migration_sources:
        try:
            if source_file.exists() and source_file.resolve() != current_file.resolve():
                current_file.write_text(
                    source_file.read_text(encoding="utf-8"),
                    encoding="utf-8",
                )
                return
        except OSError:
            continue


configure_tk_environment()

from ui.main_window import MainWindow
from ui.window_utils import set_app_user_model_id


def bootstrap_data():
    migrate_ideas_file()
    ensure_data_file(DATA_FILE)
    return load_ideas(DATA_FILE)


if __name__ == "__main__":
    set_app_user_model_id("Treenixie.IDailyx")

    ideas = bootstrap_data()
    manager = IdeaManager(ideas)

    app = MainWindow(manager, DATA_FILE)
    app.mainloop()
import os
import sys

from core.idea_manager import IdeaManager
from core.storage import load_ideas, ensure_data_file
from core.paths import get_ideas_file_path, get_legacy_ideas_file_path


DATA_FILE = str(get_ideas_file_path())


def configure_tk_environment():
    if "TCL_LIBRARY" in os.environ and "TK_LIBRARY" in os.environ:
        return

    tcl_root = os.path.join(sys.base_prefix, "tcl")

    if not os.path.isdir(tcl_root):
        return

    tcl_dir = None
    tk_dir = None

    for folder_name in os.listdir(tcl_root):
        full_path = os.path.join(tcl_root, folder_name)

        if not os.path.isdir(full_path):
            continue

        if folder_name.startswith("tcl8"):
            tcl_dir = full_path
        elif folder_name.startswith("tk8"):
            tk_dir = full_path

    if tcl_dir:
        os.environ["TCL_LIBRARY"] = tcl_dir

    if tk_dir:
        os.environ["TK_LIBRARY"] = tk_dir


def migrate_legacy_ideas_file() -> None:
    legacy_file = get_legacy_ideas_file_path()
    current_file = get_ideas_file_path()

    if current_file.exists() or not legacy_file.exists():
        return

    current_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        current_file.write_text(
            legacy_file.read_text(encoding="utf-8"),
            encoding="utf-8"
        )
    except OSError:
        pass


configure_tk_environment()

from ui.main_window import MainWindow
from ui.window_utils import set_app_user_model_id


def bootstrap_data():
    migrate_legacy_ideas_file()
    ensure_data_file(DATA_FILE)
    return load_ideas(DATA_FILE)


if __name__ == "__main__":
    set_app_user_model_id("Treenixie.IDailyx")

    ideas = bootstrap_data()
    manager = IdeaManager(ideas)

    app = MainWindow(manager, DATA_FILE)
    app.mainloop()